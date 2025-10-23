from django import forms
from .models import Team
from .models import News

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

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            'title',
            'link',
            'author',
            'source',
            'publish_time',
            'content',
            'thumbnail',
            'category',
        ]

        widgets = {
            'publish_time': forms.DateInput(attrs={'type': 'date'}),
            'content': forms.Textarea(attrs={'rows': 5}),
        }
