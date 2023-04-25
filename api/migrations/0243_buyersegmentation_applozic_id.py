# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0242_updatenotification_update_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyersegmentation',
            name='applozic_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
