# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0373_auto_20170707_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesmanlocation',
            name='salesman',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
