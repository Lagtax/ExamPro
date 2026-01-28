# users/admin_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile


# --------------------------
# List All Users
# --------------------------
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
            'class_name': profile.class_name,
            'batch': profile.batch,
            'date_joined': profile.user.date_joined
        })
    
    return Response(user_data)


# --------------------------
# Create User
# --------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_create_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'student')
    class_name = request.data.get('class_name', '')
    batch = request.data.get('batch', '')
    
    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)
    
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Create profile
    profile = UserProfile.objects.create(
        user=user,
        role=role,
        class_name=class_name,
        batch=batch
    )
    
    return Response({
        "message": "User created successfully",
        "user_id": user.id,
        "profile_id": profile.id
    }, status=201)


# --------------------------
# Update User
# --------------------------
@api_view(['PUT'])
@permission_classes([AllowAny])
def admin_update_user(request, user_id):
    try:
        profile = UserProfile.objects.get(id=user_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
    # Update user fields
    if 'email' in request.data:
        user.email = request.data['email']
    if 'username' in request.data:
        if User.objects.filter(username=request.data['username']).exclude(id=user.id).exists():
            return Response({"error": "Username already exists"}, status=400)
        user.username = request.data['username']
    
    user.save()
    
    # Update profile fields
    if 'role' in request.data:
        profile.role = request.data['role']
    if 'class_name' in request.data:
        profile.class_name = request.data['class_name']
    if 'batch' in request.data:
        profile.batch = request.data['batch']
    
    profile.save()
    
    return Response({"message": "User updated successfully"})


# --------------------------
# Delete User
# --------------------------
@api_view(['DELETE'])
@permission_classes([AllowAny])
def admin_delete_user(request, user_id):
    try:
        profile = UserProfile.objects.get(id=user_id)
        user = profile.user
        user.delete()  # This will cascade delete the profile
        return Response({"message": "User deleted successfully"})
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=404)