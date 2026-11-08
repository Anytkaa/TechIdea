from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def create_project_for_idea_owner(sender, instance, created, **kwargs):
    if created and instance.role == 'idea_owner':
        # Импорт внутри функции, чтобы избежать циклической зависимости
        from projects.models import Idea, Project, Stage, ProjectMember
        
        # 1. Создаем идею
        idea = Idea.objects.create(
            owner=instance, 
            title='Новая идея', 
            goal='', 
            work_plan=''
        )
        # 2. Создаем проект
        project = Project.objects.create(idea=idea, title='Новая идея')
        # 3. Добавляем владельца в участники
        ProjectMember.objects.create(
            project=project, user=instance, role_in_project='owner', status='accepted'
        )
        # 4. Создаем 4 этапа для канбана
        for name, _ in Stage.STAGE_NAMES:
            Stage.objects.create(project=project, name=name)