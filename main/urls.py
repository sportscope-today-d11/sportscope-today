from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('category/<slug:category_slug>/', views.thread_list, name='thread_list'),
    path('category/<slug:category_slug>/create/', views.create_thread, name='create_thread'),
    path('thread/<slug:slug>/', views.thread_detail, name='thread_detail'),
]
