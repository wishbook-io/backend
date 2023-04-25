# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0179_selection_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitee',
            name='invitee_company',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='invitee',
            name='invitee_name',
            field=models.CharField(max_length=100),
        ),
    ]
