# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0254_credit_invoicecredit'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoicePayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.PositiveIntegerField()),
                ('invoice', models.ForeignKey(to='api.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('instrument', models.CharField(max_length=200)),
                ('date', models.DateField()),
                ('amount', models.PositiveIntegerField()),
                ('detail', models.CharField(max_length=200)),
                ('company', models.ForeignKey(to='api.Company')),
            ],
        ),
        migrations.AddField(
            model_name='invoicepayment',
            name='payment',
            field=models.ForeignKey(to='api.Payment'),
        ),
    ]
