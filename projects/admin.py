from django.contrib import admin
from .models import Idea, Project, ProjectMember, Stage, ChatMessage

admin.site.register(Idea)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Stage)
admin.site.register(ChatMessage)