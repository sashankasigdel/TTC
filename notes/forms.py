# notes/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SimpleRegistrationForm(UserCreationForm):
    # Only username and passwords - super simple!
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']