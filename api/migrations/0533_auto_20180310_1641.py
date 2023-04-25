# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0532_discountrule_discountrulebrand_discountrulebuyergroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discountrulebrand',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='discountrulebrand',
            name='discount_rule',
        ),
        migrations.RemoveField(
            model_name='discountrulebuyergroup',
            name='buyer_group',
        ),
        migrations.RemoveField(
            model_name='discountrulebuyergroup',
            name='discount_rule',
        ),
        migrations.AddField(
            model_name='discountrule',
            name='brands',
            field=models.ManyToManyField(to='api.Brand'),
        ),
        migrations.AddField(
            model_name='discountrule',
            name='buyer_segmentations',
            field=models.ManyToManyField(to='api.BuyerSegmentation'),
        ),
        migrations.DeleteModel(
            name='DiscountRuleBrand',
        ),
        migrations.DeleteModel(
            name='DiscountRuleBuyerGroup',
        ),
    ]
