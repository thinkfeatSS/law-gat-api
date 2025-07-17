# core/urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import *

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/verify/', OTPVerifyView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('user/', current_user),  # GET /api/user/
    # path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', change_password, name='change-password'),

    path('subjects/', SubjectListView.as_view(), name='subject-list'),
    path('questions/random/', get_random_questions),
    path('questions/submit/', submit_batch_attempts),
    path('dashboard/', dashboard),
    path('leaderboard/', leaderboard),
    path('upload-summary/', save_user_stats),
    path('get-summary/', get_user_stats),
]
