# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0305_auto_20170320_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('total_qty', models.IntegerField(default=0)),
                ('amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('paid_amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('pending_amount', models.DecimalField(max_digits=19, decimal_places=2)),
                ('payment_status', models.CharField(max_length=20, choices=[(b'Pending', b'Pending'), (b'Paid', b'Paid'), (b'Cancelled', b'Cancelled')])),
                ('order', models.ForeignKey(to='api.SalesOrder')),
            ],
        ),
    ]
