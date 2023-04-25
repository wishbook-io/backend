# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eav', '__first__'),
        ('api', '0121_auto_20160415_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryEavAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attribute', models.ManyToManyField(to='eav.Attribute')),
                ('category', models.ForeignKey(to='api.Category')),
            ],
        ),
        migrations.AlterModelOptions(
            name='buyer',
            options={},
        ),
    ]
