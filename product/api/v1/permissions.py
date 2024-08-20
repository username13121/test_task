from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import Subscription, Balance
from django.utils import timezone
from django.shortcuts import get_object_or_404
from courses.models import Course

DEFAULT_SUBSCRIPTION_PERIOD_DAYS = 30


def make_payment(user, course) -> (bool, str):
    if not course.get_is_available():
        return False, 'Продукт недоступен для покупки'

    user_balance = Balance.objects.filter(user=user).first()

    if not user_balance or user_balance.amount < course.price:
        return False, 'Недостаточно средств на балансе'

    user_balance.amount -= course.price
    user_balance.save()

    subscription, created = Subscription.objects.get_or_create(
        user=user,
        course=course,
        defaults={'end_date': timezone.now() + timezone.timedelta(days=DEFAULT_SUBSCRIPTION_PERIOD_DAYS)}
    )

    if created:
        return True, f'Подписка активирована до {subscription.end_date}'

    if subscription.get_is_active():
        subscription.end_date += timezone.timedelta(days=DEFAULT_SUBSCRIPTION_PERIOD_DAYS)
        message = f'Подписка продлена до {subscription.end_date}'
    else:
        subscription.end_date = timezone.now() + timezone.timedelta(days=DEFAULT_SUBSCRIPTION_PERIOD_DAYS)
        message = f'Подписка активирована до {subscription.end_date}'

    subscription.save()

    return True, message


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        course_id = view.kwargs.get('course_id')
        if not course_id:
            return False

        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not subscription or not subscription.get_is_active():
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.method in SAFE_METHODS:
            return True
        return False


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
