# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0523_auto_20180201_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvancedProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('est_year', models.IntegerField(default=None, null=True, blank=True)),
                ('shop_ownership', models.CharField(default=b'Owned', max_length=20, choices=[(b'Owned', b'Owned'), (b'Rented', b'Rented')])),
                ('product_min_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
                ('product_max_price', models.DecimalField(default=None, null=True, max_digits=19, decimal_places=2, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='market_name',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='address',
            name='shop_number',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='buyer',
            name='refer_userinvitation_id',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='landline_numbers',
            field=models.CharField(default=None, max_length=13, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='refer_id',
            field=models.PositiveIntegerField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='language',
            field=models.ForeignKey(default=2, blank=True, to='api.Language', null=True),
        ),
        migrations.AddField(
            model_name='advancedprofile',
            name='company',
            field=models.OneToOneField(related_name='advancedcompanyprofile', to='api.Company'),
        ),
    ]
