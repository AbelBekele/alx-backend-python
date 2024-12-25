# chats/views.py

from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, User
from .serializers import (
    ConversationSerializer, 
    MessageSerializer,
    ConversationCreateSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__email', 'participants__first_name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        conversation = self.get_object()
        message_body = request.data.get('message_body')
        
        if not message_body:
            return Response(
                {'error': 'message_body is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response({'status': 'participant added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conversation', 'sent_at']
    search_fields = ['message_body']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation')

    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            raise PermissionError("You are not a participant in this conversation")
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def my_messages(self, request):
        messages = Message.objects.filter(sender=request.user)
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)