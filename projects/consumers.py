import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.user = self.scope['user']
        self.group_name = f'chat_{self.project_id}'

        if not self.user.is_authenticated or not await self.is_project_member():
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        
        if not message:
            return

        await self.save_message(self.user.id, message)
        
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'chat_message', 'message': message, 'user': self.user.username}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({'message': event['message'], 'user': event['user']}))

    @database_sync_to_async
    def is_project_member(self):
        from .models import ProjectMember
        return ProjectMember.objects.filter(
            project_id=self.project_id, user=self.user, status='accepted'
        ).exists()

    @database_sync_to_async
    def save_message(self, user_id, text):
        from .models import ChatMessage
        ChatMessage.objects.create(project_id=self.project_id, user_id=user_id, text=text)


class DrawingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.user = self.scope['user']
        self.group_name = f'drawing_{self.project_id}'

        if not self.user.is_authenticated or not await self.is_project_member():
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        history = await self.get_drawing_history()
        await self.send(text_data=json.dumps({'type': 'history', 'data': history}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get('type') == 'clear':
            await self.clear_drawing_history()
        elif data.get('type') == 'draw':
            await self.save_draw_line(data)

        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'draw_message', 'data': data}
        )

    async def draw_message(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def is_project_member(self):
        from .models import ProjectMember
        return ProjectMember.objects.filter(
            project_id=self.project_id, user=self.user, status='accepted'
        ).exists()

    @database_sync_to_async
    def get_drawing_history(self):
        from .models import Project
        try:
            project = Project.objects.get(id=self.project_id)
            return project.drawing_data
        except Project.DoesNotExist:
            return []

    @database_sync_to_async
    def save_draw_line(self, data):
        from .models import Project
        try:
            project = Project.objects.get(id=self.project_id)
            project.drawing_data.append(data)
            project.save()
        except Project.DoesNotExist:
            pass

    @database_sync_to_async
    def clear_drawing_history(self):
        from .models import Project
        try:
            project = Project.objects.get(id=self.project_id)
            project.drawing_data = []
            project.save()
        except Project.DoesNotExist:
            pass


class QuickdrawConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.user = self.scope['user']
        self.group_name = f'quickdraw_{self.project_id}'

        #if not self.user.is_authenticated or not await self.is_project_member():
        #    await self.close()
        #    return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'quickdraw_message', 'data': data}
        )

    async def quickdraw_message(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def is_project_member(self):
        from .models import ProjectMember
        return ProjectMember.objects.filter(
            project_id=self.project_id, user=self.user, status='accepted'
        ).exists()