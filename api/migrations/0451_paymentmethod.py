# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0450_company_default_catalog_lifetime'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('payment_status', models.CharField(max_length=50, choices=[(b'Online', b'Online'), (b'Offline', b'Offline'), (b'Credit', b'Credit')])),
                ('display_name', models.CharField(max_length=200)),
            ],
        ),
    ]
