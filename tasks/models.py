from django.db import models
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('OVERDUE', 'Overdue'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    due_date = models.DateTimeField()
    assigned_to = models.IntegerField(null=True, blank=True)
    project_id = models.IntegerField()
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def mark_as_overdue(self):
        if self.status != 'DONE' and self.due_date < timezone.now():
            self.status = 'OVERDUE'
            self.save()
            return True
        return False
    
    def can_move_to_in_progress(self):
        return self.status != 'OVERDUE'
    
    def can_be_closed(self):
        return self.status == 'OVERDUE'