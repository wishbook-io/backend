# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0369_company_buyers_assigned_to_salesman'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='salesman_mapping',
            field=models.CharField(default=b'Location', max_length=30, choices=[(b'Location', b'Location'), (b'Individual', b'Individual')]),
        ),
    ]
