# Generated by Django 5.0.4 on 2024-04-17 04:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intrusion_detection', '0002_homesettings_inferencesettings_usersettings_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserSettings',
        ),
    ]