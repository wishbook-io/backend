# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0481_auto_20171121_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrating',
            name='buyer_remark',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=107, null=True, choices=[(b'Buyer did not receive the goods', b'Buyer did not receive the goods'), (b'Buyer did not pay in promised period', b'Buyer did not pay in promised period'), (b'Issues with Wishbook application', b'Issues with Wishbook application'), (b'Other', b'Other')]),
        ),
        migrations.AlterField(
            model_name='orderrating',
            name='seller_remark',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=110, null=True, choices=[(b'Delivered product were not as described', b'Delivered product were not as described'), (b'Delivery took more time then mentioned', b'Delivery took more time then mentioned'), (b'Technical/Software issues', b'Technical/Software issues'), (b'Other', b'Other')]),
        ),
    ]
