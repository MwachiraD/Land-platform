import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"Connecting to room {self.scope['url_route']['kwargs']}")
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Add to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnecting from room {self.room_id}")
        # Remove from group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        print(f"Sending message to WebSocket: {message}")
        
        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
