from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Person, Match, Team

class RegisterForm(UserCreationForm):
    # Hidden field dengan default value 'user'
    role = forms.CharField(
        initial='user',
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Person.objects.create(
                user=user,
                role='user'
            )
        return user
        
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
