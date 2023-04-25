# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0097_auto_20160128_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='push_user',
            name='buying_company',
            field=models.ForeignKey(related_name='buying_companies_push', default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AddField(
            model_name='push_user',
            name='selling_company',
            field=models.ForeignKey(related_name='selling_companies_push', default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AddField(
            model_name='push_user',
            name='selling_price',
            field=models.DecimalField(default=0.0, max_digits=19, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='push_user_product',
            name='buying_company',
            field=models.ForeignKey(related_name='buying_companies_product', default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AddField(
            model_name='push_user_product',
            name='selling_company',
            field=models.ForeignKey(related_name='selling_companies_product', default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AddField(
            model_name='push_user_product',
            name='selling_price',
            field=models.DecimalField(default=0.0, max_digits=19, decimal_places=2),
            preserve_default=False,
        ),
    ]
