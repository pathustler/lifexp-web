# Generated by Django 5.1.7 on 2025-04-01 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_like"),
        ("users", "0021_remove_player_button_primary_accent_color_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="like",
            old_name="player",
            new_name="liked_by",
        ),
        migrations.AlterUniqueTogether(
            name="like",
            unique_together={("liked_by", "post")},
        ),
    ]
