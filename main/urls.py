from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    # TEAM URLS
    path('teams/', views.team_list, name='team_list'),
    path('teams/<slug:slug>/', views.team_detail, name='team_detail'),

    # MATCH URLS
    path('matches/<date>/', views.matches_by_date, name='matches_by_date'),
    path('matches/<uuid:match_id>/', views.match_detail, name='match_detail'),
    path('matches/history/', views.match_history, name='match_history'),

    # ADMIN URLS
    path('admin/matches/', views.match_list_admin, name='admin_match_list'),
    path('admin/matches/add/', views.add_match, name='add_match'),
    path('admin/matches/<uuid:match_id>/edit/', views.edit_match, name='edit_match'),
    path('admin/matches/<uuid:match_id>/delete/', views.delete_match, name='delete_match'),

    # Hompage
    path('', views.homepage, name='homepage'), 

    # PLAYER
    path('player',views.player_list ,name='player_list'),
    path('player/<slug:slug>', views.player_detail, name='player_detail'),
    path('', views.homepage, name="homepage"),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('user/login/', views.user_login, name='login'),
    path('user/register/', views.user_register, name='register'),
    path('user/logout/', views.user_logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)