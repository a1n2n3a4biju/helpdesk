# AI-Powered Employee Helpdesk

Employees raise IT tickets; support staff review, update and resolve them. A local AI model (Ollama) suggests category, priority and troubleshooting steps. The AI is advisory only: staff make every final decision.

**Stack:** React (frontend) → FastAPI (backend) → PostgreSQL (database), with Ollama for local AI.

```
helpdesk/
  backend/   FastAPI app, Alembic migrations, tests
  db/        seed.sql (sample data), queries.sql (demo SQL)
  frontend/  React app
```

---

## Backend and database setup

### Requirements
- Python 3.11 or newer
- PostgreSQL 15 or newer (pgAdmin optional)

### 1. Create two databases
`helpdesk` (the app) and `helpdesk_test` (automated tests only).

- **pgAdmin:** right-click **Databases → Create → Database…**, name `helpdesk`, Save. Repeat for `helpdesk_test`.
- **Terminal:** `createdb -U postgres helpdesk` and `createdb -U postgres helpdesk_test`

### 2. Install the backend
From the project root (`helpdesk`):
```
python -m venv venv
venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
pip install -r backend/requirements.txt
```

### 3. Configure
Copy `backend/.env.example` to `backend/.env` and put your PostgreSQL password in both URLs.

If your password contains special characters, encode them: `@` → `%40`, `#` → `%23`, `/` → `%2F`, `:` → `%3A`, `%` → `%25`.

Never commit `.env`. It is listed in `.gitignore`.

### 4. Create the tables
```
cd backend
alembic upgrade head
```
This creates `requesters`, `tickets`, `ticket_activity`, `ai_suggestions` and `ai_feedback`, with primary keys, foreign keys and CHECK constraints on status, priority and category.

### 5. Load sample data
**Warning:** this empties all tables first.

- **pgAdmin:** select the `helpdesk` database → **Tools → Query Tool** → open `db/seed.sql` → press **F5**.
- **Terminal:** `psql -U postgres -d helpdesk -f db/seed.sql`

Loads 6 requesters and 7 tickets with status history and support comments.

### 6. Run the backend
From `backend`, with the venv active:
```
uvicorn main:app --reload
```
- API: http://127.0.0.1:8000
- Interactive API docs (Swagger): http://127.0.0.1:8000/docs
- Database check: http://127.0.0.1:8000/db-check

See `API_CONTRACT.md` for all endpoints, rules and error formats.

### 7. Run the tests
Create the tables in the test database once (PowerShell, from `backend`):
```
$env:DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/helpdesk_test"
alembic upgrade head
Remove-Item Env:DATABASE_URL
```
Then:
```
pytest -v
```
Each test runs inside a transaction that is rolled back, so the test database stays empty and the main database is never touched.

### Demo SQL
`db/queries.sql` contains:
1. A JOIN returning each ticket with its requester details and latest status from the history table.
2. Aggregate counts of tickets by status and by priority (used by the dashboard).

### Troubleshooting
| Problem | Fix |
|---|---|
| `connection timeout` / `connection refused` | PostgreSQL service is stopped: Windows **Services** → `postgresql-x64-16` → **Start** |
| `failed to resolve host '...@localhost'` | Password contains `@`: write it as `%40` in `.env` |
| `No module named ...` | Virtual environment not active: run `venv\Scripts\activate` from the project root |
| `Could not import module "main"` | Run uvicorn from inside the `backend` folder |

---

## AI setup (Ollama)
*To be completed by Dev B.*

## Frontend setup
*To be completed by Dev C.*

## Architecture diagram
*To be completed by Dev B.*

## Demo walkthrough (6 scenarios)
*To be completed by Dev C.*