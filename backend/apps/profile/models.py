from django.db import models


class UserProfile(models.Model):
    competencies = models.TextField(blank=True)
    tech_stack = models.JSONField(default=list)
    desired_salary_min = models.IntegerField(null=True, blank=True)
    desired_salary_max = models.IntegerField(null=True, blank=True)
    preferred_contract_type = models.JSONField(default=list)  # [] = any; ["pj"], ["clt"], or ["pj","clt"]
    preferred_work_mode = models.JSONField(default=list)      # [] = any; ["remote"], ["hybrid"], ["onsite"] or combos
    preferred_roles = models.JSONField(default=list)
    score_weights = models.JSONField(default=dict)  # {"stack":2,"salary":2,"role":2,"work_mode":2,"contract":2} — 1=low,2=mid,3=high
    updated_at = models.DateTimeField(auto_now=True)

    def get_weights(self) -> dict:
        defaults = {"stack": 2, "salary": 2, "role": 2, "work_mode": 2, "contract": 2}
        return {**defaults, **(self.score_weights or {})}

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
