# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0552_usercampaignclick'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercampaignclick',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
