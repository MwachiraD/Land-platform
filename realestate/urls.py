from django.urls import path, include
from . import views
from realestate.views import buyer_dashboard, seller_dashboard, surveyor_dashboard
from django.urls import path
from .views import seller_login
from .views import chat_error
from realestate.views import custom_login, seller_login
from .views import logout_user

from django.urls import path
from .views import mpesa_callback, seller_mpesa_callback, buyer_mpesa_callback
from realestate.views import mpesa_callback, seller_mpesa_callback, buyer_mpesa_callback
from realestate.views import promote_surveyor
from .views import initiate_chat_payment
from .views import initiate_seller_verification_payment






urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/buyer/', views.register_buyer, name='register_buyer'),
    path('register/seller/', views.register_seller, name='register_seller'),
    path('register/surveyor/', views.register_surveyor, name='register_surveyor'),
    path('surveyor/dashboard/', views.surveyor_dashboard, name='surveyor_dashboard'),
    path('login/surveyor/', views.login_surveyor, name='login_surveyor'),
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer-dashboard/', buyer_dashboard, name='buyer_dashboard'),
    path('surveyor_dashboard/', surveyor_dashboard, name='surveyor_dashboard'),
    path("register/seller/", views.register_seller, name="register_seller"),
    path("login/seller/", views.seller_login, name="seller_login"),
    path('dashboard/seller/', views.seller_dashboard, name='seller_dashboard'),
    path('edit_listing/<int:listing_id>/', views.edit_listing, name='edit_listing'),
    path('edit_contact_details/', views.edit_contact_details, name='edit_contact_details'),
    path('add_land_listing/', views.add_land_listing, name='add_land_listing'),
    path('login/', views.custom_login, name='login'),
    path('surveyor/dashboard/', views.surveyor_dashboard, name='surveyor_dashboard'),
    path('chat-error/', chat_error, name='chat_error'),
    path('send-message/<int:chat_room_id>/', views.send_message, name='send_message'),
    path('chat-room/<int:chat_room_id>/', views.chat_room, name='chat_room'),
    path('send-message/<int:chat_room_id>/', views.send_message, name='send_message'),
    path('add-land/', views.add_land, name='add_land'),
    path('login/', views.custom_login, name='custom_login'),
    path('dashboard/buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('login/', custom_login, name='buyer_login'),
    path('send-message/<int:chat_room_id>/', views.send_message, name='send_message'),
    path('logout/', logout_user, name='logout'),
    path('mpesa/callback/', mpesa_callback, name='mpesa_callback'),
    path('mpesa/seller/callback/', seller_mpesa_callback, name='seller_mpesa_callback'),
    path('promote-surveyor/', promote_surveyor, name='promote_surveyor'),
    path('promote-in-progress/', views.promote_in_progress, name='promote_in_progress'),
    path('mpesa/buyer/callback/', views.buyer_mpesa_callback, name='buyer_mpesa_callback'),
    path('initiate-chat-payment/<int:seller_id>/', initiate_chat_payment, name='initiate_chat_payment'),
    path('initiate-seller-verification-payment/<int:seller_id>/', initiate_seller_verification_payment, name='initiate_seller_verification_payment'),


    

  





    
    

]

