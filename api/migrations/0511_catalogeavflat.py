# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0510_auto_20180105_1626'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogEAVFlat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('view_permission', models.CharField(default=b'push', max_length=20, choices=[(b'public', b'Public'), (b'push', b'Push')])),
                ('sell_full_catalog', models.BooleanField(default=False)),
                ('fabric', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('work', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('fabric_value', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('work_value', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('min_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('max_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('stitching_type', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('number_pcs_design_per_set', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('size', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('size_value', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('size_mix', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('brand', models.ForeignKey(to='api.Brand')),
                ('catalog', models.OneToOneField(to='api.Catalog')),
                ('category', models.ForeignKey(to='api.Category')),
            ],
        ),
    ]
