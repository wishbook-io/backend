# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0126_invitee_invitation_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push',
            name='status',
            field=models.CharField(default=b'In_Progress', max_length=20, choices=[(b'schedule', b'Schedule'), (b'delivered', b'Delivered'), (b'pending', b'Pending'), (b'In_Progress', b'In Progress')]),
        ),
    ]
