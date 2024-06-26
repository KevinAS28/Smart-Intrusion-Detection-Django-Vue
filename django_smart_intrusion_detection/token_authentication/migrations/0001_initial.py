# Generated by Django 5.0.4 on 2024-04-17 03:08

import django.db.models.deletion
import token_authentication.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('intrusion_detection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UserAuthentication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=50)),
                ('token', models.CharField(max_length=500, null=True)),
                ('token_expired', models.DateTimeField(default=token_authentication.models.get_token_expire, null=True)),
                ('cam_settings', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='intrusion_detection.camsettings')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='token_authentication.userrole')),
            ],
        ),
    ]
