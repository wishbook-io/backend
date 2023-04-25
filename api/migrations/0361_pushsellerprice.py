# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0360_auto_20170627_1124'),
    ]

    operations = [
        migrations.CreateModel(
            name='PushSellerPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=19, decimal_places=2)),
                ('product', models.ForeignKey(to='api.Product')),
                ('push', models.ForeignKey(to='api.Push')),
                ('selling_company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
