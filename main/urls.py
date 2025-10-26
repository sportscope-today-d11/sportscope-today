from django.conf import settings
from django.urls import path
from . import views
<<<<<<< HEAD
=======
from .views import *
>>>>>>> a0a90bd67e981b27d28007091ac62da3a4377fb3
from django.conf.urls.static import static


app_name = 'main'

urlpatterns = [
<<<<<<< HEAD
    # TEAM URLS
    path('teams/', views.team_list, name='team_list'),
    path('teams/<slug:slug>/', views.team_detail, name='team_detail'),

    # MATCH URLS
    path('matches/history/', views.match_history, name='match_history'),
    path('matches/<date>/', views.matches_by_date, name='matches_by_date'),
    path('matches/detail/<uuid:match_id>/', views.match_detail, name='match_detail'),

    # DASHBOARD / CUSTOM ADMIN URLS
    path('dashboard/matches/', views.match_list_admin, name='admin_match_list'),
    path('dashboard/matches/add/', views.add_match, name='add_match'),
    path('dashboard/matches/<uuid:match_id>/edit/', views.edit_match, name='edit_match'),
    path('dashboard/matches/<uuid:match_id>/delete/', views.delete_match, name='delete_match'),

    # PLAYER
    path('player/',views.player_list ,name='player_list'),
    path('player/<slug:slug>', views.player_detail, name='player_detail'),
    path('', views.homepage, name="homepage"),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('user/login/', views.user_login, name='login'),
    path('user/register/', views.user_register, name='register'),
    path('user/logout/', views.user_logout, name='logout'),
=======
    # PLAYER
    path('player',views.player_list ,name='player_list'),
    path('player/<slug:slug>', views.player_detail, name='player_detail'),
    path('', homepage, name="homepage"),
    path('news/', news_list, name='news_list'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),
    path('user/login/', user_login, name='login'),
    path('user/register/', user_register, name='register'),
    path('user/logout/', user_logout, name='logout'),
    path('user/ajax-login/', ajax_login, name='ajax_login'),
    path('user/ajax-register/', ajax_register, name='ajax_register'),
    
    # Team CRUD (Admin only)
    path('team/add/', add_team, name='add_team'),
    path('team/edit/<slug:team_slug>/', edit_team, name='edit_team'),
    path('team/delete/<slug:team_slug>/', delete_team, name='delete_team'),
>>>>>>> a0a90bd67e981b27d28007091ac62da3a4377fb3
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
