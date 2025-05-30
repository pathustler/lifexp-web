# Generated by Django 5.1.7 on 2025-03-26 12:18

import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_alter_post_post_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="activitylog",
            old_name="activity_desc",
            new_name="name",
        ),
        migrations.RemoveField(
            model_name="activitylog",
            name="productivity_score",
        ),
        migrations.AlterField(
            model_name="activitylog",
            name="xp_distribution",
            field=models.JSONField(default=main.models.ActivityLog.default_xp),
        ),
    ]
