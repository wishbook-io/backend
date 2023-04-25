# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0370_company_salesman_mapping'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyerSalesmen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('buyer', models.ForeignKey(to='api.Company')),
                ('salesman', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SalesmanLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city', models.ForeignKey(blank=True, to='api.City', null=True)),
                ('salesman', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('state', models.ForeignKey(blank=True, to='api.State', null=True)),
            ],
        ),
    ]
