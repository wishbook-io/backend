# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0282_buyersegmentation_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mapped_accout_ref', models.CharField(max_length=100)),
                ('buyer_company', models.ForeignKey(related_name='buyer', to='api.Company')),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
