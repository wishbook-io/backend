# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0396_taxclass'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryTaxClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='api.Category')),
                ('tax_class', models.ForeignKey(to='api.TaxClass')),
            ],
        ),
    ]
