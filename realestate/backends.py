# realestate/backends.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from realestate.models import Surveyor
from django.contrib.auth.backends import BaseBackend
from realestate.models import Seller

class SellerAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            seller = Seller.objects.get(email=username)
            if seller.check_password(password):
                return seller
        except Seller.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Seller.objects.get(pk=user_id)
        except Seller.DoesNotExist:
            return None

User = get_user_model()  # this will be your Buyer model

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        print(f"EmailBackend: trying to authenticate {username}")
        try:
            user = User.objects.get(email=username)
            print("EmailBackend: found user", user.email)
            if user.check_password(password):
                print("EmailBackend: password OK")
                return user
            else:
                print("EmailBackend: password incorrect")
        except User.DoesNotExist:
            print("EmailBackend: no such Buyer")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class SurveyorAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        print(f"SurveyorAuthBackend: trying to authenticate {username}")
        try:
            surveyor = Surveyor.objects.get(email=username)
            print("SurveyorAuthBackend: found surveyor", surveyor.email)
            if surveyor.check_password(password):
                print("SurveyorAuthBackend: password OK")
                return surveyor
            else:
                print("SurveyorAuthBackend: password incorrect")
        except Surveyor.DoesNotExist:
            print("SurveyorAuthBackend: no such Surveyor")
        return None

    def get_user(self, user_id):
        try:
            return Surveyor.objects.get(pk=user_id)
        except Surveyor.DoesNotExist:
            return None
