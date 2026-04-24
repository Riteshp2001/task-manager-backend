from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI()


def parse_due_date(value):
    if not value:
        return None

    try:
        due_date = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None

    if due_date.tzinfo is None:
        return due_date.replace(tzinfo=timezone.utc)

    return due_date.astimezone(timezone.utc)


def is_overdue(status, due_date):
    if status == "DONE":
        return False

    parsed_due_date = parse_due_date(due_date)
    return parsed_due_date is not None and parsed_due_date < datetime.now(timezone.utc)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Overdue rules service is running.",
        "endpoints": [
            "/api/rules/evaluate-overdue/",
            "/api/rules/validate-transition/",
        ],
    }


@app.post("/api/rules/evaluate-overdue/")
def evaluate(request: dict):
    tasks = request.get("tasks", [])
    results = []
    for task in tasks:
        status = task.get("status")
        overdue = is_overdue(status, task.get("due_date"))
        results.append({
            "id": task.get("id"),
            "should_mark_overdue": overdue,
            "resolved_status": "OVERDUE" if overdue else status,
        })
    return {"success": True, "data": {"tasks": results}}


@app.post("/api/rules/validate-transition/")
def validate(request: dict):
    current = request.get("current_status")
    next_s = request.get("next_status")
    due = request.get("due_date")
    role = request.get("actor_role", "user")
    overdue = is_overdue(current, due)

    allowed = True
    reason = ""
    if overdue and next_s == "IN_PROGRESS":
        allowed = False
        reason = "Overdue tasks cannot move back to IN_PROGRESS."
    elif overdue and next_s == "DONE" and role != "admin":
        allowed = False
        reason = "Only admins can close overdue tasks."

    return {
        "success": True,
        "data": {
            "allowed": allowed,
            "reason": reason,
            "resolved_status": next_s if allowed else current,
        },
    }
