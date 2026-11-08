from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<project_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/draw/(?P<project_id>\d+)/$', consumers.DrawingConsumer.as_asgi()),
    re_path(r'ws/quickdraw/(?P<project_id>\d+)/$', consumers.QuickdrawConsumer.as_asgi()),
]