# core/views.py

from rest_framework import generics, permissions, filters,parsers
from .models import Subject, Question, QuestionAttempt, User, UserStats
from .serializers import *
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
# from .serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser



class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    
# Random Questions with Filters
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_random_questions(request):
    subject_ids = request.GET.getlist('subjects')
    questions = Question.objects.all()

    if subject_ids:
        questions = questions.filter(subject__id__in=subject_ids)

    questions = questions.order_by('?')[:10]  # Random 10 questions

    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# Dashboard Analytics
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard(request):
    user = request.user
    attempts = QuestionAttempt.objects.filter(user=user)
    total = attempts.count()
    correct = attempts.filter(is_correct=True).count()
    wrong = total - correct
    accuracy = round((correct / total) * 100, 2) if total > 0 else 0

    # Subject-wise accuracy
    subjects = Subject.objects.all()
    subject_accuracies = []
    for subj in subjects:
        subj_attempts = attempts.filter(question__subject=subj)
        correct_subj = subj_attempts.filter(is_correct=True).count()
        total_subj = subj_attempts.count()
        accuracy_subj = round((correct_subj / total_subj) * 100, 2) if total_subj else 0
        subject_accuracies.append({
            'subject': subj.name,
            'accuracy': accuracy_subj
        })

    success_score = min(5, max(1, int(accuracy // 20)))

    return Response({
        'correct': correct,
        'wrong': wrong,
        'accuracy': accuracy,
        'success_score': success_score,
        'subject_accuracies': subject_accuracies
    })

# Leaderboard
@api_view(['GET'])
def leaderboard(request):
    leaders = User.objects.annotate(
        correct_answers=Count('questionattempt', filter=Q(questionattempt__is_correct=True))
    ).order_by('-correct_answers')[:3]

    data = [
        {
            'username': user.username,
            'correct_answers': user.correct_answers,
            'profile_picture': user.profile_picture.url if user.profile_picture else None
        }
        for user in leaders
    ]
    return Response(data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_batch_attempts(request):
    attempts = request.data.get('attempts', [])
    objects = []

    for attempt in attempts:
        q = Question.objects.get(id=attempt['question_id'])
        selected_option = attempt['selected_option']
        is_correct = selected_option == q.correct_option
        objects.append(
            QuestionAttempt(
                user=request.user,
                question=q,
                selected_option=selected_option,
                is_correct=is_correct
            )
        )

    QuestionAttempt.objects.bulk_create(objects)
    return Response({"message": "Batch submitted!"}, status=201)

class QuestionListView(ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Question.objects.all().select_related('subject')
        subject_ids = self.request.GET.getlist('subjects')
        if subject_ids:
            qs = qs.filter(subject__id__in=subject_ids)
        return qs.order_by('?')  # Randomized
    

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Registered. Check email for OTP."}, status=201)
        return Response(serializer.errors, status=400)
    
class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            return Response({"msg": "Account verified."})
        return Response(serializer.errors, status=400)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_stats(request):
    user = request.user
    try:
        stats = UserStats.objects.get(user=user)
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
    except UserStats.DoesNotExist:
        return Response({
            "correct": 0,
            "wrong": 0,
            "accuracy": 0.0,
            "success_score": 1,
            "subject_accuracies": [],
        })

@api_view(['POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def save_user_stats(request):
    user = request.user
    try:
        stats = UserStats.objects.get(user=user)
        serializer = UserStatsSerializer(stats, data=request.data)
    except UserStats.DoesNotExist:
        serializer = UserStatsSerializer(data=request.data)

    if serializer.is_valid():
        stats = serializer.save(user=user)
        return Response({"message": "Stats saved!"}, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UserProfileView(generics.RetrieveUpdateAPIView):
#     """
#     An endpoint for the authenticated user to retrieve and update their profile data,
#     specifically for uploading a profile picture.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]
    
#     # Key Change: Add parser classes to handle file uploads
#     parser_classes = [parsers.MultiPartParser, parsers.FormParser]

#     def get_object(self):
#         """
#         This view should return an object instance of the currently
#         authenticated user.
#         """
#         # Key Change: The object is simply the request.user
#         return self.request.user