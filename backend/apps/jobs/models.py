from django.db import models
from django.db.models import F


class Job(models.Model):
    SOURCE_CHOICES = [
        ("linkedin", "LinkedIn"),
        ("nerdin", "Nerdin"),
        ("geekhunter", "GeekHunter"),
        ("indeed", "Indeed"),
    ]
    CONTRACT_CHOICES = [
        ("pj", "PJ"),
        ("clt", "CLT"),
        ("both", "Both"),
        ("unknown", "Unknown"),
    ]
    WORK_MODE_CHOICES = [
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
        ("onsite", "On-site"),
        ("unknown", "Unknown"),
    ]
    LEVEL_CHOICES = [
        ("junior", "Junior"),
        ("mid", "Mid-level"),
        ("senior", "Senior"),
        ("unknown", "Unknown"),
    ]

    external_id = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(unique=True, max_length=1000)
    location = models.CharField(max_length=255, blank=True)
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES, default="unknown")
    contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default="unknown")
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    tech_stack = models.JSONField(default=list)
    experience_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="unknown")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    posted_at = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    APPLICATION_STATUS_CHOICES = [
        ("applied", "Applied"),
        ("rejected", "Rejected"),
    ]

    score = models.FloatField(null=True, blank=True)
    score_breakdown = models.JSONField(default=dict)
    application_status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, blank=True, default="")

    class Meta:
        unique_together = ("external_id", "source")
        ordering = [F("score").desc(nulls_last=True), "-scraped_at"]

    def __str__(self):
        return f"{self.title} @ {self.company} ({self.source})"
