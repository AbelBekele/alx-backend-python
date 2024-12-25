# chats/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    @action(detail=False, methods=['post'])
    def create_conversation(self, request):
        """Create a new conversation with initial participants"""
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            # Create conversation
            conversation = serializer.save()
            # Add creator as participant
            conversation.participants.add(request.user)
            # Add other participants
            for participant_id in request.data.get('participants', []):
                conversation.participants.add(participant_id)
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in an existing conversation"""
        conversation = self.get_object()
        
        # Check if user is participant
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "You are not a participant in this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create message
        message_data = {
            'conversation': conversation.conversation_id,
            'message_body': request.data.get('message_body'),
            'sender': request.user.user_id
        }
        
        message_serializer = MessageSerializer(data=message_data)
        if message_serializer.is_valid():
            message = message_serializer.save()
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            message_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_queryset(self):
        """Only return conversations where user is participant"""
        return Conversation.objects.filter(participants=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    def get_queryset(self):
        """Only return messages from conversations where user is participant"""
        return Message.objects.filter(
            conversation__participants=self.request.user
        )

    def perform_create(self, serializer):
        """Set sender to current user when creating message"""
        serializer.save(sender=self.request.user)