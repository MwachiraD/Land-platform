# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chat-room/<int:room_id>/', views.chat_room, name='chat_room_detail'),
]
