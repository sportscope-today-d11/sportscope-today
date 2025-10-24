from django import forms
from django.contrib.auth.forms import UserCreationForm
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Role otomatis diset ke 'user'
            Person.objects.create(
                user=user,
                email=self.cleaned_data['email'],
                role='user'
            )
        return user
