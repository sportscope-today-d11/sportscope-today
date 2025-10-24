from django.conf import settings
from django.urls import path
from .views import *
from django.conf.urls.static import static


app_name = 'main'

urlpatterns = [
    path('', homepage, name="homepage"),
    path('news/', news_list, name='news_list'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),
    path('user/login/', user_login, name='login'),
    path('user/register/', user_register, name='register'),
    path('user/logout/', user_logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)