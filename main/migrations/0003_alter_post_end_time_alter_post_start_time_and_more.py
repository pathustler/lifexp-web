# Generated by Django 5.1.7 on 2025-03-23 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_activitylog_comment"),
        ("users", "0013_searchhistory"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="end_time",
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name="post",
            name="start_time",
            field=models.TimeField(),
        ),
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "activity_desc",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("xp_distribution", models.JSONField()),
                ("productivity_score", models.IntegerField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("total_time_done", models.IntegerField(editable=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_logs",
                        to="users.player",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
