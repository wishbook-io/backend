# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0363_pushsellerprice_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyProductView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(to='api.Company')),
                ('product', models.ForeignKey(to='api.Product')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='companyproductview',
            unique_together=set([('company', 'product')]),
        ),
    ]
