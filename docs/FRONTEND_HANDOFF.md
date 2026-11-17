# Frontend handoff (for Dev C)

Everything you need to build the React app against the backend. Detailed rules are in `API_CONTRACT.md`, and live docs are at http://127.0.0.1:8000/docs once the backend runs.

---

## 1. What you get (and what you don't)

| Item | Where |
|---|---|
| Code | GitHub repo `helpdesk`, branch `ai-integration` (or `main` once merged) |
| Setup steps | `Readme.md` (backend, PostgreSQL, Ollama) |
| Endpoint list, rules, error formats | `API_CONTRACT.md` |
| OpenAPI spec (for codegen or Postman import, optional) | `docs/openapi.json` |
| Sample data | `db/seed.sql` (6 employees, 7 tickets) |

**Not shared:** `backend/.env`. It holds each person's own PostgreSQL password. Create your own from `backend/.env.example`.

No API keys exist anywhere. Ollama is local and free, and the backend has no login.

---

## 2. Run the backend on your machine (one-time setup)

You need: **Python 3.11+**, **PostgreSQL 15+**, **Ollama**, and **Node 18+** for React.

```
# 1. Databases (pgAdmin or terminal)
createdb -U postgres helpdesk
createdb -U postgres helpdesk_test        # only needed to run pytest

# 2. Python environment (from the project root)
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt

# 3. Config
copy backend\.env.example backend\.env
#    -> put YOUR postgres password in DATABASE_URL and TEST_DATABASE_URL
#    -> if the password has @ # / : %, encode it (@ = %40, # = %23, ...)

# 4. Tables + sample data
cd backend
alembic upgrade head
psql -U postgres -d helpdesk -f ../db/seed.sql

# 5. Local AI model
ollama pull llama3.2:3b                   # ~2 GB, one time

# 6. Start the API (keep this terminal open)
uvicorn main:app --reload
```

Checks:
- http://127.0.0.1:8000/docs opens Swagger
- http://127.0.0.1:8000/db-check shows `"database": "connected"`
- http://127.0.0.1:8000/ai/status shows `"available": true` (if not, start Ollama from the Start menu)

---

## 3. Connection settings for React

| Setting | Value |
|---|---|
| API base URL | `http://127.0.0.1:8000` (put it in a Vite env var, e.g. `VITE_API_URL`) |
| Allowed frontend origin (CORS) | `http://localhost:5173`, the Vite default |
| Body format | JSON, `Content-Type: application/json` |
| Auth | None |

**CORS gotcha:** the backend only accepts requests from the origin in `FRONTEND_URL` in `backend/.env` (default `http://localhost:5173`). If you open the app as `http://127.0.0.1:5173`, or use another port (CRA uses 3000), the browser blocks the calls. Either open it at exactly `http://localhost:5173`, or change `FRONTEND_URL` and restart uvicorn.

---

## 4. Fixed values (use for dropdowns and filters)

| Field | Values |
|---|---|
| Status | `New`, `In Progress`, `Resolved` |
| Priority | `Low`, `Medium`, `High` |
| Category | `Hardware`, `Software`, `Network`, `Access`, `Other` |

New tickets always start as `New` / `Medium`. If no category is given, it is `Other`.

**Status moves allowed** (others return 409). Show only these buttons:

| Current | Buttons to show |
|---|---|
| New | Start → `In Progress` |
| In Progress | Resolve → `Resolved` |
| Resolved | Reopen → `In Progress` |

---

## 5. Who is the user? (no login)

- **Employee view:** call `GET /requesters` and let the user pick themselves from a dropdown, e.g. "Priya Raman (Finance)". Use that `id` as `requester_id`. Remembering it in `localStorage` is a nice touch.
- **Support view:** a "Staff name" text box (e.g. `Support - Anil`). Send it as `actor` on status, priority, comment and feedback calls so the history shows who did what.

Seed employees: IDs 1-6 (Priya Raman, Arjun Mehta, Kavya Iyer, Rahul Nair, Sneha Kapoor, Vikram Rao).

---

## 6. Screens → endpoints

### Employee
| Screen | Call |
|---|---|
| Raise ticket | `POST /tickets` `{requester_id, title, description, category?}` → 201 ticket |
| My tickets | `GET /tickets?requester_id={id}`, showing id, category, priority, status, created_at |
| Ticket details | `GET /tickets/{id}` + `GET /tickets/{id}/history`. Comments are the history rows with `action = "comment"` |

Validation: `title` needs at least 5 characters (max 200) and `description` at least 10.

### Support staff
| Screen | Call |
|---|---|
| Dashboard counts | `GET /dashboard/summary` → `{total, by_status:{New,..}, by_priority:{Low,..}}` |
| Work queue + filters | `GET /tickets?status=&category=&priority=` (omit empty filters) |
| Open ticket | `GET /tickets/{id}`, `GET /tickets/{id}/history`, `GET /tickets/{id}/suggestions` |
| Change status | `PATCH /tickets/{id}/status` `{status, actor?, note?}` |
| Change priority | `PATCH /tickets/{id}/priority` `{priority, actor?, note?}` |
| Add support note | `POST /tickets/{id}/comments` `{note, actor?}` |
| Edit title/description/category | `PATCH /tickets/{id}` `{title?, description?, category?}` |
| AI badge | `GET /ai/status` → `{available, model, detail}` |
| Run AI | `POST /tickets/{id}/analyze` (no body) → 201 suggestion |
| AI feedback | `POST /tickets/{id}/feedback` (see section 8) |

History rows: `action` is `created`, `updated`, `status_change`, `priority_change`, `category_change` or `comment`. Status changes have `old_status` / `new_status`, and every row has `note`, `actor` and `created_at`. The list is oldest first.

`GET /tickets` returns `requester_id` only. To show the requester's name, look it up in the `GET /requesters` list.

---

## 7. Error handling (show the backend's message, don't invent your own)

| Code | `detail` shape | What to show |
|---|---|---|
| 422 | **list** `[{"loc":["body","title"],"msg":"String should have at least 5 characters"}]` | `msg` under the field named by the last item of `loc` |
| 404 | string | Message, e.g. "Ticket 42 not found" |
| 409 | string | Message, e.g. "Cannot change status from New to Resolved..." |
| 502 | string | AI gave a bad answer: show message + "Try again" |
| 503 | string | AI offline: show message; the rest of the page must keep working |

```js
const err = await res.json();
if (Array.isArray(err.detail)) {
  err.detail.forEach(e => setFieldError(e.loc.at(-1), e.msg));
} else {
  showBanner(err.detail);
}
```

---

## 8. AI panel (support ticket page)

**Suggestion object** (from `/analyze` and each item of `/suggestions`, newest first):
```json
{
  "id": 3, "ticket_id": 8,
  "suggested_category": "Network",
  "suggested_priority": "High",
  "priority_reason": "Whole department is blocked from the file share.",
  "troubleshooting_steps": ["Check the file server is online", "Check DNS for the share", "..."],
  "model_name": "llama3.2:3b",
  "input_flagged": false,
  "created_at": "2026-11-17T09:28:03+05:30",
  "feedback": null
}
```

Rules for the UI:
1. **Keep the AI separate.** Show "AI suggestion" (suggested_*) in its own box, clearly apart from the ticket's real `category` / `priority` (the staff-confirmed values). Never write AI values into the ticket automatically.
2. **Loading:** analysis takes **15-20 s** (longer on the first call). Show a spinner and disable the button while it runs.
3. **Failure:** on 503 or 502, show `detail` in the AI box only. Ticket editing must still work.
4. **`input_flagged: true`:** show a small warning such as "Ticket text contained instructions aimed at the AI; they were ignored."
5. **Steps** are an array; render them as a numbered list.
6. **Status** has no AI button. The AI never resolves tickets.

**Feedback form** (shown when `feedback` is `null`, prefilled with the suggested values):
```
POST /tickets/{id}/feedback
{
  "suggestion_id": 3,
  "useful": true,                    // Useful / Not useful toggle
  "final_category": "Network",       // staff's final choice
  "final_priority": "High",
  "actor": "Support - Anil",         // optional
  "comment": "Confirmed with Finance" // optional
}
```
- "Accept" sends the suggested values unchanged. "Correct" lets staff change the dropdowns first.
- The response has `accepted: true/false`, computed by the backend.
- After saving, re-fetch the ticket, history and suggestions. The ticket's category and priority now show the final values, history has `category_change` / `priority_change` rows, and the suggestion's `feedback` is filled in, so you can show "AI said X / staff chose Y ✓ useful".

---

## 9. The six demo scenarios (all must be shown in the React app)

| # | What to click | Expected |
|---|---|---|
| 01 Routine | Employee raises "Wireless keyboard not working" → staff opens it → Analyze | Hardware, Low/Medium, keyboard steps |
| 02 Outage | Raise "Finance department cannot open the shared drive, month-end blocked" → Analyze | Network / **High** |
| 03 Correction | Change the AI's values in the feedback form, mark Not useful, save, press F5 | AI and staff values both still shown |
| 04 AI down | Quit Ollama (tray icon → Quit), then create, list and update tickets; press Analyze | Tickets work; AI box shows the 503 message |
| 05 Invalid | Submit with a 3-letter title / empty description | Field errors from FastAPI's 422 |
| 06 Persistence | Stop uvicorn (Ctrl+C), start it again, F5 | Tickets, history, comments and feedback all still there |

The README needs a **Frontend setup** section and a **Demo walkthrough** section from you (the headings are already there).

---

## 10. Who to ask
- Tickets, workflow, dashboard, database: Dev A
- AI, feedback, `/ai/status`, logging, CORS/config: Dev B
