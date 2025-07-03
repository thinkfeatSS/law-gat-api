# core/views.py

from rest_framework import generics, permissions, filters
from .models import Subject, Question, QuestionAttempt, User
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

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