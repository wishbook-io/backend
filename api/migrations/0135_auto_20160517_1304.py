# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0134_auto_20160517_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitee',
            name='country',
            field=models.ForeignKey(related_name='invitee_country', default=1, to='api.Country'),
        ),
        migrations.AlterField(
            model_name='invitee',
            name='invitee_number',
            field=models.CharField(max_length=13),
        ),
    ]
