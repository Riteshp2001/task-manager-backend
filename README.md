# Overdue Rules Service (FastAPI)

This FastAPI app is the small secondary service used by the Laravel API to evaluate overdue-task rules.

## What it does

- Marks tasks as overdue when `due_date` is in the past and status is not `DONE`
- Blocks overdue tasks from moving back to `IN_PROGRESS`
- Allows only admins to close overdue tasks

## Endpoints

- `POST /api/rules/evaluate-overdue/`
- `POST /api/rules/validate-transition/`

Both endpoints optionally accept the shared `X-Service-Key` header when `OVERDUE_SERVICE_KEY` is configured.

## Environment

Copy `.env.example` values into your deployment environment:

- `OVERDUE_SERVICE_KEY`

## Local setup

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\uvicorn index:app --host 127.0.0.1 --port 9000
```

## Health check

```bash
GET /
```

## Laravel handoff

Laravel calls this service through [`app/Services/OverdueRuleService.php`](../../task-manager-laravel-api/app/Services/OverdueRuleService.php).
