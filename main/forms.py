from django import forms
from .models import Team
from .models import Match

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
        fields = ['home_team', 'away_team', 'date', 'time', 'score_home', 'score_away', 'league', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'home_team': forms.TextInput(attrs={'class': 'form-control'}),
            'away_team': forms.TextInput(attrs={'class': 'form-control'}),
            'score_home': forms.NumberInput(attrs={'class': 'form-control'}),
            'score_away': forms.NumberInput(attrs={'class': 'form-control'}),
            'league': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
