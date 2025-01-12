from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password123')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password123')

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Test message")

    def test_notification_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        # Check if notification was automatically created
        notification = Notification.objects.filter(
            user=self.user2,
            message=message
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.read) 