from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('register/idea/', views.register_idea, name='register_idea'),
    path('register/member/', views.register_member, name='register_member'),
    path('project/<int:project_id>/invite/', views.invite_team_member, name='invite_team_member'),
    path('profile/update-photo/', views.update_photo, name='update_photo'),
    path('profile/upload-achievement/', views.upload_achievement, name='upload_achievement'),
    path('user/<int:user_id>/', views.view_public_profile, name='public_profile'),
]