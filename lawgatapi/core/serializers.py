# core/serializers.py

from rest_framework import serializers
from .models import User, Subject, Question, QuestionAttempt, UserStats
from django.core.mail import send_mail
import random

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile_picture']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAttempt
        fields = '__all__'

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.save()

        send_mail(
            'Verify your account',
            f'Your OTP is {otp}',
            'noreply@lawgat.com',
            [user.email],
            fail_silently=False,
        )
        return user

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        user = User.objects.get(email=data['email'])
        if user.otp == data['otp']:
            user.is_verified = True
            user.save()
            return data
        raise serializers.ValidationError("Invalid OTP")
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = ['correct', 'wrong', 'accuracy', 'success_score', 'subject_accuracies']


# class ProfileImageSerializer(serializers.ModelSerializer):
#     profile_picture = serializers.SerializerMethodField()

#     def get_profile_picture(self, obj):
#         request = self.context.get("request")
#         if request and obj.profile_picture and hasattr(obj.profile_picture, 'url'):
#             return request.build_absolute_uri(obj.profile_picture.url)
#         return None

#     class Meta:
#         model = User
#         fields = ['profile_picture']

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'id', 
#             'username', 
#             'email', 
#             'profile_picture'
#         ]
#         # Make most fields read-only; this endpoint is just for the picture
#         read_only_fields = ['id', 'username', 'email']