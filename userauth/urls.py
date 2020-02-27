from django.contrib.auth import views
from django.urls import path
from userauth import views as CustomViews
from django.shortcuts import redirect
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)

urlpatterns = [
    path('',CustomViews.CustomLogin.as_view(),name="index"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(),{'template_name':'registration/logged_out.html'}, name='logout'),
]