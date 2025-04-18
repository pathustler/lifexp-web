# Generated by Django 5.1.7 on 2025-03-25 11:52

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_alter_post_end_time_alter_post_start_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="post_image",
            field=cloudinary.models.CloudinaryField(
                blank=True,
                default="Screenshot_2025-03-25_at_10.40.01_PM_vugdxk",
                max_length=255,
                null=True,
                verbose_name="image",
            ),
        ),
    ]
