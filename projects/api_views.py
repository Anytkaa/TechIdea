import json
import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Stage, Project, ProjectMember, Notification
from accounts.models import User

@login_required
def api_stages(request, project_id):
    stages = Stage.objects.filter(project_id=project_id)
    data = [{
        'id': s.id,
        'name': s.get_name_display(),
        'status': s.status,
        'tasks': s.tasks,
    } for s in stages]
    return JsonResponse({'stages': data})

@login_required
@require_POST
def api_update_stage(request, stage_id):
    body = json.loads(request.body)
    new_status = body.get('status')
    if new_status not in ['pending', 'in_progress', 'done']:
        return JsonResponse({'error': 'Неверный статус'}, status=400)
    
    stage = get_object_or_404(Stage, id=stage_id)
    if not stage.project.members.filter(user=request.user, status='accepted').exists():
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    stage.status = new_status
    stage.save()
    return JsonResponse({'ok': True})

@login_required
@require_POST
def api_add_task(request, stage_id):
    body = json.loads(request.body)
    text = body.get('text')
    assignee_id = body.get('assignee_id')
    
    if not text:
        return JsonResponse({'error': 'Текст задачи не может быть пустым'}, status=400)
    
    stage = get_object_or_404(Stage, id=stage_id)
    if not stage.project.members.filter(user=request.user, status='accepted').exists():
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    assignee_name = 'Не назначен'
    
    if assignee_id:
        try:
            assignee = User.objects.get(id=assignee_id)
            if stage.project.members.filter(user=assignee, status='accepted').exists():
                assignee_name = assignee.first_name or assignee.username
                
                Notification.objects.create(
                    user=assignee,
                    text=f"Вам назначена новая задача: «{text}» в проекте «{stage.project.title}»",
                    project_id=stage.project.id
                )
        except User.DoesNotExist:
            pass

    new_task = {
        'id': str(len(stage.tasks) + 1), 
        'text': text, 
        'assignee': assignee_name,
        'assignee_id': assignee_id,
        'files': []
    }
    stage.tasks.append(new_task)
    stage.save()
    
    return JsonResponse({'ok': True, 'task': new_task})

@login_required
@require_POST
def api_delete_task(request, stage_id):
    body = json.loads(request.body)
    task_id = body.get('task_id')
    
    stage = get_object_or_404(Stage, id=stage_id)
    if not stage.project.members.filter(user=request.user, status='accepted').exists():
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    stage.tasks = [t for t in stage.tasks if str(t.get('id')) != str(task_id)]
    stage.save()
    return JsonResponse({'ok': True})

@login_required
@require_POST
def api_upload_task_file(request, stage_id):
    task_id = request.POST.get('task_id')
    file = request.FILES.get('file')
    
    if not file or not task_id:
        return JsonResponse({'error': 'Файл или ID задачи не передан'}, status=400)
    
    stage = get_object_or_404(Stage, id=stage_id)
    if not stage.project.members.filter(user=request.user, status='accepted').exists():
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    file_name = f"task_files/{file.name}"
    saved_name = default_storage.save(file_name, file)
    file_url = default_storage.url(saved_name)
    
    for task in stage.tasks:
        if str(task.get('id')) == str(task_id):
            if 'files' not in task:
                task['files'] = []
            task['files'].append({
                'name': file.name,
                'url': file_url
            })
            break
            
    stage.save()
    return JsonResponse({'ok': True, 'file_url': file_url, 'file_name': file.name})

@login_required
@require_POST
def api_add_member(request, project_id):
    data = json.loads(request.body)
    email = data.get('email')
    role = data.get('role', 'specialist')
    
    project = get_object_or_404(Project, id=project_id)
    if project.idea.owner != request.user:
        return JsonResponse({'error': 'Только владелец может добавлять'}, status=403)
    
    try:
        user_to_add = User.objects.get(email=email)
        if ProjectMember.objects.filter(project=project, user=user_to_add).exists():
            return JsonResponse({'error': 'Пользователь уже в проекте'}, status=400)
            
        ProjectMember.objects.create(project=project, user=user_to_add, role_in_project=role, status='accepted')
        return JsonResponse({'ok': True})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь с таким email не найден'}, status=404)

@login_required
@require_POST
def api_join_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        
        if ProjectMember.objects.filter(project=project, user=request.user).exists():
            return JsonResponse({'error': 'Вы уже подали заявку или участвуете'}, status=400)
        
        role = request.user.role 
        if role == 'idea_owner':
            role = 'specialist'

        ProjectMember.objects.create(
            project=project,
            user=request.user,
            role_in_project=role,
            status='invited'
        )
        
        Notification.objects.create(
            user=project.idea.owner,
            text=f"Пользователь {request.user.first_name or request.user.username} хочет вступить в ваш проект «{project.title}»",
            project_id=project.id
        )
        
        return JsonResponse({'ok': True, 'message': 'Заявка отправлена!'})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Проект не найден'}, status=404)

@login_required
@require_POST
def api_accept_member(request, member_id):
    member = get_object_or_404(ProjectMember, id=member_id)
    if member.project.idea.owner != request.user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    member.status = 'accepted'
    member.save()
    
    Notification.objects.create(
        user=member.user,
        text=f"Ваша заявка в проект «{member.project.title}» одобрена! Добро пожаловать в команду.",
        project_id=member.project.id
    )
    
    return JsonResponse({'ok': True})

@login_required
@require_POST
def api_decline_member(request, member_id):
    member = get_object_or_404(ProjectMember, id=member_id)
    if member.project.idea.owner != request.user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    Notification.objects.create(
        user=member.user,
        text=f"К сожалению, ваша заявка в проект «{member.project.title}» была отклонена.",
        project_id=member.project.id
    )
    
    member.delete()
    return JsonResponse({'ok': True})

@login_required
@require_POST
def api_read_notifications(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})

@login_required
@require_POST
def api_ai_chat(request):
    body = json.loads(request.body)
    message = body.get('message', '').lower()
    
    if "приглас" in message or "команд" in message or "добав" in message:
        reply = "Чтобы добавить человека в команду, введите его Email в поле «Пригласить в команду» в вашем профиле. Система автоматически создаст для него аккаунт и отправит пароль на почту."
    elif "канбан" in message or "задач" in message or "этап" in message:
        reply = "На вкладке «Комната кейса» находится канбан-доска. Нажмите на «+» в нужной колонке, чтобы создать задачу. Вы можете назначить её конкретному участнику, и ему придет уведомление."
    elif "идея" in message or "проект" in message:
        reply = "Если у вас есть идея, заполните форму регистрации. Если вы хотите присоединиться к чужой идее, перейдите на Главную страницу и нажмите «Присоединиться» на карточке проекта."
    elif "доск" in message or "рисов" in message:
        reply = "На вкладке «Доска» вы можете рисовать схемы, добавлять стикеры и загружать картинки. Это отличное место для мозгового штурма с командой."
    elif "наставник" in message:
        reply = "Наставники — это опытные эксперты. Вы можете пригласить их в свой проект, если им интересна ваша идея. Они помогают советами и направляют команду."
    else:
        reply = "Я пока еще учусь и не совсем понял вопрос. Попробуйте спросить про: «как добавить в команду», «как создать задачу», «как работает доска» или «как найти наставника»."

    return JsonResponse({'reply': reply})

@login_required
@require_POST
def api_invite_specialist(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    
    if not user_id or not project_id:
        return JsonResponse({'error': 'Не переданы данные'}, status=400)
    
    try:
        project = Project.objects.get(id=project_id)
        if project.idea.owner != request.user:
            return JsonResponse({'error': 'Только владелец может приглашать'}, status=403)
            
        user_to_invite = User.objects.get(id=user_id)
        
        if ProjectMember.objects.filter(project=project, user=user_to_invite).exists():
            return JsonResponse({'error': 'Пользователь уже в проекте или приглашён'}, status=400)
            
        ProjectMember.objects.create(
            project=project, 
            user=user_to_invite, 
            role_in_project=user_to_invite.role,
            status='invited'
        )
        
        Notification.objects.create(
            user=user_to_invite,
            text=f"Владелец проекта «{project.title}» приглашает вас в команду в роли {user_to_invite.get_role_display()}.",
            project_id=project.id
        )
        
        return JsonResponse({'ok': True})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Проект не найден'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)

@login_required
@require_POST
def api_delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if project.idea.owner != request.user:
        return JsonResponse({'error': 'Только владелец может удалить проект'}, status=403)
    
    project.delete()
    return JsonResponse({'ok': True})

@login_required
def api_user_projects(request):
    projects = Project.objects.filter(
        members__user=request.user, 
        members__status='accepted'
    ).values('id', 'title').distinct()
    return JsonResponse({'projects': list(projects)})

# --- API ДЛЯ СОХРАНЕНИЯ ДОСКИ ---
@login_required
@require_POST
def api_save_board(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not project.members.filter(user=request.user, status='accepted').exists():
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    data = json.loads(request.body)
    project.drawing_data = data.get('snapshot')
    project.save()
    return JsonResponse({'ok': True})

@login_required
def api_load_board(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not project.members.filter(user=request.user, status='accepted').exists():
        return JsonResponse({'error': 'Нет доступа'}, status=403)
    
    return JsonResponse({'snapshot': project.drawing_data})