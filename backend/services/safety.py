"""Safety helpers for anything that goes to the AI model or into the logs.

1. redact_secrets()      - hides passwords, API keys, tokens and credentials in URLs.
2. neutralize_injection() - removes instruction-like text from untrusted ticket content
                            so it cannot override the application's rules.
"""
import re

REDACTED = "[REDACTED]"
REMOVED = "[instruction-like text removed]"

# Each pattern keeps the label (group 1) and hides the secret value.
_SECRET_PATTERNS = [
    # password: abc / pwd=abc / passcode is abc / api key: abc / token = abc
    re.compile(
        r"(?i)\b((?:password|passwd|pwd|passcode|secret|api[ _-]?key|access[ _-]?key|"
        r"token|auth[ _-]?token|client[ _-]?secret)s?\s*(?:\bis\b|\bwas\b|=|:)\s*)"
        r"(?!\[REDACTED\])(?!(?:not|now|expired|wrong|incorrect|locked|invalid|reset|correct)\b)"
        r"[\"']?[^\s\"',;]{3,}"
    ),
    # Bearer tokens
    re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._\-~+/]{8,}=*"),
]
# Credentials inside URLs: scheme://user:password@host
_URL_CREDENTIALS = re.compile(r"(?i)\b([a-z][a-z0-9+.\-]*://[^\s:/@]+:)[^\s@/]+(@)")
# Well-known key formats that need no label
_KNOWN_KEYS = re.compile(
    r"\b(?:sk-[A-Za-z0-9_\-]{16,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"xox[abpr]-[A-Za-z0-9\-]{10,}|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]+)"
)


def redact_secrets(text: str | None) -> str | None:
    if not text:
        return text
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(lambda m: m.group(1) + REDACTED, text)
    text = _URL_CREDENTIALS.sub(lambda m: m.group(1) + REDACTED + m.group(2), text)
    text = _KNOWN_KEYS.sub(REDACTED, text)
    return text


# Phrases that try to talk to the model instead of describing an IT problem.
_INJECTION_PATTERNS = [
    r"\b(?:ignore|disregard|forget|override|bypass)\b[^.!?\n]{0,40}\b(?:instructions?|rules?|prompts?|guidelines?|above|previous|prior|system)\b",
    r"\byou are (?:now|no longer)\b",
    r"\b(?:act|behave|pretend|roleplay) (?:as|like)\b",
    r"\bnew (?:instructions?|rules?|role)\b",
    r"\bsystem prompt\b",
    r"\b(?:set|change|make|mark|update|classify|rate)\b[^.!?\n]{0,30}\b(?:priority|status|category|severity)\b[^.!?\n]{0,20}\b(?:to|as|=)\b",
    r"\b(?:resolve|close|mark)\b[^.!?\n]{0,15}\b(?:this|the) ticket\b[^.!?\n]{0,25}\b(?:resolved|closed|done)?",
    r"\b(?:respond|reply|answer|output|return)\b[^.!?\n]{0,20}\b(?:only|with|in)\b[^.!?\n]{0,20}\b(?:json|yes|no|priority|category)\b",
    r"</?\s*(?:ticket|system|assistant|user|instructions?)\s*>",
    r"^\s*(?:system|assistant)\s*:",
]
_INJECTION_RE = re.compile("|".join(f"(?:{p})" for p in _INJECTION_PATTERNS), re.IGNORECASE | re.MULTILINE)
# Split into sentences/lines so we remove only the offending sentence.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def neutralize_injection(text: str) -> tuple[str, bool]:
    """Return (clean_text, flagged). Sentences containing instructions aimed at the
    model are replaced with a placeholder; the technical description is kept."""
    if not text:
        return text, False
    flagged = False
    kept = []
    for sentence in _SENTENCE_SPLIT.split(text):
        if not sentence.strip():
            continue
        if _INJECTION_RE.search(sentence):
            flagged = True
            if not kept or kept[-1] != REMOVED:
                kept.append(REMOVED)
        else:
            kept.append(sentence.strip())
    return " ".join(kept), flagged


def prepare_untrusted(text: str, max_chars: int) -> tuple[str, bool]:
    """Redact secrets, strip injection attempts and cap the length."""
    clean, flagged = neutralize_injection(redact_secrets(text) or "")
    if len(clean) > max_chars:
        clean = clean[:max_chars] + " [truncated]"
    return clean, flagged
