# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0384_salesorder_tranferred_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouse',
            name='supplier',
            field=models.ManyToManyField(related_name='suppliers', to='api.Company', blank=True),
        ),
    ]
