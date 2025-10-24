from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    # PLAYER
    path('player',views.player_list ,name='player_list'),
    path('player/<slug:slug>', views.player_detail, name='player_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)