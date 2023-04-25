# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0171_promotionalnotification_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='broker_company',
            field=models.ForeignKey(related_name='broker_companies', default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='broker_company',
            field=models.ForeignKey(related_name='broker_company', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
