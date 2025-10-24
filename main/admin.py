from django.contrib import admin
from .models import Team, News, Match, Player

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'players', 'goals', 'assists', 'possession')
    search_fields = ('name',)
    list_filter = ('possession',)
    ordering = ('name',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'publish_time', 'source')
    search_fields = ('title', 'author', 'category')
    list_filter = ('category', 'publish_time')
    ordering = ('-publish_time',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'league', 'match_date', 'full_time_home_goals', 'full_time_away_goals')
    search_fields = ('home_team__name', 'away_team__name', 'league')
    list_filter = ('league', 'match_date')
    ordering = ('-match_date',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'nationality', 'overall_rating', 'value_euro', 'likes')
    search_fields = ('name', 'nationality', 'positions')
    list_filter = ('nationality', 'overall_rating')
    ordering = ('-overall_rating',)
