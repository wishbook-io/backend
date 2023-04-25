# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0113_auto_20160322_1042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invite',
            options={},
        ),
        migrations.AlterModelOptions(
            name='invitee',
            options={},
        ),
        migrations.AlterModelOptions(
            name='push',
            options={},
        ),
        migrations.AlterModelOptions(
            name='push_user',
            options={},
        ),
        migrations.AlterModelOptions(
            name='push_user_product',
            options={},
        ),
        migrations.AddField(
            model_name='invitee',
            name='group_type',
            field=models.ForeignKey(default=2, to='api.GroupType'),
            preserve_default=False,
        ),
    ]
