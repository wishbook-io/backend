# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0428_auto_20170823_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='enquiry_catalog',
            field=models.ForeignKey(default=None, blank=True, to='api.Catalog', null=True),
        ),
        migrations.AddField(
            model_name='buyer',
            name='enquiry_item_type',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Sets', b'Sets'), (b'Pieces', b'Pieces')]),
        ),
        migrations.AddField(
            model_name='buyer',
            name='enquiry_quantity',
            field=models.IntegerField(default=0),
        ),
    ]
