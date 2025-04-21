"""
URL configuration for Landplatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from realestate import views
from django.urls import path
from realestate.forms import LandForm
from realestate.views import buyer_dashboard
from realestate.views import buyer_dashboard, seller_dashboard, surveyor_dashboard
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls import path, re_path
from Landplatform.consumers import ChatConsumer
from . import consumers




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('realestate.urls')),
    path('', views.landing_page, name='landing_page'),
    path('register/buyer/', views.register_buyer, name='register_buyer'),
    path('register/seller/', views.register_seller, name='register_seller'),
    path('register/surveyor/', views.register_surveyor, name='register_surveyor'),
    path('buyer-dashboard/', buyer_dashboard, name='buyer_dashboard'),
    path('surveyor_dashboard/', surveyor_dashboard, name='surveyor_dashboard'),
    path('realestate/', include('realestate.urls')), 
    path('register/seller/', views.register_seller, name='register_seller'),
    path('login/seller/', views.seller_login, name='seller_login'),
    path('dashboard/seller/', views.seller_dashboard, name='seller_dashboard'),
    path('edit_listing/<int:listing_id>/', views.edit_listing, name='edit_listing'),
    path('edit_contact_details/', views.edit_contact_details, name='edit_contact_details'),
    path('login/', views.custom_login, name='login'),
    path('surveyor/dashboard/', views.surveyor_dashboard, name='surveyor_dashboard'),
    path('login/surveyor/', views.login_surveyor, name='login_surveyor'),
    path('start-chat/<int:target_id>/', views.start_chat, name='start-chat'),
    path('start-chat/<str:target_type>/<int:target_id>/', views.start_chat, name='start-chat'),
    path('respond-to-message/<int:message_id>/', views.respond_to_message, name='respond_to_message'),
    path('chat-room/<int:chat_room_id>/', views.chat_room, name='chat_room'),
    path('send-message/<int:chat_room_id>/', views.send_message, name='send_message'),
    path('messages/surveyor/', views.get_surveyor_messages, name='get_surveyor_messages'),
    path('messages/seller/', views.get_seller_messages, name='get_seller_messages'),
    path('chat/send/', views.send_message, name='send_message'),
    path('login/', views.custom_login, name='custom_login'),
    path('login/', views.custom_login, name='login'),
    path('send-message/<int:chat_room_id>/', views.send_message, name='send_message'),

    



 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

