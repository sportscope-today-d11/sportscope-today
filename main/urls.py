from django.conf import settings
from django.urls import path
from main.views import *
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)