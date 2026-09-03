from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class CadreChoices(models.TextChoices):
        ISS = 'ISS', 'Indian Statistical Service (ISS)'
        SSS = 'SSS', 'Subordinate Statistical Service (SSS)'
        STATE_DES = 'STATE_DES', 'State DES Cadre'
        CONTRACTUAL = 'CONTRACTUAL', 'Contractual / Technical Consultant'

    class WingChoices(models.TextChoices):
        FOD = 'FOD', 'Field Operations Division (FOD)'
        NAD = 'NAD', 'National Accounts Division (NAD)'
        ESD = 'ESD', 'Economic Statistics Division (ESD)'
        SSD = 'SSD', 'Social Statistics Division (SSD)'
        NSSTA = 'NSSTA', 'National Statistical Systems Training Academy (NSSTA)'

    class RoleChoices(models.TextChoices):
        OFFICER = 'OFFICER', 'Statistical Officer / Learner'
        NSSTA_CURATOR = 'NSSTA_CURATOR', 'NSSTA Curator / Evaluator'
        SUPERADMIN = 'SUPERADMIN', 'System SuperAdmin'

    cadre = models.CharField(
        max_length=20, 
        choices=CadreChoices.choices, 
        default=CadreChoices.ISS
    )
    designation = models.CharField(
        max_length=100, 
        default='Statistical Officer',
        help_text='Current official designation (e.g., Director, Assistant Director, JSO)'
    )
    department_wing = models.CharField(
        max_length=20, 
        choices=WingChoices.choices, 
        default=WingChoices.FOD
    )
    employee_code = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        help_text='Official MoSPI Employee / Registration ID'
    )
    igot_user_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='Linked iGOT Karmayogi Profile ID'
    )
    role = models.CharField(
        max_length=20, 
        choices=RoleChoices.choices, 
        default=RoleChoices.OFFICER
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.cadre} - {self.designation})"

    @property
    def is_evaluator(self):
        return self.role in [self.RoleChoices.NSSTA_CURATOR, self.RoleChoices.SUPERADMIN] or self.is_superuser
