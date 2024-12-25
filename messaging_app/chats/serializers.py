# chats/serializers.py

from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 
                 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'email', 'password', 'first_name', 
                 'last_name', 'phone_number', 'role']
        read_only_fields = ['user_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 
                 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at', 'sender']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']