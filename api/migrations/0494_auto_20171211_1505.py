# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0493_companysellstostate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companysellstostate',
            name='state',
        ),
        migrations.AddField(
            model_name='companysellstostate',
            name='state',
            field=models.ForeignKey(default=1, to='api.State'),
            preserve_default=False,
        ),
    ]
