from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect_view, name='root_redirect'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
]

