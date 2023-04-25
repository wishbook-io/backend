# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0180_auto_20160629_1527'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogSelectionStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'Disable', max_length=20, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('catalog', models.ForeignKey(default=None, blank=True, to='api.Catalog', null=True)),
                ('company', models.ForeignKey(to='api.Company')),
                ('selection', models.ForeignKey(default=None, blank=True, to='api.Selection', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'Disable', max_length=20, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('company', models.ForeignKey(to='api.Company')),
                ('product', models.ForeignKey(to='api.Product')),
            ],
        ),
    ]
