from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser, Balance


@receiver(post_save, sender=CustomUser)
def create_user_balance(sender, instance, created, **kwargs):
    """Создание баланса пользователя"""
    if created:
        Balance.objects.create(user=instance)