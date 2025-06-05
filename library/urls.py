from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('add/', views.add_book, name='add_book'),
    path('edit/<str:doc_id>/', views.edit_book, name='edit_book'),
    path('delete/<str:doc_id>/', views.delete_book, name='delete_book'),
    path('view/<str:doc_id>/', views.view_book, name='view_book'),
    
    # Additional features
    path('genre/<str:genre>/', views.books_by_genre, name='books_by_genre'),
    path('statistics/', views.statistics, name='statistics'),
    
    # API endpoints for testing
    path('api/books/', views.api_books, name='api_books'),
] 