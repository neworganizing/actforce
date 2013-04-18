from django import forms

from actforce.apps.base.models import SalesforceAccount


class SalesforceAccountForm(forms.ModelForm):
    login = forms.EmailField(widget=forms.TextInput(attrs={'class': 'span6'}), label="Salesforce Login")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'span6'}), label="Salesforce Password")
    token = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'span6'}), label="Salesforce Security Token")

    class Meta:
        model = SalesforceAccount
        exclude = ('account',)
