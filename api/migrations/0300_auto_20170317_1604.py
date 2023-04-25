# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0299_buyer_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyer',
            name='buyer_type',
            field=models.CharField(default=b'Relationship', max_length=20, choices=[(b'Relationship', b'Relationship'), (b'Enquiry', b'Enquiry')]),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='group_type',
            field=models.ForeignKey(blank=True, to='api.GroupType', null=True),
        ),
    ]
