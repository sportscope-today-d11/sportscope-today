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
    path('matches/', views.match_list, name='match_list'),
    path('matches/<uuid:match_id>/', views.match_detail, name='match_detail'),

    # NEWS URLS
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:news_id>/edit/', views.news_update, name='news_update'),
    path('news/<int:news_id>/delete/', views.news_delete, name='news_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)