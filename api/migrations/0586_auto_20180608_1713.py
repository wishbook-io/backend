# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0585_auto_20180604_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCreditSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bureau_score', models.PositiveIntegerField(null=True, blank=True)),
                ('bank_data_source', models.CharField(blank=True, max_length=50, null=True, choices=[(b'SMS', b'SMS'), (b'Bank Statement', b'Bank Statement')])),
                ('bank_statement_pdf', models.FileField(null=True, upload_to=b'bank_statement_pdf', blank=True)),
                ('bank_monthly_transaction_6m', models.PositiveIntegerField(null=True, blank=True)),
                ('bank_average_balance_6m', models.PositiveIntegerField(null=True, blank=True)),
                ('bank_check_bounces_6m', models.PositiveIntegerField(null=True, blank=True)),
                ('salary', models.PositiveIntegerField(null=True, blank=True)),
                ('gst_credit_rating', models.PositiveIntegerField(null=True, blank=True)),
                ('average_payment_duration', models.CharField(max_length=20, choices=[(b'Less than 30 days', b'Less than 30 days'), (b'30 to 60 days', b'30 to 60 days'), (b'60 to 90 days', b'60 to 90 days'), (b'More than 90 days', b'More than 90 days')])),
                ('average_gr_rate', models.CharField(max_length=20, choices=[(b'Less than 5%', b'Less than 5%'), (b'5% to 10%', b'5% to 10%'), (b'10% to 20%', b'10% to 20%'), (b'More than 20%', b'More than 20%')])),
                ('rating', models.CharField(default=b'Unrated', max_length=20, choices=[(b'Good', b'Good'), (b'Unrated', b'Unrated'), (b'Poor', b'Poor')])),
                ('bureau_report_rating', models.CharField(max_length=20, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative'), (b'Unavailable', b'Unavailable')])),
                ('financial_statement_rating', models.CharField(max_length=20, choices=[(b'Positive', b'Positive'), (b'Negative', b'Negative'), (b'Unavailable', b'Unavailable')])),
                ('bureau_type', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Crif', b'Crif')])),
                ('bureau_status', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Verification Failed', b'Verification Failed'), (b'Verification But Miss', b'Verification But Miss'), (b'Hit', b'Hit')])),
                ('bureau_xml', models.TextField(null=True, blank=True)),
                ('bureau_order_id', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('bureau_report_id', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(to='api.Company')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='companycreditrating',
            old_name='crif_score',
            new_name='bureau_score',
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='bureau_order_id',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='bureau_report_id',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='bureau_status',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Verification Failed', b'Verification Failed'), (b'Verification But Miss', b'Verification But Miss'), (b'Hit', b'Hit')]),
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='bureau_type',
            field=models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Crif', b'Crif')]),
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='bureau_xml',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 8, 11, 43, 36, 674710, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companycreditrating',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 8, 11, 43, 42, 112147, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='sugar_crm_user_id',
            field=models.CharField(default=None, max_length=250, null=True, blank=True),
        ),
    ]
