from django.core.management.base import BaseCommand
from apps.jobs.models import Job
from apps.scraper import linkedin


class Command(BaseCommand):
    help = "Backfill salary and work_mode for LinkedIn jobs that have none"

    def handle(self, *args, **options):
        jobs = Job.objects.filter(source="linkedin", salary_min__isnull=True)
        total = jobs.count()
        self.stdout.write(f"Filling salary for {total} LinkedIn jobs...")

        updated = 0
        for i, job in enumerate(jobs, 1):
            _, _, salary_min, salary_max, work_mode = linkedin._fetch_detail(job.external_id)

            fields = []
            if salary_min:
                job.salary_min = salary_min
                job.salary_max = salary_max
                fields += ["salary_min", "salary_max"]
            if job.work_mode == "unknown" and work_mode != "unknown":
                job.work_mode = work_mode
                fields.append("work_mode")

            if fields:
                job.save(update_fields=fields)
                updated += 1

            if i % 10 == 0:
                self.stdout.write(f"  {i}/{total} processed ({updated} updated)")

        self.stdout.write(self.style.SUCCESS(f"Done. {updated}/{total} jobs updated."))
