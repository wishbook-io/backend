# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0395_taxcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tax_name', models.CharField(max_length=50)),
                ('from_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('to_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('location_type', models.CharField(max_length=50, choices=[(b'Same State', b'Same State'), (b'Inter State', b'Inter State'), (b'UT', b'UT')])),
                ('percentage', models.PositiveIntegerField()),
                ('tax_code', models.ForeignKey(to='api.TaxCode')),
            ],
        ),
    ]
