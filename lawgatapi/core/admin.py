from django.contrib import admin
from .models import User, Subject, Question, QuestionAttempt

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'profile_picture')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'subject', 'correct_option')
    list_filter = ('subject',)

@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'created_at')
