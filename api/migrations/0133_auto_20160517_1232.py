# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0132_auto_20160517_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationotp',
            name='country',
            field=models.ForeignKey(related_name='otp_country', default=1, to='api.Country'),
        ),
        migrations.AlterField(
            model_name='registrationotp',
            name='phone_number',
            field=models.CharField(max_length=13),
        ),
    ]
