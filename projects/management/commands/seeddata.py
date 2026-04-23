from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from projects.models import Project, UserProfile
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create demo users and initial data'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo users...')
        
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@demo.com',
                password='demo123',
                first_name='Admin',
                last_name='User'
            )
            UserProfile.objects.create(user=admin_user, role='admin')
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin / demo123'))
        
        if not User.objects.filter(username='demo_user').exists():
            demo_user = User.objects.create_user(
                username='demo_user',
                email='user@demo.com',
                password='demo123',
                first_name='Regular',
                last_name='User'
            )
            UserProfile.objects.create(user=demo_user, role='user')
            self.stdout.write(self.style.SUCCESS(f'Created demo user: user@demo.com / demo123'))
        
        admin_user = User.objects.get(username='admin')
        
        if Project.objects.count() == 0:
            project = Project.objects.create(
                name='Sample Project',
                description='This is a sample project to get you started',
                created_by=admin_user.id
            )
            
            Task.objects.create(
                title='Sample Task 1',
                description='This is a sample task with low priority',
                status='TODO',
                priority='LOW',
                due_date=timezone.now() + timedelta(days=7),
                project_id=project.id,
                created_by=admin_user.id,
                assigned_to=admin_user.id
            )
            
            Task.objects.create(
                title='Sample Task 2 - Overdue',
                description='This task is already overdue',
                status='TODO',
                priority='HIGH',
                due_date=timezone.now() - timedelta(days=1),
                project_id=project.id,
                created_by=admin_user.id,
                assigned_to=admin_user.id
            )
            
            self.stdout.write(self.style.SUCCESS('Created sample project with tasks'))
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))