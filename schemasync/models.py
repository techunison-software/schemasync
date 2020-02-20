from django.db import models
from django import forms

# Create your models here.
class SourceForm(forms.Form):
    # required_css_class = 'form-control'
    s_hostname = forms.CharField(label='Host Name', max_length=200)
    s_port = forms.CharField(label='Port', max_length=5)
    s_database = forms.CharField(label='Database', max_length=50)
    s_username = forms.CharField(label='Username', max_length=50)
    s_password = forms.CharField(label="Password",widget=forms.PasswordInput(),max_length=20)
    d_hostname = forms.CharField(label='Host Name', max_length=200)
    d_port = forms.CharField(label='Port', max_length=5)
    d_database = forms.CharField(label='Database', max_length=50)
    d_username = forms.CharField(label='Username', max_length=50)
    d_password = forms.CharField(label="Password",widget=forms.PasswordInput(),max_length=20)

class DatabaseModel(models.Model):
    
    hostname = models.CharField(max_length=200)
    port = models.IntegerField()
    database = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
class SyncInfoForm(forms.Form):
    textarea = forms.CharField(
        widget = forms.Textarea(),
    )