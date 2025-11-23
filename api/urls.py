from django.urls import path
from api.views import login, register, logout

app_name = 'api'

urlpatterns = [
    # ENDPOINT AUTHENTIKASI
    path('auth/login/', login, name='login'),
    path('auth/register/', register, name='register'),
    path('auth/logout/', logout, name='logout'),

    # ENDPOINT MODUL TEAM

    # ENDPOINT MODUL NEWS

    # ENDPOINT MODUL PLAYER

    # ENDPOINT MODUL MATCH RESULTS

    # ENDPOINT MODUL FORUM

]