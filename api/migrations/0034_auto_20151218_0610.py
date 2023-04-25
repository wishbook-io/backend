# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_auto_20151218_0607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='phone_number',
            field=models.CharField(blank=True, max_length=13, null=True, validators=[django.core.validators.RegexValidator(regex=b'^(?:\\+\\d{10,15}|)$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")]),
        ),
        migrations.AlterField(
            model_name='company',
            name='pincode',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.RegexValidator(regex=b'^(?:\\d{6}|)$', message=b'Invalid pincode!')]),
        ),
    ]
