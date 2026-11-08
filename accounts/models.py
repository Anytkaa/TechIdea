from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('idea_owner', 'Идея'),
        ('mentor', 'Наставник'),
        ('specialist', 'Специалист'),
        ('consultant', 'Консультант'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='idea_owner')
    phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    about = models.TextField(blank=True)

    def is_admin_role(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()