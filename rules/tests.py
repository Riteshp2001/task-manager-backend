from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient


class RulesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_evaluate_overdue_marks_past_due_undone_tasks(self):
        response = self.client.post(
            '/api/rules/evaluate-overdue/',
            {
                'tasks': [
                    {
                        'id': 1,
                        'status': 'TODO',
                        'due_date': (timezone.now() - timedelta(days=1)).isoformat(),
                    },
                    {
                        'id': 2,
                        'status': 'DONE',
                        'due_date': (timezone.now() - timedelta(days=1)).isoformat(),
                    },
                ]
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['data']['tasks'][0]['should_mark_overdue'])
        self.assertFalse(response.data['data']['tasks'][1]['should_mark_overdue'])

    def test_member_cannot_close_overdue_task(self):
        response = self.client.post(
            '/api/rules/validate-transition/',
            {
                'current_status': 'TODO',
                'next_status': 'DONE',
                'due_date': (timezone.now() - timedelta(days=1)).isoformat(),
                'actor_role': 'user',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['data']['allowed'])
        self.assertEqual(response.data['data']['resolved_status'], 'OVERDUE')

    def test_admin_can_close_overdue_task(self):
        response = self.client.post(
            '/api/rules/validate-transition/',
            {
                'current_status': 'IN_PROGRESS',
                'next_status': 'DONE',
                'due_date': (timezone.now() - timedelta(days=1)).isoformat(),
                'actor_role': 'admin',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['data']['allowed'])
        self.assertEqual(response.data['data']['resolved_status'], 'OVERDUE')
