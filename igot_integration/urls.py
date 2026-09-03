from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.course_recommendations_view, name='igot_courses'),
    path('enroll/<int:course_id>/', views.enroll_course_view, name='igot_enroll'),
]
