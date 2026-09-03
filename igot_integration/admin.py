from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('igot_course_id', 'title', 'provider', 'duration_minutes')
    search_fields = ('igot_course_id', 'title', 'provider', 'description')
    filter_horizontal = ('mapped_competencies',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'completion_percentage', 'enrolled_at')
    list_filter = ('status', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
