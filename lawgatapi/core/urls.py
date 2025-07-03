# core/urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import *


urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/verify/', OTPVerifyView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),


    path('questions/random/', get_random_questions),
    path('questions/submit/', submit_batch_attempts),
    path('dashboard/', dashboard),
    path('leaderboard/', leaderboard),
]
