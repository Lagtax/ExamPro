# exams/admin_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Exam, Question
from .serializers import ExamSerializer, QuestionSerializer


# --------------------------
# List All Exams (Admin)
# --------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_exam_list(request):
    exams = Exam.objects.all()
    exam_data = []
    
    for exam in exams:
        question_count = Question.objects.filter(exam=exam).count()
        exam_data.append({
            'id': exam.id,
            'title': exam.title,
            'duration': exam.duration,
            'total_marks': exam.total_marks,
            'allowed_class': exam.allowed_class,
            'allowed_batch': exam.allowed_batch,
            'question_count': question_count
        })
    
    return Response(exam_data)


# --------------------------
# Create Exam
# --------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_exam(request):
    title = request.data.get('title')
    duration = request.data.get('duration')
    total_marks = request.data.get('total_marks')
    allowed_class = request.data.get('allowed_class')
    allowed_batch = request.data.get('allowed_batch')
    
    if not all([title, duration, total_marks, allowed_class, allowed_batch]):
        return Response({"error": "All fields required"}, status=400)
    
    exam = Exam.objects.create(
        title=title,
        duration=duration,
        total_marks=total_marks,
        allowed_class=allowed_class,
        allowed_batch=allowed_batch
    )
    
    return Response({
        "message": "Exam created successfully",
        "exam_id": exam.id
    }, status=201)


# --------------------------
# Update Exam
# --------------------------
@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_exam(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=404)
    
    if 'title' in request.data:
        exam.title = request.data['title']
    if 'duration' in request.data:
        exam.duration = request.data['duration']
    if 'total_marks' in request.data:
        exam.total_marks = request.data['total_marks']
    if 'allowed_class' in request.data:
        exam.allowed_class = request.data['allowed_class']
    if 'allowed_batch' in request.data:
        exam.allowed_batch = request.data['allowed_batch']
    
    exam.save()
    return Response({"message": "Exam updated successfully"})


# --------------------------
# Delete Exam
# --------------------------
@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_exam(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
        exam.delete()  # This will cascade delete questions and attempts
        return Response({"message": "Exam deleted successfully"})
    except Exam.DoesNotExist:
        return Response({"error": "Exam not found"}, status=404)


# --------------------------
# List Questions for Exam
# --------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_question_list(request, exam_id):
    questions = Question.objects.filter(exam_id=exam_id)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


# --------------------------
# Create Question
# --------------------------
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


# --------------------------
# Update Question
# --------------------------
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
    
    question.save()
    return Response({"message": "Question updated successfully"})


# --------------------------
# Delete Question
# --------------------------
@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return Response({"message": "Question deleted successfully"})
    except Question.DoesNotExist:
        return Response({"error": "Question not found"}, status=404)