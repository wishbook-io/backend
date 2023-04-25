# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitee',
            name='invitee_number',
            field=models.CharField(unique=True, max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")]),
        ),
    ]
