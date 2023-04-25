# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0322_meeting_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='company',
            field=models.ForeignKey(related_name='attendance_user_company', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
