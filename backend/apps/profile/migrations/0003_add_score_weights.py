from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('profile', '0002_profile_array_preferences')]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='score_weights',
            field=models.JSONField(default=dict),
        ),
    ]
