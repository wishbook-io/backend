# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0115_remove_invitee_group_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='whatsapp_verified',
            field=models.CharField(default=b'no', max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
