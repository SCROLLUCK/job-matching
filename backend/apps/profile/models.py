from django.db import models


class UserProfile(models.Model):
    CONTRACT_CHOICES = [("pj", "PJ"), ("clt", "CLT"), ("both", "Both")]
    WORK_MODE_CHOICES = [("remote", "Remote"), ("hybrid", "Hybrid"), ("onsite", "On-site"), ("any", "Any")]

    competencies = models.TextField(blank=True)
    tech_stack = models.JSONField(default=list)
    desired_salary_min = models.IntegerField(null=True, blank=True)
    desired_salary_max = models.IntegerField(null=True, blank=True)
    preferred_contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default="both")
    preferred_work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default="any")
    preferred_roles = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
