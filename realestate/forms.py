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






class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['land_size', 'location', 'price', 'image', 'contact_details', 'other_contact_methods']

class BuyerForm(UserCreationForm):
    class Meta:
        model = Buyer
        fields = ['username', 'email'] 



class SellerRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Seller
        fields = ['land_size', 'location', 'price', 'image', 'contact_details', 'other_contact_methods']

    def save(self, commit=True):
        # Create the seller instance directly without a User
        seller = super().save(commit=False)
        seller.username = self.cleaned_data['username']
        seller.email = self.cleaned_data['email']
        
        # Use set_password to handle password hashing
        seller.set_password(self.cleaned_data['password'])

        # Save the seller to the database if commit is True
        if commit:
            seller.save()
        
        return seller

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
        fields = ['size', 'location', 'price', 'image']


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
        fields = ['size', 'location', 'price', 'image']  # Add all fields you want in the form
        widgets = {
            'size': forms.TextInput(attrs={'placeholder': 'Enter land size in acres'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Enter price'}),
        }   


        
User = get_user_model()

class SurveyorLoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=254, label='Username or Email')
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


