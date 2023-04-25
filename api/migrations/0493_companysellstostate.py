# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0492_category_sort_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanySellsToState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.ForeignKey(related_name='companysellstostate', to='api.Company')),
                ('intermediate_buyer', models.ForeignKey(related_name='intermediatecompanysellstostate', default=None, blank=True, to='api.Company', null=True)),
                ('state', models.ManyToManyField(to='api.State')),
            ],
        ),
    ]
