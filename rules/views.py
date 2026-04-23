from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import (
    EvaluateOverdueRequestSerializer,
    ValidateTransitionRequestSerializer,
)


STATUS_DONE = 'DONE'
STATUS_IN_PROGRESS = 'IN_PROGRESS'
STATUS_OVERDUE = 'OVERDUE'
ROLE_ADMIN = 'admin'


def json_response(success=True, message='', data=None, status_code=200):
    payload = {
        'success': success,
        'message': message,
    }

    if data is not None:
        payload['data'] = data

    return Response(payload, status=status_code)


def has_valid_service_key(request):
    expected_key = getattr(settings, 'OVERDUE_SERVICE_KEY', '')

    if not expected_key:
        return True

    return request.headers.get('X-Service-Key') == expected_key


def resolve_status(current_status, due_date):
    if due_date and due_date < timezone.now() and current_status != STATUS_DONE:
        return STATUS_OVERDUE

    return current_status


@api_view(['POST'])
@permission_classes([AllowAny])
def evaluate_overdue(request):
    if not has_valid_service_key(request):
        return json_response(False, 'Invalid service key.', status_code=403)

    serializer = EvaluateOverdueRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return json_response(False, 'Validation failed.', serializer.errors, 422)

    evaluated_tasks = []

    for task in serializer.validated_data['tasks']:
        resolved_status = resolve_status(task['status'], task['due_date'])

        evaluated_tasks.append({
            'id': task['id'],
            'should_mark_overdue': resolved_status == STATUS_OVERDUE,
            'resolved_status': resolved_status,
        })

    return json_response(True, 'Overdue rules evaluated successfully.', {
        'tasks': evaluated_tasks,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_transition(request):
    if not has_valid_service_key(request):
        return json_response(False, 'Invalid service key.', status_code=403)

    serializer = ValidateTransitionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return json_response(False, 'Validation failed.', serializer.errors, 422)

    current_status = serializer.validated_data['current_status']
    next_status = serializer.validated_data['next_status']
    due_date = serializer.validated_data['due_date']
    actor_role = serializer.validated_data['actor_role']

    resolved_status = resolve_status(current_status, due_date)
    allowed = True
    reason = ''

    if resolved_status == STATUS_OVERDUE and next_status == STATUS_IN_PROGRESS:
        allowed = False
        reason = 'Overdue tasks cannot move back to IN_PROGRESS.'
    elif resolved_status == STATUS_OVERDUE and next_status == STATUS_DONE and actor_role != ROLE_ADMIN:
        allowed = False
        reason = 'Only admins can close overdue tasks.'

    return json_response(True, 'Transition validated successfully.', {
        'allowed': allowed,
        'reason': reason,
        'resolved_status': resolved_status,
    })
