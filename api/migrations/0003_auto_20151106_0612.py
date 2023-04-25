# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20151106_0611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitee',
            name='invitee_number',
            field=models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")]),
        ),
    ]
