from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import Project, UserProfile
from .serializers import ProjectSerializer, ProjectCreateSerializer


def json_response(success=True, message='', data=None, status_code=200):
    response = {
        'success': success,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return Response(response, status=status_code)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    from .serializers import UserSerializer
    
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name', '')
    
    if not all([username, email, password]):
        return json_response(False, 'All fields are required', status_code=400)
    
    if User.objects.filter(username=username).exists():
        return json_response(False, 'Username already exists', status_code=400)
    
    if User.objects.filter(email=email).exists():
        return json_response(False, 'Email already exists', status_code=400)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=name.split()[0] if name else '',
        last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
    )
    
    UserProfile.objects.create(user=user, role='user')
    
    return json_response(True, 'User registered successfully', {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
    }, status_code=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('email')
    password = request.data.get('password')
    
    if not all([username, password]):
        return json_response(False, 'Email and password are required', status_code=400)
    
    user = authenticate(username=username, password=password)
    
    if not user:
        try:
            user_obj = User.objects.get(email=username)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if not user:
        return json_response(False, 'Invalid credentials', status_code=401)
    
    try:
        profile = user.profile
        role = profile.role
    except UserProfile.DoesNotExist:
        role = 'user'
        UserProfile.objects.create(user=user, role='user')
    
    return json_response(True, 'Login successful', {
        'token': f'user_{user.id}_token',
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def project_list_create(request):
    user_role = get_user_role(request.user)
    user_id = request.user.id
    
    if request.method == 'GET':
        if user_role == 'admin':
            projects = Project.objects.all().select_related()
        else:
            projects = Project.objects.filter(
                tasks__assigned_to=user_id
            ).distinct().select_related()
        
        serializer = ProjectSerializer(projects, many=True)
        return json_response(True, 'Projects fetched successfully', serializer.data)
    
    elif request.method == 'POST':
        if user_role != 'admin':
            return json_response(False, 'Only admins can create projects', status_code=403)
        
        serializer = ProjectCreateSerializer(data=request.data, context={'user_id': user_id})
        if serializer.is_valid():
            project = serializer.save()
            return json_response(True, 'Project created successfully', 
                           ProjectSerializer(project).data, status_code=201)
        return json_response(False, serializer.errors, status_code=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def project_detail(request, project_id):
    user_role = get_user_role(request.user)
    user_id = request.user.id
    
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        return json_response(False, 'Project not found', status_code=404)
    
    if request.method == 'GET':
        return json_response(True, 'Project fetched successfully', ProjectSerializer(project).data)
    
    elif request.method == 'PUT':
        if user_role != 'admin':
            return json_response(False, 'Only admins can update projects', status_code=403)
        
        serializer = ProjectCreateSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            return json_response(True, 'Project updated successfully', ProjectSerializer(project).data)
        return json_response(False, serializer.errors, status_code=400)
    
    elif request.method == 'DELETE':
        if user_role != 'admin':
            return json_response(False, 'Only admins can delete projects', status_code=403)
        
        project.delete()
        return json_response(True, 'Project deleted successfully')


def get_user_role(user):
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return 'user'