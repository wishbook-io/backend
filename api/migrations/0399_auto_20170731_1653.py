# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0398_auto_20170728_1700'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoiceitem',
            name='tax_code_1',
        ),
        migrations.RemoveField(
            model_name='invoiceitem',
            name='tax_code_2',
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='tax_class_1',
            field=models.ForeignKey(related_name='tax_class_1', default=None, blank=True, to='api.TaxClass', null=True),
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='tax_class_2',
            field=models.ForeignKey(related_name='tax_class_2', default=None, blank=True, to='api.TaxClass', null=True),
        ),
    ]
