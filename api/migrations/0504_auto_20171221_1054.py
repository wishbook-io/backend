# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0503_userreview_language'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='catalogseller',
            unique_together=set([('catalog', 'selling_company', 'selling_type')]),
        ),
    ]
