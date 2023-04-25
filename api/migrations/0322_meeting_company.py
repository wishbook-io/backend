# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0321_auto_20170410_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='company',
            field=models.ForeignKey(related_name='meeting_user_company', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
