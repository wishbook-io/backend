# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0281_auto_20170103_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyersegmentation',
            name='state',
            field=models.ManyToManyField(to='api.State', blank=True),
        ),
    ]
