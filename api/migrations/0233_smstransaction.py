# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0232_auto_20160820_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmsTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('total_sent', models.IntegerField(default=0)),
                ('provider', models.CharField(max_length=50)),
            ],
        ),
    ]
