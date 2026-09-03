from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import get_user_competency_gaps
from .models import Competency

@login_required
def competency_list_view(request):
    gaps = get_user_competency_gaps(request.user)
    return render(request, 'competencies/matrix.html', {'gaps': gaps})
