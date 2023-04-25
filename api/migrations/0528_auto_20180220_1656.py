# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0527_auto_20180214_1118'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreDefinedFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(default=b'Enable', max_length=20, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('url', models.URLField(null=True, blank=True)),
                ('category', models.ForeignKey(to='api.Category')),
            ],
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='processing_status',
            field=models.CharField(default=b'Pending', max_length=20, null=True, choices=[(b'Cart', b'Cart'), (b'Pending', b'Pending'), (b'Draft', b'Draft'), (b'Accepted', b'Accepted'), (b'In Progress', b'In Progress'), (b'Dispatched', b'Dispatched'), (b'Partially Dispatched', b'Partially Dispatched'), (b'Delivered', b'Delivered'), (b'Cancelled', b'Cancelled'), (b'Transferred', b'Transferred'), (b'ordered', b'ordered'), (b'dispatched', b'dispatched'), (b'delivered', b'delivered'), (b'cancelled', b'cancelled'), (b'Closed', b'Closed'), (b'Buyer Cancelled', b'Buyer Cancelled')]),
        ),
    ]
