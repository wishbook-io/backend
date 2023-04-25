# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0135_auto_20160517_1304'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyPhoneAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias_number', models.CharField(unique=True, max_length=13)),
                ('status', models.CharField(default=b'Verification_Pending', max_length=10, choices=[(b'Verification_Pending', b'Verification Pending'), (b'Approved', b'Approved')])),
                ('company', models.ForeignKey(related_name='alias_company', to='api.Company')),
                ('country', models.ForeignKey(related_name='alias_country', default=1, to='api.Country')),
            ],
        ),
    ]
