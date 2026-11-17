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
| POST | `/tickets/{id}/analyze` | – | *Dev B* | 503 model down, 502 bad output |
| GET | `/tickets/{id}/suggestions` | – | *Dev B* | |
| POST | `/tickets/{id}/feedback` | *Dev B* | *Dev B* | |

## Error formats (important for the frontend)
- **422** → `detail` is a **list**: `[{"loc": ["body", "title"], "msg": "...", "type": "..."}]`. The last item of `loc` is the field name, so show `msg` next to that field.
- **404 / 409 / 502 / 503** → `detail` is a **string**: `{"detail": "Ticket 42 not found"}`. Show it as a message.

## History rows (`/tickets/{id}/history`)
`action` is one of: `created`, `updated`, `status_change`, `priority_change`, `category_change`, `comment`.
Status changes fill `old_status` and `new_status`; comments use `note`; `actor` is the staff member's name.