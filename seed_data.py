import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mospi_upskill.settings')
django.setup()

from cadre_users.models import User
from competencies.models import Competency, RoleCompetencyMapping, LearnerCompetencyScore
from igot_integration.models import Course, Enrollment
from assessment_engine.models import Document, QuestionBank, MCQQuestion
from django.core.files.base import ContentFile

def run_seed():
    print("--- Seeding SatatSankhyiki (SIH26101) MoSPI Platform Data ---")


    # 1. Create Core Users
    officer, _ = User.objects.get_or_create(
        username='officer1',
        defaults={
            'first_name': 'Shubh',
            'last_name': 'Jaiswal',
            'email': 'officer1@mospi.gov.in',
            'cadre': User.CadreChoices.ISS,
            'designation': 'Assistant Director',
            'department_wing': User.WingChoices.FOD,
            'employee_code': 'ISS-2026-042',
            'igot_user_id': 'IGOT-ISS-8842',
            'role': User.RoleChoices.OFFICER,
            'is_staff': True
        }
    )
    officer.set_password('pass123')
    officer.save()

    nssta_admin, _ = User.objects.get_or_create(
        username='nssta_admin',
        defaults={
            'first_name': 'NSSTA',
            'last_name': 'Evaluator',
            'email': 'evaluator@nssta.gov.in',
            'cadre': User.CadreChoices.ISS,
            'designation': 'Deputy Director General',
            'department_wing': User.WingChoices.NSSTA,
            'employee_code': 'NSSTA-CURATOR-01',
            'role': User.RoleChoices.NSSTA_CURATOR,
            'is_staff': True,
            'is_superuser': True
        }
    )
    nssta_admin.set_password('pass123')
    nssta_admin.save()

    # 2. Create MoSPI FRAC Competencies
    competencies_data = [
        {
            'official_code': 'MoSPI-DOM-001',
            'name': 'Periodic Labour Force Survey (PLFS) & CWS Dynamics',
            'type': Competency.TypeChoices.DOMAIN,
            'description': 'Mastery over PLFS survey design, Usual Status vs Current Weekly Status (CWS) definitions, and workforce participation rate calculations.'
        },
        {
            'official_code': 'MoSPI-DOM-002',
            'name': 'Consumer Price Index (CPI/WPI) Aggregation Methodology',
            'type': Competency.TypeChoices.DOMAIN,
            'description': 'Understanding item weight derivation, Modified Laspeyres price index formula, and rural/urban price compilation procedures.'
        },
        {
            'official_code': 'MoSPI-DOM-003',
            'name': 'National Accounts Statistics (NAS) & GDP Estimation',
            'type': Competency.TypeChoices.DOMAIN,
            'description': 'Computation of Gross Value Added (GVA), GDP at Basic vs Market Prices, and Gross Fixed Capital Formation (GFCF).'
        },
        {
            'official_code': 'MoSPI-DOM-004',
            'name': 'NSS Sample Survey Design & Multi-Stage Sampling',
            'type': Competency.TypeChoices.DOMAIN,
            'description': 'Designing First Stage Units (FSUs), UFS urban block stratification, sampling variance estimation, and non-sampling error audit.'
        },
        {
            'official_code': 'MoSPI-DOM-005',
            'name': 'Collection of Statistics Act 2008 & Statutory Audits',
            'type': Competency.TypeChoices.DOMAIN,
            'description': 'Legal powers of Statistics Officers, data confidentiality provisions, and enforcement mechanisms for industrial units.'
        },
        {
            'official_code': 'MoSPI-FUN-001',
            'name': 'Statistical Data Analytics & Quality Control Audits',
            'type': Competency.TypeChoices.FUNCTIONAL,
            'description': 'Automated outlier detection, consistency validation in survey returns, and data cleaning scripts.'
        },
        {
            'official_code': 'MoSPI-BEH-001',
            'name': 'Evidence-Based Policy Communication & Executive Briefing',
            'type': Competency.TypeChoices.BEHAVIORAL,
            'description': 'Translating statistical indicators into actionable policy insights for inter-ministerial committees.'
        }
    ]

    comp_objs = {}
    for c_data in competencies_data:
        comp, _ = Competency.objects.get_or_create(
            official_code=c_data['official_code'],
            defaults=c_data
        )
        comp_objs[comp.official_code] = comp

    # 3. Create Role Competency Target Mappings for ISS Assistant Director
    targets = [
        ('MoSPI-DOM-001', 4),
        ('MoSPI-DOM-002', 4),
        ('MoSPI-DOM-003', 3),
        ('MoSPI-DOM-004', 5),
        ('MoSPI-DOM-005', 3),
        ('MoSPI-FUN-001', 4),
        ('MoSPI-BEH-001', 3),
    ]

    for code, target_level in targets:
        RoleCompetencyMapping.objects.get_or_create(
            cadre=officer.cadre,
            designation=officer.designation,
            competency=comp_objs[code],
            defaults={'target_level': target_level}
        )

    # 4. Create Learner Evaluated Scores for officer1 (creating realistic gaps)
    scores = [
        ('MoSPI-DOM-001', 2),  # Target 4 -> Gap = 2
        ('MoSPI-DOM-002', 2),  # Target 4 -> Gap = 2
        ('MoSPI-DOM-003', 3),  # Target 3 -> Gap = 0
        ('MoSPI-DOM-004', 3),  # Target 5 -> Gap = 2
        ('MoSPI-DOM-005', 3),  # Target 3 -> Gap = 0
        ('MoSPI-FUN-001', 3),  # Target 4 -> Gap = 1
        ('MoSPI-BEH-001', 3),  # Target 3 -> Gap = 0
    ]

    for code, eval_level in scores:
        LearnerCompetencyScore.objects.update_or_create(
            user=officer,
            competency=comp_objs[code],
            defaults={'evaluated_level': eval_level}
        )

    # 5. Create iGOT Courses
    courses_data = [
        {
            'igot_course_id': 'IGOT-MOSPI-101',
            'title': 'Advanced PLFS Survey Design & CWS Computation',
            'provider': 'NSSTA Greater Noida',
            'duration_minutes': 180,
            'description': 'Comprehensive module covering Periodic Labour Force Survey methodology, Usual Status vs CWS estimation, and field error audits.',
            'competencies': ['MoSPI-DOM-001', 'MoSPI-DOM-004']
        },
        {
            'igot_course_id': 'IGOT-MOSPI-202',
            'title': 'Consumer Price Index (CPI) Weight Derivation & Item Laspeyres Formula',
            'provider': 'ESD MoSPI / DoPT',
            'duration_minutes': 120,
            'description': 'Step-by-step masterclass on price aggregation, geometric mean price relatives, and base-year revision protocols.',
            'competencies': ['MoSPI-DOM-002']
        },
        {
            'igot_course_id': 'IGOT-MOSPI-303',
            'title': 'NSS Stratified Multi-Stage Sampling & Frame Optimization',
            'provider': 'NSSTA / ISI Kolkata',
            'duration_minutes': 240,
            'description': 'Mathematical framework of UFS urban block stratification, First Stage Units (FSUs), and sampling variance calculation.',
            'competencies': ['MoSPI-DOM-004', 'MoSPI-FUN-001']
        },
        {
            'igot_course_id': 'IGOT-MOSPI-404',
            'title': 'National Accounts Statistics: GDP & Gross Value Added (GVA)',
            'provider': 'NAD MoSPI',
            'duration_minutes': 150,
            'description': 'In-depth guide to compilation of GDP at Basic Prices, Net Product Taxes, and Sectoral Gross Capital Formation.',
            'competencies': ['MoSPI-DOM-003']
        }
    ]

    for c_info in courses_data:
        comps = [comp_objs[code] for code in c_info.pop('competencies')]
        course_obj, _ = Course.objects.get_or_create(
            igot_course_id=c_info['igot_course_id'],
            defaults=c_info
        )
        course_obj.mapped_competencies.set(comps)

    # 6. Seed Sample Document & Question Bank
    fake_pdf_content = b"%PDF-1.4 Mock MoSPI PLFS & CPI Manual PDF Content for SIH26101 Platform"
    doc_file = ContentFile(fake_pdf_content, name="MoSPI_PLFS_CPI_Methodology_Guide.pdf")

    doc, _ = Document.objects.get_or_create(
        title='MoSPI PLFS & CPI Operational Methodology Guide 2026',
        uploaded_by=officer,
        defaults={
            'file': doc_file,
            'document_type': Document.DocTypeChoices.PLFS_REPORT,
            'processed': True,
            'chunks_count': 6
        }
    )

    qbank, _ = QuestionBank.objects.get_or_create(
        source_document=doc,
        defaults={'title': 'MoSPI Statistical Operational Assessment (PLFS & CPI)'}
    )

    # Seed Sample MCQs matching Bloom's Taxonomy
    mcqs_data = [
        {
            'question_text': "Under MoSPI's Periodic Labour Force Survey (PLFS), how is the Current Weekly Status (CWS) of a surveyed individual classified?",
            'options': {
                "A": "Activity status during a reference period of 7 days preceding the survey date.",
                "B": "Activity status during the preceding 365 days from the date of survey.",
                "C": "Activity status recorded only for gainful employment exceeding 180 days.",
                "D": "Activity status based on daily hours worked in agricultural operations only."
            },
            'correct_option': "A",
            'explanation': "CWS determines the activity status during a short reference period of 7 days preceding the survey date, capturing short-term employment fluctuations.",
            'source_citation': "Page 4, Section 2.1 (PLFS Manual)",
            'blooms_level': MCQQuestion.BloomsTaxonomyChoices.REMEMBERING,
            'mapped_competency': comp_objs['MoSPI-DOM-001'],
            'is_verified': True
        },
        {
            'question_text': "In the official Consumer Price Index (CPI) compiled by MoSPI, which formula is utilized for aggregating item-level price relatives?",
            'options': {
                "A": "Modified Laspeyres Price Index Formula",
                "B": "Paasche Price Index Formula",
                "C": "Fisher Ideal Index Formula",
                "D": "Marshall-Edgeworth Index Formula"
            },
            'correct_option': "A",
            'explanation': "MoSPI uses the Modified Laspeyres Price Index formula with base year weights derived from Consumer Expenditure Surveys.",
            'source_citation': "Page 8, Section 4.3 (CPI Methodology)",
            'blooms_level': MCQQuestion.BloomsTaxonomyChoices.APPLYING,
            'mapped_competency': comp_objs['MoSPI-DOM-002'],
            'is_verified': True
        },
        {
            'question_text': "What sampling design strategy is predominantly employed in National Sample Surveys (NSS) for multi-stage stratified household data collection?",
            'options': {
                "A": "Stratified Multi-Stage Sampling with Census Villages/Urban Frame Survey (UFS) blocks as First Stage Units (FSUs)",
                "B": "Simple Random Sampling without Replacement (SRSWOR) across national households",
                "C": "Purposive Judgment Sampling based on district population density",
                "D": "Quota Sampling based on occupational categories"
            },
            'correct_option': "A",
            'explanation': "NSS survey designs rely on stratified multi-stage sampling where rural census villages and urban UFS blocks act as FSUs.",
            'source_citation': "Page 12, Section 5.1 (Sampling Manual)",
            'blooms_level': MCQQuestion.BloomsTaxonomyChoices.ANALYZING,
            'mapped_competency': comp_objs['MoSPI-DOM-004'],
            'is_verified': True
        }
    ]

    for item in mcqs_data:
        MCQQuestion.objects.get_or_create(
            question_bank=qbank,
            question_text=item['question_text'],
            defaults=item
        )

    print("SUCCESS: SatatSankhyiki Seeding Complete!")

    print("   User Accounts Created:")
    print("   - ISS Officer: username='officer1' | password='pass123'")
    print("   - NSSTA Evaluator: username='nssta_admin' | password='pass123'")

if __name__ == '__main__':
    run_seed()
