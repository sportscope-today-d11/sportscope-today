from django.conf import settings
from django.urls import path
from . import views
from .views import *
from django.conf.urls.static import static


app_name = 'main'

urlpatterns = [
    # NEWS URLS
    path('news/', news_list, name='news_list'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),
    path('news/<int:news_id>/toggle_bookmark/', toggle_bookmark, name='toggle_bookmark'),
    path('news/bookmarked/', bookmarked_news, name='bookmarked_news'),
    path('news/create/', news_create, name='news_create'),
    path('news/<int:news_id>/edit/', news_update, name='news_update'),
    path('news/<int:news_id>/delete/', news_delete, name='news_delete'),
    path('ajax/', news_list_ajax, name='news_list_ajax'),

    path('', homepage, name="homepage"),
    path('user/login', user_login, name='login'),
    path('user/register', user_register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)