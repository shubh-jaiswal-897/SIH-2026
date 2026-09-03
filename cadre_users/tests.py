from django.test import TestCase
from cadre_users.models import User
from competencies.models import Competency, RoleCompetencyMapping, LearnerCompetencyScore
from competencies.services import get_user_competency_gaps
from igot_integration.models import Course, Enrollment
from igot_integration.services import IGoTRecommenderService
from assessment_engine.models import Document, QuestionBank, MCQQuestion, QuizAttempt

class MospiPlatformTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_officer',
            password='password123',
            cadre=User.CadreChoices.ISS,
            designation='Assistant Director',
            department_wing=User.WingChoices.FOD
        )
        self.comp1 = Competency.objects.create(
            official_code='MoSPI-DOM-001',
            name='PLFS Statistics',
            type=Competency.TypeChoices.DOMAIN,
            description='Periodic Labour Force Survey'
        )
        RoleCompetencyMapping.objects.create(
            cadre=self.user.cadre,
            designation=self.user.designation,
            competency=self.comp1,
            target_level=4
        )
        LearnerCompetencyScore.objects.create(
            user=self.user,
            competency=self.comp1,
            evaluated_level=2
        )

    def test_competency_gap_calculation(self):
        gaps = get_user_competency_gaps(self.user)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]['current_level'], 2)
        self.assertEqual(gaps[0]['target_level'], 4)
        self.assertEqual(gaps[0]['gap'], 2)

    def test_igot_recommender_service(self):
        course = Course.objects.create(
            igot_course_id='COURSE-1',
            title='PLFS Advanced Workshop',
            duration_minutes=60,
            description='Covers PLFS Survey methods and CWS.'
        )
        course.mapped_competencies.add(self.comp1)
        
        recs = IGoTRecommenderService.get_recommendations_for_user(self.user)
        self.assertGreater(len(recs), 0)
        self.assertEqual(recs[0]['course'].id, course.id)
        self.assertGreater(recs[0]['relevance_score'], 0)

    def test_quiz_attempt_scoring(self):
        doc = Document.objects.create(
            title='Sample CPI SOP',
            uploaded_by=self.user,
            processed=True
        )
        qbank = QuestionBank.objects.create(title='CPI Bank', source_document=doc)
        mcq = MCQQuestion.objects.create(
            question_bank=qbank,
            question_text='Sample Question?',
            options={"A": "Ans 1", "B": "Ans 2"},
            correct_option="A",
            explanation="Explanation",
            blooms_level="Remembering"
        )
        
        attempt = QuizAttempt.objects.create(
            user=self.user,
            question_bank=qbank,
            score=1,
            total_questions=1
        )
        self.assertEqual(attempt.percentage, 100.0)
