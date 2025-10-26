from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('category/<slug:category_slug>/', views.thread_list, name='thread_list'),
    path('category/<slug:category_slug>/create/', views.create_thread, name='create_thread'),
    path('thread/<slug:slug>/', views.thread_detail, name='thread_detail'),
    path('threads/', views.all_threads, name='all_threads'),
    path('categories/', views.category_list, name='category_list'),
    path("api/categories/", views.category_list_json, name="category_list_json"),
    path('categories/create/', views.create_category, name='create_category'),


]
