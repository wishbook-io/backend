# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0483_auto_20171121_1448'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPlatformInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.CharField(max_length=250, null=True, blank=True)),
                ('app_version', models.CharField(max_length=250, null=True, blank=True)),
                ('app_version_code', models.CharField(max_length=250, null=True, blank=True)),
                ('device_model', models.CharField(max_length=250, null=True, blank=True)),
                ('brand', models.CharField(max_length=250, null=True, blank=True)),
                ('operating_system', models.CharField(max_length=250, null=True, blank=True)),
                ('operating_system_version', models.CharField(max_length=250, null=True, blank=True)),
                ('screen_width', models.CharField(max_length=250, null=True, blank=True)),
                ('screen_height', models.CharField(max_length=250, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
