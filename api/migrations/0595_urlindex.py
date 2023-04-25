# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0594_companycreditaprovedline'),
    ]

    operations = [
        migrations.CreateModel(
            name='URLIndex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('urlobject_id', models.IntegerField(default=0, null=True, blank=True)),
                ('urltype', models.CharField(default=b'Catalog', max_length=30, null=True, blank=True, choices=[(b'Catalog', b'Catalog')])),
                ('urlkey', models.CharField(unique=True, max_length=250)),
            ],
        ),
    ]
