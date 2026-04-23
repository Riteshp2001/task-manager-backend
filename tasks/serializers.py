from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'due_date', 
                  'assigned_to', 'project_id', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TaskStatusUpdateSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    new_status = serializers.CharField()


class OverdueCheckRequestSerializer(serializers.Serializer):
    task_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    project_id = serializers.IntegerField(required=False)