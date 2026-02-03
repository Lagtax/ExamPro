# exams/admin_views.py - WITH DEBUG PRINTS

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import Exam, Question
from .serializers import ExamSerializer, QuestionSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_exam_list(request):
    print("=" * 50)
    print("ADMIN_EXAM_LIST called")
    print("=" * 50)
    
    exams = Exam.objects.all()
    print(f"Found {exams.count()} exams")
    
    exam_data = []
    for exam in exams:
        question_count = Question.objects.filter(exam=exam).count()
        exam_data.append({
            'id': exam.id,
            'title': exam.title,
            'duration': exam.duration,
            'total_marks': question_count,
            'department': exam.department,
            'allowed_batch': exam.allowed_batch,
            'question_count': question_count,
            'start_time': exam.start_time,
            'end_time': exam.end_time,
            'created_by': exam.created_by.user.username if exam.created_by else 'Admin',
        })
    
    return Response(exam_data)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_exam(request):
    print("=" * 50)
    print("ADMIN_CREATE_EXAM called")
    print("Request data:", request.data)
    print("=" * 50)
    
    title = request.data.get('title')
    duration = request.data.get('duration')
    department = request.data.get('department')
    allowed_batch = request.data.get('allowed_batch', '')
    start_time = request.data.get('start_time')
    end_time = request.data.get('end_time')
    
    print(f"Parsed data: title={title}, duration={duration}, department={department}")
    print(f"Times: start={start_time}, end={end_time}")
    
    if not all([title, duration, department]):
        error_msg = "title, duration, and department are required"
        print(f"ERROR: {error_msg}")
        return Response({"error": error_msg}, status=400)
    
    exam_data = {
        'title': title,
        'duration': duration,
        'department': department,
        'allowed_batch': allowed_batch,
        'created_by': None,
    }
    
    if start_time and end_time:
        try:
            start_dt = timezone.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = timezone.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            print(f"Parsed times: start={start_dt}, end={end_dt}")
            
            if end_dt <= start_dt:
                error_msg = "end_time must be after start_time"
                print(f"ERROR: {error_msg}")
                return Response({"error": error_msg}, status=400)
            
            exam_data['start_time'] = start_dt
            exam_data['end_time'] = end_dt
        except ValueError as e:
            error_msg = f"Invalid datetime format: {str(e)}"
            print(f"ERROR: {error_msg}")
            return Response({"error": error_msg}, status=400)
    else:
        exam_data['start_time'] = timezone.now()
        exam_data['end_time'] = timezone.now() + timezone.timedelta(days=7)
        print("Using default times (now to +7 days)")
    
    print(f"Creating exam with data: {exam_data}")
    
    try:
        exam = Exam.objects.create(**exam_data)
        print(f"SUCCESS! Created exam with ID: {exam.id}")
        return Response({
            "message": "Exam created successfully",
            "exam_id": exam.id
        }, status=201)
    except Exception as e:
        error_msg = f"Failed to create exam: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return Response({"error": error_msg}, status=500)


@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_exam(request, exam_id):
    print("=" * 50)
    print(f"ADMIN_UPDATE_EXAM called for exam_id={exam_id}")
    print("Request data:", request.data)
    print("=" * 50)
    
    try:
        exam = Exam.objects.get(id=exam_id)
        print(f"Found exam: {exam.title}")
    except Exam.DoesNotExist:
        print(f"ERROR: Exam {exam_id} not found")
        return Response({"error": "Exam not found"}, status=404)
    
    if 'title' in request.data:
        exam.title = request.data['title']
    if 'duration' in request.data:
        exam.duration = request.data['duration']
    if 'department' in request.data:
        exam.department = request.data['department']
    if 'allowed_batch' in request.data:
        exam.allowed_batch = request.data['allowed_batch']
    
    if 'start_time' in request.data:
        try:
            exam.start_time = timezone.datetime.fromisoformat(
                request.data['start_time'].replace('Z', '+00:00')
            )
        except ValueError as e:
            error_msg = f"Invalid start_time format: {str(e)}"
            print(f"ERROR: {error_msg}")
            return Response({"error": error_msg}, status=400)
    
    if 'end_time' in request.data:
        try:
            exam.end_time = timezone.datetime.fromisoformat(
                request.data['end_time'].replace('Z', '+00:00')
            )
        except ValueError as e:
            error_msg = f"Invalid end_time format: {str(e)}"
            print(f"ERROR: {error_msg}")
            return Response({"error": error_msg}, status=400)
    
    if exam.start_time and exam.end_time:
        if exam.end_time <= exam.start_time:
            print("ERROR: end_time must be after start_time")
            return Response({"error": "end_time must be after start_time"}, status=400)
    
    try:
        exam.save()
        print(f"SUCCESS! Updated exam {exam_id}")
        return Response({"message": "Exam updated successfully"})
    except Exception as e:
        error_msg = f"Failed to update exam: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return Response({"error": error_msg}, status=500)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_exam(request, exam_id):
    print("=" * 50)
    print(f"ADMIN_DELETE_EXAM called for exam_id={exam_id}")
    print("=" * 50)
    
    try:
        exam = Exam.objects.get(id=exam_id)
        print(f"Found exam: {exam.title}")
        exam.delete()
        print(f"SUCCESS! Deleted exam {exam_id}")
        return Response({"message": "Exam deleted successfully"})
    except Exam.DoesNotExist:
        print(f"ERROR: Exam {exam_id} not found")
        return Response({"error": "Exam not found"}, status=404)
    except Exception as e:
        error_msg = f"Failed to delete exam: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return Response({"error": error_msg}, status=500)


# Question views remain the same...
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_question_list(request, exam_id):
    questions = Question.objects.filter(exam_id=exam_id)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_question(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=404)
    
    question_text = request.data.get('question_text')
    option_a = request.data.get('option_a')
    option_b = request.data.get('option_b')
    option_c = request.data.get('option_c')
    option_d = request.data.get('option_d')
    correct_option = request.data.get('correct_option')
    
    if not all([question_text, option_a, option_b, option_c, option_d, correct_option]):
        return Response({"error": "All fields required"}, status=400)
    
    if correct_option not in ['A', 'B', 'C', 'D']:
        return Response({"error": "Correct option must be A, B, C, or D"}, status=400)
    
    try:
        question = Question.objects.create(
            exam=exam,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option
        )
        return Response({
            "message": "Question created successfully",
            "question_id": question.id
        }, status=201)
    except Exception as e:
        return Response({"error": f"Failed to create question: {str(e)}"}, status=500)


@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({"error": "Question not found"}, status=404)
    
    if 'question_text' in request.data:
        question.question_text = request.data['question_text']
    if 'option_a' in request.data:
        question.option_a = request.data['option_a']
    if 'option_b' in request.data:
        question.option_b = request.data['option_b']
    if 'option_c' in request.data:
        question.option_c = request.data['option_c']
    if 'option_d' in request.data:
        question.option_d = request.data['option_d']
    if 'correct_option' in request.data:
        if request.data['correct_option'] not in ['A', 'B', 'C', 'D']:
            return Response({"error": "Correct option must be A, B, C, or D"}, status=400)
        question.correct_option = request.data['correct_option']
    
    try:
        question.save()
        return Response({"message": "Question updated successfully"})
    except Exception as e:
        return Response({"error": f"Failed to update question: {str(e)}"}, status=500)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return Response({"message": "Question deleted successfully"})
    except Question.DoesNotExist:
        return Response({"error": "Question not found"}, status=404)
    except Exception as e:
        return Response({"error": f"Failed to delete question: {str(e)}"}, status=500)