from .models import Competency, RoleCompetencyMapping, LearnerCompetencyScore, KarmaBadge, UserBadge

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


def calculate_officer_cpri(user):
    """
    Calculates Promotion & Posting Readiness Index (CPRI) Score (0 to 100%)
    and manages automated Karma Badge awards for the officer.
    """
    gaps = get_user_competency_gaps(user)
    if not gaps:
        return 75.0, []

    total_current = sum(g['current_level'] for g in gaps)
    total_target = sum(g['target_level'] for g in gaps)
    
    cpri_score = round((total_current / total_target) * 100, 1) if total_target > 0 else 100.0
    cpri_score = min(100.0, max(0.0, cpri_score))

    # Auto-award badges based on milestones
    badges_unlocked = []
    
    # 1. Karma Champion Badge (CPRI >= 70%)
    if cpri_score >= 70.0:
        b1, _ = KarmaBadge.objects.get_or_create(
            name='Karmayogi Champion',
            defaults={'icon': 'award', 'description': 'Achieved >70% Promotion & Posting Readiness Score (CPRI)', 'category': 'HR Analytics'}
        )
        UserBadge.objects.get_or_create(user=user, badge=b1)
        badges_unlocked.append(b1)

    # 2. PLFS Specialist Badge
    plfs_comp = Competency.objects.filter(official_code='MoSPI-DOM-001').first()
    if plfs_comp:
        plfs_score = LearnerCompetencyScore.objects.filter(user=user, competency=plfs_comp).first()
        if plfs_score and plfs_score.evaluated_level >= 2:
            b2, _ = KarmaBadge.objects.get_or_create(
                name='PLFS Specialist',
                defaults={'icon': 'bar-chart-2', 'description': 'Demonstrated advanced mastery in Periodic Labour Force Survey methodology', 'category': 'Domain'}
            )
            UserBadge.objects.get_or_create(user=user, badge=b2)
            badges_unlocked.append(b2)

    # 3. Data Audit Specialist Badge
    b3, _ = KarmaBadge.objects.get_or_create(
        name='Data Integrity Auditor',
        defaults={'icon': 'shield-check', 'description': 'Completed MoSPI Data Anomaly Detection & Quality Audit simulations', 'category': 'Audit'}
    )
    UserBadge.objects.get_or_create(user=user, badge=b3)
    badges_unlocked.append(b3)

    user_badges = [ub.badge for ub in UserBadge.objects.filter(user=user)]
    return cpri_score, user_badges
