import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectMember

@login_required
def board_view(request, project_id=None):
    # Берем ТОЛЬКО те проекты, где пользователь принят в команду
    user_projects = Project.objects.filter(
        members__user=request.user, 
        members__status='accepted'
    ).distinct()
    
    if not user_projects.exists():
        return redirect('home') # Если нет проектов, кидаем на главную

    # Если ID передан в URL, проверяем, что он есть в списке доступных
    if project_id:
        project = get_object_or_404(
            Project, 
            id=project_id, 
            members__user=request.user, 
            members__status='accepted'
        )
    else:
        project = user_projects.first()

    # Превращаем список проектов в JSON для передачи в React
    projects_list = [{'id': p.id, 'title': p.title} for p in user_projects]
    
    return render(request, 'board.html', {
        'project': project,
        'user_projects': user_projects,
        'user_projects_json': json.dumps(projects_list), # <--- Передаем JSON
    })

@login_required
def case_room(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if not project.members.filter(user=request.user, status='accepted').exists():
        return redirect('profile')
        
    stages = project.stages.all()
    members = project.members.filter(status='accepted')
    pending_members = project.members.filter(status='invited') 
    chat_messages = project.messages.all().order_by('created_at')
    
    roles_present = set(member.role_in_project for member in members)
    is_team_complete = all(
        role in roles_present for role in ['owner', 'mentor', 'specialist', 'consultant']
    )
    
    return render(request, 'case_room.html', {
        'project': project,
        'stages': stages,
        'members': members,
        'pending_members': pending_members,
        'chat_messages': chat_messages,
        'is_team_complete': is_team_complete,
    })

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    members = project.members.filter(status='accepted')
    
    is_member = project.members.filter(user=request.user, status='accepted').exists()
    has_invited = project.members.filter(user=request.user, status='invited').exists()
    
    return render(request, 'project_detail.html', {
        'project': project,
        'members': members,
        'is_member': is_member,
        'has_invited': has_invited,
    })