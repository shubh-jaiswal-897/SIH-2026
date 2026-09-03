from django.urls import path
from . import views

urlpatterns = [
    path('', views.competency_list_view, name='competency_matrix'),
]
