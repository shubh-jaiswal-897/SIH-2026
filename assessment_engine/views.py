import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from competencies.services import get_user_competency_gaps, calculate_officer_cpri
from igot_integration.services import IGoTRecommenderService
from igot_integration.models import Enrollment
from .models import Document, QuestionBank, MCQQuestion, QuizAttempt, SpacedRepetitionReview
from .tasks import process_uploaded_document_and_generate_mcqs

@login_required
def officer_dashboard_view(request):
    """
    Main Officer Dashboard showing FRAC radar/bar chart data,
    CPRI Promotion Readiness Score, Karma Badges, Spaced Repetition Reviews due,
    current course progress, and iGOT recommendations.
    """
    gaps = get_user_competency_gaps(request.user)
    cpri_score, user_badges = calculate_officer_cpri(request.user)
    recommendations = IGoTRecommenderService.get_recommendations_for_user(request.user)[:4]
    enrollments = Enrollment.objects.filter(user=request.user)
    recent_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-completed_at')[:5]

    # Spaced Repetition Due Reviews today
    reviews_due = SpacedRepetitionReview.objects.filter(
        user=request.user,
        next_review_date__lte=timezone.now().date(),
        is_mastered=False
    )

    # Prepare Chart.js data
    chart_labels = [g['competency'].name for g in gaps]
    chart_current = [g['current_level'] for g in gaps]
    chart_target = [g['target_level'] for g in gaps]

    context = {
        'gaps': gaps,
        'cpri_score': cpri_score,
        'user_badges': user_badges,
        'reviews_due': reviews_due,
        'recommendations': recommendations,
        'enrollments': enrollments,
        'recent_attempts': recent_attempts,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_current_json': json.dumps(chart_current),
        'chart_target_json': json.dumps(chart_target),
    }
    return render(request, 'dashboard/officer_dashboard.html', context)


@login_required
def upload_document_view(request):
    """File upload interface with async Celery extraction trigger."""
    if request.method == 'POST':
        title = request.POST.get('title')
        doc_type = request.POST.get('document_type', 'MANUAL')
        file_obj = request.FILES.get('file')

        if not file_obj:
            messages.error(request, "Please attach a valid PDF document.")
            return redirect('assessment_upload')

        doc = Document.objects.create(
            title=title or file_obj.name,
            file=file_obj,
            uploaded_by=request.user,
            document_type=doc_type
        )

        # Process document and extract MCQs instantly
        process_uploaded_document_and_generate_mcqs(doc.id, num_questions=8)
        
        messages.success(
            request, 
            f"Document '{doc.title}' processed successfully! GenAI MCQs extracted."
        )
        return redirect('review_mcqs', doc_id=doc.id)


    recent_docs = Document.objects.filter(uploaded_by=request.user).order_by('-created_at')[:10]
    all_qbanks = QuestionBank.objects.all().order_by('-created_at')
    return render(request, 'assessment/upload.html', {'recent_docs': recent_docs, 'question_banks': all_qbanks})


@login_required
def review_mcqs_view(request, doc_id):
    """
    NSSTA Admin human-in-the-loop interface to review, approve, edit, or toggle verification on MCQs.
    """
    document = get_object_or_404(Document, id=doc_id)
    question_bank = QuestionBank.objects.filter(source_document=document).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve_all':
            if question_bank:
                question_bank.questions.update(is_verified=True)
                messages.success(request, "All generated MCQs in this Question Bank have been verified and approved!")
                
        elif action == 'toggle_verify':
            mcq_id = request.POST.get('mcq_id')
            mcq = get_object_or_404(MCQQuestion, id=mcq_id)
            mcq.is_verified = not mcq.is_verified
            mcq.save()
            messages.info(request, f"Question ID {mcq.id} status updated to: {'Verified' if mcq.is_verified else 'Unverified'}.")

        return redirect('review_mcqs', doc_id=doc_id)

    questions = question_bank.questions.all() if question_bank else []
    return render(request, 'assessment/review_mcqs.html', {
        'document': document,
        'question_bank': question_bank,
        'questions': questions
    })


@login_required
def take_quiz_view(request, qbank_id):
    """
    Interactive, timed, distraction-free quiz interface with Web Speech audio assistance & Spaced Repetition memory tracking.
    """
    qbank = get_object_or_404(QuestionBank, id=qbank_id)
    # Get verified questions or fall back to all generated questions
    questions = qbank.questions.filter(is_verified=True)
    if not questions.exists():
        questions = qbank.questions.all()

    if request.method == 'POST':
        score = 0
        user_answers = {}
        for q in questions:
            ans = request.POST.get(f'question_{q.id}')
            user_answers[str(q.id)] = ans
            if ans and ans == q.correct_option:
                score += 1
            else:
                # Schedule Spaced Repetition Review for incorrect answers (Day 3 Forgetting Curve)
                SpacedRepetitionReview.objects.get_or_create(
                    user=request.user,
                    question=q,
                    defaults={'next_review_date': timezone.now().date() + timezone.timedelta(days=3)}
                )

        attempt = QuizAttempt.objects.create(
            user=request.user,
            question_bank=qbank,
            score=score,
            total_questions=questions.count(),
            answers_json=user_answers
        )

        return render(request, 'assessment/quiz_result.html', {
            'attempt': attempt,
            'qbank': qbank,
            'questions': questions,
            'user_answers': user_answers
        })

    return render(request, 'assessment/take_quiz.html', {
        'qbank': qbank,
        'questions': questions
    })


@login_required
def anomaly_challenge_view(request):
    """
    Live MoSPI Open Data Survey Anomaly Detection Challenge.
    Simulates real-world PLFS / CPI survey audit returns for officers to identify statistical outliers.
    """
    sample_returns = [
        {
            'id': 'RET-PLFS-2026-081',
            'state': 'Uttar Pradesh',
            'district': 'Lucknow',
            'fsu_type': 'Urban UFS Block 104',
            'reported_weekly_hours': 168,
            'reported_wage': 450,
            'cws_status': 'Employed',
            'has_anomaly': True,
            'anomaly_reason': 'Improbable 168 weekly hours reported (24 hrs x 7 days) without non-working period. Exceeds PLFS physical thresholds.'
        },
        {
            'id': 'RET-CPI-2026-114',
            'state': 'Maharashtra',
            'district': 'Pune',
            'fsu_type': 'Rural Village Code 401',
            'item_name': 'Rice (Common Variety)',
            'price_prev_month': 42.0,
            'price_curr_month': 420.0,
            'has_anomaly': True,
            'anomaly_reason': '1000% single-month price spike (decimal point entry error: Rs 42.00 mis-entered as Rs 420.00).'
        },
        {
            'id': 'RET-NAS-2026-009',
            'state': 'Karnataka',
            'district': 'Bengaluru Urban',
            'fsu_type': 'ASI Industrial Unit',
            'gva_reported': 1250000,
            'capital_formation': 300000,
            'has_anomaly': False,
            'anomaly_reason': 'Consistent within expected 3-sigma statistical variance.'
        }
    ]

    return render(request, 'assessment/anomaly_challenge.html', {'sample_returns': sample_returns})
