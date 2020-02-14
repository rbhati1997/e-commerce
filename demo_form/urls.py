from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='author-list'),
    path('add/', views.add_author, name='add-author'),
    path('add-book/', views.add_book, name='add-book'),
    path('books/<int:author_id>', views.book_list, name='book-list'),
]