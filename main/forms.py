from django import forms
from .models import Team, Match, Person
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name', 'players', 'age', 'possession', 'goals',
            'assists', 'penalty_kicks', 'penalty_kick_attempts',
            'yellows', 'reds', 'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Team name'}),
            'players': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            'season',
            'match_date',
            'league',
            'home_team',
            'away_team',
            'full_time_home_goals',
            'full_time_away_goals',
            'full_time_result',
        ]
        widgets = {
            'match_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'home_team': forms.Select(attrs={'class': 'form-select'}),
            'away_team': forms.Select(attrs={'class': 'form-select'}),
            'league': forms.TextInput(attrs={'class': 'form-control'}),
            'full_time_home_goals': forms.NumberInput(attrs={'class': 'form-control'}),
            'full_time_away_goals': forms.NumberInput(attrs={'class': 'form-control'}),
            'full_time_result': forms.Select(
                choices=[('H', 'Home Win'), ('A', 'Away Win'), ('D', 'Draw')],
                attrs={'class': 'form-select'}
            ),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    # FIX: Syntax error diperbaiki
    role = forms.ChoiceField(
        choices=Person.ROLE_CHOICES,
        initial='user',
        required=False,
        widget=forms.HiddenInput(),  # Default hidden untuk user biasa
        label='Role'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Jika admin yang membuat user, tampilkan pilihan role
        if self.request and self.request.user.is_authenticated:
            try:
                if self.request.user.person.is_admin():
                    self.fields['role'].widget = forms.RadioSelect(attrs={'class': 'form-radio'})
                    self.fields['role'].required = True
            except Person.DoesNotExist:
                # Jika user tidak punya Person, tetap hidden
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Buat Person dengan role yang dipilih
            Person.objects.create(
                user=user,
                role=self.cleaned_data.get('role', 'user')
            )
        return user

# Form khusus untuk admin membuat user
class AdminUserCreationForm(RegisterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tampilkan pilihan role untuk admin
        self.fields['role'].widget = forms.RadioSelect(attrs={'class': 'form-radio'})
        self.fields['role'].required = True
        self.fields['role'].initial = 'user'