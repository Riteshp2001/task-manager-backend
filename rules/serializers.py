from rest_framework import serializers


class RuleTaskSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField(max_length=20)
    due_date = serializers.DateTimeField(allow_null=True)


class EvaluateOverdueRequestSerializer(serializers.Serializer):
    tasks = RuleTaskSerializer(many=True)


class ValidateTransitionRequestSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(required=False)
    current_status = serializers.CharField(max_length=20)
    next_status = serializers.CharField(max_length=20)
    due_date = serializers.DateTimeField(allow_null=True)
    actor_role = serializers.CharField(max_length=20)
