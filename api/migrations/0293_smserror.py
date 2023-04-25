# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0292_auto_20170215_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmsError',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('sms_text', models.CharField(max_length=250)),
                ('mobile_no', models.CharField(max_length=15)),
                ('is_sent', models.BooleanField(default=False)),
                ('provider', models.CharField(max_length=50)),
                ('error_text', models.CharField(max_length=250)),
            ],
        ),
    ]
