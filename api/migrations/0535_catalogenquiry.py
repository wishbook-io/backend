# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0534_userprofile_send_sms_to_contacts'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogEnquiry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('enquiry_type', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Text', b'Text'), (b'Chat', b'Chat'), (b'Call', b'Call')])),
                ('status', models.CharField(default=b'Created', max_length=30, choices=[(b'Created', b'Created'), (b'Cancelled', b'Cancelled'), (b'Converted to Order', b'Converted to Order'), (b'Rejected', b'Rejected')])),
                ('text', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('item_type', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Sets', b'Sets'), (b'Pieces', b'Pieces')])),
                ('item_quantity', models.IntegerField(default=0)),
                ('buying_company', models.ForeignKey(related_name='ce_buying_companies', to='api.Company')),
                ('catalog', models.ForeignKey(to='api.Catalog')),
                ('selling_company', models.ForeignKey(related_name='ce_selling_companies', to='api.Company')),
            ],
        ),
    ]
