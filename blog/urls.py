from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('blogs/', views.blogs, name='blogs'),
    path('blog-detail/<slug:slug>/', views.blog_detail, name='blog-detail'),
]
