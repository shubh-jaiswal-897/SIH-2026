from django.db import models
from django.conf import settings

class Competency(models.Model):
    class TypeChoices(models.TextChoices):
        DOMAIN = 'DOMAIN', 'Domain Competency (Statistical Systems, NAS, CPI)'
        FUNCTIONAL = 'FUNCTIONAL', 'Functional Competency (Data Analytics, Survey Operations)'
        BEHAVIORAL = 'BEHAVIORAL', 'Behavioral Competency (Leadership, Communication)'

    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=TypeChoices.choices, default=TypeChoices.DOMAIN)
    official_code = models.CharField(max_length=50, unique=True, help_text='Official FRAC Code (e.g., MoSPI-DOM-001)')
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Competencies"
        ordering = ['type', 'name']

    def __str__(self):
        return f"[{self.official_code}] {self.name} ({self.get_type_display()})"


class RoleCompetencyMapping(models.Model):
    cadre = models.CharField(max_length=20, help_text='Target Cadre (ISS, SSS, State DES, etc.)')
    designation = models.CharField(max_length=100, help_text='Target Designation (e.g. Deputy Director General, JSO)')
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='role_mappings')
    target_level = models.PositiveSmallIntegerField(default=3, help_text='Required Proficiency Level (1 to 5)')

    class Meta:
        unique_together = ('cadre', 'designation', 'competency')
        verbose_name = "Role Competency Target Mapping"
        verbose_name_plural = "Role Competency Target Mappings"

    def __str__(self):
        return f"{self.cadre} - {self.designation} | {self.competency.name} -> Target Level {self.target_level}"


class LearnerCompetencyScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='competency_scores')
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='learner_scores')
    evaluated_level = models.PositiveSmallIntegerField(default=1, help_text='Assessed Proficiency Level (1 to 5)')
    last_assessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'competency')
        verbose_name = "Learner Competency Score"

    def __str__(self):
        return f"{self.user.username} | {self.competency.name}: Level {self.evaluated_level}"

    @property
    def target_level(self):
        """Finds target level based on user's cadre and designation"""
        mapping = RoleCompetencyMapping.objects.filter(
            cadre=self.user.cadre,
            designation=self.user.designation,
            competency=self.competency
        ).first()
        return mapping.target_level if mapping else 3  # Default target level 3 if unmapped

    @property
    def gap(self):
        """Competency Gap: target_level - evaluated_level"""
        return max(0, self.target_level - self.evaluated_level)


class KarmaBadge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='award', help_text='Lucide icon name (e.g., award, shield-check, zap)')
    description = models.TextField()
    category = models.CharField(max_length=50, default='General')

    def __str__(self):
        return f"Badge: {self.name}"


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(KarmaBadge, on_delete=models.CASCADE, related_name='awarded_users')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} -> {self.badge.name}"
