# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0423_paidclient'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seller_score', models.DecimalField(default=None, null=True, max_digits=4, decimal_places=2, blank=True)),
                ('buyer_score', models.DecimalField(default=None, null=True, max_digits=4, decimal_places=2, blank=True)),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='OrderRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seller_rating', models.DecimalField(default=None, null=True, max_digits=4, decimal_places=2, blank=True)),
                ('buyer_rating', models.DecimalField(default=None, null=True, max_digits=4, decimal_places=2, blank=True)),
                ('seller_remark', multiselectfield.db.fields.MultiSelectField(max_length=117, choices=[(b'Delivered product were not as described', b'Delivered product were not as described'), (b'Delivery took more time then mentioned', b'Delivery took more time then mentioned'), (b'Issues with Wishbook Application', b'Issues with Wishbook Application'), (b'Other', b'Other')])),
                ('seller_remark_other', models.TextField(null=True, blank=True)),
                ('buyer_remark', multiselectfield.db.fields.MultiSelectField(max_length=38, choices=[(b'Issues with Wishbook Application', b'Issues with Wishbook Application'), (b'Other', b'Other')])),
                ('buyer_remark_other', models.TextField(null=True, blank=True)),
                ('order', models.ForeignKey(to='api.SalesOrder')),
            ],
        ),
    ]
