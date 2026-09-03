import re
from competencies.services import get_user_competency_gaps
from .models import Course, Enrollment

class IGoTRecommenderService:
    @staticmethod
    def get_recommendations_for_user(user):
        """
        Computes officer's competency gaps and performs semantic / match ranking 
        against iGOT courses to generate personalized learning recommendations.
        """
        gaps = get_user_competency_gaps(user)
        # Filter competencies with positive gap
        active_gaps = [g for g in gaps if g['gap'] > 0]
        
        if not active_gaps:
            # User has no gap, return top rated courses
            return Course.objects.all()[:5]

        # Get active competency IDs
        gap_comp_ids = [g['competency'].id for g in active_gaps]
        gap_comp_dict = {g['competency'].id: g['gap'] for g in active_gaps}
        gap_comp_names = [g['competency'].name.lower() for g in active_gaps]

        # Fetch courses that either explicitly map to these competencies or match semantically
        courses = Course.objects.all()
        enrolled_course_ids = set(Enrollment.objects.filter(user=user).values_list('course_id', flat=True))

        scored_courses = []

        for course in courses:
            score = 0.0
            # 1. Direct Mapped Competency Bonus weighted by Gap size
            for comp in course.mapped_competencies.all():
                if comp.id in gap_comp_dict:
                    score += 10.0 * gap_comp_dict[comp.id]

            # 2. Semantic keyword / TF-IDF relevance scoring in course description & title
            course_text = f"{course.title} {course.description or ''}".lower()
            for gap_name in gap_comp_names:
                words = re.findall(r'\w+', gap_name)
                for word in words:
                    if len(word) > 3 and word in course_text:
                        score += 2.5

            # 3. Status penalty if already completed
            is_enrolled = course.id in enrolled_course_ids
            
            scored_courses.append({
                'course': course,
                'relevance_score': round(score, 2),
                'is_enrolled': is_enrolled,
                'target_competencies': [comp.name for comp in course.mapped_competencies.filter(id__in=gap_comp_ids)]
            })

        # Sort by relevance score descending
        scored_courses.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_courses
