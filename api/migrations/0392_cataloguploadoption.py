# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0391_assigngroups'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogUploadOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('private_single_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('public_single_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('fabric', models.TextField(null=True, blank=True)),
                ('work', models.TextField(null=True, blank=True)),
                ('without_price', models.BooleanField(default=False)),
                ('without_sku', models.BooleanField(default=False)),
                ('catalog', models.ForeignKey(to='api.Catalog')),
            ],
        ),
    ]
