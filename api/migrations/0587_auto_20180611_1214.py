# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0586_auto_20180608_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='source_type',
            field=models.CharField(default=b'Marketplace', max_length=50, choices=[(b'Saas', b'Saas'), (b'Marketplace', b'Marketplace')]),
        ),
        migrations.AddField(
            model_name='salesorderauditlogentry',
            name='source_type',
            field=models.CharField(default=b'Marketplace', max_length=50, choices=[(b'Saas', b'Saas'), (b'Marketplace', b'Marketplace')]),
        ),
    ]
