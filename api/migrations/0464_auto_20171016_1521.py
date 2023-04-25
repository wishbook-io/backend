# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0463_auto_20171016_1022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('street_address', models.CharField(max_length=500, null=True, blank=True)),
                ('pincode', models.IntegerField(null=True, blank=True)),
                ('city', models.ForeignKey(to='api.City')),
                ('country', models.ForeignKey(to='api.Country')),
                ('state', models.ForeignKey(to='api.State')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='catalog',
            name='default_product_weight',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='pincodezone',
            name='is_servicable',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='box_volumetric_dimension',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='branch',
            name='address',
            field=models.ForeignKey(default=None, blank=True, to='api.Address', null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.ForeignKey(default=None, blank=True, to='api.Address', null=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='ship_to',
            field=models.ForeignKey(default=None, blank=True, to='api.Address', null=True),
        ),
    ]
