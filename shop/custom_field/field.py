from django.db.models import Field


class MyField(Field):

    description = 'can accept only 4 digit'

    def __int__(self, *args,**kwargs):
        pass
