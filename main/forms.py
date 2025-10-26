from django import forms
from .models import News

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
