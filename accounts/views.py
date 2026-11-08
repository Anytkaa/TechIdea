from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
import random
import string

from .models import User
from projects.models import Idea, Project, ProjectMember, Stage, Attachment, Notification

def home(request):
    if request.user.is_authenticated:
        # Проекты, в которых пользователь ещё не участвует
        joined_projects = ProjectMember.objects.filter(user=request.user).values_list('project_id', flat=True)
        available_projects = Project.objects.exclude(id__in=joined_projects)
        
        # Специалисты, наставники и консультанты (все, кроме админов и самого пользователя)
        specialists = User.objects.filter(role__in=['mentor', 'specialist', 'consultant']).exclude(id=request.user.id)
        
        # Проекты, где текущий пользователь — владелец (для выбора при приглашении)
        my_projects = Project.objects.filter(idea__owner=request.user)
        
        return render(request, 'home.html', {
            'projects': available_projects,
            'specialists': specialists,
            'my_projects': my_projects,
        })
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    projects = request.user.projectmember_set.filter(status='accepted')
    invitations = request.user.projectmember_set.filter(status='invited')
    attachments = request.user.attachments.all()
    return render(request, 'profile.html', {
        'projects': projects,
        'invitations': invitations,
        'attachments': attachments
    })

def register_idea(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register_idea.html', {'error': 'Пользователь уже существует'})

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, role='idea_owner')
        
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')
            user.save()
        
        idea = Idea.objects.create(
            owner=user,
            title=request.POST.get('title', 'Новая идея'),
            goal=request.POST.get('goal', ''),
            work_plan=request.POST.get('work_plan', ''),
            description=request.POST.get('description', ''),
            looking_for_mentor=request.POST.get('looking_for_mentor') == 'on',
            mentor_competencies=request.POST.get('mentor_competencies', ''),
            looking_for_specialist=request.POST.get('looking_for_specialist') == 'on',
            specialist_area=request.POST.get('specialist_area', ''),
            looking_for_consultant=request.POST.get('looking_for_consultant') == 'on',
            consultant_area=request.POST.get('consultant_area', ''),
        )
        
        for file in request.FILES.getlist('files'):
            Attachment.objects.create(user=user, idea=idea, file=file)
        
        project = Project.objects.create(idea=idea, title=idea.title)
        for name, _ in Stage.STAGE_NAMES:
            Stage.objects.create(project=project, name=name)
        ProjectMember.objects.create(project=project, user=user, role_in_project='owner', status='accepted')
        
        login(request, user)
        return redirect('profile')

    return render(request, 'register_idea.html')

def register_member(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        role = request.POST.get('role', 'specialist')
        about = request.POST.get('about', '')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register_member.html', {'error': 'Пользователь уже существует'})
            
        user = User.objects.create_user(username=username, password=password, email=email, role=role)
        user.about = about
        
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')
            
        user.save()
        
        login(request, user)
        return redirect('profile')
        
    return render(request, 'register_member.html')

@login_required
def invite_team_member(request, project_id):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            username = email.split('@')[0] + str(random.randint(10, 99))
            
            if not User.objects.filter(email=email).exists():
                new_user = User.objects.create_user(username=username, email=email, password=password, role='specialist')
                project = get_object_or_404(Project, id=project_id)
                ProjectMember.objects.create(project=project, user=new_user, role_in_project='specialist', status='accepted')
                
                send_mail(
                    'Приглашение в команду Tech Idea Hub',
                    f'Вас добавили в команду проекта "{project.title}".\nВаш логин: {username}\nВаш пароль: {password}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                return redirect('profile')
    return redirect('profile')

@login_required
def update_photo(request):
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if photo:
            user = request.user
            user.photo = photo
            user.save()
    return redirect('profile')

@login_required
def upload_achievement(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file:
            Attachment.objects.create(user=request.user, file=file)
    return redirect('profile')

@login_required
def view_public_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    # Получаем только достижения (файлы) этого пользователя
    attachments = profile_user.attachments.all()
    
    return render(request, 'public_profile.html', {
        'profile_user': profile_user,
        'attachments': attachments,
    })