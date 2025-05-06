from django import forms
from .models import Buyer, Seller, Surveyor
from .models import Seller
from realestate.models import Seller
from django.contrib.auth.models import User
from .models import Land
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth import get_user_model
from .models import Seller
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Surveyor
from .models import Message, ChatRoom
from .models import Land
from django.contrib.auth.hashers import make_password



class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        label="M-Pesa Phone Number",
        max_length=13,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 2547XXXXXXXX'})
    )

class SurveyorPromotionForm(forms.Form):
    surveyor_id = forms.IntegerField()
    phone_number = forms.CharField(max_length=15, required=True)


class SellerRegistrationForm(forms.ModelForm):
    # User credentials
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    # Initial land fields
    land_size   = forms.DecimalField(max_digits=10, decimal_places=2)
    location    = forms.CharField(max_length=255)
    price       = forms.DecimalField(max_digits=10, decimal_places=2)
    image       = forms.ImageField(required=False)
    latitude    = forms.FloatField()
    longitude   = forms.FloatField()

    class Meta:
        model = Seller
        fields = [
            'username', 'email', 'password',
            'land_size', 'location', 'price', 'image', 'latitude', 'longitude',
            'contact_details', 'other_contact_methods'
        ]

    def save(self, commit=True):
        # 1) Create the Seller
        seller = super().save(commit=False)
        # set the user/pass fields on your Seller
        seller.username = self.cleaned_data['username']
        seller.email    = self.cleaned_data['email']
        seller.password = make_password(self.cleaned_data['password'])
        if commit:
            seller.save()

            # 2) Create the initial Land record
            Land.objects.create(
                seller    = seller,
                size      = self.cleaned_data['land_size'],
                location  = self.cleaned_data['location'],
                price     = self.cleaned_data['price'],
                image     = self.cleaned_data.get('image'),
                latitude  = self.cleaned_data['latitude'],
                longitude = self.cleaned_data['longitude'],
            )
        return seller


class BuyerForm(UserCreationForm):
    class Meta:
        model = Buyer
        fields = ['username', 'email'] 




class SurveyorForm(forms.ModelForm):
    class Meta:
        model = Surveyor
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'qualifications', 'price', 'contacts']
        widgets = {
            'password': forms.PasswordInput(),  # Ensure password is inputted securely
        }
class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ['size', 'location', 'price', 'image', 'latitude', 'longitude']


class EditListingForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['land_size', 'location', 'price', 'image', 'contact_details', 'other_contact_methods']


class SellerContactForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['contact_details', 'other_contact_methods']
        

class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ['size', 'location', 'price', 'image', 'latitude', 'longitude']  # ✅ Add these two
        widgets = {
            'size': forms.TextInput(attrs={'placeholder': 'Enter land size in acres'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Enter price'}),
            'latitude': forms.NumberInput(attrs={'placeholder': 'Enter latitude (e.g. -1.2921)'}),
            'longitude': forms.NumberInput(attrs={'placeholder': 'Enter longitude (e.g. 36.8219)'}),
        }


        
User = get_user_model()

class SurveyorLoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    def clean_username_or_email(self):
        username_or_email = self.cleaned_data['username_or_email']
        # Check if the input is an email or username, then fetch the surveyor accordingly
        try:
            if '@' in username_or_email:  # If email is provided
                surveyor = Surveyor.objects.get(email=username_or_email)
            else:  # If username is provided
                surveyor = Surveyor.objects.get(username=username_or_email)
            return surveyor
        except Surveyor.DoesNotExist:
            raise forms.ValidationError("Invalid username or email.")
class SurveyorProfileForm(forms.ModelForm):
    class Meta:
        model = Surveyor
        fields = ['qualifications', 'price', 'contacts']  # Only the editable fields
        widgets = {
            'qualifications': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),  # For price field
            'contacts': forms.TextInput(attrs={'size': '40'}),
        }


