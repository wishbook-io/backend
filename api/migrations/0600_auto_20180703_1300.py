# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0599_auto_20180703_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companycreditrating',
            name='bureau_status',
            field=models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(b'Verification Failed', b'Verification Failed'), (b'Verification But Miss', b'Verification But Miss'), (b'Hit', b'Hit')]),
        ),
        migrations.AlterField(
            model_name='usercreditsubmission',
            name='bureau_status',
            field=models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(b'Verification Failed', b'Verification Failed'), (b'Verification But Miss', b'Verification But Miss'), (b'Hit', b'Hit')]),
        ),
    ]
