from django.db import models


class UserProfile(models.Model):
    competencies = models.TextField(blank=True)
    tech_stack = models.JSONField(default=list)
    desired_salary_min = models.IntegerField(null=True, blank=True)
    desired_salary_max = models.IntegerField(null=True, blank=True)
    preferred_contract_type = models.JSONField(default=list)  # [] = any; ["pj"], ["clt"], or ["pj","clt"]
    preferred_work_mode = models.JSONField(default=list)      # [] = any; ["remote"], ["hybrid"], ["onsite"] or combos
    preferred_roles = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
