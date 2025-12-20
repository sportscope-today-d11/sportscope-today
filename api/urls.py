from django.urls import path
from api.views import *

app_name = 'api'

urlpatterns = [
    # ENDPOINT AUTHENTIKASI
    path('auth/login/', login, name='login'),
    path('auth/register/', register, name='register'),
    path('auth/logout/', logout, name='logout'),

    # ENDPOINT MODUL TEAM
    path('teams/', team_list, name='team_list'),
    path('teams/<slug:slug>/', team_detail, name='team_detail'),

    # ENDPOINT MODUL NEWS
    path("news/create/", api_create_news, name="api_create_news"),
    path("news/update/", api_update_news, name="api_update_news"),
    path("news/delete/", api_delete_news, name="api_delete_news"),
    path("news/bookmarks/", api_bookmarked_news, name="api_bookmarked_news"),
    path("news/<int:news_id>/bookmark/", api_toggle_bookmark, name="api_toggle_bookmark"),
    path("news/<int:news_id>/", api_news_detail, name="api_news_detail"),
    path("news/", api_news_list, name="api_news_list"),

    # ENDPOINT MODUL PLAYER

    # ENDPOINT MODUL MATCH RESULTS
    path("matches/by-date/<str:date>/", api_matches_by_date, name="api_matches_by_date"),
    path("matches/", api_match_history, name="api_match_history"),
    path("matches/<str:match_id>/", api_match_detail, name="api_match_detail"),
    
    path("admin/matches/", api_match_list_admin, name="api_match_list_admin"),
    path("admin/matches/add/", api_add_match, name="api_add_match"),
    path("admin/matches/<uuid:match_id>/edit/", api_edit_match, name="api_edit_match"),
    path("admin/matches/<uuid:match_id>/delete/", api_delete_match, name="api_delete_match"),

    # ENDPOINT MODUL FORUM
    path("forum/add-forum/", api_add_forum, name="api_add_forum"),
    path("forum/<uuid:forum_id>/add-comment/", api_add_comment, name="api_add_comment"),
    path("forum/delete-forum/", api_delete_forum, name="api_delete_forum"),
    path("forum/delete-comment/", api_delete_comment, name="api_delete_comment"),
    path("forum/add-bookmart/", api_add_bookmart, name="api_add_bookmart"),
    path("forum/forums/", api_forum_list, name="api_forum_list"),
    path("forum/<uuid:forum_id>/", api_forum_detail, name="api_forum_detail"),
    path("forum/<uuid:forum_id>/comments/", api_forum_comments, name="api_forum_comments"),
    path("forum/my-bookmark/", api_forum_my_bookmark, name="api_forum_my_bookmark"),
    path("forum/like/", api_forum_like, name="api_forum_like"),
    path("forum/comment-like/", api_comment_like, name="api_comment_like"),
]