from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.officer_dashboard_view, name='officer_dashboard'),
    path('upload/', views.upload_document_view, name='assessment_upload'),
    path('review/<int:doc_id>/', views.review_mcqs_view, name='review_mcqs'),
    path('quiz/<int:qbank_id>/', views.take_quiz_view, name='take_quiz'),
]
