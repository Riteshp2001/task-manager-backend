from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from tasks.models import Task
from tasks.serializers import TaskSerializer, TaskStatusUpdateSerializer


def json_response(success=True, message='', data=None, status_code=200):
    response = {
        'success': success,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return Response(response, status=status_code)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_create(request):
    project_id = request.query_params.get('project_id')
    user_role = get_user_role(request.user)
    user_id = request.user.id
    
    if request.method == 'GET':
        tasks = Task.objects.select_related('project')
        
        if project_id:
            tasks = tasks.filter(project_id=project_id)
        
        if user_role != 'admin':
            tasks = tasks.filter(assigned_to=user_id)
        
        serializer = TaskSerializer(tasks, many=True)
        return json_response(True, 'Tasks fetched successfully', serializer.data)
    
    elif request.method == 'POST':
        if user_role != 'admin':
            return json_response(False, 'Only admins can create tasks', status_code=403)
        
        serializer = TaskSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            task = serializer.save()
            return json_response(True, 'Task created successfully', 
                           TaskSerializer(task).data, status_code=201)
        return json_response(False, serializer.errors, status_code=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request, task_id):
    user_role = get_user_role(request.user)
    user_id = request.user.id
    
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return json_response(False, 'Task not found', status_code=404)
    
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return json_response(True, 'Task fetched successfully', serializer.data)
    
    elif request.method == 'PUT':
        if user_role != 'admin' and task.created_by != user_id:
            return json_response(False, 'Not authorized to update this task', status_code=403)
        
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            task = serializer.save()
            return json_response(True, 'Task updated successfully', TaskSerializer(task).data)
        return json_response(False, serializer.errors, status_code=400)
    
    elif request.method == 'DELETE':
        if user_role != 'admin':
            return json_response(False, 'Only admins can delete tasks', status_code=403)
        
        task.delete()
        return json_response(True, 'Task deleted successfully')


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task_status(request, task_id):
    from tasks.serializers import TaskStatusUpdateSerializer
    
    user_role = get_user_role(request.user)
    is_admin = user_role == 'admin'
    new_status = request.data.get('status')
    
    if not new_status:
        return json_response(False, 'Status is required', status_code=400)
    
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return json_response(False, 'Task not found', status_code=404)
    
    if task.status == 'OVERDUE' and new_status == 'IN_PROGRESS':
        return json_response(False, 'Overdue tasks cannot be moved back to In Progress', status_code=400)
    
    if task.status == 'OVERDUE' and new_status == 'DONE' and not is_admin:
        return json_response(False, 'Only Admin can close overdue tasks', status_code=403)
    
    task.status = new_status
    task.save()
    
    return json_response(True, 'Task status updated successfully', TaskSerializer(task).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_and_mark_overdue(request):
    project_id = request.data.get('project_id')
    
    if project_id:
        tasks = Task.objects.filter(project_id=project_id)
    else:
        tasks = Task.objects.all()
    
    now = timezone.now()
    tasks = tasks.filter(
        Q(due_date__lt=now) & ~Q(status='DONE')
    )
    
    updated_count = 0
    updated_tasks = []
    
    for task in tasks:
        if task.status != 'OVERDUE':
            task.status = 'OVERDUE'
            task.save()
            updated_count += 1
            updated_tasks.append(TaskSerializer(task).data)
    
    return json_response(True, f'Marked {updated_count} tasks as overdue', {
        'count': updated_count,
        'tasks': updated_tasks
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def can_change_status(request):
    task_id = request.data.get('task_id')
    new_status = request.data.get('new_status')
    is_admin = request.data.get('is_admin', False)
    
    if not task_id or not new_status:
        return json_response(False, 'task_id and new_status are required', status_code=400)
    
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return json_response(False, 'Task not found', status_code=404)
    
    can_change = True
    reason = ''
    
    if task.status == 'OVERDUE' and new_status == 'IN_PROGRESS':
        can_change = False
        reason = 'Overdue tasks cannot be moved back to In Progress'
    elif task.status == 'OVERDUE' and new_status == 'DONE' and not is_admin:
        can_change = False
        reason = 'Only Admin can close overdue tasks'
    
    return json_response(True, '', {
        'can_change': can_change,
        'reason': reason
    })


def get_user_role(user):
    try:
        return user.profile.role
    except:
        return 'user'


from rest_framework import serializers as drf_serializers


class TaskSerializer(drf_serializers.ModelSerializer):
    project_name = drf_serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'due_date', 
                  'assigned_to', 'project_id', 'project_name', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_project_name(self, obj):
        try:
            from projects.models import Project
            project = Project.objects.filter(id=obj.project_id).first()
            return project.name if project else None
        except:
            return None
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context.get('user_id')
        return super().create(validated_data)