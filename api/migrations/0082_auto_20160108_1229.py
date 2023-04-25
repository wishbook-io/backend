# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0081_historicalimagetest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalimagetest',
            name='history_user',
        ),
        migrations.AddField(
            model_name='imagetest',
            name='deleted',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='HistoricalImageTest',
        ),
    ]
