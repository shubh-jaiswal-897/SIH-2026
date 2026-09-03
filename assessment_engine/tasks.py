try:
    from celery import shared_task
except ImportError:
    # Fallback decorator if celery package is not installed
    def shared_task(func):
        class TaskWrapper:
            def __init__(self, fn):
                self.fn = fn
            def delay(self, *args, **kwargs):
                return self.fn(*args, **kwargs)
            def __call__(self, *args, **kwargs):
                return self.fn(*args, **kwargs)
        return TaskWrapper(func)

from .models import Document, QuestionBank, MCQQuestion
from competencies.models import Competency
from .services import DocumentProcessorService, MCQGeneratorService

@shared_task
def process_uploaded_document_and_generate_mcqs(document_id, num_questions=10):
    """
    Celery background task for asynchronous document vectorization and GenAI MCQ generation.
    """
    try:
        doc = Document.objects.get(id=document_id)
        file_path = doc.file.path

        # 1. Parse PDF pages
        pages = DocumentProcessorService.extract_text_from_pdf(file_path)
        
        # 2. Chunk text
        chunks = DocumentProcessorService.chunk_text(pages)
        doc.chunks_count = len(chunks)
        doc.processed = True
        doc.save()

        # 3. Create Question Bank
        qbank, _ = QuestionBank.objects.get_or_create(
            source_document=doc,
            defaults={'title': f"GenAI Question Bank: {doc.title}"}
        )

        # 4. Generate MCQs using structured schema
        raw_mcqs = MCQGeneratorService.generate_mcqs_from_chunks(chunks, num_questions=num_questions)

        # 5. Save generated items to DB with is_verified=False (human-in-the-loop review)
        created_questions = []
        for item in raw_mcqs:
            comp_code = item.get('competency_code')
            comp = Competency.objects.filter(official_code=comp_code).first() if comp_code else None
            
            mcq = MCQQuestion(
                question_bank=qbank,
                question_text=item['question_text'],
                options=item['options'],
                correct_option=item['correct_option'],
                explanation=item['explanation'],
                source_citation=item.get('source_citation', f"Document {doc.id}"),
                blooms_level=item.get('blooms_level', 'Understanding'),
                mapped_competency=comp,
                is_verified=False
            )
            created_questions.append(mcq)

        MCQQuestion.objects.bulk_create(created_questions)
        print(f"Successfully processed document '{doc.title}' & generated {len(created_questions)} MCQs!")
        return {"status": "SUCCESS", "document_id": doc.id, "mcq_count": len(created_questions)}

    except Exception as e:
        print(f"Error in document processing task for doc ID {document_id}: {e}")
        return {"status": "ERROR", "error": str(e)}
