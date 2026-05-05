from django.db import migrations, models


def to_array(apps, schema_editor):
    UserProfile = apps.get_model("profile", "UserProfile")
    wm_map = {"any": [], "remote": ["remote"], "hybrid": ["hybrid"], "onsite": ["onsite"]}
    ct_map = {"both": [], "pj": ["pj"], "clt": ["clt"]}
    for p in UserProfile.objects.all():
        p.preferred_work_mode = wm_map.get(p.preferred_work_mode_old, [])
        p.preferred_contract_type = ct_map.get(p.preferred_contract_type_old, [])
        p.save()


class Migration(migrations.Migration):
    dependencies = [("profile", "0001_initial")]

    operations = [
        migrations.RenameField("userprofile", "preferred_work_mode", "preferred_work_mode_old"),
        migrations.RenameField("userprofile", "preferred_contract_type", "preferred_contract_type_old"),
        migrations.AddField("userprofile", "preferred_work_mode", models.JSONField(default=list)),
        migrations.AddField("userprofile", "preferred_contract_type", models.JSONField(default=list)),
        migrations.RunPython(to_array, migrations.RunPython.noop),
        migrations.RemoveField("userprofile", "preferred_work_mode_old"),
        migrations.RemoveField("userprofile", "preferred_contract_type_old"),
    ]
