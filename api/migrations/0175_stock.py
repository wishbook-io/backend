# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0174_warehouse'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('in_stock', models.IntegerField(default=0)),
                ('blocked', models.IntegerField(default=0)),
                ('open_sale', models.IntegerField(default=0)),
                ('open_purchase', models.IntegerField(default=0)),
                ('product', models.ForeignKey(to='api.Product')),
                ('warehouse', models.ForeignKey(to='api.Warehouse')),
            ],
        ),
    ]
