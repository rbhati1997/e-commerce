from allauth.account.forms import SignupForm
from django import forms
from shop.models import DeliveryAddress, Product
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

from shop.utils import get_user


class CustomSignupForm(SignupForm):
    TYPE_CHOICE = (
        ('S', 'Seller'),
        ('C', 'Customer')
    )
    user_type = forms.ChoiceField(widget=forms.Select, choices=TYPE_CHOICE)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user_type = self.cleaned_data['user_type']
        if user_type == 'S':
            user.is_seller = True
            seller_group = Group.objects.get(name='seller_permission')
            seller_group.user_set.add(user)
        else:
            user.is_customer = True
            customer_group = Group.objects.get(name='customer_permission')
            customer_group.user_set.add(user)
        user.user_type = user_type
        user.save()
        return user


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = "__all__"
        widgets = {'customer_user': forms.HiddenInput()}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        # widgets = {'store': forms.HiddenInput()}

    def save(self, request):
        user = get_user(request)
        product = super(ProductForm, self).save(request)
        assign_perm('delete_product', user, product)
        assign_perm('view_product', user, product)
        customer_group = Group.objects.get(name='customer_permission')
        assign_perm('view_product', customer_group, product)
        user.save()
        return user
