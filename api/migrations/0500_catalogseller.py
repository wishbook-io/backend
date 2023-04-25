# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0499_auto_20171214_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogSeller',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('selling_type', models.CharField(default=b'Public', max_length=20, choices=[(b'Public', b'Public'), (b'Private', b'Private')])),
                ('sell_full_catalog', models.BooleanField(default=False)),
                ('full_catalog_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('status', models.CharField(default=b'Enable', max_length=20, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('catalog', models.ForeignKey(to='api.Catalog')),
                ('selling_company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
