from django.core.management.base import BaseCommand
from apps.jobs.models import Job
from apps.scraper import nerdin, linkedin


class Command(BaseCommand):
    help = "Backfill descriptions and contract_type for jobs that have none"

    def handle(self, *args, **options):
        jobs = Job.objects.filter(description="")
        total = jobs.count()
        self.stdout.write(f"Filling descriptions for {total} jobs...")

        updated = 0
        for i, job in enumerate(jobs, 1):
            desc, contract_type = "", "unknown"
            if job.source == "nerdin":
                desc, contract_type = nerdin._fetch_detail(job.url)
            elif job.source == "linkedin":
                desc, contract_type = linkedin._fetch_detail(job.external_id)

            fields = []
            if desc:
                job.description = desc
                fields.append("description")
            if contract_type != "unknown" and job.contract_type == "unknown":
                job.contract_type = contract_type
                fields.append("contract_type")

            if fields:
                job.save(update_fields=fields)
                updated += 1

            if i % 10 == 0:
                self.stdout.write(f"  {i}/{total} processed ({updated} filled)")

        self.stdout.write(self.style.SUCCESS(f"Done. {updated}/{total} jobs updated."))
