# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0158_auto_20160524_1745'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manufacturer', models.BooleanField(default=False)),
                ('distributor', models.BooleanField(default=False)),
                ('wholesaler', models.BooleanField(default=False)),
                ('semi_wholesaler', models.BooleanField(default=False)),
                ('retailer', models.BooleanField(default=False)),
                ('online_retailer', models.BooleanField(default=False)),
                ('resellers', models.BooleanField(default=False)),
                ('agents', models.BooleanField(default=False)),
                ('company', models.OneToOneField(related_name='company_group_flag', to='api.Company')),
            ],
        ),
        migrations.RemoveField(
            model_name='companygroupflag',
            name='company',
        ),
        migrations.DeleteModel(
            name='CompanyGroupFlag',
        ),
    ]
