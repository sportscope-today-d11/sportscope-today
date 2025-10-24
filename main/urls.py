from django.conf import settings
from django.urls import path
from . import views
from .views import *
from django.conf.urls.static import static


app_name = 'main'

urlpatterns = [
    # PLAYER
    path('player',views.player_list ,name='player_list'),
    path('player/<slug:slug>', views.player_detail, name='player_detail')
    path('', homepage, name="homepage"),
    path('news/', news_list, name='news_list'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),
    path('user/login', user_login, name='login'),
    path('user/register', user_register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)