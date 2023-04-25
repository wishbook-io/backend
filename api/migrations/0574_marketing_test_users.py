# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0573_auto_20180516_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketing',
            name='test_users',
            field=models.ManyToManyField(related_name='test_users', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
