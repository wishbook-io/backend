# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0541_auto_20180403_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companycreditrating',
            name='rating',
            field=models.CharField(default=b'Unrated', max_length=20, choices=[(b'Good', b'Good'), (b'Unrated', b'Unrated')]),
        ),
        migrations.AlterUniqueTogether(
            name='creditreference',
            unique_together=set([('selling_company', 'buying_company')]),
        ),
    ]
