# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0273_companyuser_deputed_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='warehouse',
            field=models.ForeignKey(default=None, blank=True, to='api.Warehouse', null=True),
        ),
    ]
