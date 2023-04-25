# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0226_companyproductflat_push_reference'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnsubcribedNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=13)),
                ('country', models.ForeignKey(to='api.Country')),
            ],
        ),
    ]
