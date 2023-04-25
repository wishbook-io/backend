# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0459_auto_20171010_1331'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=250)),
                ('value', models.CharField(max_length=250)),
                ('display_text', models.TextField(null=True, blank=True)),
                ('visible_on_frontend', models.BooleanField(default=False)),
            ],
        ),
    ]
