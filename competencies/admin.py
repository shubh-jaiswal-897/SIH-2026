from django.contrib import admin
from .models import Competency, RoleCompetencyMapping, LearnerCompetencyScore

@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ('official_code', 'name', 'type')
    list_filter = ('type',)
    search_fields = ('official_code', 'name', 'description')

@admin.register(RoleCompetencyMapping)
class RoleCompetencyMappingAdmin(admin.ModelAdmin):
    list_display = ('cadre', 'designation', 'competency', 'target_level')
    list_filter = ('cadre', 'target_level')
    search_fields = ('designation', 'competency__name')

@admin.register(LearnerCompetencyScore)
class LearnerCompetencyScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'competency', 'evaluated_level', 'last_assessed')
    list_filter = ('evaluated_level', 'last_assessed')
    search_fields = ('user__username', 'competency__name')
