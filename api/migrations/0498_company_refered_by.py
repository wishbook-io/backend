# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0497_auto_20171213_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='refered_by',
            field=models.ForeignKey(related_name='refereds_by', blank=True, to='api.Company', null=True),
        ),
    ]
