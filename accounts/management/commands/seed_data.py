from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Idea, Project, Stage, ProjectMember

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестовые данные для проверки'

    def handle(self, *args, **kwargs):
        self.stdout.write('Очистка старых данных...')
        User.objects.all().delete() # Удаляем всех пользователей (вместе с проектами)

        self.stdout.write('Создание Админа...')
        admin = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='123', role='admin'
        )

        self.stdout.write('Создание Владельца идеи (Иван)...')
        ivan = User.objects.create_user(
            username='ivan', email='ivan@test.com', password='123', role='idea_owner', first_name='Иван Иванов'
        )
        idea = Idea.objects.create(
            owner=ivan, title='Эко-стартап "Зеленый город"', 
            goal='Создать приложение для мониторинга мусорных баков', 
            description='Мы хотим сделать город чище с помощью IoT и краудсорсинга.'
        )
        project = Project.objects.create(idea=idea, title=idea.title)
        for name, _ in Stage.STAGE_NAMES:
            Stage.objects.create(project=project, name=name)
        ProjectMember.objects.create(project=project, user=ivan, role_in_project='owner', status='accepted')

        self.stdout.write('Создание Наставника (Елена)...')
        elena = User.objects.create_user(
            username='elena', email='elena@test.com', password='123', role='mentor', first_name='Елена Смирнова',
            about='10 лет опыта в экологических проектах. Помогу с бизнес-планом.'
        )
        # Приглашаем Елену в проект Ивана
        ProjectMember.objects.create(project=project, user=elena, role_in_project='mentor', status='invited')

        self.stdout.write('Создание Специалиста (Максим)...')
        maxim = User.objects.create_user(
            username='maxim', email='maxim@test.com', password='123', role='specialist', first_name='Максим Козлов',
            about='Python-разработчик, специализация: Django и IoT.'
        )

        self.stdout.write(self.style.SUCCESS('Готово! Созданы аккаунты (пароль у всех: 123)'))
        self.stdout.write(' - admin (Админ)')
        self.stdout.write(' - ivan (Владелец идеи)')
        self.stdout.write(' - elena (Наставник, есть приглашение)')
        self.stdout.write(' - maxim (Специалист)')