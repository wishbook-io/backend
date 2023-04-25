# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0589_auto_20180612_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercreditsubmission',
            name='average_gr_rate',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Less than 5%', b'Less than 5%'), (b'5% to 10%', b'5% to 10%'), (b'10% to 20%', b'10% to 20%'), (b'More than 20%', b'More than 20%')]),
        ),
        migrations.AlterField(
            model_name='usercreditsubmission',
            name='average_payment_duration',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Less than 30 days', b'Less than 30 days'), (b'30 to 60 days', b'30 to 60 days'), (b'60 to 90 days', b'60 to 90 days'), (b'More than 90 days', b'More than 90 days')]),
        ),
        migrations.AlterField(
            model_name='usercreditsubmission',
            name='bureau_report_rating',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative'), (b'Unavailable', b'Unavailable')]),
        ),
        migrations.AlterField(
            model_name='usercreditsubmission',
            name='financial_statement_rating',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative'), (b'Unavailable', b'Unavailable')]),
        ),
    ]
