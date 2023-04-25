# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0124_userprofile_tnc_agreed'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='connections_preapproved',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='company',
            name='discovery_ok',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='company',
            name='have_salesmen',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='company',
            name='no_suppliers',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='company',
            name='sell_all_received_catalogs',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='company',
            name='sell_shared_catalogs',
            field=models.BooleanField(default=True),
        ),
    ]
