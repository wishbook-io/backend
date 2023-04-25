# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0422_promotion_show_on_webapp'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaidClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
    ]
