# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0418_company_trusted_seller'),
    ]

    operations = [
        migrations.CreateModel(
            name='WbCoupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('discount_type', models.CharField(max_length=20, choices=[(b'Percentage', b'Percentage'), (b'Fixed', b'Fixed')])),
                ('value', models.DecimalField(max_digits=19, decimal_places=2)),
                ('valid_till', models.DateField()),
                ('num_uses', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
