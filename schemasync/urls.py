from django.contrib.auth import views
from django.urls import path
from schemasync import views as CustomViews
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)

urlpatterns = [
    path('',CustomViews.CustomView.as_view(),name="index"),
    path('sync/', CustomViews.SyncView.as_view(), name='sync'),
]