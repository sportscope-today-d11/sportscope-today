from django.shortcuts import render
from .models import Team

# Create your views here.
def homepage(request):
    teams = Team.objects.all()
    context={
        "teams":teams,
    }
    return render(request, 'homepage.html', context)
