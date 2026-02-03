# users/admin_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile


@api_view(['GET'])
@permission_classes([AllowAny])
def admin_user_list(request):
    users = UserProfile.objects.select_related('user').all()
    
    user_data = []
    for profile in users:
        user_data.append({
            'id': profile.id,
            'user_id': profile.user.id,
            'username': profile.user.username,
            'email': profile.user.email,
            'role': profile.role,
            'department': profile.department,  
            'batch': profile.batch,
            'date_joined': profile.user.date_joined
        })
    
    return Response(user_data)



@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_user(request):
    username = request.data.get('username')
    email = request.data.get('email', '')
    password = request.data.get('password')
    role = request.data.get('role', 'student')
    department = request.data.get('department', '')  
    batch = request.data.get('batch', '')
    
    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)
    
    if role not in ['student', 'teacher', 'admin']:
        return Response({"error": "Invalid role"}, status=400)
    
    if role == 'student' and (not department or not batch):
        return Response({"error": "Students must have department and batch"}, status=400)
    
    if role == 'teacher' and not department:
        return Response({"error": "Teachers must have department"}, status=400)
    
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    profile = UserProfile.objects.create(
        user=user,
        role=role,
        department=department,
        batch=batch if role == 'student' else ''
    )
    
    return Response({
        "message": "User created successfully",
        "user_id": user.id,
        "profile_id": profile.id
    }, status=201)


@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_user(request, user_id):
    try:
        profile = UserProfile.objects.get(id=user_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    if 'email' in request.data:
        user.email = request.data['email']
    if 'username' in request.data:
        if User.objects.filter(username=request.data['username']).exclude(id=user.id).exists():
            return Response({"error": "Username already exists"}, status=400)
        user.username = request.data['username']
    
    user.save()
    
    if 'role' in request.data:
        profile.role = request.data['role']
    if 'department' in request.data:  
        profile.department = request.data['department']
    if 'batch' in request.data:
        profile.batch = request.data['batch']
    
    profile.save()
    
    return Response({"message": "User updated successfully"})



@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_user(request, user_id):
    try:
        profile = UserProfile.objects.get(id=user_id)
        user = profile.user
        user.delete()  
        return Response({"message": "User deleted successfully"})
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)