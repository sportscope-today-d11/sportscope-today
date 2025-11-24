from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

app_name = 'main'

urlpatterns = [
    # HOMEPAGE
    path('', views.homepage, name='homepage'),
    
    # TEAM URLS
    path('teams/', views.team_list, name='team_list'),
    path('teams/<slug:slug>/', views.team_detail, name='team_detail'),
    path('team/add/', views.add_team, name='add_team'),
    path('team/edit/<slug:team_slug>/', views.edit_team, name='edit_team'),
    path('team/delete/<slug:team_slug>/', views.delete_team, name='delete_team'),
    
    # MATCH URLS
    path('matches/history/', views.match_history, name='match_history'),
    path('matches/<str:date>/', views.matches_by_date, name='matches_by_date'),
    path('matches/detail/<uuid:match_id>/', views.match_detail, name='match_detail'),
    path('api/matches_detail/', views.api_match_detail, name='api_match_detail'),
    path('api/matches_history/', views.api_match_history, name='api_match_history'),
    
    # DASHBOARD / ADMIN MATCH URLS
    path('dashboard/matches/', views.match_list_admin, name='admin_match_list'),
    path('dashboard/matches/add/', views.add_match, name='add_match'),
    path('dashboard/matches/<uuid:match_id>/edit/', views.edit_match, name='edit_match'),
    path('dashboard/matches/<uuid:match_id>/delete/', views.delete_match, name='delete_match'),
    
    # PLAYER URLS
    path('player/', views.player_list, name='player_list'),
    path('player/<slug:slug>/', views.player_detail, name='player_detail'),
    path('player/add/', views.player_add_ajax, name='player_add_ajax'),
    
    # NEWS URLS
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/<int:news_id>/toggle_bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('news/bookmarked/', views.bookmarked_news, name='bookmarked_news'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:news_id>/edit/', views.news_update, name='news_update'),
    path('news/<int:news_id>/delete/', views.news_delete, name='news_delete'),
    path('ajax/', views.news_list_ajax, name='news_list_ajax'),
    
    # AUTH URLS
    path('user/login/', views.user_login, name='login'),
    path('user/register/', views.user_register, name='register'),
    path('user/logout/', views.user_logout, name='logout'),
    path('user/ajax-login/', views.ajax_login, name='ajax_login'),
    path('user/ajax-register/', views.ajax_register, name='ajax_register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
