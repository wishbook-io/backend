# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0458_auto_20171006_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='PincodeZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pincode', models.IntegerField()),
                ('zone', models.CharField(max_length=200)),
                ('city', models.ForeignKey(to='api.City')),
            ],
        ),
        migrations.AddField(
            model_name='salesorder',
            name='buyer_preferred_logistics',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
