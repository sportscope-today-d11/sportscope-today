from django import forms
from .models import Thread, Comment
from .models import Category


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['category', 'title', 'content']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

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