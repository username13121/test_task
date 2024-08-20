from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers.user_serializer import (CustomUserSerializer,
                                                BalanceSerializer,
                                                CreateBalanceSerializer,
                                                SubscriptionSerializer,
                                                CreateSubscriptionSerializer)

from users.models import Balance, Subscription
from courses.models import Course

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = (permissions.IsAdminUser,)


class BalanceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = BalanceSerializer
    http_method_names = ('get', 'post', 'put', 'delete')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BalanceSerializer
        return CreateBalanceSerializer

    def perform_create(self, serializer):
        user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        serializer.save(user=user)

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        return Balance.objects.filter(user=user)


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = SubscriptionSerializer
    http_method_names = ('get', 'post', 'put', 'delete')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SubscriptionSerializer
        return CreateSubscriptionSerializer

    def perform_create(self, serializer):
        user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        course = get_object_or_404(Course, id=self.request.data.get('course_id'))
        serializer.save(user=user, course=course)

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs.get('user_id'))
        return Subscription.objects.filter(user=user)
