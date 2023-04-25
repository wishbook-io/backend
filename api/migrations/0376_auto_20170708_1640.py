# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0375_auto_20170708_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyersalesmen',
            name='buyer',
            field=models.ForeignKey(related_name='salesmen_buyer', to='api.Company'),
        ),
    ]
