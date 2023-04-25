# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0438_companybrandfollow'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='companybrandfollow',
            unique_together=set([('brand', 'company', 'user')]),
        ),
    ]
