# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0608_marketing_login_url_in_sms'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 31, 782330, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 34, 188093, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brand',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 36, 134479, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='brand',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 38, 46614, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='branddistributor',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 39, 779440, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='branddistributor',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 41, 349835, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cataloguploadoption',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 43, 78032, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cataloguploadoption',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 45, 699018, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 47, 525732, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 49, 204642, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='categoryeavattribute',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 51, 83522, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='categoryeavattribute',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 53, 515714, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 55, 172867, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 56, 941071, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companybrandfollow',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 16, 59, 586176, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companybrandfollow',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 1, 508099, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companybuyergroup',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 4, 481939, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companybuyergroup',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 6, 380526, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companynumber',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 8, 378417, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companynumber',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 10, 210345, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companyphonealias',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 12, 282760, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companyphonealias',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 13, 915642, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companytype',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 15, 601187, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companytype',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 17, 185351, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companyuser',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 19, 147035, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companyuser',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 21, 122156, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 22, 881083, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 24, 624877, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 26, 472774, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unregisteredphonealias',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 28, 106138, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unregisteredphonealias',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 12, 7, 17, 29, 737142, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
