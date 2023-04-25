# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0530_predefinedfilter_sort_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('-sort_order',)},
        ),
        migrations.AddField(
            model_name='promotionalnotification',
            name='company_type_not_selected',
            field=models.BooleanField(default=False),
        ),
    ]
