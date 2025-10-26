from django.contrib import admin
from .models import Player, News, Team, Person

# Register your models here.
admin.site.register(Player)
admin.site.register(News)
admin.site.register(Team)
admin.site.register(Person)
