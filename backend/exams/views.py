from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from proctoring.constants import MAX_VIOLATIONS

from .models import Exam, Question, ExamAttempt, Answer
from users.models import UserProfile
from .serializers import ExamSerializer, QuestionSerializer


# --------------------------
# List Exams (UPDATED)
# --------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def exam_list(request):
    user_id = request.query_params.get('user_id')

    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)

    # Get all exams for this student's class and batch
    exams = Exam.objects.filter(
        allowed_class=profile.class_name,
        allowed_batch=profile.batch
    )

    # Get all exam IDs that this student has already submitted
    submitted_exam_ids = ExamAttempt.objects.filter(
        student=profile,
        is_submitted=True
    ).values_list('exam_id', flat=True)

    # Exclude submitted exams from the list
    exams = exams.exclude(id__in=submitted_exam_ids)

    serializer = ExamSerializer(exams, many=True)
    return Response(serializer.data)


# --------------------------
# Exam Questions
# --------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def exam_questions(request, exam_id):
    # 1️⃣ Get the user_id from query params
    user_id = request.query_params.get("user_id")
    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    try:
        user_id = int(user_id)
    except ValueError:
        return Response({"error": "Invalid user_id"}, status=400)

    # 2️⃣ Fetch the user profile
    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)

    # 3️⃣ Fetch the exam
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=404)

    # 4️⃣ Check batch/class restrictions
    if exam.allowed_class != user.class_name or exam.allowed_batch != user.batch:
        return Response({"error": "Not allowed"}, status=403)

    # 5️⃣ Return all questions for this exam
    questions = Question.objects.filter(exam_id=exam_id)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# --------------------------
# Start Exam
# --------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def start_exam(request, exam_id):
    user_id = request.data.get("user_id")

    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    try:
        profile = UserProfile.objects.get(user_id=user_id)
        exam = Exam.objects.get(id=exam_id)
    except (UserProfile.DoesNotExist, Exam.DoesNotExist):
        return Response({"error": "Invalid user or exam"}, status=404)

    if exam.allowed_class != profile.class_name or exam.allowed_batch != profile.batch:
        return Response({"error": "Not allowed"}, status=403)

    attempt, created = ExamAttempt.objects.get_or_create(
        student=profile,
        exam=exam
    )

    if attempt.is_submitted:
        return Response({"error": "Exam already submitted"}, status=400)

    return Response({
        "message": "Exam started",
        "start_time": attempt.start_time,
        "duration": exam.duration
    })


# --------------------------
# Submit Exam
# --------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_exam(request, exam_id):
    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    try:
        attempt = ExamAttempt.objects.get(student__user_id=user_id, exam_id=exam_id)
    except ExamAttempt.DoesNotExist:
        return Response({"error": "Exam attempt not found"}, status=404)

    if attempt.is_submitted:
        return Response({"error": "Already submitted"}, status=400)

    exam = attempt.exam
    end_time = attempt.start_time + timezone.timedelta(minutes=exam.duration)

    if timezone.now() > end_time:
        attempt.is_submitted = True
        attempt.end_time = end_time
        attempt.save()
        return Response({"message": "Time over. Exam auto-submitted.", "score": attempt.score})

    if attempt.violation_count >= MAX_VIOLATIONS:
        attempt.is_submitted = True
        attempt.end_time = timezone.now()
        attempt.save()
        return Response({"message": "Violation limit exceeded. Exam auto-submitted.", "score": attempt.score})

    answers = request.data.get('answers', [])
    score = 0
    Answer.objects.filter(attempt=attempt).delete()

    for item in answers:
        question = Question.objects.get(id=item['question_id'], exam=attempt.exam)
        Answer.objects.create(attempt=attempt, question=question, selected_option=item['selected_option'])
        if item['selected_option'] == question.correct_option:
            score += 1

    attempt.score = score
    attempt.is_submitted = True
    attempt.end_time = timezone.now()
    attempt.save()

    return Response({"message": "Exam submitted", "score": score})


# --------------------------
# Exam Result
# --------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def exam_result(request, exam_id):
    user_id = request.query_params.get("user_id")
    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    try:
        attempt = ExamAttempt.objects.get(student__user_id=user_id, exam_id=exam_id)
    except ExamAttempt.DoesNotExist:
        return Response({"error": "Result not found"}, status=404)

    # Get total number of questions for this exam
    total_questions = Question.objects.filter(exam_id=exam_id).count()

    return Response({
        "score": attempt.score,
        "total_questions": total_questions,
        "submitted": attempt.is_submitted
    })