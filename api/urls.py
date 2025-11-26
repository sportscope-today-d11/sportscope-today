from django.urls import path
from api.views import *

app_name = 'api'

urlpatterns = [
    # ENDPOINT AUTHENTIKASI
    path('auth/login/', login, name='login'),
    path('auth/register/', register, name='register'),
    path('auth/logout/', logout, name='logout'),

    # ENDPOINT MODUL TEAM
    path('api/teams/', team_list, name='team_list'),
    path('api/teams/<slug:slug>/', team_detail, name='team_detail'),

    # ENDPOINT MODUL NEWS

    # ENDPOINT MODUL PLAYER

    # ENDPOINT MODUL MATCH RESULTS

    # ENDPOINT MODUL FORUM

]