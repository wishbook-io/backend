# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0137_auto_20160517_1558'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnregisteredPhoneAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('master_number', models.CharField(max_length=13)),
                ('alias_number', models.CharField(unique=True, max_length=13)),
                ('alias_country', models.ForeignKey(related_name='alias_country_ref', default=1, to='api.Country')),
                ('master_country', models.ForeignKey(related_name='master_country_ref', default=1, to='api.Country')),
            ],
        ),
    ]
