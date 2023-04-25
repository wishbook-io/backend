# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eav', '__first__'),
        ('api', '0129_auto_20160506_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryeavattribute',
            name='is_required',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name='categoryeavattribute',
            name='attribute',
        ),
        migrations.AddField(
            model_name='categoryeavattribute',
            name='attribute',
            field=models.ForeignKey(default=1, to='eav.Attribute'),
            preserve_default=False,
        ),
    ]
