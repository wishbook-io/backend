# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0426_auto_20170823_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrating',
            name='buyer_remark',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=38, null=True, choices=[(b'Issues with Wishbook Application', b'Issues with Wishbook Application'), (b'Other', b'Other')]),
        ),
        migrations.AlterField(
            model_name='orderrating',
            name='seller_remark',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=117, null=True, choices=[(b'Delivered product were not as described', b'Delivered product were not as described'), (b'Delivery took more time then mentioned', b'Delivery took more time then mentioned'), (b'Issues with Wishbook Application', b'Issues with Wishbook Application'), (b'Other', b'Other')]),
        ),
    ]
