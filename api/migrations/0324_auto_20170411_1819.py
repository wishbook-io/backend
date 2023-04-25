# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0323_attendance_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='city',
            field=models.ForeignKey(blank=True, to='api.City', null=True),
        ),
        migrations.AlterField(
            model_name='branch',
            name='state',
            field=models.ForeignKey(blank=True, to='api.State', null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='city',
            field=models.ForeignKey(blank=True, to='api.City', null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='state',
            field=models.ForeignKey(blank=True, to='api.State', null=True),
        ),
    ]
