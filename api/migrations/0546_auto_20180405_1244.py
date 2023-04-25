# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0545_discountrule_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companycreditrating',
            name='rating',
            field=models.CharField(default=b'Unrated', max_length=20, choices=[(b'Good', b'Good'), (b'Unrated', b'Unrated'), (b'Poor', b'Poor')]),
        ),
    ]
