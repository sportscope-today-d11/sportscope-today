from django.conf import settings
from django.urls import path
from . import views
from .views import *
from django.conf.urls.static import static


app_name = 'main'

urlpatterns = [
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
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
