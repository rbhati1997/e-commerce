# from allauth.account.forms import LoginForm, SignupForm
# from django import forms
#
# from shop.models import CustomUser
#
#
# class SignupForm(forms.Form):
#     first_name = forms.CharField(max_length=30, label='Voornaam')
#     last_name = forms.CharField(max_length=30, label='Achternaam')
#
#     def signup(self, request, user):
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.save()