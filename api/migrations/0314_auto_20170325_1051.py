# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0313_auto_20170325_1049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('mode', models.CharField(max_length=250)),
                ('tracking_number', models.CharField(max_length=250)),
                ('details', models.TextField(null=True, blank=True)),
                ('invoice', models.ForeignKey(to='api.Invoice')),
            ],
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
