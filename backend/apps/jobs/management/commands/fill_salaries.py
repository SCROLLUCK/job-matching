from django.core.management.base import BaseCommand
from apps.jobs.models import Job
from apps.scraper import linkedin, geekhunter


class Command(BaseCommand):
    help = "Backfill salary and work_mode for jobs that have none"

    def handle(self, *args, **options):
        self._fill_linkedin()
        self._fill_geekhunter()

    def _fill_linkedin(self):
        jobs = list(Job.objects.filter(source="linkedin", salary_min__isnull=True))
        self.stdout.write(f"LinkedIn: {len(jobs)} jobs to fill...")
        updated = 0
        for i, job in enumerate(jobs, 1):
            _, _, salary_min, salary_max, work_mode = linkedin._fetch_detail(job.external_id)
            updated += self._save(job, salary_min, salary_max, work_mode)
            if i % 10 == 0:
                self.stdout.write(f"  {i}/{len(jobs)} ({updated} updated)")
        self.stdout.write(self.style.SUCCESS(f"LinkedIn done. {updated}/{len(jobs)} updated."))

    def _fill_geekhunter(self):
        jobs = list(Job.objects.filter(source="geekhunter", salary_min__isnull=True))
        self.stdout.write(f"GeekHunter: {len(jobs)} jobs to fill...")
        updated = 0
        for i, job in enumerate(jobs, 1):
            salary_min, salary_max, work_mode = geekhunter._fetch_detail(job.url)
            updated += self._save(job, salary_min, salary_max, work_mode)
            if i % 5 == 0:
                self.stdout.write(f"  {i}/{len(jobs)} ({updated} updated)")
        self.stdout.write(self.style.SUCCESS(f"GeekHunter done. {updated}/{len(jobs)} updated."))

    def _save(self, job, salary_min, salary_max, work_mode):
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
            return 1
        return 0
