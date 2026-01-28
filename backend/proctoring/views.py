from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from exams.models import ExamAttempt
from .models import ProctorLog
from .constants import MAX_VIOLATIONS

@api_view(['POST'])
def log_event(request):
    user_id = request.data.get('user_id')
    exam_id = request.data.get('exam_id')
    event = request.data.get('event')

    if not user_id or not exam_id or not event:
        return Response({"error": "user_id, exam_id, and event required"}, status=400)

    try:
        attempt = ExamAttempt.objects.get(student_id=user_id, exam_id=exam_id)
    except ExamAttempt.DoesNotExist:
        return Response({"error": "Exam attempt not found"}, status=404)

    if attempt.is_submitted:
        return Response({"message": "Exam already submitted"})

    # Save violation
    ProctorLog.objects.create(student_id=user_id, exam_id=exam_id, event=event)
    attempt.violation_count += 1
    attempt.save()

    # Auto-submit if violations exceed limit
    if attempt.violation_count >= MAX_VIOLATIONS:
        attempt.is_submitted = True
        attempt.end_time = timezone.now()
        attempt.save()
        return Response({"message": "Violation limit exceeded. Exam auto-submitted."})

    return Response({
        "message": "Violation logged",
        "violations": attempt.violation_count,
        "remaining": MAX_VIOLATIONS - attempt.violation_count
    })
