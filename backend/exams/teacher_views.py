# exams/teacher_views.py (FIXED BATCH FILTERING)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Avg, Count
from .models import Exam, Question, ExamAttempt
from users.models import UserProfile
from .serializers import ExamSerializer, QuestionSerializer


def should_student_take_exam(student, exam):
 
    if student.department != exam.department:
        return False
    
    if not exam.allowed_batch or exam.allowed_batch.strip() == '':
        return True
    
    return student.batch == exam.allowed_batch



@api_view(['GET'])
@permission_classes([AllowAny])
def teacher_exam_list(request):
    user_id = request.query_params.get('user_id')
    
    if not user_id:
        return Response({"error": "user_id required"}, status=400)
    
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)
    
    if profile.role != 'teacher':
        return Response({"error": "Access denied. Teachers only."}, status=403)
    
    exams = Exam.objects.filter(created_by=profile)
    
    exam_data = []
    for exam in exams:
        question_count = Question.objects.filter(exam=exam).count()
        attempt_count = ExamAttempt.objects.filter(exam=exam, is_submitted=True).count()
        
        exam_data.append({
            'id': exam.id,
            'title': exam.title,
            'duration': exam.duration,
            'department': exam.department,
            'allowed_batch': exam.allowed_batch,
            'start_time': exam.start_time,
            'end_time': exam.end_time,
            'total_marks': question_count,
            'question_count': question_count,
            'attempts': attempt_count,
            'is_active': exam.is_active,
            'is_upcoming': exam.is_upcoming,
            'is_expired': exam.is_expired
        })
    
    return Response(exam_data)



@api_view(['POST'])
@permission_classes([AllowAny])
def teacher_create_exam(request):
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({"error": "user_id required"}, status=400)
    
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)
    
    if profile.role != 'teacher':
        return Response({"error": "Access denied. Teachers only."}, status=403)
    
    title = request.data.get('title')
    duration = request.data.get('duration')
    allowed_batch = request.data.get('allowed_batch', '')
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    
    if not all([title, duration, start_time, end_time]):
        return Response({"error": "title, duration, start_time, and end_time are required"}, status=400)
    
    try:
        start_dt = timezone.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = timezone.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        if end_dt <= start_dt:
            return Response({"error": "end_time must be after start_time"}, status=400)
    except ValueError:
        return Response({"error": "Invalid datetime format"}, status=400)
    
    exam = Exam.objects.create(
        title=title,
        duration=duration,
        department=profile.department,
        allowed_batch=allowed_batch,
        start_time=start_dt,
        end_time=end_dt,
        created_by=profile
    )
    
    return Response({
        "message": "Exam created successfully",
        "exam_id": exam.id
    }, status=201)



@api_view(['GET'])
@permission_classes([AllowAny])
def teacher_student_performance(request):
    user_id = request.query_params.get('user_id')
    exam_id = request.query_params.get('exam_id')
    
    if not user_id:
        return Response({"error": "user_id required"}, status=400)
    
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)
    
    if profile.role != 'teacher':
        return Response({"error": "Access denied. Teachers only."}, status=403)
    
    now = timezone.now()
    
    if exam_id:
        try:
            exam = Exam.objects.get(id=exam_id, created_by=profile)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found or not created by you"}, status=404)
        
        exam_expired = exam.end_time < now
        
        students_query = UserProfile.objects.filter(
            role='student',
            department=exam.department
        )
        
        if exam.allowed_batch and exam.allowed_batch.strip():
            students_query = students_query.filter(batch=exam.allowed_batch)
        
        all_students = students_query.select_related('user')
        
        student_data = []
        submitted_count = 0
        absent_count = 0
        not_attempted_count = 0
        total_score = 0
        
        for student in all_students:
            try:
                attempt = ExamAttempt.objects.get(student=student, exam=exam)
                
                if attempt.is_submitted:
                    status = 'submitted'
                    submitted_count += 1
                    total_score += attempt.score
                elif exam_expired:
                    status = 'absent'
                    absent_count += 1
                else:
                    status = 'in_progress'
                
                percentage = (attempt.score / exam.total_marks * 100) if exam.total_marks > 0 else 0
                
                student_info = {
                    'student_id': student.id,
                    'student_name': student.user.username,
                    'batch': student.batch,
                    'score': attempt.score,
                    'total_marks': exam.total_marks,
                    'percentage': round(percentage, 2),
                    'status': status,
                    'violations': attempt.violation_count,
                    'start_time': attempt.start_time,
                    'end_time': attempt.end_time,
                    'attempted': True
                }
                
            except ExamAttempt.DoesNotExist:
                if exam_expired:
                    status = 'absent'
                    absent_count += 1
                else:
                    status = 'not_attempted'
                    not_attempted_count += 1
                
                student_info = {
                    'student_id': student.id,
                    'student_name': student.user.username,
                    'batch': student.batch,
                    'score': 0,
                    'total_marks': exam.total_marks,
                    'percentage': 0,
                    'status': status,
                    'violations': 0,
                    'start_time': None,
                    'end_time': None,
                    'attempted': False
                }
            
            student_data.append(student_info)
        
        avg_score = (total_score / submitted_count) if submitted_count > 0 else 0
        avg_percentage = (avg_score / exam.total_marks * 100) if exam.total_marks > 0 else 0
        
        student_data.sort(key=lambda x: x['score'], reverse=True)
        
        return Response({
            'exam_title': exam.title,
            'exam_id': exam.id,
            'total_marks': exam.total_marks,
            'exam_expired': exam_expired,
            'allowed_batch': exam.allowed_batch or 'All Batches',
            'total_students': len(all_students),
            'submitted': submitted_count,
            'absent': absent_count,
            'not_attempted': not_attempted_count,
            'average_score': round(avg_score, 2),
            'average_percentage': round(avg_percentage, 2),
            'students': student_data
        })
    
    else:
        teacher_exams = Exam.objects.filter(created_by=profile)
        
        students = UserProfile.objects.filter(
            role='student',
            department=profile.department
        ).select_related('user')
        
        student_data = []
        for student in students:
            submitted = 0
            absent = 0
            not_attempted = 0
            
            total_score = 0
            total_possible = 0
            
            exam_details = []
            eligible_exam_count = 0  
            
            for exam in teacher_exams:
                if not should_student_take_exam(student, exam):
                    continue  
                
                eligible_exam_count += 1
                exam_expired = exam.end_time < now
                
                try:
                    attempt = ExamAttempt.objects.get(student=student, exam=exam)
                    
                    if attempt.is_submitted:
                        status = 'submitted'
                        submitted += 1
                        total_score += attempt.score
                        total_possible += exam.total_marks
                    elif exam_expired:
                        status = 'absent'
                        absent += 1
                    else:
                        status = 'in_progress'
                    
                    percentage = (attempt.score / exam.total_marks * 100) if exam.total_marks > 0 else 0
                    
                    exam_details.append({
                        'exam_id': exam.id,
                        'exam_title': exam.title,
                        'exam_batch': exam.allowed_batch or 'All Batches',
                        'score': attempt.score,
                        'total_marks': exam.total_marks,
                        'percentage': round(percentage, 2),
                        'status': status
                    })
                    
                except ExamAttempt.DoesNotExist:
                    if exam_expired:
                        status = 'absent'
                        absent += 1
                    else:
                        status = 'not_attempted'
                        not_attempted += 1
                    
                    exam_details.append({
                        'exam_id': exam.id,
                        'exam_title': exam.title,
                        'exam_batch': exam.allowed_batch or 'All Batches',
                        'score': 0,
                        'total_marks': exam.total_marks,
                        'percentage': 0,
                        'status': status
                    })
            
            avg_score = (total_score / submitted) if submitted > 0 else 0
            avg_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
            
            student_data.append({
                'student_id': student.id,
                'student_name': student.user.username,
                'batch': student.batch,
                'total_exams': eligible_exam_count,  # Only count eligible exams
                'submitted': submitted,
                'absent': absent,
                'not_attempted': not_attempted,
                'average_score': round(avg_score, 2),
                'average_percentage': round(avg_percentage, 2),
                'exam_details': exam_details
            })
        
        return Response({
            'department': profile.department,
            'total_students': len(student_data),
            'total_exams': teacher_exams.count(),
            'students': student_data
        })



@api_view(['PUT'])
@permission_classes([AllowAny])
def teacher_update_exam(request, exam_id):
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({"error": "user_id required"}, status=400)
    
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        exam = Exam.objects.get(id=exam_id, created_by=profile)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found or you don't have permission"}, status=404)
    
    if 'title' in request.data:
        exam.title = request.data['title']
    if 'duration' in request.data:
        exam.duration = request.data['duration']
    if 'allowed_batch' in request.data:
        exam.allowed_batch = request.data['allowed_batch']
    if 'start_time' in request.data:
        try:
            exam.start_time = timezone.datetime.fromisoformat(
                request.data['start_time'].replace('Z', '+00:00')
            )
        except ValueError:
            return Response({"error": "Invalid start_time format"}, status=400)
    if 'end_time' in request.data:
        try:
            exam.end_time = timezone.datetime.fromisoformat(
                request.data['end_time'].replace('Z', '+00:00')
            )
        except ValueError:
            return Response({"error": "Invalid end_time format"}, status=400)
    
    if exam.end_time <= exam.start_time:
        return Response({"error": "end_time must be after start_time"}, status=400)
    
    exam.save()
    return Response({"message": "Exam updated successfully"})




@api_view(['DELETE'])
@permission_classes([AllowAny])
def teacher_delete_exam(request, exam_id):
    user_id = request.query_params.get('user_id')
    
    if not user_id:
        return Response({"error": "user_id required"}, status=400)
    
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        exam = Exam.objects.get(id=exam_id, created_by=profile)
    except UserProfile.DoesNotExist:
        return Response({"error": "UserProfile not found"}, status=404)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found or you don't have permission"}, status=404)
    
    exam.delete()
    return Response({"message": "Exam deleted successfully"})