from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from proctoring.constants import MAX_VIOLATIONS

from .models import Exam, Question, ExamAttempt, Answer
from users.models import UserProfile
from .serializers import ExamSerializer, QuestionSerializer



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

    now = timezone.now()

    exams = Exam.objects.filter(
        department=profile.department,  
    ).filter(
        Q(allowed_batch='') | Q(allowed_batch=profile.batch)
    )
    
    
    if hasattr(Exam, 'start_time'):
        exams = exams.filter(
            start_time__lte=now,  
            end_time__gte=now     
        )

    submitted_exam_ids = ExamAttempt.objects.filter(
        student=profile,
        is_submitted=True
    ).values_list('exam_id', flat=True)

    exams = exams.exclude(id__in=submitted_exam_ids)

    exam_data = []
    for exam in exams:
        data = {
            'id': exam.id,
            'title': exam.title,
            'duration': exam.duration,
            'department': exam.department,
            'allowed_batch': exam.allowed_batch,
            'total_marks': exam.total_marks,
        }
        
        if hasattr(exam, 'start_time') and hasattr(exam, 'end_time'):
            data['start_time'] = exam.start_time
            data['end_time'] = exam.end_time
            data['is_active'] = exam.is_active
            data['time_remaining'] = (exam.end_time - now).total_seconds() / 3600  # hours
        
        exam_data.append(data)

    return Response(exam_data)



@api_view(['GET'])
@permission_classes([AllowAny])
def exam_questions(request, exam_id):
    user_id = request.query_params.get("user_id")
    if not user_id:
        return Response({"error": "user_id required"}, status=400)

    try:
        user_id = int(user_id)
    except ValueError:
        return Response({"error": "Invalid user_id"}, status=400)

    try:
        user = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)

    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=404)

    if exam.department != user.department:  # Changed from allowed_class
        return Response({"error": "Not allowed"}, status=403)
    
    if exam.allowed_batch and exam.allowed_batch != user.batch:
        return Response({"error": "Not allowed"}, status=403)

    if hasattr(exam, 'start_time') and hasattr(exam, 'end_time'):
        now = timezone.now()
        if now < exam.start_time:
            return Response({"error": "Exam has not started yet"}, status=403)
        if now > exam.end_time:
            return Response({"error": "Exam has ended"}, status=403)

    questions = Question.objects.filter(exam_id=exam_id)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)



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

    if exam.department != profile.department:  
        return Response({"error": "Not allowed"}, status=403)
    
    if exam.allowed_batch and exam.allowed_batch != profile.batch:
        return Response({"error": "Not allowed"}, status=403)

    if hasattr(exam, 'start_time') and hasattr(exam, 'end_time'):
        now = timezone.now()
        if now < exam.start_time:
            return Response({"error": "Exam has not started yet"}, status=403)
        if now > exam.end_time:
            return Response({"error": "Exam has ended"}, status=403)

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


@api_view(['POST'])
@permission_classes([AllowAny])
def mark_absent_students(request):
    """
    This endpoint should be called periodically (e.g., via cron job)
    to mark students as absent for expired exams they didn't attend
    """
    now = timezone.now()
    
    if hasattr(Exam, 'end_time'):
        expired_exams = Exam.objects.filter(end_time__lt=now)
        
        marked_count = 0
        
        for exam in expired_exams:
            students = UserProfile.objects.filter(
                role='student',
                department=exam.department
            )
            
            if exam.allowed_batch:
                students = students.filter(batch=exam.allowed_batch)
            
            for student in students:
                attempt, created = ExamAttempt.objects.get_or_create(
                    student=student,
                    exam=exam,
                    defaults={
                        'status': 'absent',
                        'is_submitted': True,
                        'score': 0,
                        'end_time': exam.end_time
                    }
                )
                
                if not created and not attempt.is_submitted:
                    attempt.status = 'absent'
                    attempt.is_submitted = True
                    attempt.score = 0
                    attempt.end_time = exam.end_time
                    attempt.save()
                    marked_count += 1
        
        return Response({
            "message": f"Marked {marked_count} students as absent",
            "marked_count": marked_count
        })
    else:
        return Response({"message": "Scheduling not enabled"})