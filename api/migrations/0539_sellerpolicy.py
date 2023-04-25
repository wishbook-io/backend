# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0538_userprofile_company_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellerPolicy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('policy_type', models.CharField(max_length=20, choices=[(b'Return', b'Return'), (b'Dispatch Duration', b'Dispatch Duration')])),
                ('policy', models.TextField()),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
