from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, CourseVideo, CourseNote, Certificate, Enrollment, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

# Serializer for google auth 
class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

class AuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserSerializer()

class CourseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseVideo
        fields = ['id', 'title', 'video_url', 'video_file', 'part_number', 'uploaded_at']

class CourseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseNote
        fields = ['id', 'title', 'content', 'uploaded_at']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'student_name', 'issue_date', 'certificate_file', 'course']

class CourseSerializer(serializers.ModelSerializer):
    videos = CourseVideoSerializer(many=True, read_only=True)
    notes = CourseNoteSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    thumbnail = serializers.ImageField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Course
        fields = ['id', 'name', 'teacher_name', 'duration', 'description', 'thumbnail', 'price', 'created_at', 'updated_at', 'videos', 'notes', 'certificates']
        read_only_fields = ['created_at', 'updated_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), source='course', write_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'course_id', 'enrolled_at']
        read_only_fields = ['id', 'user', 'course', 'enrolled_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'video', 'user', 'content', 'parent', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'replies', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return [] 