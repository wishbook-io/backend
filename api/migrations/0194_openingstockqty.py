# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0193_openingstock'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpeningStockQty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('in_stock', models.IntegerField(default=0)),
                ('opening_stock', models.ForeignKey(to='api.OpeningStock')),
                ('product', models.ForeignKey(to='api.Product')),
            ],
        ),
    ]
