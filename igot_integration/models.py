from django.db import models
from django.conf import settings
from competencies.models import Competency

class Course(models.Model):
    igot_course_id = models.CharField(max_length=100, unique=True, help_text='iGOT Portal Unique Identifier')
    title = models.CharField(max_length=255)
    provider = models.CharField(max_length=100, default='NSSTA / DoPT')
    url = models.URLField(default='https://igotkarmayogi.gov.in')
    duration_minutes = models.PositiveIntegerField(default=120)
    description = models.TextField(blank=True, null=True)
    mapped_competencies = models.ManyToManyField(Competency, related_name='igot_courses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.provider}] {self.title} ({self.duration_minutes} mins)"


class Enrollment(models.Model):
    class StatusChoices(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='igot_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_enrollments')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.NOT_STARTED)
    completion_percentage = models.PositiveIntegerField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} -> {self.course.title} ({self.get_status_display()} - {self.completion_percentage}%)"
