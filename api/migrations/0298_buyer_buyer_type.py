# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0297_auto_20170309_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='buyer_type',
            field=models.CharField(default=b'Relationship', max_length=20, choices=[(b'Relationship', b'Relationship'), (b'Inquiry', b'Inquiry')]),
        ),
    ]
