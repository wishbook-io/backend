# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0085_auto_20160112_1140'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('catalogs', models.ManyToManyField(related_name='catalog_list', to='api.Catalog')),
            ],
        ),
    ]
