from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import IGoTRecommenderService
from .models import Course, Enrollment

@login_required
def course_recommendations_view(request):
    recommendations = IGoTRecommenderService.get_recommendations_for_user(request.user)
    my_enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'igot/courses.html', {
        'recommendations': recommendations,
        'my_enrollments': my_enrollments
    })

@login_required
def enroll_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'status': Enrollment.StatusChoices.IN_PROGRESS, 'completion_percentage': 10}
    )
    if created:
        messages.success(request, f"Enrolled in '{course.title}' via iGOT Karmayogi!")
    else:
        messages.info(request, f"You are already enrolled in '{course.title}'. Progress: {enrollment.completion_percentage}%")
    return redirect('igot_courses')
