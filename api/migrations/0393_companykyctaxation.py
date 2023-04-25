# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0392_cataloguploadoption'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyKycTaxation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pan', models.CharField(max_length=20, null=True, blank=True)),
                ('gstin', models.CharField(max_length=20, null=True, blank=True)),
                ('arn', models.CharField(max_length=20, null=True, blank=True)),
                ('add_gst_to_price', models.BooleanField(default=True)),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
