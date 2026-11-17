# API Contract: AI Employee Helpdesk

Base URL: `http://127.0.0.1:8000`. Interactive docs: `/docs`

## Allowed values
- **Status:** `New`, `In Progress`, `Resolved`
- **Priority:** `Low`, `Medium`, `High`
- **Category:** `Hardware`, `Software`, `Network`, `Access`, `Other`

New tickets always start as `New` / `Medium`. Category defaults to `Other` if not given.

## Status rules
| From | Allowed to |
|---|---|
| New | In Progress |
| In Progress | Resolved |
| Resolved | In Progress (reopen) |

Any other change returns **409**.

## Endpoints
| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| GET | `/requesters` | – | 200 list | – |
| POST | `/tickets` | `requester_id`, `title` (min 5), `description` (min 10), `category` (optional) | 201 ticket | 422 |
| GET | `/tickets?status=&category=&priority=&requester_id=` | – | 200 list (newest first) | 422 bad filter value |
| GET | `/tickets/{id}` | – | 200 ticket | 404 |
| PATCH | `/tickets/{id}` | any of `title`, `description`, `category` | 200 ticket | 404, 422 (other fields rejected) |
| GET | `/tickets/{id}/history` | – | 200 list (oldest first) | 404 |
| PATCH | `/tickets/{id}/status` | `status`, `actor` (opt), `note` (opt) | 200 ticket | 404, 409, 422 |
| PATCH | `/tickets/{id}/priority` | `priority`, `actor` (opt), `note` (opt) | 200 ticket | 404, 422 |
| POST | `/tickets/{id}/comments` | `note` (min 2), `actor` (opt) | 201 activity | 404, 422 |
| GET | `/dashboard/summary` | – | 200 `{total, by_status, by_priority}` | – |
| GET | `/ai/status` | – | 200 `{available, model, model_installed, detail}` | – |
| POST | `/tickets/{id}/analyze` | – | 201 suggestion | 404, 502 bad model output, 503 model down/timeout |
| GET | `/tickets/{id}/suggestions` | – | 200 list (newest first), each with latest `feedback` or `null` | 404 |
| POST | `/tickets/{id}/feedback` | `suggestion_id`, `useful` (bool), `final_category`, `final_priority`, `actor` (opt), `comment` (opt) | 201 feedback | 404 (ticket or suggestion), 422 |

## Error formats (important for the frontend)
- **422** → `detail` is a **list**: `[{"loc": ["body", "title"], "msg": "...", "type": "..."}]`. The last item of `loc` is the field name, so show `msg` next to that field.
- **404 / 409 / 502 / 503** → `detail` is a **string**: `{"detail": "Ticket 42 not found"}`. Show it as a message.

## History rows (`/tickets/{id}/history`)
`action` is one of: `created`, `updated`, `status_change`, `priority_change`, `category_change`, `comment`.
Status changes fill `old_status` and `new_status`; comments use `note`; `actor` is the staff member's name.

## AI suggestion (`/analyze`, `/suggestions`)
```json
{
  "id": 3, "ticket_id": 8,
  "suggested_category": "Network", "suggested_priority": "High",
  "priority_reason": "A whole department cannot reach the file share.",
  "troubleshooting_steps": ["Check the file server is online", "..."],
  "model_name": "llama3.2:3b",
  "input_flagged": false,
  "created_at": "2026-11-17T10:42:19+05:30",
  "feedback": null
}
```
- Show `suggested_*` **separately** from the ticket's own `category` / `priority` (those are the staff-confirmed values).
- `input_flagged: true` means instruction-like text was removed from the ticket before analysis. Show a small warning.
- Analysis never changes the ticket. A 502/503 saves nothing; show `detail` and let staff carry on manually.
- Analysis takes about 10-20 s on a laptop CPU, so show a loading state.

## Feedback (`/feedback`)
- Send the staff's **final** values. `accepted` is set by the server: `true` if both equal the suggestion.
- The ticket's `category` / `priority` are updated to the final values and `category_change` / `priority_change` history rows are added. Status is never changed.
- `status` or any unknown field in the body is rejected with 422.