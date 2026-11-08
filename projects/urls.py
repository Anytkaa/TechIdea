from django.urls import path
from . import views, api_views

urlpatterns = [
    # Страницы
    path('board/', views.board_view, name='board'),
    path('board/<int:project_id>/', views.board_view, name='board_project'),
    path('project/<int:project_id>/', views.case_room, name='case_room'),
    path('project/<int:project_id>/info/', views.project_detail, name='project_detail'),
    
    # API для канбана
    path('api/project/<int:project_id>/stages/', api_views.api_stages, name='api_stages'),
    path('api/stage/<int:stage_id>/update/', api_views.api_update_stage, name='api_update_stage'),
    path('api/stage/<int:stage_id>/add-task/', api_views.api_add_task, name='api_add_task'),
    path('api/stage/<int:stage_id>/delete-task/', api_views.api_delete_task, name='api_delete_task'),
    path('api/stage/<int:stage_id>/upload-file/', api_views.api_upload_task_file, name='api_upload_task_file'),
    
    # API для участников
    path('api/project/<int:project_id>/add-member/', api_views.api_add_member, name='api_add_member'),
    path('api/project/<int:project_id>/join/', api_views.api_join_project, name='api_join_project'),
    path('api/member/<int:member_id>/accept/', api_views.api_accept_member, name='api_accept_member'),
    path('api/member/<int:member_id>/decline/', api_views.api_decline_member, name='api_decline_member'),
    
    # API для уведомлений и ИИ
    path('api/notifications/read/', api_views.api_read_notifications, name='api_read_notifications'),
    path('api/ai-chat/', api_views.api_ai_chat, name='api_ai_chat'),
    
    # API для специалистов и проектов
    path('api/invite-specialist/', api_views.api_invite_specialist, name='api_invite_specialist'),
    path('api/project/<int:project_id>/delete/', api_views.api_delete_project, name='api_delete_project'),
    path('api/user-projects/', api_views.api_user_projects, name='api_user_projects'),
    
    # API для сохранения доски
    path('api/project/<int:project_id>/save-board/', api_views.api_save_board, name='api_save_board'),
    path('api/project/<int:project_id>/load-board/', api_views.api_load_board, name='api_load_board'),
]