# Generated by Django 4.2.11 on 2025-03-28 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmStructureRegistry', '0011_auto_20250317_0109'),
    ]

    operations = [
        migrations.AddField(
            model_name='structureregistry',
            name='pos_online',
            field=models.BooleanField(default=False),
        ),
    ]
