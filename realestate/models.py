from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager 
from django.db import models   
from django.db import models
from django.conf import settings



# models.py
class Payment(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=[('pending', 'Pending'), ('completed', 'Completed')])

    def __str__(self):
        return f"Payment of {self.amount} from {self.buyer.username} to {self.seller.name}"


class UnlockedChat(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='unlocked_chats')
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE, related_name='received_chats')  # <-- notice quotes
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'seller')

    def __str__(self):
        return f"{self.buyer.username} unlocked chat with {self.seller.name}"







class SurveyorManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Surveyors must have an email address.")
        email = self.normalize_email(email)
        surveyor = self.model(username=username, email=email, **extra_fields)
        surveyor.set_password(password)
        surveyor.save(using=self._db)
        return surveyor

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)


class Surveyor(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, null=False, default='dennis')
    last_name = models.CharField(max_length=30, null=False, default='wachira')
    qualifications = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    contacts = models.CharField(max_length=255,default=1)
    chat_rooms = GenericRelation('ChatRoom', related_query_name='surveyors')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = SurveyorManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    is_promoted = models.BooleanField(default=False)


    def __str__(self):
        return self.username



from django.db import models

class STKPushTransaction(models.Model):
    surveyor = models.ForeignKey('Surveyor', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    checkout_request_id = models.CharField(max_length=255)
    merchant_request_id = models.CharField(max_length=255)
    amount = models.FloatField()
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class SellerManager(BaseUserManager):
    def create_seller(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        seller = self.model(email=email, **extra_fields)
        seller.set_password(password)
        seller.save(using=self._db)
        return seller
class Buyer(AbstractUser):  # Inherit from AbstractUser
    groups = models.ManyToManyField(Group, related_name="buyer_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="buyer_permissions", blank=True)
    sellers = models.ManyToManyField("Seller", related_name="buyers")
    surveyors = models.ManyToManyField(Surveyor, blank=True)
    @property
    def is_buyer(self):
        return True


    def __str__(self):
        return self.username
    
from django.db import models
from django.conf import settings

class SellerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Seller(AbstractBaseUser):
    email = models.EmailField(unique=True)
    land_size = models.IntegerField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='land_images/')
    contact_details = models.CharField(max_length=255)
    other_contact_methods = models.CharField(max_length=255)
    chat_rooms = GenericRelation('ChatRoom', related_query_name='sellers')

    objects = SellerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['land_size', 'location', 'price', 'image', 'contact_details', 'other_contact_methods']

    def __str__(self):
        return self.email
    




class Land(models.Model):
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE, null=True, blank=True, related_name='lands')
    size = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='land_images/', blank=True, null=True)
    
    # New field for featuring
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.size} acres at {self.location}"




class ChatRoom(models.Model):
    buyer = models.ForeignKey('Buyer', on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE, null=True, blank=True)
    surveyor = models.ForeignKey('Surveyor', on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, default=1)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Polymorphic sender fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False, default=1)
    object_id = models.PositiveIntegerField(null=False, default=1)
    sender = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.sender} in room {self.chat_room.id}"


