from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, mixins
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
# from .models import UserProfile
import json
from .models import Course, CourseVideo, CourseNote, Certificate, Enrollment, Comment
from .serializers import CourseSerializer, CourseVideoSerializer, CourseNoteSerializer, CertificateSerializer, EnrollmentSerializer, CommentSerializer
import requests
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class GoogleLoginView(APIView):
    """
    Login with Google: Only allows login if user already exists.
    """
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        google_response = requests.get(f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}')
        if google_response.status_code != 200:
            return Response({'error': 'Invalid Google token.'}, status=status.HTTP_400_BAD_REQUEST)
        google_data = google_response.json()
        email = google_data.get('email')
        if not email:
            return Response({'error': 'Google token did not return an email.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist. Please sign up first.'}, status=status.HTTP_404_NOT_FOUND)
        # Get or create DRF token
        token_obj, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token_obj.key,
            'user': {'username': user.username, 'email': user.email}
        })

class GoogleSignupView(APIView):
    """
    Signup with Google: Only allows signup if user does NOT already exist.
    """
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        google_response = requests.get(f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}')
        if google_response.status_code != 200:
            return Response({'error': 'Invalid Google token.'}, status=status.HTTP_400_BAD_REQUEST)
        google_data = google_response.json()
        email = google_data.get('email')
        if not email:
            return Response({'error': 'Google token did not return an email.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'User already exists. Please log in.'}, status=status.HTTP_400_BAD_REQUEST)
        username = google_data.get('name', email.split('@')[0])
        user = User.objects.create_user(username=username, email=email)
        user.save()
        # Create DRF token
        token_obj, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token_obj.key,
            'user': {'username': user.username, 'email': user.email}
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken(refresh_token)
        return Response({
            'access_token': str(refresh.access_token)
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    profile = user.profile
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_picture': profile.profile_picture,
        'last_login_method': profile.last_login_method,
        'created_at': profile.created_at,
        'updated_at': profile.updated_at
    })

# Template views for web interface
def login_view(request):
    return render(request, 'login.html')

@login_required
def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

class CourseVideoViewSet(viewsets.ModelViewSet):
    queryset = CourseVideo.objects.all()
    serializer_class = CourseVideoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CourseNoteViewSet(viewsets.ModelViewSet):
    queryset = CourseNote.objects.all()
    serializer_class = CourseNoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CurrentUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'username': request.user.username})
    
    
    # login with google API which checks the database for the user who have the same email and anotherAPI for signup with google 

class EnrollmentViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = Enrollment.objects.none()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.enrollments.select_related('course')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_staff:
            return True
        # Users can edit/delete only their own comments
        return obj.user == request.user

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        video_id = self.request.query_params.get('video')
        qs = Comment.objects.all()
        if video_id:
            qs = qs.filter(video_id=video_id, parent=None)
        return qs.select_related('user', 'video').prefetch_related('replies')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 