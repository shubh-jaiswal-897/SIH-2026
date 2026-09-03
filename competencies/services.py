from .models import Competency, RoleCompetencyMapping, LearnerCompetencyScore

def get_user_competency_gaps(user):
    """
    Computes a user's competency gaps across all mapped competencies.
    Returns a list of dicts:
    [{
        'competency': competency_obj,
        'current_level': int,
        'target_level': int,
        'gap': int
    }]
    """
    scores = {score.competency_id: score for score in LearnerCompetencyScore.objects.filter(user=user)}
    role_mappings = RoleCompetencyMapping.objects.filter(cadre=user.cadre, designation=user.designation)
    
    # If no specific role mapping, fall back to all competencies
    if not role_mappings.exists():
        all_comps = Competency.objects.all()
        results = []
        for comp in all_comps:
            score_obj = scores.get(comp.id)
            curr_level = score_obj.evaluated_level if score_obj else 1
            target = 3
            gap = max(0, target - curr_level)
            results.append({
                'competency': comp,
                'current_level': curr_level,
                'target_level': target,
                'gap': gap
            })
        return results

    results = []
    for mapping in role_mappings:
        comp = mapping.competency
        score_obj = scores.get(comp.id)
        curr_level = score_obj.evaluated_level if score_obj else 1
        target = mapping.target_level
        gap = max(0, target - curr_level)
        results.append({
            'competency': comp,
            'current_level': curr_level,
            'target_level': target,
            'gap': gap
        })

    return results
