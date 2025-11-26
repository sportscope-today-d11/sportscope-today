from django.urls import path
from api.views import login, register, logout
from api.views import api_news_list, api_news_detail, api_toggle_bookmark, api_bookmarked_news

app_name = 'api'

urlpatterns = [
    # ENDPOINT AUTHENTIKASI
    path('auth/login/', login, name='login'),
    path('auth/register/', register, name='register'),
    path('auth/logout/', logout, name='logout'),

    # ENDPOINT MODUL TEAM

    # ENDPOINT MODUL NEWS
    path("api/news/", api_news_list, name="api_news_list"),
    path("api/news/<int:news_id>/", api_news_detail, name="api_news_detail"),
    path("api/news/<int:news_id>/bookmark/", api_toggle_bookmark, name="api_toggle_bookmark"),
    path("api/bookmarks/", api_bookmarked_news, name="api_bookmarked_news"),

    # ENDPOINT MODUL PLAYER

    # ENDPOINT MODUL MATCH RESULTS

    # ENDPOINT MODUL FORUM

]