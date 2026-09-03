from django.contrib import admin
from .models import Document, QuestionBank, MCQQuestion, QuizAttempt

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'document_type', 'processed', 'chunks_count', 'created_at')
    list_filter = ('document_type', 'processed')
    search_fields = ('title', 'uploaded_by__username')

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_document', 'created_at')
    search_fields = ('title', 'source_document__title')

@admin.register(MCQQuestion)
class MCQQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_bank', 'blooms_level', 'correct_option', 'is_verified', 'mapped_competency')
    list_filter = ('blooms_level', 'is_verified', 'correct_option')
    search_fields = ('question_text', 'explanation', 'source_citation')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_bank', 'score', 'total_questions', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'question_bank__title')
