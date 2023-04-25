# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0439_auto_20170921_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='buying_company_name',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='buyer',
            name='buying_person_name',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='name_updated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='buying_company_name',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
