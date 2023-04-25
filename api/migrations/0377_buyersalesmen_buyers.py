# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0376_auto_20170708_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyersalesmen',
            name='buyers',
            field=models.ManyToManyField(to='api.Company'),
        ),
    ]
