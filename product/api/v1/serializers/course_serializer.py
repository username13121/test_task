from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework import serializers

from courses.models import Course, Group, Lesson
from users.models import Subscription

User = get_user_model()

MAX_CAPACITY_PER_GROUP = 30


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""

    students = StudentSerializer(many=True, read_only=True)
    course = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
            'students'
        )

    def get_course(self, obj):
        return obj.course.title if obj.course.title else None


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
        )


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    is_available = serializers.SerializerMethodField(read_only=True)
    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)

    def get_is_available(self, obj):
        return obj.get_is_available()

    def get_lessons_count(self, obj):
        """Количество уроков в курсе."""
        return obj.lessons.count()

    def get_students_count(self, obj):
        """Общее количество студентов на курсе."""
        return obj.subscriptions.count()

    def get_groups_filled_percent(self, obj):
        """Процент заполнения групп, если в группе максимум 30 чел.."""
        total_students = obj.subscriptions.filter().count()
        total_groups = obj.groups.count()

        if total_groups == 0:
            return 0

        total_capacity = total_groups * MAX_CAPACITY_PER_GROUP

        return int((total_students / total_capacity) * 100)

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""
        total_users = User.objects.count()

        if total_users == 0:
            return 0

        total_subscriptions = obj.subscriptions.count()
        return int((total_subscriptions / total_users) * 100)

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'is_available',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price'
        )
