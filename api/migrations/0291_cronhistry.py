# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0290_auto_20170214_1203'),
    ]

    operations = [
        migrations.CreateModel(
            name='CronHistry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cron_type', models.CharField(max_length=100)),
                ('time', models.DateTimeField()),
            ],
        ),
    ]
