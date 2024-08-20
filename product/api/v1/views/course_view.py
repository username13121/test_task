from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin, make_payment
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course
from users.models import Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action == 'pay':
            return None
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),

    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        user = request.user
        course = get_object_or_404(Course, pk=pk)

        success, message = make_payment(user, course)

        if success:
            return Response(
                data=message,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                data=message,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def explore(self, request):
        """Список доступных некупленных курсов"""
        bought_courses_ids = Subscription.objects.filter(user=request.user).values_list('course_id', flat=True)

        not_bought_courses = [course
                              for course in Course.objects.all()
                              if course.get_is_available()
                              and course.id not in bought_courses_ids]

        serializer = self.get_serializer(not_bought_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
