# Overdue Rules Service (Django)

This Django app is a small secondary service. It only evaluates overdue-task rules for the Laravel API.

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

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_TIME_ZONE`
- `CORS_ALLOWED_ORIGINS`
- `OVERDUE_SERVICE_KEY`

## Local setup

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py runserver 9000
```

## Tests

```bash
.venv\Scripts\python manage.py test rules
```

## Laravel handoff

Laravel calls this service through [`app/Services/OverdueRuleService.php`](../../task-manager-laravel-api/app/Services/OverdueRuleService.php).
