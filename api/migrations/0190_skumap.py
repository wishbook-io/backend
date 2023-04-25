# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0189_auto_20160711_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='SKUMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_sku', models.CharField(max_length=100)),
                ('app_instance', models.ForeignKey(to='api.AppInstance')),
                ('sku', models.ForeignKey(to='api.Product')),
            ],
        ),
    ]
