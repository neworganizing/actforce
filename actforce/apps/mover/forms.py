from django import forms

from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.forms import USStateField, USZipCodeField


class SalesforceForm(forms.Form):
    firstname = forms.CharField(label="First Name", widget=forms.TextInput(attrs={'placeholder': 'First', 'class': 'name left firstname'}))
    lastname = forms.CharField(label="First Name", widget=forms.TextInput(attrs={'placeholder': 'First', 'class': 'name right lastname'}))
    title = forms.CharField(required=False, label="Title", widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    email = forms.EmailField(label="Primary Email Address", widget=forms.TextInput(attrs={'placeholder': 'Email', 'class': 'left'}))
    alt_email = forms.EmailField(required=False, label="Alt Email", widget=forms.TextInput(attrs={'placeholder': 'Alt Email', 'class': 'right'}))
    phone = forms.CharField(required=False, label="Phone Number", widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
    address = forms.CharField(required=False, label="Address 1", widget=forms.Textarea(attrs={'placeholder': 'Mailing Address', 'class': 'addressarea'}))
    city = forms.CharField(required=False, label="City", widget=forms.TextInput(attrs={'placeholder': 'City'}))
    state = forms.CharField(widget=forms.Select(choices=(('', '----------'),) + STATE_CHOICES, attrs={'class': 'left'}), required=False, label="State")
    zip = USZipCodeField(required=False, label="Zip Code", widget=forms.TextInput(attrs={'placeholder': 'Zip', 'class': 'right'}))
    orgid = forms.CharField(required=True, widget=forms.HiddenInput())
    orgname = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'uneditable-input org', 'disabled': 'disabled'}))
    akuserid = forms.CharField(required=True, widget=forms.HiddenInput())
    akactionid = forms.CharField(required=True, widget=forms.HiddenInput())
    akpageid = forms.CharField(required=True, widget=forms.HiddenInput())
    salesforceid = forms.CharField(required=False, widget=forms.HiddenInput())
    action = forms.CharField(required=False, widget=forms.HiddenInput())
