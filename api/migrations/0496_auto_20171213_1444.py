# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0495_auto_20171211_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrating',
            name='buyer_remark',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=104, null=True, choices=[(b'Buyer declined to receive the goods', b'Buyer declined to receive the goods'), (b'Buyer did not pay in promised period', b'Buyer did not pay in promised period'), (b'Technical/Software issues', b'Technical/Software issues'), (b'Other', b'Other')]),
        ),
    ]
