from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

# This is the main Course model where I store all course-related information
class Course(models.Model):
    """
    Stores all course-related information, including name, teacher, duration, description, thumbnail, price, and timestamps.
    """
    name = models.CharField(max_length=200)
    teacher_name = models.CharField(max_length=200)
    duration = models.CharField(max_length=100)  # e.g., "3 months", "6 weeks"
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        # I want the course name to show up in the admin and shell
        return self.name

    class Meta:
        ordering = ['-created_at']

# This model stores all the videos for each course
class CourseVideo(models.Model):
    """
    Stores all the videos for each course, including title, video URL/file, part number, and upload timestamp.
    """
    # Link to the course this video belongs to
    course = models.ForeignKey(Course, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    # URL for the video (if hosted externally)
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True)
    # The part/sequence number of the video in the course
    part_number = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show course name and part number for clarity
        return f"{self.course.name} - Part {self.part_number}: {self.title}"

    class Meta:
        ordering = ['course', 'part_number']

# This model stores notes for each course
class CourseNote(models.Model):
    """
    Stores notes for each course, including title, content, and upload timestamp.
    """
  
    course = models.ForeignKey(Course, related_name='notes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show course name and note title for clarity
        return f"{self.course.name} - {self.title}"

    class Meta:
        ordering = ['course', 'uploaded_at']

# This model stores certificates issued for a course
class Certificate(models.Model):
    """
    Stores certificates issued for a course, including student name, issue date, and certificate file.
    """
    course = models.ForeignKey(Course, related_name='certificates', on_delete=models.CASCADE)
    student_name = models.CharField(max_length=200)
    issue_date = models.DateField()
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        # Show student name, course, and issue date for clarity
        return f"{self.student_name} - {self.course.name} ({self.issue_date})"

    class Meta:
        ordering = ['-issue_date']
# Catagories such as web development , data science, mobile app development, etc.

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True) 

# This model tracks which users are enrolled in which courses
class Enrollment(models.Model):
    """
    Tracks which users are enrolled in which courses, with enrollment timestamp.
    """
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        # Show username and course for clarity
        return f"{self.user.username} enrolled in {self.course.name}" 

# This model stores notices made by teachers for a course
class Notice(models.Model):
    """
    Stores notices made by teachers for a course, including title, content, and creation timestamp.
    """
    # The course this notice is for
    course = models.ForeignKey(Course, related_name='notices', on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, related_name='notices', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show title and course for clarity
        return f"{self.title} ({self.course.name})"

    class Meta:
        ordering = ['-created_at']

# This model stores comments on course videos (supports replies)
class Comment(models.Model):
    """
    Stores comments on course videos (supports replies), including user, content, parent comment, and timestamps.
    """
    # The video this comment is for
    video = models.ForeignKey('CourseVideo', related_name='comments', on_delete=models.CASCADE)
    # The user who made the comment
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    # If this is a reply, the parent comment
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Show username and a snippet of the comment
        return f"{self.user.username}: {self.content[:30]}"

    class Meta:
        ordering = ['created_at'] 
    