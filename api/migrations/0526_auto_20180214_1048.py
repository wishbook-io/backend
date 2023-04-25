# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0525_usersavedfilter'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version_code', models.CharField(max_length=100, null=True, blank=True)),
                ('update', models.BooleanField(default=False)),
                ('force_update', models.BooleanField(default=False)),
                ('platform', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.AlterField(
            model_name='usersavedfilter',
            name='sub_text',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
