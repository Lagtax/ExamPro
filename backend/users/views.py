from django.contrib.auth.models import User
from users.models import UserProfile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    department = request.data.get('department', '')
    batch = request.data.get('batch', '')
    role = request.data.get('role', 'student')

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=400)

    if role not in ['student', 'teacher', 'admin']:
        return Response({"error": "Invalid role"}, status=400)

    if role == 'student' and (not department or not batch):
        return Response({"error": "Students must provide department and batch"}, status=400)
    
    if role == 'teacher' and not department:
        return Response({"error": "Teachers must provide department"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)

    UserProfile.objects.create(
        user=user,
        role=role,
        department=department,
        batch=batch if role == 'student' else ''
    )

    return Response({
        "message": "User registered",
        "user_id": user.id,
        "role": role
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        login(request, user)

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found"}, status=404)

        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "role": profile.role,
            "department": profile.department
        })

    return Response({"error": "Invalid credentials"}, status=400)



@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out"})