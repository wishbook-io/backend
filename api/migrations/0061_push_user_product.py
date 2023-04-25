# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0060_auto_20151226_0715'),
    ]

    operations = [
        migrations.CreateModel(
            name='Push_User_Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(max_digits=19, decimal_places=2)),
                ('is_viewed', models.CharField(default=b'no', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')])),
                ('catalog', models.ForeignKey(related_name='pup_catalog', default=None, to='api.Catalog')),
                ('product', models.ForeignKey(related_name='pup_product', to='api.Product')),
                ('push', models.ForeignKey(to='api.Push')),
                ('selection', models.ForeignKey(related_name='pup_selection', default=None, to='api.Selection')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('push',),
            },
        ),
    ]
