# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0379_remove_buyersalesmen_buyer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyersalesmen',
            name='salesman',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
