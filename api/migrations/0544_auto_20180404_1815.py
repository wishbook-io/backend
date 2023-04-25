# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0543_auto_20180404_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='companycreditrating',
            name='bureau_report_rating',
            field=models.CharField(default='Unavailable', max_length=20, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative'), (b'Unavailable', b'Unavailable')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='financial_statement_rating',
            field=models.CharField(default='Unavailable', max_length=20, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative'), (b'Unavailable', b'Unavailable')]),
            preserve_default=False,
        ),
    ]
