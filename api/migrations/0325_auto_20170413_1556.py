# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0324_auto_20170411_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotionalnotification',
            name='category',
            field=models.ManyToManyField(to='api.Category', blank=True),
        ),
        migrations.AlterField(
            model_name='promotionalnotification',
            name='city',
            field=models.ManyToManyField(to='api.City', blank=True),
        ),
        migrations.AlterField(
            model_name='promotionalnotification',
            name='state',
            field=models.ManyToManyField(to='api.State', blank=True),
        ),
        migrations.AlterField(
            model_name='promotionalnotification',
            name='user',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
