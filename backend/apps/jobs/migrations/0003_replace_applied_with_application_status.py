from django.db import migrations, models


def copy_applied(apps, schema_editor):
    Job = apps.get_model("jobs", "Job")
    Job.objects.filter(applied=True).update(application_status="applied")


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_alter_job_options_job_applied'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='application_status',
            field=models.CharField(blank=True, choices=[('applied', 'Applied'), ('rejected', 'Rejected')], default='', max_length=20),
        ),
        migrations.RunPython(copy_applied, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='job',
            name='applied',
        ),
    ]
