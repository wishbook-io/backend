# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0553_auto_20180413_1924'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrderInternal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('internal_remark', models.TextField(null=True, blank=True)),
                ('last_modified_by', models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('salesorder', models.OneToOneField(to='api.SalesOrder')),
            ],
        ),
    ]
