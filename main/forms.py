from django import forms
from .models import Thread, Comment

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 1,    
                'cols': 40, 
                'style': 'resize: vertical; width: 100%;',
                'placeholder': 'Write a comment...'
            })
        }
