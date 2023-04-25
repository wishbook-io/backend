# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0576_auto_20180522_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditreference',
            name='average_gr_rate',
            field=models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(b'Less than 5%', b'Less than 5%'), (b'5% to 10%', b'5% to 10%'), (b'10% to 20%', b'10% to 20%'), (b'More than 20%', b'More than 20%')]),
        ),
        migrations.AlterField(
            model_name='creditreference',
            name='average_payment_duration',
            field=models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(b'Less than 30 days', b'Less than 30 days'), (b'30 to 60 days', b'30 to 60 days'), (b'60 to 90 days', b'60 to 90 days'), (b'More than 90 days', b'More than 90 days')]),
        ),
    ]
