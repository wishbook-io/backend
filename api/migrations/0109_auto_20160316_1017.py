# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0108_auto_20160312_0631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='company',
            field=models.ForeignKey(related_name='branches', to='api.Company'),
        ),
    ]
