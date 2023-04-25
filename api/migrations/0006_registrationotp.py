# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20151123_0521'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationOTP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
                ('otp', models.PositiveIntegerField()),
                ('created_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
