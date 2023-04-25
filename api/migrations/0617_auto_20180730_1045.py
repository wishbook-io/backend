# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0616_auto_20180728_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companycreditaprovedline',
            name='approved_line',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='companycreditaprovedline',
            name='available_line',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='companycreditaprovedline',
            name='used_line',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='companycreditaprovedline',
            unique_together=set([('company', 'nbfc_partner')]),
        ),
    ]
