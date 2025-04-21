from django.urls import path
from django.urls import re_path
from Landplatform.consumers import ChatConsumer  # Replace `your_app_name` with your actual app name

# Define WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),  # URL pattern for the WebSocket connection
]