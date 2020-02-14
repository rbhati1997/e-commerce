from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=40)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.name
