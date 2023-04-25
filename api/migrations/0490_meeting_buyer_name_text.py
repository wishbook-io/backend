# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0489_invoiceitem_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='buyer_name_text',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
