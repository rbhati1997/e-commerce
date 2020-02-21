from allauth.account.forms import SignupForm
from django import forms
from shop.models import DeliveryAddress

from shop.models import MyUser


class CustomSignupForm(SignupForm):
    TYPE_CHOICE = (
        ('A', 'Admin'),
        ('S', 'Seller'),
        ('C', 'Customer')
    )
    user_type = forms.ChoiceField(widget=forms.Select, choices=TYPE_CHOICE)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.save()
        custom_user = MyUser(user_type=self.cleaned_data['user_type'], user=user)
        custom_user.save()
        return user


class DeliveryAddressForm(forms.ModelForm):

    class Meta:
        model = DeliveryAddress
        fields = "__all__"
        widgets = {'customer_user': forms.HiddenInput()}
