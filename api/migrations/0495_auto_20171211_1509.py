# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0494_auto_20171211_1505'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companysellstostate',
            unique_together=set([('company', 'intermediate_buyer', 'state')]),
        ),
    ]
