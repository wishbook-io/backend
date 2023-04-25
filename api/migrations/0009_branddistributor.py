# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20151126_0702'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrandDistributor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('brand', models.ManyToManyField(to='api.Brand')),
                ('company', models.ForeignKey(to='api.Company', unique=True)),
            ],
        ),
    ]
