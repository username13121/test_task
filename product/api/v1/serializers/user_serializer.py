from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscription, Balance
from courses.models import Course
from api.v1.serializers.course_serializer import CourseSerializer

User = get_user_model()

class MiniSubscriptionSerializer(serializers.ModelSerializer):
    """Список подписок."""

    course = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('course', 'end_date', 'is_active')

    def get_is_active(self, obj) -> bool:
        return obj.get_is_active()

    def get_course(self, obj):
        return obj.course.title if obj.course.title else None


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    balance = serializers.SerializerMethodField()
    subscriptions = MiniSubscriptionSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'balance',
            'subscriptions'
        )

    def get_balance(self, obj):
        return obj.balance.amount if obj.balance else None


class MiniCustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Список подписок."""

    user = MiniCustomUserSerializer(read_only=True)
    course = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'course', 'end_date', 'is_active')

    def get_is_active(self, obj) -> bool:
        return obj.get_is_active()

    def get_course(self, obj):
        return obj.course.title if obj.course.title else None


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    """Создать подписку."""

    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        write_only=True,
        source='course'
    )

    class Meta:
        model = Subscription
        fields = ('id', 'course_id', 'end_date')


class BalanceSerializer(serializers.ModelSerializer):
    """Показать баланс"""
    user = MiniCustomUserSerializer(read_only=True)

    class Meta:
        model = Balance
        fields = ('id', 'amount', 'user')


class CreateBalanceSerializer(serializers.ModelSerializer):
    """Показать баланс"""
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Balance
        fields = ('id', 'amount', 'user')
