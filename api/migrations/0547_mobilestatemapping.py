# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0546_auto_20180405_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileStateMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mobile_no_start_with', models.CharField(max_length=5)),
                ('state', models.ForeignKey(to='api.State')),
            ],
        ),
    ]
