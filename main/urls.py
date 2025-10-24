from django.conf import settings
from django.urls import path
from .views import homepage
from django.conf.urls.static import static


app_name = 'main'

urlpatterns = [
    path('', homepage, name="homepage")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)