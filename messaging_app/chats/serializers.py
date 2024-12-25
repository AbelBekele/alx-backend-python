# chats/serializers.py

from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    conversation_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 
                 'phone_number', 'role', 'created_at', 'full_name',
                 'conversation_count']
        read_only_fields = ['user_id', 'created_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_conversation_count(self, obj):
        return obj.conversations.count()

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'email', 'password', 'confirm_password',
                 'first_name', 'last_name', 'phone_number', 'role']
        read_only_fields = ['user_id']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_name = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 
                 'message_body', 'sent_at', 'sender_name', 'is_read']
        read_only_fields = ['message_id', 'sent_at', 'sender']

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"

    def get_is_read(self, obj):
        # This is a placeholder - you might want to implement message read status
        return False

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty")
        return value

    def validate_conversation(self, value):
        user = self.context['request'].user
        if user not in value.participants.all():
            raise serializers.ValidationError(
                "You are not a participant in this conversation"
            )
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 
                 'created_at', 'last_message', 'unread_count',
                 'participant_ids']
        read_only_fields = ['conversation_id', 'created_at']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender_name': f"{last_message.sender.first_name} {last_message.sender.last_name}"
            }
        return None

    def get_unread_count(self, obj):
        # This is a placeholder - you might want to implement message read status
        return 0

    def validate_participant_ids(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one participant is required"
            )
        
        # Check if all users exist
        existing_users = User.objects.filter(user_id__in=value).count()
        if existing_users != len(value):
            raise serializers.ValidationError(
                "One or more users do not exist"
            )
        
        return value

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        # Add the creator as a participant
        conversation.participants.add(self.context['request'].user)
        
        # Add other participants
        for user_id in participant_ids:
            conversation.participants.add(user_id)
        
        return conversation

class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    initial_message = serializers.CharField(write_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participant_ids', 'initial_message']
        read_only_fields = ['conversation_id']

    def validate(self, data):
        if not data.get('participant_ids'):
            raise serializers.ValidationError(
                "At least one participant is required"
            )
        if not data.get('initial_message'):
            raise serializers.ValidationError(
                "Initial message is required"
            )
        return data

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        initial_message = validated_data.pop('initial_message')
        
        # Create conversation
        conversation = Conversation.objects.create()
        
        # Add participants
        conversation.participants.add(self.context['request'].user)
        for user_id in participant_ids:
            try:
                user = User.objects.get(user_id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f"User with id {user_id} does not exist"
                )
        
        # Create initial message
        Message.objects.create(
            sender=self.context['request'].user,
            conversation=conversation,
            message_body=initial_message
        )
        
        return conversation