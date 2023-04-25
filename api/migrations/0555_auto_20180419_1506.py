# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0554_salesorderinternal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='aadhar_card',
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='address',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='birth_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='city',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='email',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='full_name',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='gender',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'Male', b'Male'), (b'Female', b'Female'), (b'Transgender', b'Transgender')]),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='mobile_no',
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='pan_card',
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='pincode',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='solepropreitorshipkyc',
            name='state',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
