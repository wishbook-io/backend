# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0192_auto_20160712_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpeningStock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('warehouse', models.ForeignKey(to='api.Warehouse')),
            ],
        ),
    ]
