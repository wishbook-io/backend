# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0430_auto_20170829_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorderitem',
            name='note',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='salesorderitem',
            name='packing_type',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Box', b'Box'), (b'Naked', b'Naked')]),
        ),
    ]
