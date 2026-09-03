from django.db import models
from django.conf import settings
from competencies.models import Competency

class Document(models.Model):
    class DocTypeChoices(models.TextChoices):
        MANUAL = 'MANUAL', 'MoSPI Manual / Operational Guide'
        ACT = 'ACT', 'Collection of Statistics Act / Legislation'
        SOP = 'SOP', 'Standard Operating Procedure (SOP)'
        PLFS_REPORT = 'PLFS_REPORT', 'Periodic Labour Force Survey (PLFS) Manual'
        CPI_GUIDE = 'CPI_GUIDE', 'Consumer Price Index (CPI/WPI) Methodology'

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploaded_docs/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_documents')
    document_type = models.CharField(max_length=20, choices=DocTypeChoices.choices, default=DocTypeChoices.MANUAL)
    processed = models.BooleanField(default=False)
    chunks_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} [{self.get_document_type_display()}]"


class QuestionBank(models.Model):
    title = models.CharField(max_length=255)
    source_document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='question_banks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question Bank: {self.title}"


class MCQQuestion(models.Model):
    class BloomsTaxonomyChoices(models.TextChoices):
        REMEMBERING = 'Remembering', 'Remembering (Recall facts/definitions)'
        UNDERSTANDING = 'Understanding', 'Understanding (Explain concepts/methodologies)'
        APPLYING = 'Applying', 'Applying (Execute statistical procedures/CPI formula)'
        ANALYZING = 'Analyzing', 'Analyzing (Interpret survey errors & data anomalies)'

    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    options = models.JSONField(help_text='JSON map e.g. {"A": "...", "B": "...", "C": "...", "D": "..."}')
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    explanation = models.TextField(help_text='Detailed rationale for correct answer')
    source_citation = models.CharField(max_length=255, blank=True, null=True, help_text='Section/Page reference in PDF')
    blooms_level = models.CharField(max_length=20, choices=BloomsTaxonomyChoices.choices, default=BloomsTaxonomyChoices.UNDERSTANDING)
    mapped_competency = models.ForeignKey(Competency, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    is_verified = models.BooleanField(default=False, help_text='Human-in-the-loop review approval status by NSSTA Evaluators')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.blooms_level}] {self.question_text[:60]}..."


class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    answers_json = models.JSONField(default=dict, help_text='Recorded user answers per question ID')
    completed_at = models.DateTimeField(auto_now_add=True)

    @property
    def percentage(self):
        return round((self.score / self.total_questions * 100), 1) if self.total_questions > 0 else 0.0

    def __str__(self):
        return f"{self.user.username} - Quiz {self.question_bank.id}: {self.score}/{self.total_questions} ({self.percentage}%)"
