"""
URL configuration for DigitalPathshala project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ApiDigitalpathshala.views import (
    login_view, 
    home, 
    logout_view, 
    get_user_info,
    GoogleLoginView,
    GoogleSignupView,
    refresh_token,
    CourseViewSet,
    CourseVideoViewSet,
    CourseNoteViewSet,
    CertificateViewSet,
    CommentViewSet,
    # CurrentUsernameView,
    # EnrollmentViewSet,
    # NoticeViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'course-videos', CourseVideoViewSet)
router.register(r'course-notes', CourseNoteViewSet)
router.register(r'certificates', CertificateViewSet)
router.register(r'video-comments', CommentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Web interface URLs
    path('', login_view, name='login'),
    path('home/', home, name='home'),
    path('logout/', logout_view, name='logout'),
    
    # API endpoints
    path('api/auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('api/auth/refresh/', refresh_token, name='refresh_token'),
    path('api/user/', get_user_info, name='user_info'),
    path('api/', include(router.urls)),  # This will include all our API endpoints
    
    # Social auth URLs
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('api/auth/google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('api/auth/google-signup/', GoogleSignupView.as_view(), name='google_signup'),
]
