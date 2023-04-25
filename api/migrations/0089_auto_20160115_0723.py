# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0088_auto_20160115_0709'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyer',
            name='invitee',
            field=models.ForeignKey(related_name='invitee_id', default=None, blank=True, to='api.Invitee', null=True),
        ),
        migrations.AddField(
            model_name='buyer',
            name='supplier_status',
            field=models.CharField(default=b'pending', max_length=20, choices=[(b'registrationpending', b'Registration Pending'), (b'pending', b'Pending'), (b'approved', b'Approved'), (b'rejected', b'Rejected')]),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='buying_company',
            field=models.ForeignKey(related_name='buying_companies', default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='selling_company',
            field=models.ForeignKey(related_name='selling_companies', default=None, blank=True, to='api.Company', null=True),
        ),
    ]
