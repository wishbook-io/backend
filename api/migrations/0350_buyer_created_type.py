# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0349_auto_20170519_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='created_type',
            field=models.CharField(default=b'Relationship', max_length=20, choices=[(b'Relationship', b'Relationship'), (b'Enquiry', b'Enquiry')]),
        ),
    ]
