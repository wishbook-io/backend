# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0227_unsubcribednumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnsubscribedNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=13)),
                ('country', models.ForeignKey(to='api.Country')),
            ],
        ),
        migrations.RemoveField(
            model_name='unsubcribednumber',
            name='country',
        ),
        migrations.DeleteModel(
            name='UnsubcribedNumber',
        ),
    ]
