from django.shortcuts import render
from .forms import AuthorForm, BookForm
from .models import Author, Book
from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):

    authors = Author.objects.all()
    return render(request, 'author_index.html', {'authors': authors})


def add_author(request):
    if request.method == 'POST':
        a = Author(name=request.POST['name'])
        a.save()
        return HttpResponseRedirect(reverse('author-list'))
    form = AuthorForm()
    return render(request, 'add_author.html', {'form': form})


def add_book(request):
    if request.method == 'POST':
        b = Book(name=request.POST['name'], author_id=request.POST['author'])
        b.save()
        return HttpResponseRedirect(reverse('author-list'))

    form = BookForm()
    return render(request, 'add_book.html', {'form': form})


def book_list(request, author_id):
    books = Book.objects.filter(author_id=author_id)
    return render(request, 'book_list.html', {'books': books})
