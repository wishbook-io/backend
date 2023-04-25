# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0593_catalog_single_piece_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyCreditAprovedLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nbfc_partner', models.CharField(default=b'Indifi', max_length=30, null=True, blank=True, choices=[(b'Indifi', b'Indifi')])),
                ('approved_line', models.DecimalField(max_digits=19, decimal_places=2, blank=True)),
                ('available_line', models.DecimalField(max_digits=19, decimal_places=2, blank=True)),
                ('used_line', models.DecimalField(max_digits=19, decimal_places=2, blank=True)),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
