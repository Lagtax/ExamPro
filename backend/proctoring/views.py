from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from exams.models import ExamAttempt
from users.models import UserProfile
from .models import ProctorLog
from .constants import MAX_VIOLATIONS

@api_view(['POST'])
@permission_classes([AllowAny])
def log_event(request):
    user_id = request.data.get('user_id')
    exam_id = request.data.get('exam_id')
    event = request.data.get('event')

    if not user_id or not exam_id or not event:
        return Response({"error": "user_id, exam_id, and event required"}, status=400)

    try:
        profile = UserProfile.objects.get(user_id=user_id)
        attempt = ExamAttempt.objects.get(student=profile, exam_id=exam_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    except ExamAttempt.DoesNotExist:
        return Response({"error": "Exam attempt not found"}, status=404)

    if attempt.is_submitted:
        return Response({"message": "Exam already submitted"})

    # Save violation log
    ProctorLog.objects.create(
        student=profile.user,
        exam_id=exam_id,
        event=event
    )
    
    attempt.violation_count += 1
    attempt.save()

    # Auto-submit if violations exceed limit
    if attempt.violation_count >= MAX_VIOLATIONS:
        attempt.is_submitted = True
        attempt.end_time = timezone.now()
        attempt.save()
        return Response({
            "message": "Violation limit exceeded. Exam auto-submitted.",
            "auto_submitted": True,
            "violations": attempt.violation_count
        })

    return Response({
        "message": "Violation logged",
        "violations": attempt.violation_count,
        "remaining": MAX_VIOLATIONS - attempt.violation_count,
        "auto_submitted": False
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_violations(request):
    """Get violation count for a specific exam attempt"""
    user_id = request.query_params.get('user_id')
    exam_id = request.query_params.get('exam_id')

    if not user_id or not exam_id:
        return Response({"error": "user_id and exam_id required"}, status=400)

    try:
        profile = UserProfile.objects.get(user_id=user_id)
        attempt = ExamAttempt.objects.get(student=profile, exam_id=exam_id)
    except (UserProfile.DoesNotExist, ExamAttempt.DoesNotExist):
        return Response({"error": "Exam attempt not found"}, status=404)

    return Response({
        "violations": attempt.violation_count,
        "remaining": MAX_VIOLATIONS - attempt.violation_count,
        "max_violations": MAX_VIOLATIONS
    })