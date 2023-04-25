# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0574_marketing_test_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogenquiry',
            name='applogic_conversation_id',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
