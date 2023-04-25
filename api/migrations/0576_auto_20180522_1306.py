# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0575_catalogenquiry_applogic_conversation_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditreference',
            name='buyer_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='creditreference',
            name='supplier_responded',
            field=models.BooleanField(default=False),
        ),
    ]
