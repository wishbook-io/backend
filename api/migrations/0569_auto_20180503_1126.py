# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0568_story'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditreference',
            name='duration_of_work',
            field=models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(b'Less than 6 months', b'Less than 6 months'), (b'6 months to 2 years', b'6 months to 2 years'), (b'2 years to 5 years', b'2 years to 5 years'), (b'More than 5 years', b'More than 5 years')]),
        ),
        migrations.AlterField(
            model_name='creditreference',
            name='average_gr_rate',
            field=models.CharField(max_length=50, choices=[(b'Less than 5%', b'Less than 5%'), (b'5% to 10%', b'5% to 10%'), (b'10% to 20%', b'10% to 20%'), (b'More than 20%', b'More than 20%')]),
        ),
        migrations.AlterField(
            model_name='creditreference',
            name='average_payment_duration',
            field=models.CharField(max_length=50, choices=[(b'Less than 30 days', b'Less than 30 days'), (b'30 to 60 days', b'30 to 60 days'), (b'60 to 90 days', b'60 to 90 days'), (b'More than 90 days', b'More than 90 days')]),
        ),
        migrations.AlterField(
            model_name='creditreference',
            name='transaction_value',
            field=models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(b'Less than 1 Lakh', b'Less than 1 Lakh'), (b'1 Lakh to 5 Lakh', b'1 Lakh to 5 Lakh'), (b'5 Lakh to 10 Lakh', b'5 Lakh to 10 Lakh'), (b'More than 10 Lakh', b'More than 10 Lakh')]),
        ),
    ]
