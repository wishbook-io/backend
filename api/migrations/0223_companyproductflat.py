# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0222_salesorder_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyProductFlat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('final_price', models.DecimalField(max_digits=19, decimal_places=2)),
                ('selling_price', models.DecimalField(max_digits=19, decimal_places=2)),
                ('status', models.CharField(default=b'Enable', max_length=20, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('like', models.BooleanField(default=False)),
                ('buying_company', models.ForeignKey(related_name='cpf_buying_company', to='api.Company')),
                ('catalog', models.ForeignKey(default=None, blank=True, to='api.Catalog', null=True)),
                ('product', models.ForeignKey(to='api.Product')),
                ('selection', models.ForeignKey(default=None, blank=True, to='api.Selection', null=True)),
                ('selling_company', models.ForeignKey(related_name='cpf_selling_company', to='api.Company')),
            ],
        ),
    ]
