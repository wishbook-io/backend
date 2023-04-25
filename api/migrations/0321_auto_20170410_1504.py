# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0320_auto_20170408_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='buying_company_ref',
            field=models.ForeignKey(related_name='meeting_buying_company', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
