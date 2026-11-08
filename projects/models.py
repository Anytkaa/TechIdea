from django.db import models
from django.conf import settings

class Idea(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name="Название идеи")
    goal = models.TextField(verbose_name="Цель проекта", blank=True)
    work_plan = models.TextField(verbose_name="План работ", blank=True)
    description = models.TextField(verbose_name="Описание идеи", blank=True)
    
    looking_for_mentor = models.BooleanField(default=False, verbose_name="Требуется наставник")
    mentor_competencies = models.TextField(blank=True, verbose_name="Компетенции наставника")
    looking_for_specialist = models.BooleanField(default=False, verbose_name="Требуется специалист")
    specialist_area = models.CharField(max_length=255, blank=True, verbose_name="Область специализации")
    looking_for_consultant = models.BooleanField(default=False, verbose_name="Требуется консультант")
    consultant_area = models.CharField(max_length=255, blank=True, verbose_name="Область консультирования")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    idea = models.OneToOneField(Idea, on_delete=models.CASCADE, related_name='project')
    title = models.CharField(max_length=200)
    drawing_data = models.JSONField(default=list)  # <--- ДОБАВЛЕНО ПОЛЕ ДЛЯ РИСУНКОВ
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProjectMember(models.Model):
    ROLE_IN_PROJECT = [
        ('owner', 'Владелец (Идея)'),
        ('mentor', 'Наставник'),
        ('specialist', 'Специалист'),
        ('consultant', 'Консультант'),
    ]
    STATUS = [
        ('invited', 'Приглашён'),
        ('accepted', 'Принят'),
        ('declined', 'Отклонён'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role_in_project = models.CharField(max_length=20, choices=ROLE_IN_PROJECT)
    status = models.CharField(max_length=20, choices=STATUS, default='invited')

    class Meta:
        unique_together = ('project', 'user')

class Stage(models.Model):
    STAGE_NAMES = [
        ('planning', 'Планировка'),
        ('development', 'Разработка'),
        ('testing', 'Тестирование'),
        ('presentation', 'Презентация'),
    ]
    STAGE_STATUS = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнен'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=20, choices=STAGE_NAMES)
    status = models.CharField(max_length=20, choices=STAGE_STATUS, default='pending')
    tasks = models.JSONField(default=list)

class ChatMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Attachment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attachments')
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Файл {self.file.name} от {self.user.username}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    text = models.CharField(max_length=255)
    project_id = models.IntegerField(null=True, blank=True) 
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text}"