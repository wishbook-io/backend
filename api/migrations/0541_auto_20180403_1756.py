# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0540_auto_20180403_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyCreditRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('crif_score', models.PositiveIntegerField(null=True, blank=True)),
                ('bank_data_source', models.CharField(blank=True, max_length=50, null=True, choices=[(b'SMS', b'SMS'), (b'Bank Statement', b'Bank Statement')])),
                ('bank_statement_pdf', models.FileField(null=True, upload_to=b'bank_statement_pdf', blank=True)),
                ('bank_monthly_transaction_6m', models.PositiveIntegerField(null=True, blank=True)),
                ('bank_average_balance_6m', models.PositiveIntegerField(null=True, blank=True)),
                ('bank_check_bounces_6m', models.PositiveIntegerField(null=True, blank=True)),
                ('salary', models.PositiveIntegerField(null=True, blank=True)),
                ('gst_credit_rating', models.PositiveIntegerField(null=True, blank=True)),
                ('rating', models.CharField(default=b'Unrated', max_length=20, choices=[(b'Good', b'Good'), (b'Poor', b'Poor'), (b'Unrated', b'Unrated')])),
                ('company', models.OneToOneField(to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='CreditReference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_on_credit', models.BooleanField()),
                ('number_transactions', models.PositiveIntegerField(null=True, blank=True)),
                ('transaction_value', models.CharField(max_length=20, choices=[(b'Less_1L', b'Less_1L'), (b'1L_5L', b'1L_5L'), (b'More_5L', b'More_5L')])),
                ('average_payment_duration', models.CharField(max_length=20, choices=[(b'Less_30days', b'Less_30days'), (b'30_60days', b'30_60days'), (b'60_90days', b'60_90days'), (b'More_90days', b'More_90days')])),
                ('average_gr_rate', models.CharField(max_length=20, choices=[(b'Less_5', b'Less_5'), (b'5_10', b'5_10'), (b'10_20', b'10_20'), (b'More_20', b'More_20')])),
                ('remarks', models.TextField(null=True, blank=True)),
                ('buying_company', models.ForeignKey(related_name='buying_companies_cr', to='api.Company')),
                ('selling_company', models.ForeignKey(related_name='selling_companies_cr', to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='SolePropreitorshipKYC',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('proprietor', models.CharField(max_length=250)),
                ('company', models.OneToOneField(to='api.Company')),
            ],
        ),
        migrations.AddField(
            model_name='companykyctaxation',
            name='company_type',
            field=models.CharField(default=None, max_length=50, null=True, blank=True, choices=[(b'Sole Propreitorship', b'Sole Propreitorship'), (b'Partnership', b'Partnership'), (b'LLP', b'LLP'), (b'Private Limited', b'Private Limited'), (b'Public Limited', b'Public Limited')]),
        ),
        migrations.AddField(
            model_name='companykyctaxation',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
