# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0237_auto_20160909_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductEAVFlat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fabric', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('work', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('fabric_text', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('work_text', models.CharField(default=None, max_length=100, null=True, blank=True)),
                ('catalog', models.ForeignKey(to='api.Catalog')),
                ('category', models.ForeignKey(to='api.Category')),
                ('product', models.ForeignKey(to='api.Product')),
            ],
        ),
    ]
