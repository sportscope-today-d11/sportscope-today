from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Person

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    # Hidden field dengan default value 'user'
    role = forms.CharField(
        initial='user',
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Role otomatis diset ke 'user'
            Person.objects.create(
                user=user,
                role='user'
            )
        return user
