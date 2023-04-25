# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0394_taxtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tax_code', models.CharField(max_length=50)),
                ('tax_code_type', models.CharField(max_length=50, choices=[(b'HSN', b'HSN')])),
                ('tax_type', models.ForeignKey(to='api.TaxType')),
            ],
        ),
    ]
