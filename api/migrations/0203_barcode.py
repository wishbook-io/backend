# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0202_buyer_is_visible'),
    ]

    operations = [
        migrations.CreateModel(
            name='Barcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('barcode', models.CharField(max_length=200)),
                ('product', models.ForeignKey(to='api.Product')),
                ('warehouse', models.ForeignKey(to='api.Warehouse')),
            ],
        ),
    ]
