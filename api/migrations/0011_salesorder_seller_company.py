# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20151127_0522'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='seller_company',
            field=models.ForeignKey(related_name='seller_companies', default=34, to='api.Company'),
            preserve_default=False,
        ),
    ]
