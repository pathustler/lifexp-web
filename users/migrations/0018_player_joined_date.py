# Generated by Django 5.1.7 on 2025-03-29 10:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0017_player_following"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="joined_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
