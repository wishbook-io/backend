# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0353_catalog_sort_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyCatalogView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('catalog_type', models.CharField(max_length=20, choices=[(b'public', b'Public'), (b'push', b'Push')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('catalog', models.ForeignKey(to='api.Catalog')),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='companycatalogview',
            unique_together=set([('company', 'catalog', 'catalog_type')]),
        ),
    ]
