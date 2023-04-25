# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0125_auto_20160427_0541'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitee',
            name='invitation_type',
            field=models.CharField(default='Buyer', max_length=20, choices=[(b'Buyer', b'Buyer'), (b'Supplier', b'Supplier')]),
            preserve_default=False,
        ),
    ]
