# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0118_auto_20160412_1009'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{10,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
                ('alias_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{10,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
                ('is_verified', models.CharField(default=b'no', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')])),
            ],
        ),
    ]
