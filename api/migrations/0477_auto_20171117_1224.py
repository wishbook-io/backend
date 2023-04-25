# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0476_auto_20171117_1022'),
    ]

    operations = [
        migrations.CreateModel(
            name='WarehouseStock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('in_stock', models.IntegerField(default=0)),
                ('product', models.ForeignKey(to='api.Product')),
                ('warehouse', models.ForeignKey(to='api.Warehouse')),
            ],
        ),
        migrations.AddField(
            model_name='stock',
            name='company',
            field=models.ForeignKey(default=None, blank=True, to='api.Company', null=True),
        ),
    ]
