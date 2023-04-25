# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0415_auto_20170811_1523'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='invoice',
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice',
            field=models.ManyToManyField(default=None, related_name='payments', to='api.Invoice'),
        ),
    ]
