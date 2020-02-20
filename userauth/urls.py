from django.contrib.auth import views
from django.urls import path
from userauth import views as CustomViews
from django.shortcuts import redirect
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)

urlpatterns = [
    path('',views.LoginView.as_view(),name="index"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(),{'template_name':'registration/logged_out.html'}, name='logout'),
    # path('sync/', CustomViews.SyncView.as_view(), name='sync'),
    # path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    # path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    # path('password-change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]