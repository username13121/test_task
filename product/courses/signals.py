from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from users.models import Subscription
from courses.models import Group, Course

GROUPS_PER_COURSE = 10


@receiver(post_save, sender=Course)
def create_groups_for_course(sender, instance: Course, created, **kwargs):
    """Создание групп курса"""

    if created:
        for i in range(1, GROUPS_PER_COURSE+1):
            Group.objects.create(
                title=f'{instance.title}-{i}',
                course=instance
            )


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """Распределение нового студента в группу курса."""

    if created:
        user = instance.user
        course = instance.course

        groups = Group.objects.filter(course=course)

        if groups.exists():
            smallest_group = (
                Group.objects.filter(course=course)
                .annotate(students_count=Count('students'))
                .order_by('students_count')
                .first()
            )
            smallest_group.students.add(user)
