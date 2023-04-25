# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0542_auto_20180403_1922'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solepropreitorshipkyc',
            old_name='proprietor',
            new_name='full_name',
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='average_gr_rate',
            field=models.CharField(default='Less than 5%', max_length=20, choices=[(b'Less than 5%', b'Less than 5%'), (b'5% to 10%', b'5% to 10%'), (b'10% to 20%', b'10% to 20%'), (b'More than 20%', b'More than 20%')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='average_payment_duration',
            field=models.CharField(default='Less than 30 days', max_length=20, choices=[(b'Less than 30 days', b'Less than 30 days'), (b'30 to 60 days', b'30 to 60 days'), (b'60 to 90 days', b'60 to 90 days'), (b'More than 90 days', b'More than 90 days')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='aadhar_card',
            field=models.CharField(default=0, max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='address',
            field=models.TextField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='birth_date',
            field=models.DateField(default=datetime.datetime(2018, 4, 4, 5, 53, 8, 746368, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='city',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='email',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='father_name',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='gender',
            field=models.CharField(default='Male', max_length=20, choices=[(b'Male', b'Male'), (b'Female', b'Female'), (b'Transgender', b'Transgender')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='mobile_no',
            field=models.CharField(default=0, max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='pan_card',
            field=models.CharField(default=0, max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='pincode',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='spouse_name',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='solepropreitorshipkyc',
            name='state',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='creditreference',
            name='average_gr_rate',
            field=models.CharField(max_length=20, choices=[(b'Less than 5%', b'Less than 5%'), (b'5% to 10%', b'5% to 10%'), (b'10% to 20%', b'10% to 20%'), (b'More than 20%', b'More than 20%')]),
        ),
        migrations.AlterField(
            model_name='creditreference',
            name='average_payment_duration',
            field=models.CharField(max_length=20, choices=[(b'Less than 30 days', b'Less than 30 days'), (b'30 to 60 days', b'30 to 60 days'), (b'60 to 90 days', b'60 to 90 days'), (b'More than 90 days', b'More than 90 days')]),
        ),
        migrations.AlterField(
            model_name='creditreference',
            name='transaction_value',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Less than 1 Lakh', b'Less than 1 Lakh'), (b'1 Lakh to 5 Lakh', b'1 Lakh to 5 Lakh'), (b'5 Lakh to 10 Lakh', b'5 Lakh to 10 Lakh'), (b'More than 10 Lakh', b'More than 10 Lakh')]),
        ),
    ]
