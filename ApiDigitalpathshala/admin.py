from django.contrib import admin
from .models import Course, CourseVideo, CourseNote, Certificate, Enrollment, Comment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher_name', 'duration', 'created_at')
    search_fields = ('name', 'teacher_name')
    list_filter = ('created_at',)

@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'part_number', 'uploaded_at')
    search_fields = ('course__name', 'title')
    list_filter = ('course',)

@admin.register(CourseNote)
class CourseNoteAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'uploaded_at')
    search_fields = ('course__name', 'title')
    list_filter = ('course',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'course', 'issue_date')
    search_fields = ('student_name', 'course__name')
    list_filter = ('course', 'issue_date')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at')
    search_fields = ('user__username', 'course__name')
    list_filter = ('course', 'enrolled_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'content', 'parent', 'created_at')
    search_fields = ('user__username', 'video__title', 'content')
    list_filter = ('video', 'user', 'created_at')
