# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('street_address', models.CharField(max_length=40)),
                ('pincode', models.IntegerField(validators=[django.core.validators.RegexValidator(regex=b'^\\d{6}$', message=b'Invalid pincode!')])),
                ('phone_number', models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('company',),
            },
        ),
        migrations.CreateModel(
            name='BrandDistributor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('brand', models.ForeignKey(to='api.Brand')),
            ],
        ),
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'approved', b'Approved')])),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='BuyerSegmentation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('segmentation_name', models.CharField(max_length=50)),
                ('last_generated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=20)),
                ('thumbnail', models.ImageField(null=True, upload_to=b'catalog_image', blank=True)),
                ('view_permission', models.CharField(default=b'public', max_length=20, choices=[(b'public', b'Public'), (b'push', b'Push')])),
                ('brand', models.ForeignKey(to='api.Brand')),
            ],
            options={
                'ordering': ('brand',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category_name', models.CharField(max_length=30)),
                ('parent_category', models.ForeignKey(related_name='child_category', blank=True, to='api.Category', null=True)),
            ],
            options={
                'ordering': ('category_name',),
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ChannelType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('credential_format', models.CharField(max_length=20)),
                ('file_format', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('user', models.ForeignKey(related_name='choices', to=settings.AUTH_USER_MODEL)),
                ('userlist', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city_name', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('city_name',),
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('push_downstream', models.CharField(max_length=10, choices=[(b'yes', b'Yes'), (b'no', b'No')])),
                ('street_address', models.CharField(max_length=40)),
                ('pincode', models.IntegerField(validators=[django.core.validators.RegexValidator(regex=b'^\\d{6}$', message=b'Invalid pincode!')])),
                ('phone_number', models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
                ('website', models.URLField(null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('status', models.CharField(default=b'okay', max_length=20, choices=[(b'okay', b'Okay'), (b'overdue', b'Overdue'), (b'terminated', b'Terminated')])),
                ('thumbnail', models.ImageField(null=True, upload_to=b'company_image', blank=True)),
                ('category', models.ManyToManyField(to='api.Category')),
                ('city', models.ForeignKey(to='api.City')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CompanyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.ForeignKey(related_name='company_users', to='api.Company')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('time', models.DateTimeField()),
                ('channel', models.ForeignKey(to='api.Channel')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Export_Catalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('catalog', models.ForeignKey(to='api.Catalog')),
                ('export', models.ForeignKey(to='api.Export')),
            ],
            options={
                'ordering': ('export_id',),
            },
        ),
        migrations.CreateModel(
            name='Export_Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('export', models.ForeignKey(to='api.Export')),
            ],
            options={
                'ordering': ('export_id',),
            },
        ),
        migrations.CreateModel(
            name='Export_Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_path', models.CharField(max_length=20)),
                ('export', models.ForeignKey(to='api.Export')),
            ],
            options={
                'ordering': ('export',),
            },
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relationship_type', models.CharField(default=b'None', max_length=20, choices=[(b'buyer', b'Buyer'), (b'salesperson', b'Salesperson'), (b'administrator', b'Administrator')])),
                ('date', models.DateField(auto_now=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(to='api.Company')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Invitee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invitee_number', models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
                ('invitee_company', models.CharField(max_length=40)),
                ('invitee_name', models.CharField(max_length=20)),
                ('status', models.CharField(default=b'invited', max_length=20, choices=[(b'invited', b'Invited'), (b'registered', b'Registered')])),
                ('invite_type', models.CharField(default=b'userinvitation', max_length=20, choices=[(b'userinvitation', b'User Invitation'), (b'directinvitation', b'Direct Invitation'), (b'selfservicecheckin', b'Self Service Check-In')])),
                ('invite', models.ForeignKey(default=None, blank=True, to='api.Invite', null=True)),
                ('registered_user', models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('invitee_number',),
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charges_amount', models.PositiveIntegerField(null=True, blank=True)),
                ('credit_amount', models.PositiveIntegerField(null=True, blank=True)),
                ('net_value', models.PositiveIntegerField(null=True, blank=True)),
                ('payment_status', models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'paid', b'Paid')])),
                ('payment_datetime', models.DateTimeField(null=True, blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('company', models.ForeignKey(related_name='invoice_company', to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credit_amount', models.PositiveIntegerField()),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('expire_date', models.DateField()),
                ('company', models.ForeignKey(related_name='invoice_credit_company', to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField(null=True, blank=True)),
                ('duration', models.DurationField(null=True, blank=True)),
                ('start_lat', models.FloatField()),
                ('start_long', models.FloatField()),
                ('end_lat', models.FloatField(null=True, blank=True)),
                ('end_long', models.FloatField(null=True, blank=True)),
                ('status', models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'done', b'Done')])),
                ('buying_company_ref', models.ForeignKey(related_name='meeting_buying_company', to='api.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(max_length=160)),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('subject', models.CharField(max_length=20)),
                ('mtype', models.CharField(blank=True, max_length=20, choices=[(b'Type1', b'Type1'), (b'Type2', b'Type2'), (b'Type3', b'Type3'), (b'Type4', b'Type4')])),
                ('status', models.CharField(default=b'unread', max_length=20, choices=[(b'read', b'Read'), (b'unread', b'Unread')])),
                ('receiver_user', models.ForeignKey(related_name='receiver_set', to=settings.AUTH_USER_MODEL)),
                ('sender_user', models.ForeignKey(related_name='sender_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('datetime',),
            },
        ),
        migrations.CreateModel(
            name='MessageFolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('folder', models.CharField(default=b'', max_length=20, choices=[(b'inbox', b'Inbox'), (b'sent', b'Sent'), (b'trash', b'Trash'), (b'drafts', b'Drafts')])),
                ('message', models.ForeignKey(related_name='message_folder_set', to='api.Message')),
            ],
            options={
                'ordering': ('folder',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('sku', models.CharField(unique=True, max_length=20)),
                ('fabric', models.CharField(max_length=20, null=True, blank=True)),
                ('work', models.CharField(max_length=20, null=True, blank=True)),
                ('price', models.DecimalField(max_digits=19, decimal_places=2)),
                ('image_small', models.ImageField(null=True, upload_to=b'product_image', blank=True)),
                ('catalog', models.ManyToManyField(related_name='products', to='api.Catalog')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Push',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('push_type', models.CharField(default=b'buyers', max_length=20, choices=[(b'buyers', b'Buyers'), (b'discovery', b'Discovery')])),
                ('push_downstream', models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')])),
                ('status', models.CharField(default=b'delivered', max_length=20, choices=[(b'schedule', b'Schedule'), (b'delivered', b'Delivered'), (b'pending', b'Pending')])),
                ('message', models.TextField(null=True, blank=True)),
                ('buyer_segmentation', models.ForeignKey(related_name='push_buyer_segmentation', to='api.BuyerSegmentation')),
                ('company', models.ForeignKey(to='api.Company')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Push_Catalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('catalog', models.ForeignKey(related_name='push_catalog_id', default=None, to='api.Catalog')),
                ('push', models.ForeignKey(related_name='push_catalog', default=None, to='api.Push')),
            ],
            options={
                'ordering': ('push',),
            },
        ),
        migrations.CreateModel(
            name='Push_Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product', models.ForeignKey(related_name='push_product_id', default=None, to='api.Product')),
                ('push', models.ForeignKey(to='api.Push')),
            ],
            options={
                'ordering': ('push',),
            },
        ),
        migrations.CreateModel(
            name='Push_Selection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('push', models.ForeignKey(related_name='push_selection', default=None, to='api.Push')),
            ],
            options={
                'ordering': ('push',),
            },
        ),
        migrations.CreateModel(
            name='Push_User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_viewed', models.CharField(default=b'no', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')])),
                ('push', models.ForeignKey(related_name='push_users', default=None, to='api.Push')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.CharField(max_length=20)),
                ('date', models.DateField(auto_now=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('processing_status', models.CharField(max_length=20, null=True, choices=[(b'ordered', b'Ordered'), (b'dispatched', b'Dispatched'), (b'delivered', b'Delivered'), (b'canceled', b'Canceled')])),
                ('customer_status', models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'finalize', b'Finalize')])),
                ('screenshot', models.ImageField(null=True, upload_to=b'images', blank=True)),
                ('company', models.ForeignKey(to='api.Company')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='SalesOrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('rate', models.DecimalField(null=True, max_digits=19, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('product', models.ForeignKey(to='api.Product')),
                ('sales_order', models.ForeignKey(related_name='items', default=None, to='api.SalesOrder')),
            ],
        ),
        migrations.CreateModel(
            name='Selection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('thumbnail', models.ImageField(null=True, upload_to=b'selection_image', blank=True)),
                ('products', models.ManyToManyField(to='api.Product')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state_name', models.CharField(unique=True, max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='UserNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
                ('user', models.ForeignKey(related_name='phone_nos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user',),
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alternate_email', models.EmailField(max_length=254, blank=True)),
                ('phone_number', models.CharField(max_length=13, validators=[django.core.validators.RegexValidator(regex=b'^\\+\\d{12,15}$', message=b"Phone number must be entered in the format. Eg: '+915432112345'.")])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='push_selection',
            name='selection',
            field=models.ForeignKey(related_name='push_selection_id', default=None, to='api.Selection'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='salesorder',
            field=models.ManyToManyField(related_name='meeting', to='api.SalesOrder', blank=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='invoice',
            name='push',
            field=models.ManyToManyField(to='api.Push'),
        ),
        migrations.AddField(
            model_name='export_product',
            name='product',
            field=models.ForeignKey(to='api.Product'),
        ),
        migrations.AddField(
            model_name='company',
            name='state',
            field=models.ForeignKey(to='api.State'),
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(related_name='state_city', to='api.State'),
        ),
        migrations.AddField(
            model_name='channel',
            name='channel_type',
            field=models.ForeignKey(to='api.ChannelType'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='category',
            field=models.ForeignKey(to='api.Category'),
        ),
        migrations.AddField(
            model_name='catalog',
            name='company',
            field=models.ForeignKey(to='api.Company'),
        ),
        migrations.AddField(
            model_name='buyersegmentation',
            name='category',
            field=models.ManyToManyField(to='api.Category'),
        ),
        migrations.AddField(
            model_name='buyersegmentation',
            name='city',
            field=models.ManyToManyField(to='api.City'),
        ),
        migrations.AddField(
            model_name='buyersegmentation',
            name='company',
            field=models.ForeignKey(to='api.Company'),
        ),
        migrations.AddField(
            model_name='buyer',
            name='buying_company',
            field=models.ForeignKey(related_name='buying_companies', to='api.Company'),
        ),
        migrations.AddField(
            model_name='buyer',
            name='selling_company',
            field=models.ForeignKey(related_name='selling_companies', to='api.Company'),
        ),
        migrations.AddField(
            model_name='branddistributor',
            name='company',
            field=models.ForeignKey(to='api.Company'),
        ),
        migrations.AddField(
            model_name='brand',
            name='company',
            field=models.ForeignKey(to='api.Company'),
        ),
        migrations.AddField(
            model_name='branch',
            name='city',
            field=models.ForeignKey(to='api.City'),
        ),
        migrations.AddField(
            model_name='branch',
            name='company',
            field=models.ForeignKey(to='api.Company'),
        ),
        migrations.AddField(
            model_name='branch',
            name='state',
            field=models.ForeignKey(to='api.State'),
        ),
        migrations.AlterUniqueTogether(
            name='usernumber',
            unique_together=set([('user', 'phone_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='salesorderitem',
            unique_together=set([('sales_order', 'product')]),
        ),
        migrations.AlterUniqueTogether(
            name='companyuser',
            unique_together=set([('user', 'company')]),
        ),
        migrations.AlterUniqueTogether(
            name='city',
            unique_together=set([('state', 'city_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='choice',
            unique_together=set([('user', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('category_name', 'parent_category')]),
        ),
        migrations.AlterUniqueTogether(
            name='buyer',
            unique_together=set([('selling_company', 'buying_company')]),
        ),
        migrations.AlterUniqueTogether(
            name='branddistributor',
            unique_together=set([('brand', 'company')]),
        ),
        migrations.AlterUniqueTogether(
            name='brand',
            unique_together=set([('name', 'company')]),
        ),
        migrations.AlterUniqueTogether(
            name='branch',
            unique_together=set([('company', 'name')]),
        ),
    ]
