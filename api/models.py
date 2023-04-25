from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator, MinValueValidator
from decimal import *
from push_notifications.models import GCMDevice ,APNSDevice

from django.db.models.signals import post_save, pre_delete, post_delete, m2m_changed

#from api.models import *
from django.db.models import Q

from django.conf import settings

from django.db.models import Sum
#import os
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from versatileimagefield.fields import VersatileImageField, PPOIField
from versatileimagefield.placeholder import OnStoragePlaceholderImage
#from versatileimagefield.placeholder import OnDiscPlaceholderImage

from decimal import Decimal

##from simple_history.models import HistoricalRecords

#from sorl.thumbnail import get_thumbnail
#from django.core.files.base import ContentFile

'''from imagekit.models import ImageSpecField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill'''
#import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

import eav
from eav.models import *



from datetime import datetime, date, time, timedelta
from django.db.models import Sum, Min, Max, Count

import re

from django.dispatch import receiver
from multiselectfield import MultiSelectField

from django.db.models import Value
from django.db.models.functions import Concat

import random

from django_q.brokers import get_broker
# set up a broker instance for better performance
priority_broker = get_broker('priority')

from django.db.models import ProtectedError
from django.http import JsonResponse



from audit_log.models.fields import CreatingUserField, CreatingSessionKeyField, LastUserField
from audit_log.models.managers import AuditLog

from django.core.cache import cache


from api.common_functions import *
from api.search import CatalogIndex
from api.v1.sugar_crm import user_to_crm,company_to_crm_q,enquiry_to_crm_q
from api.cache_functions import *

#import Notification models
from api.notification.notification_models import *
#from api.models_functions import *

# Define the choices
SALES_ORDER_PROCESSING_STATUS = ( ('Cart','Cart'), ('Draft','Draft'), ('COD Verification Pending','COD Verification Pending'), ('Field Verification Pending','Field Verification Pending'), ('Pending','Pending'), ('Accepted', 'Accepted'), ('In Progress', 'In Progress'), ('Dispatched','Dispatched'), ('Partially Dispatched','Partially Dispatched'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Transferred', 'Transferred'), ('ordered','ordered'), ('dispatched','dispatched'), ('delivered', 'delivered'), ('cancelled', 'cancelled'), ('Closed', 'Closed'), ('Buyer Cancelled', 'Buyer Cancelled'))#('notfinalized','Not Finalized')
SALES_ORDER_CUSTOMER_STATUS = (('Pending','Pending'), ('Draft','Draft'), ('Placed','Placed'), ('Paid','Paid'), ('Payment Confirmed','Payment Confirmed'), ('Cancelled','Cancelled'), ('pending','pending'), ('finalized', 'finalized'))
RELATIONSHIP_TYPE = (('buyer','Buyer'), ('supplier','Supplier'), ('salesperson', 'Salesperson'), ('administrator', 'Administrator'))
YES_OR_NO = (('yes','Yes'), ('no', 'No'))
MESSAGE_TYPE = (('Type1','Type1'), ('Type2', 'Type2'), ('Type3','Type3'), ('Type4', 'Type4'))
MESSAGE_FOLDER = (('inbox','Inbox'), ('sent', 'Sent'), ('trash', 'Trash'), ('drafts', 'Drafts'))
MEETING_STATUS = (('pending','Pending'), ('done', 'Done'))
MESSAGE_STATUS = (('read','Read'), ('unread', 'Unread'))
SALES_PERSON_STATUS = (('inservice','In Service'), ('outofservice', 'Out Of Service'))
PUSH_STATUS = (('Schedule','Schedule'), ('Delivered', 'Delivered'), ('Pending', 'Pending'), ('In Progress', 'In Progress'))
INVOICE_STATUS = (('pending', 'Pending'), ('paid','Paid'))
PUSH_TYPE = (('buyers', 'Buyers'), ('discovery','Discovery'))
CATALOG_PERMISSION = (('public', 'Public'), ('push','Push'))
COMPANY_STATUS = (('okay', 'Okay'), ('overdue','Overdue'), ('terminated','Terminated'))
INVITE_TYPE = (('userinvitation','User Invitation'), ('directinvitation', 'Direct Invitation'), ('selfservicecheckin', 'Self Service Check-In'))
INVITE_STATUS = (('invited','Invited'), ('registered', 'Registered'))
BUYER_STATUS = (('buyer_registrationpending','Buyer Registration Pending'), ('supplier_registrationpending','Supplier Registration Pending'), ('buyer_pending','Buyer Pending'), ('supplier_pending','Supplier Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('Pending References', 'Pending References'), ('Transferred', 'Transferred'), ('References Filled', 'References Filled'))
COMPANY_TYPE = (('manufacturer','Manufacturer'), ('nonmanufacturer', 'Non Manufacturer'), ('retailer', 'Retailer'))
GROUP_TYPE = (('distributor','Distributor'), ('wholesaler', 'Wholesaler'), ('semi-wholesaler', 'Semi-Wholesaler'), ('retailer', 'Retailer'), ('online-retailer', 'Online Retailer'), ('other', 'Other'))
INVITATION_TYPE = (('Buyer','Buyer'), ('Supplier','Supplier'))
ALIAS_STATUS = (('Verification_Pending','Verification Pending'), ('Approved', 'Approved'))
ENABLE_DISABLE = (('Enable','Enable'), ('Disable','Disable'))
DISPATCH_STATUS = (('Dispatched','Dispatched'), ('Delivered', 'Delivered'), ('Canceled','Canceled'), ('Closed', 'Closed'))
ADJUSTMENT_QTY_STATUS = (('Add','Add'), ('Remove', 'Remove'), ('Transfer','Transfer'))
UPDATE_FOR = (('Android','Android'), ('IOS', 'IOS'))
ATTENDANCE_ACTION = (('Checkin','Checkin'), ('Checkout', 'Checkout'))
BUYER_TYPE = (('Relationship','Relationship'), ('Enquiry', 'Enquiry'))
PAYMENT_STATUS = (('Pending', 'Pending'), ('Partially Paid','Partially Paid'), ('Paid','Paid'), ('Cancelled','Cancelled'), ('Success','Success'), ('Failure','Failure'))
PAYMENT_MODE = (('NEFT', 'NEFT'), ('Cheque','Cheque'), ('PayTM','PayTM'), ('Mobikwik','Mobikwik'), ('Zaakpay','Zaakpay'), ('Other','Other'), ('Wishbook Credit','Wishbook Credit'), ('COD','COD'))
JOBS_STATUS = (('Created', 'Created'), ('Scheduled', 'Scheduled'), ('In Progress','In Progress'), ('Complete','Complete'), ('Complete With Errors','Complete With Errors'), ('Completed','Completed'), ('Completed With Errors','Completed With Errors'))
JOB_TYPE = (('Buyer', 'Buyer'), ('Supplier','Supplier'), ('Sales Order CSV','Sales Order CSV'), ('Shipment Sales Order CSV','Shipment Sales Order CSV'), ('SKU Map CSV', 'SKU Map CSV'), ('Company Map CSV', 'Company Map CSV'), ('Catalog CSV', 'Catalog CSV'),('Catalog Bulk CSV', 'Catalog Bulk CSV'), ('Product CSV', 'Product CSV'), ('Shipment Dispatch CSV', 'Shipment Dispatch CSV'))
LANDING_PAGE_TYPE = (('Tab', 'Tab'), ('Html','Html'), ('Webview','Webview'), ('support_chat','support_chat'), ('faq','faq'), ('deep_link','deep_link'))
SALESMAN_MAPPING = (('Location', 'Location'), ('Individual','Individual'))
BUYER_GROUPING_TYPE = (('Location Wise', 'Location Wise'), ('Custom','Custom'))
TAX_CODE_TYPE = (('HSN', 'HSN'), )
LOCATION_TYPE = (('Same State', 'Same State'), ('Inter State', 'Inter State'), ('UT', 'UT'))
ORDER_INVOICE_STATUS = (('Invoiced', 'Invoiced'), ('Dispatched','Dispatched'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'))
STATE_TYPE = (('STATE', 'STATE'), ('UT','UT'))
WB_COUPON = (('Percentage', 'Percentage'), ('Fixed','Fixed'))
RELEASE_INSTRUMENT = (('NEFT', 'NEFT'), )
SELLER_REMARK = (('Delivered product were not as described', 'Delivered product were not as described'), ('Delivery took more time then mentioned', 'Delivery took more time then mentioned'), ('Technical/Software issues', 'Technical/Software issues'), ('Other', 'Other'))
BUYER_REMARK = (('Buyer declined to receive the goods', 'Buyer declined to receive the goods'), ('Buyer did not pay in promised period', 'Buyer did not pay in promised period'), ('Technical/Software issues', 'Technical/Software issues'), ('Other', 'Other'))
ENQUIRY_ITEM_TYPE = (('Sets', 'Sets'), ('Pieces','Pieces'))
PACKING_TYPE = (('Box', 'Box'), ('Naked','Naked'))
LOGIN_PLATFORM = (('Lite', 'Lite'), ('Android','Android'), ('iOS', 'iOS'), ('Webapp','Webapp'))
LENDER_COMPANY = (('Capital Float', 'Capital Float'), )
LOAN_STATUS = (('Pending', 'Pending'), ('Processed','Processed'), ('Repaid', 'Repaid'), ('Canceled','Canceled'))
PAYMENT_METHOD_TYPE = (('Online', 'Online'), ('Offline','Offline'), ('Credit', 'Credit'), ('Cash on Delivery', 'Cash on Delivery'),('Credit Line', 'Credit Line'))
COMPANY_BUYER_GROUP_TYPE = (('Wholesaler', 'Wholesaler'), ('Retailer','Retailer'), ('Broker', 'Broker'), ('Public', 'Public'))
SHIPPING_PROVIDER = (('WB Provided', 'WB Provided'), ('Buyer Suggested','Buyer Suggested'))
CASHBACK_STATUS = (('Pending', 'Pending'), ('Paid','Paid'))
SHIPPING_STATUS = (('Pending', 'Pending'), ('Dispatched','Dispatched'), ('Delivered', 'Delivered'), ('Canceled','Canceled'))
CATALOG_TYPE = (('Public', 'Public'), ('Private','Private'))
APPROVAL_STATUS = (('Approved', 'Approved'), ('Pending','Pending'))
SHOP_OWNERSHIP = (('Owned', 'Owned'), ('Rented','Rented'))
APP_PLATFORM = (('Android', 'Android'), ('iOS','iOS'))
ENQUIRY_TYPE = (('Text', 'Text'), ('Chat','Chat'), ('Call','Call'))
CATALOG_ENQUIRY_STATUS = (('Created', 'Created'), ('Resolved', 'Resolved'))
MARKETING_TO = (('All', 'All'), ('Location','Location'), ('Specific Numbers','Specific Numbers'))
POLICY_TYPE = (('Return', 'Return'), ('Dispatch Duration','Dispatch Duration'))
COMPANY_KYC_TYPE = (('Sole Propreitorship', 'Sole Propreitorship'), ('Partnership','Partnership'), ('LLP','LLP'), ('Private Limited','Private Limited'), ('Public Limited','Public Limited'))
BANK_DATA_SOURCE = (('SMS', 'SMS'), ('Bank Statement','Bank Statement'))
CREDIT_RATING = (('Good', 'Good'), ('Unrated','Unrated'), ('Poor','Poor'))
TRANSACTION_VALUE = (('Less than 1 Lakh', 'Less than 1 Lakh'), ('1 Lakh to 5 Lakh','1 Lakh to 5 Lakh'), ('5 Lakh to 10 Lakh','5 Lakh to 10 Lakh'), ('More than 10 Lakh','More than 10 Lakh'))
AVERAGE_PAYMENT_DURATION = (('Less than 30 days', 'Less than 30 days'), ('30 to 60 days','30 to 60 days'), ('60 to 90 days','60 to 90 days'), ('More than 90 days','More than 90 days')) #for days
AVERAGE_GR_RATE = (('Less than 5%', 'Less than 5%'), ('5% to 10%','5% to 10%'), ('10% to 20%','10% to 20%'), ('More than 20%','More than 20%'))#in percentage
DURATION_OF_WORK = (('Less than 6 months', 'Less than 6 months'), ('6 months to 2 years','6 months to 2 years'), ('2 years to 5 years','2 years to 5 years'), ('More than 5 years','More than 5 years'))

KYC_GENDER = (('Male', 'Male'), ('Female','Female'), ('Transgender','Transgender'))
REPORT_RATING = (('Positive', 'Positive'), ('Negative','Negative'), ('Unavailable','Unavailable'))
TRANSACTION_TYPE = (('Sale Purchase', 'Sale Purchase'), ('Marketplace','Marketplace'))
SOURCE_TYPE = (('Saas', 'Saas'), ('Marketplace','Marketplace'))
CANCELLED_BY = (('Buyer', 'Buyer'), ('Seller','Seller'))
SELLER_CANCEL_REASON = (('Not In Stock', 'Not In Stock'), ('Credit','Credit'), ('Other','Other'))
ORDER_TYPE = (('Prepaid','Prepaid'), ('Credit','Credit'))
CART_CREATED_TYPE = (('Cart','Cart'), ('Order','Order'))
CART_STATUS = (('Created','Created'), ('Converted','Converted'))

BUREAU_TYPE = (('Crif','Crif'), )
BUREAU_STATUS = (('Verification Failed', 'Verification Failed'), ('Verification But Miss','Verification But Miss'), ('Hit','Hit'))
NBFC_PARTNER = (('Indifi','Indifi'),)
URLINDEX_CATALOG = (('Catalog', 'Catalog'),)
ACCOUNT_TYPE = (('Savings', 'Savings'), ('Current', 'Current'))
CATALOG_UPLOAD_TYPE = (('catalog', 'catalog'), ('noncatalog', 'noncatalog'))

# Define the validators
phone_regex = RegexValidator(regex=r'^\+\d{10,15}$', message="Phone number must be entered in the format. Eg: '+915432112345'.")
pincode_regex = RegexValidator(regex=r'^\d{6}$', message="Invalid pincode!")
#alphanumeric_ifsc = RegexValidator(r'^[0-9a-zA-Z]$', 'Only alphanumeric characters are allowed.')
#alphanumeric_ifsc = RegexValidator(regex=r'^[0-9a-zA-Z]$', message="Only alphanumeric characters are allowed.")

'''@receiver(post_save, sender=GCMDevice)
def gcmdevice_postsave(sender, instance, **kwargs):
	logger.info("in gcmdevice_postsave instance = %s"% (instance))
	GCMorAPNSpostsave(instance)

class GCMDeviceCustom(GCMDevice):
	def save(self, *args, **kwargs):
		logger.info("in GCMDeviceCustom self = %s"% (self))
		super(GCMDeviceCustom, self).save(*args, **kwargs)
		GCMorAPNSpostsave(self)
	class Meta:
		proxy=True

@receiver(post_save, sender=APNSDevice)
def apnsdevice_postsave(sender, instance, **kwargs):
	logger.info("in apnsdevice_postsave instance = %s"% (instance))
	GCMorAPNSpostsave(instance)'''



class SoftDeleteManager(models.Manager):
	''' Use this manager to get objects that have a deleted field '''
	def get(self, *args, **kwargs):
		#print "softdelete/////////get"
		''' if a specific record was requested, return it even if it's deleted '''
		#return self.all_with_deleted().get(*args, **kwargs)
		return self.get_queryset().get(*args, **kwargs)

	def filter(self, *args, **kwargs):
		#print "softdelete/////////filter"
		''' if pk was specified as a kwarg, return even if it's deleted '''
		#if 'pk' in kwargs:
		#	#return self.all_with_deleted().filter(*args, **kwargs)
		#	return self.get_queryset().filter(*args, **kwargs)
		return self.get_queryset().filter(*args, **kwargs)

	def get_queryset(self):
		#print "deleted=False"
		return super(SoftDeleteManager, self).get_queryset().filter(deleted=False)

	def all_with_deleted(self):
		#print "softdelete/////////all_with_deleted"
		return super(SoftDeleteManager, self).get_queryset()

	def deleted_set(self):
		#print "softdelete/////////deleted_set"
		return super(SoftDeleteManager, self).get_queryset().filter(deleted=True)


class UserCompanyDetail(User):
    class Meta:
        proxy=True

class Country(models.Model):
	name = models.CharField(max_length=20, unique=True)
	phone_code = models.CharField(max_length=20, unique=True)

	def save(self, *args, **kwargs):
		self.name = self.name.title()
		super(Country, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s' % (self.name)

class UserNumber(models.Model):
	user = models.ForeignKey(User, related_name='phone_nos')
	phone_number = models.CharField(validators=[phone_regex], max_length=13)

	def __unicode__(self):
		return self.phone_number
	class Meta:
		unique_together = ('user', 'phone_number',)
		#ordering = ('user',)

class Choice(models.Model):
	user = models.ForeignKey(User, related_name='choices')
	name = models.CharField(max_length = 20)
	userlist = models.ManyToManyField(User)

	def __unicode__(self):
		return str(self.name)

	class Meta:
		ordering = ('name',)
		unique_together = ('user', 'name')

class State(models.Model):
	state_name = models.CharField(max_length = 30, unique=True)
	state_type = models.CharField(choices=STATE_TYPE, default='STATE', max_length=10)

	def save(self, *args, **kwargs):
		self.state_name = self.state_name.title()
		super(State, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s' % (self.state_name)

class City(models.Model):
	state = models.ForeignKey(State, related_name='state_city')
	city_name = models.CharField(max_length = 30)

	def save(self, *args, **kwargs):
		self.city_name = self.city_name.title()
		super(City, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s' % (self.city_name)

	class Meta:
		ordering = ('city_name',)
		unique_together = ('state', 'city_name',)

class Category(models.Model):
	category_name = models.CharField(max_length = 30)
	parent_category = models.ForeignKey('self', blank=True, null=True, related_name='child_category')
	sort_order =  models.PositiveIntegerField(default=0)

	is_home_display = models.BooleanField(default=False)
	image = VersatileImageField(
		upload_to='category_images/',
		blank=True,
		placeholder_image=OnStoragePlaceholderImage(
			path='logo-single.png'
		)
	)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self.category_name = self.category_name.title()
		super(Category, self).save(*args, **kwargs)

	def __unicode__(self):
		'''parent_category = ""
		if self.parent_category:
			if self.parent_category.parent_category:
				return '%s <= %s <= %s' % (self.parent_category.parent_category.category_name, self.parent_category.category_name, self.category_name)
			else:
				return '%s <= %s' % (self.parent_category.category_name, self.category_name)
		else:
			return '%s' % (self.category_name)'''
		return '%s : %s' % (self.id, self.category_name)

	class Meta:
		ordering = ('-sort_order',)
		unique_together = ('category_name', 'parent_category',)

class CategoryEavAttribute(models.Model):
	category = models.ForeignKey(Category)
	attribute = models.ForeignKey(Attribute)
	is_required = models.BooleanField(default=False)
	filterable = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('category', 'attribute',)

	def __unicode__(self):
		return '%s' % (self.category.category_name)

'''
class MainCategory(models.Model):
	category_name = models.CharField(max_length = 30, unique=True)

	def __unicode__(self):
		return str(self.category_name)

	class Meta:
		ordering = ('category_name',)

class SubCategory(models.Model):
	main_category = models.ForeignKey(MainCategory)
	category_name = models.CharField(max_length = 30, unique=True)

	def __unicode__(self):
		return str(self.category_name)

	class Meta:
		ordering = ('category_name',)
'''
def allCategories():
	categories = Category.objects.all().values_list('id', flat=True)

	return categories

class Address(models.Model):
	name = models.CharField(max_length = 100, blank = True, null = True)
	city = models.ForeignKey(City)
	state = models.ForeignKey(State)
	street_address = models.CharField(max_length = 500, blank = True, null = True)
	pincode = models.IntegerField(blank = True, null = True)
	country = models.ForeignKey(Country, default=1)
	user = models.ForeignKey(User)

	latitude = models.DecimalField(max_digits=10, decimal_places=7, default=None, blank=True, null=True)
	longitude = models.DecimalField(max_digits=10, decimal_places=7, default=None, blank=True, null=True)

	location_address = models.TextField(default=None, blank = True, null = True)
	location_city = models.CharField(max_length=250, default=None, blank = True, null = True)
	location_state = models.CharField(max_length=250, default=None, blank = True, null = True)

	shop_number = models.CharField(max_length=250, default=None, blank = True, null = True)
	market_name = models.CharField(max_length=250, default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	'''def delete(self, *args, **kwargs):
		try:
			print "delete in"
			#self.delete()
			super(Address, self).delete(*args, **kwargs)
			print "delete after"
		except ProtectedError:
			return JsonResponse({"Faild":"This Address can't be deleted!!"})'''

	def __unicode__(self):
		#return '%s' % (self.name)
		return '%s : %s' % (self.id, self.name)

class Company(models.Model):
	name = models.CharField(max_length = 100)
	push_downstream = models.CharField(choices=YES_OR_NO, default='yes', max_length=10)
	#admin = models.ManyToManyField(User)
	street_address = models.CharField(max_length = 500, blank = True, null = True)
	city = models.ForeignKey(City, blank = True, null = True)
	state = models.ForeignKey(State, blank = True, null = True)
	pincode = models.IntegerField(blank = True, null = True)
	category = models.ManyToManyField(Category, blank=True)
	country = models.ForeignKey(Country, related_name='company_country', default=1)
	phone_number = models.CharField(max_length=13, blank = True, null = True)
	phone_number_verified = models.CharField(choices=YES_OR_NO, default='no', max_length=10)
	email = models.CharField(max_length = 50, blank = True, null = True)
	website = models.URLField(blank = True, null = True)
	note = models.TextField(blank = True, null = True)
	status = models.CharField(choices=COMPANY_STATUS, default='okay', max_length=20)
	company_type = models.CharField(choices=COMPANY_TYPE, default='nonmanufacturer', max_length=20)
	thumbnail = models.ImageField(upload_to='company_image', null=True, blank=True)
	#thumbnail = VersatileImageField(
	#	upload_to='company_image/',
	#	ppoi_field='thumbnail_ppoi',
	#	null=True, blank=True
	#)
	#thumbnail_ppoi = PPOIField()
	brand_added_flag = models.CharField(choices=YES_OR_NO, default='no', max_length=10)

	discovery_ok = models.BooleanField(default=True)
	connections_preapproved = models.BooleanField(default=True)
	no_suppliers = models.BooleanField(default=False)
	no_buyers = models.BooleanField(default=False)
	have_salesmen = models.BooleanField(default=True)
	sell_all_received_catalogs = models.BooleanField(default=False)
	sell_shared_catalogs = models.BooleanField(default=True)
	newsletter_subscribe = models.BooleanField(default=True)

	sms_buyers_on_overdue = models.BooleanField(default=True)

	company_type_filled = models.BooleanField(default=False)

	chat_admin_user = models.ForeignKey(User, blank = True, null = True, default=None)

	exp_push_delay = models.IntegerField(default=0)

	paytm_country = models.ForeignKey(Country, default=1)
	paytm_phone_number = models.CharField(max_length=13, blank = True, null = True)

	is_profile_set = models.BooleanField(default=True)
	wishbook_salesman = models.TextField(blank = True, null = True)

	buyers_assigned_to_salesman = models.BooleanField(default=False)
	salesman_mapping = models.CharField(choices=SALESMAN_MAPPING, default='Location', max_length=30)

	trusted_seller = models.BooleanField(default=False)

	name_updated = models.BooleanField(default=False)

	default_catalog_lifetime = models.IntegerField(default=60)

	address = models.ForeignKey(Address, default=None, blank = True, null = True)

	refered_by = models.ForeignKey('self', blank=True, null=True, related_name='refereds_by')

	cod_available = models.BooleanField(default=False)
	location_verified = models.BooleanField(default=False)

	refer_id = models.PositiveIntegerField(default=None, blank = True, null = True)
	landline_numbers = models.CharField(max_length=13, default=None, blank = True, null = True)

	transaction_type = models.CharField(choices=TRANSACTION_TYPE, default='Sale Purchase', max_length=50)

	sugar_crm_account_id = models.CharField(max_length=250, default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __init__(self, *args, **kwargs):
		super(Company, self).__init__(*args, **kwargs)
		self.old_salesman_mapping = self.salesman_mapping
		self.old_name = self.name
		#self.old_state = self.state
		#self.old_city = self.city

	def __unicode__(self):
		#return '%s' % (self.name)
		return '%s : %s' % (self.id, self.name)

	'''class Meta:
		ordering = ('name',)'''
	def thumbnail_url(self):
		return '%s%s' % (settings.MEDIA_URL, self.thumbnail)

	class Meta:
		index_together = [
			["country", "phone_number"],
		]

	def save(self, *args, **kwargs):
		print('class Company: save')
		self.name = self.name.title()

		if self.buyers_assigned_to_salesman == True and self.salesman_mapping == "Location" and self.old_salesman_mapping != self.salesman_mapping:
			BuyerSalesmen.objects.filter(salesman__companyuser__company=self.id).delete()

			slObjs = SalesmanLocation.objects.filter(salesman__companyuser__company=self.id)

			for slObj in slObjs:
				'''buyers = Buyer.objects.filter(selling_company=slObj.salesman.companyuser.company, buying_company__city__in=slObj.city.all(), buying_company__state__in=slObj.state.all())

				for buyer in buyers:
					BuyerSalesmen.objects.create(salesman=slObj.salesman, buyer=buyer.buying_company)'''
				states = slObj.state.all()
				if slObj.city.count() == 0:
					cities = City.objects.filter(state__in=states)
				else:
					cities = slObj.city.all()
				buying_company_ids = Buyer.objects.filter(selling_company=slObj.salesman.companyuser.company, buying_company__city__in=cities, buying_company__state__in=states).values_list('buying_company', flat=True)
				companyObjs = Company.objects.filter(id__in=buying_company_ids)
				bsObj = BuyerSalesmen.objects.create(salesman=slObj.salesman)
				bsObj.buyers=companyObjs
				bsObj.save()

		elif self.buyers_assigned_to_salesman == True and self.salesman_mapping == "Individual" and self.old_salesman_mapping != self.salesman_mapping:
			BuyerSalesmen.objects.filter(salesman__companyuser__company=self.id).delete()

		if self.state is not None and self.city is not None and self.state.state_name != "-" and self.city.city_name != "-" :
			self.is_profile_set = True

		#if self.old_state != self.state or self.old_city != self.city:
		if self.state:
			self.address.state = self.state
		if self.city:
			self.address.city = self.city
		if self.state or self.city:
			self.address.save()

		super(Company, self).save(*args, **kwargs)

		#WB-1610 : Django: If someone changes company name - then all catalog entries for that company in elastic search should be updated
		if self.old_name != self.name:
			cs_queryset = CatalogSeller.objects.filter(selling_company = self, selling_type="Public", status="Enable")#.exclude(catalog__company = self)
			for cs_obj in cs_queryset:
				cs_obj.save()


#post_save connect from Company
def company_to_crm(sender, instance, **kwargs):
	if kwargs['created']:
		if settings.DEBUG == False:
			company_to_crm_q(instance.id,created=True)

# for creating account on crm
post_save.connect(company_to_crm, sender = Company, dispatch_uid = 'sugar_company_update')

class AdvancedProfile(models.Model):
	company = models.OneToOneField(Company, related_name='advancedcompanyprofile')
	est_year = models.IntegerField(default=None, blank = True, null = True)
	shop_ownership = models.CharField(choices=SHOP_OWNERSHIP, default='Owned', max_length=20)
	product_min_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	product_max_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)

class SalesmanLocation(models.Model):
	salesman = models.OneToOneField(User) #models.ForeignKey(User)
	city = models.ManyToManyField(City, blank=True) #models.ForeignKey(City, blank = True, null = True)#null means all
	state = models.ManyToManyField(State, blank=True) #models.ForeignKey(State, blank = True, null = True)

	#def __unicode__(self):
	#	return '%s' % (self.salesman.id)

class BuyerSalesmen(models.Model):
	#buyer = models.ForeignKey(Company, related_name="salesmen_buyer")
	buyers = models.ManyToManyField(Company)
	salesman = models.OneToOneField(User)

	#class Meta:
	#	unique_together = ('buyer', 'salesman')

class CompanyPhoneAlias(models.Model):
	company = models.ForeignKey(Company, related_name='alias_company')
	country = models.ForeignKey(Country, related_name='alias_country', default=1)
	alias_number = models.CharField(max_length=13)#, unique=True
	status = models.CharField(choices=ALIAS_STATUS, default='Verification_Pending', max_length=30)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.id)

	class Meta:
		unique_together = ('country', 'alias_number')

class UnregisteredPhoneAlias(models.Model):
	master_country = models.ForeignKey(Country, related_name='master_country_ref', default=1)
	master_number = models.CharField(max_length=13)
	alias_country = models.ForeignKey(Country, related_name='alias_country_ref', default=1)
	alias_number = models.CharField(max_length=13, unique=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class CompanyType(models.Model):
	company = models.OneToOneField(Company, related_name='company_group_flag')
	manufacturer = models.BooleanField(default=False)
	#distributor = models.BooleanField(default=False)
	wholesaler_distributor = models.BooleanField(default=False)
	#semi_wholesaler = models.BooleanField(default=False)
	retailer = models.BooleanField(default=False)
	online_retailer_reseller = models.BooleanField(default=False)
	#resellers = models.BooleanField(default=False)
	broker = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if self.manufacturer == True and self.wholesaler_distributor == False and self.retailer == False and self.online_retailer_reseller == False and self.broker == False:
			self.company.company_type = 'manufacturer'
			self.company.save()
		else:
			self.company.company_type = 'nonmanufacturer'
			self.company.save()

		if self.manufacturer or self.wholesaler_distributor or self.retailer or self.online_retailer_reseller or self.broker:
			self.company.company_type_filled = True
			self.company.save()

		'''if self.manufacturer == False and self.wholesaler_distributor == False and self.retailer == True and self.online_retailer_reseller == False and self.broker == False:
			self.company.company_type = 'retailer'
			self.company.save()'''

		return super(CompanyType, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s' % (self.id)



class GroupType(models.Model):
	name = models.CharField(max_length = 20, unique=True)

	def __unicode__(self):
		return '%s' % (self.name)

	'''def save(self, *args, **kwargs):
		self.name = self.name.title()
		super(GroupType, self).save(*args, **kwargs)'''

	class Meta:
		ordering = ('name',)

class CompanyPriceList(models.Model):
	company = models.ForeignKey(Company, related_name = 'pricelist')
	number_pricelists = models.CharField(max_length=10)
	pricelist2_multiplier = models.CharField(max_length=10)

	def __unicode__(self):
		return '%s' % (self.number_pricelists)

class CompanyBuyerGroup(models.Model):
	company = models.ForeignKey(Company, related_name = 'company_buyer_group')
	#buyer_type = models.ForeignKey(GroupType)
	buyer_type = models.CharField(choices=COMPANY_BUYER_GROUP_TYPE, max_length=50)
	price_list = models.ForeignKey(CompanyPriceList, related_name = 'pricelist_buyer_group', default=None, blank = True, null = True)
	payment_duration = models.IntegerField(default=0)
	discount = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))
	cash_discount = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))
	credit_limit = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if self.pk is None:
			print "created"
			super(CompanyBuyerGroup, self).save(*args, **kwargs)
			#grouptypes = companyBuyerGroupTypeToBuyerType(self.buyer_type)

			#Buyer.objects.filter(selling_company=self.company, group_type__in=grouptypes, payment_duration=0, discount=Decimal('0.00'), cash_discount=Decimal('0.00'), credit_limit=Decimal('0.00')).update(discount=self.discount, cash_discount=self.cash_discount, credit_limit=self.credit_limit, payment_duration=self.payment_duration)
		else:
			print "update"
			super(CompanyBuyerGroup, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s' % (self.id)
	class Meta:
		unique_together = ('company', 'buyer_type')

class CompanyNumber(models.Model):
	phone_number = models.CharField(validators=[phone_regex], max_length=15)
	alias_number = models.CharField(validators=[phone_regex], max_length=15)#, unique=True
	is_verified = models.CharField(choices=YES_OR_NO, default='no', max_length=10)
	#company = models.ForeignKey(Company, related_name='company_number')

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)


class Branch(models.Model):
	company = models.ForeignKey(Company, related_name='branches')
	name = models.CharField(max_length=100)
	street_address = models.CharField(max_length = 500, blank = True, null = True)
	city = models.ForeignKey(City, blank = True, null = True)
	state = models.ForeignKey(State, blank = True, null = True)
	pincode = models.IntegerField(blank = True, null = True)
	country = models.ForeignKey(Country, related_name='branch_country', default=1)
	phone_number = models.CharField(blank = True, null = True, max_length=13)
	address = models.ForeignKey(Address, default=None, blank = True, null = True)
	# branch manager?

	def __unicode__(self):
		return '%s' % (self.name)
	class Meta:
		unique_together = ('company', 'name')

class CompanyUser(models.Model):
	company = models.ForeignKey(Company, related_name='company_users')
	deputed_from = models.ForeignKey(Company, default=None, blank = True, null = True)
	user = models.OneToOneField(User)#models.ForeignKey(User, related_name='user_companies', unique=True)
	deputed_to = models.ForeignKey(Company, related_name='deputed_to', default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		index_together = [
			["company", "deputed_to"],
			["company", "deputed_to", "user"],
		]
	#relationship_type = models.CharField(choices=RELATIONSHIP_TYPE, max_length=20)

	#def __unicode__(self):
	#	return '%s : %s' % (self.company.name, self.user.username)

	#class Meta:
		#ordering = ('relationship_type',)
		###unique_together = ('user', 'company')

class Brand(models.Model):
	name = models.CharField(max_length = 100, unique=True)
	manufacturer_company = models.ForeignKey(Company, related_name = 'manufacturer_brand', default=None, blank = True, null = True)
	company = models.ForeignKey(Company)##Creator
	#image = models.ImageField(upload_to='brand_image', null=True, blank=True)
	image = VersatileImageField(
		upload_to='brand_image/',
		ppoi_field='image_ppoi'
	)
	image_ppoi = PPOIField()

	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)
	total_catalog = models.PositiveIntegerField(default=0)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self.name = self.name.title()

		super(Brand, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s : %s' % (self.id, self.name)
	class Meta:
		#ordering = ('company',)
		unique_together = ('name', 'company',)
		index_together = [
			["company", "id"],
		]
'''
class BrandDistributor(models.Model):
	brand = models.ForeignKey(Brand)
	company = models.ForeignKey(Company)

	def __unicode__(self):
		return str('%s :: %s'% (self.brand.name, self.company.name))
	class Meta:
		unique_together = ('brand', 'company',)
'''

class BrandDistributor(models.Model):
	brand = models.ManyToManyField(Brand)
	company = models.OneToOneField(Company)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if self.pk:
			print "BrandDistributor save update"
			bids = Brand.objects.filter(Q(manufacturer_company=self.company) | Q(company=self.company)).values_list('id', flat=True)
			bids = list(bids)
			tempbids = self.brand.all().values_list('id', flat=True)
			bids.extend(list(tempbids))

			print bids
			csObjs = CatalogSeller.objects.filter(selling_company=self.company, status="Enable").exclude(catalog__brand__in=bids)
			print csObjs.count()
			#csObjs.update(status="Disable")
			for csObj in csObjs:
				csObj.status="Disable"
				csObj.save()

		super(BrandDistributor, self).save(*args, **kwargs)

	'''@staticmethod
	def autocomplete_search_fields():
		return ("id__iexact", "company__name__icontains",)'''

	#def __unicode__(self):
	#	return '%s' % (self.company.name)

	'''class Meta:
		ordering = ('id',)'''

class CompanyBrandFollow(models.Model):
	brand = models.ForeignKey(Brand)
	company = models.ForeignKey(Company)
	user = models.ForeignKey(User)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('brand', 'company', 'user')

def company_brand_follow_on_create(sender, instance, **kwargs):
	if kwargs['created']:
		company = instance.brand.manufacturer_company
		if company is None:
			company = instance.brand.company
		users = CompanyUser.objects.filter(company = company, user__groups__name="administrator").values_list('user', flat=True).distinct()
		users = list(users)

		rno = random.randrange(100000, 999999, 1)
		#image = instance.brand.image.thumbnail[settings.MEDIUM_IMAGE].url

		# message = "You have a new follower! "+str(instance.company.name)+" followed your brand "+str(instance.brand.name)
		message = notificationTemplates("brand_follower")% (instance.company.name, instance.brand.name)

		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((users, message, {"notId": rno, "title":"Brand Follower", "push_type":"promotional", "type":"tab", "other_para":{"deep_link":str(settings.GLOBAL_SITE_URL)+"?type=tab&page=myfollowers"}}), expires=datetime.now() + timedelta(days=2)) #, "image":image
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		users, message, {"notId": rno, "title":"Brand Followed", "push_type":"promotional", "type":"tab", "other_para":{"deep_link":str(settings.GLOBAL_SITE_URL)+"?type=tab&page=myfollowers"}}
		# 	)
		sendNotifications(users, message, {"notId": rno, "title":"Brand Followed", "push_type":"promotional", "type":"tab", "other_para":{"deep_link":str(settings.GLOBAL_SITE_URL)+"?type=tab&page=myfollowers"}})


post_save.connect(company_brand_follow_on_create, sender = CompanyBrandFollow, dispatch_uid = 'company_brand_follow_on_create_unique')

class URLIndex(models.Model):
	urlobject_id = models.IntegerField(blank=True, null=True, default=0)
	urltype = models.CharField(choices=URLINDEX_CATALOG, max_length=30, default='Catalog', blank=True, null=True) #choice
	urlkey = models.CharField(max_length=250, unique=True)

	def __unicode__(self):
		return 'urlobject_id = %s : urltype = %s : urlkey = %s' % (self.urlobject_id, self.urltype, self.urlkey)

class Catalog(models.Model):
	title = models.CharField(max_length = 100)
	brand = models.ForeignKey(Brand)
	#thumbnail = models.ImageField(upload_to='catalog_image', null=True, blank=True)
	thumbnail = VersatileImageField(
		upload_to='catalog_image/',
		ppoi_field='thumbnail_ppoi'
	)
	thumbnail_ppoi = PPOIField()
	view_permission = models.CharField(choices=CATALOG_PERMISSION, default='push', max_length=20)
	#category = models.ManyToManyField(Category, related_name = 'categories')
	category = models.ForeignKey(Category, default=12, related_name = 'categories')
	company = models.ForeignKey(Company)
	picasa_url = models.CharField(max_length = 200,blank = True, null = True)
	picasa_id = models.CharField(max_length = 100,blank = True, null = True)

	is_hidden = models.BooleanField(default=False)
	#is_approved = models.BooleanField(default=False)

	deleted = models.BooleanField(default=False)
	objects = SoftDeleteManager()
	all_objects = models.Manager()

	sell_full_catalog = models.BooleanField(default=False)

	mirror = models.ForeignKey('self', related_name = 'catalog_mirror', default=None, blank = True, null = True, on_delete=models.SET_NULL)

	created_at = models.DateField(auto_now_add=True)
	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)

	sort_order =  models.PositiveIntegerField(default=0)
	trusted_sort_order =  models.PositiveIntegerField(default=0)

	supplier_disabled = models.BooleanField(default=False)
	expiry_date = models.DateTimeField(blank = True, null = True)

	default_product_weight = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)

	modified = models.DateTimeField(auto_now=True)

	total_products_uploaded = models.PositiveIntegerField(default=0)

	#in percentage to increase product price if single user buy single product
	single_piece_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	single_piece_price_percentage = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)

	dispatch_date = models.DateField(blank = True, null = True)
	catalog_type = models.CharField(choices=CATALOG_UPLOAD_TYPE, default='catalog', max_length=30)

	'''def clean_category(self):
		category = self.cleaned_data['category']
		print category
		if category is None:
			raise ValidationError("This field is required.")'''
	def __init__(self, *args, **kwargs):
		super(Catalog, self).__init__(*args, **kwargs)
		self.old_deleted = self.deleted
		self.old_view_permission = self.view_permission
		self.old_expiry_date = self.expiry_date

		self.old_single_piece_price = self.single_piece_price
		self.old_single_piece_price_percentage = self.single_piece_price_percentage

	# Add indexing method to Catalog
	def indexing(self):
		logger.info("catalog model elasticsearch indexing = %s"% (self))
		eavdata = getCatalogEAV(self, "allInJson")
		fabric = []
		if "fabric" in eavdata:
			fabric = eavdata["fabric"]
		work = []
		if "work" in eavdata:
			work = eavdata["work"]
		stitching_type = ""
		if "stitching_type" in eavdata:
			stitching_type = ""#eavdata["stitching_type"]

		sellerslist = get_catalog_sellers_names(self)

		obj = CatalogIndex(
			meta={'id': self.id},
			title=self.title,
			brand=self.brand.name,
			category=self.category.category_name,
			work=work,
			fabric=fabric,

			company=self.company.name,
			stitching_type = stitching_type,
			min_price=0,
			max_price=0,
			sellers=list(sellerslist),
			catalog_suggest=[self.title, self.brand.name, self.company.name, self.category.category_name] + work + fabric
			)

		obj.save()
		logger.info("catalog model elasticsearch indexing = %s, obj status = %s"% (self, obj))
		return obj.to_dict(include_meta=True)

	def save(self, *args, **kwargs):
		'''if self.deleted == True: #if self.deleted != self.old_deleted:
			Product.all_objects.filter(catalog=self.id).update(deleted=self.deleted)
			Push_User.all_objects.filter(catalog=self.id).update(deleted=self.deleted)
			Push_User_Product.all_objects.filter(catalog=self.id).update(deleted=self.deleted)

		if self.is_hidden == True:
			#Product.all_objects.filter(catalog=self.id).update(deleted=self.deleted)
			Push_User.all_objects.filter(catalog=self.id).update(deleted=self.deleted)
			Push_User_Product.all_objects.filter(catalog=self.id).update(deleted=self.deleted)'''

		'''if self.pk is not None and self.old_view_permission != self.view_permission and self.view_permission == "public":
			products = Product.objects.filter(Q(catalog=self) & (Q(public_price__isnull=True) | Q(public_price__lt=Decimal('0.01'))))
			for product in products:
				product.public_price = product.price
				product.save()'''
		pk_value = self.pk
		self.title = self.title.title()

		if pk_value is None and self.expiry_date is None:
			todayDate = date.today()
			self.expiry_date = todayDate + timedelta(days=self.company.default_catalog_lifetime)


		super(Catalog, self).save(*args, **kwargs)

		if self.view_permission == "public" and pk_value is None:
			csobj = CatalogSeller.objects.create(catalog=self, selling_company=self.company, selling_type="Public", sell_full_catalog=self.sell_full_catalog, status="Enable", expiry_date=self.expiry_date)
		if self.old_view_permission == "public" and self.view_permission != self.old_view_permission:
			CatalogSeller.objects.filter(catalog=self, selling_company=self.company).update(selling_type="Private")
		if self.old_view_permission == "push" and self.view_permission != self.old_view_permission:
			if CatalogSeller.objects.filter(catalog=self, selling_company=self.company).exists():
				CatalogSeller.objects.filter(catalog=self, selling_company=self.company).update(selling_type="Public")
			else:
				csobj = CatalogSeller.objects.create(catalog=self, selling_company=self.company, selling_type="Public", sell_full_catalog=self.sell_full_catalog, status="Enable", expiry_date=self.expiry_date)

		#print 'about to update catalog expiry date'
		if self.old_expiry_date != self.expiry_date:
			print "catalog save expiredate update"
			if CatalogSeller.objects.filter(catalog=self, selling_company=self.company).exists():
				CatalogSeller.objects.filter(catalog=self, selling_company=self.company).update(expiry_date = self.expiry_date)

		if self.old_deleted != self.deleted and self.deleted is True:
			logger.info("catalog pre soft delete catalog id = %s"% (self.id))
			catalogDeleteElesticEntry(self)

		if self.view_permission == "public" and self.old_deleted != self.deleted:
			deleteCache("public")

		if self.old_single_piece_price != self.single_piece_price or self.old_single_piece_price_percentage != self.single_piece_price_percentage:
			logger.info("catalog old_single_piece_price catalog id = %s"% (self.id))
			products = Product.objects.filter(catalog=self)
			for product in products:
				product.save()

	'''def delete(self, *args, **kwargs):
		self.deleted = True
		self.save()'''

	def __unicode__(self):
		#return '%s' % (self.title)
		return 'id = %s : title = %s' % (self.id, self.title)

	def total_products(self):
		totalProducts = Product.objects.filter(catalog=self.id).values_list('id', flat=True).distinct().count()
		return totalProducts

	def is_product_price_null(self):
		if Product.objects.filter(Q(catalog=self.id) & (Q(price__isnull=True) | Q(price__lt=Decimal('0.01')))).exists():
			return True
		else:
			return False

	#~ def delete(self, *args, **kwargs):
		#~ obj = CatalogIndex.get(id=self.id, ignore=404)
		#~ print "delete catalog CatalogIndex =",obj
		#~ if obj:
			#~ obj.delete()
		#~ super(Catalog, self).delete(*args, **kwargs)

	class Meta:
		index_together = [
			["company", "brand"],
			["company", "id"],
			["company", "id", "brand"],
		]
	'''class Meta:
		ordering = ('brand',)
		#unique_together = ('title', 'company',)'''

@receiver(post_save, sender=Catalog)
def catalog_postsave(sender, instance, **kwargs):
	if kwargs['created']:
		print "created catalog_postsave"
		instance.sort_order = instance.id
		instance.save()

		# if instance.view_permission == "public": #meaning less as catalog has no products
		# 	deleteCache("public")

		if not URLIndex.objects.filter(urlobject_id = instance.id, urltype='Catalog').exists():
			urlkey_value = '-'.join(instance.brand.name.split()) + '-' + '-'.join(instance.title.split()) + '-' + str(instance.id)
			urlkey_value = urlkey_value.lower()
			urlindex_obj = URLIndex(urlobject_id=instance.id, urltype = 'Catalog', urlkey=urlkey_value)
			urlindex_obj.save()

		#if instance.view_permission == "public":
		#	instance.indexing()
	if instance.view_permission == "public":
		try:
			instance.indexing()
		except Exception as e:
			if settings.DEBUG==False:
				mail_status = send_mail("catalog_postsave", "Error = "+str(e)+", Catalog ID = "+str(instance.id), "tech@wishbook.io", ["tech@wishbook.io"])
				logger.info(str(mail_status))
			pass
	#catalogEAVset(instance)

@receiver(pre_delete, sender=Catalog)
def catalog_predelete(sender, instance, **kwargs):
	logger.info("catalog_predelete catalog id = %s"% (instance.id))
	if instance.view_permission == "public":
		deleteCache("public")
	catalogDeleteElesticEntry(instance)
#~ def catalog_sort_order(sender, instance, **kwargs):
	#~ if kwargs['created']:
		#~ instance.sort_order = instance.id
		#~ instance.save()

#~ post_save.connect(catalog_sort_order, sender = Catalog, dispatch_uid = 'catalog_sort_order_unique')

class CatalogUploadOption(models.Model):
	catalog = models.OneToOneField(Catalog)
	private_single_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	public_single_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	fabric = models.TextField(blank = True, null = True)
	work = models.TextField(blank = True, null = True)
	without_price = models.BooleanField(default=False)
	without_sku = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)


from django.core.exceptions import NON_FIELD_ERRORS
class CompanyCatalogView(models.Model):
	company = models.ForeignKey(Company, default=None, blank = True, null = True)
	catalog = models.ForeignKey(Catalog)
	catalog_type = models.CharField(choices=CATALOG_PERMISSION, max_length=20)
	created_at = models.DateTimeField(auto_now_add=True)
	clicks = models.PositiveIntegerField(default=1)

	user = models.ForeignKey(User, default=None, blank = True, null = True)

	class Meta:
		unique_together = ('company', 'catalog', 'catalog_type', 'user')
		'''error_messages = {
			NON_FIELD_ERRORS: {
				'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
			}
		}'''

def company_catalog_view(sender, instance, **kwargs):
	#if kwargs['created']:
	logger.info("company_catalog_view")
	try:
		logger.info("company_catalog_view try")
		#ccvtotal = CompanyCatalogView.objects.filter(catalog=instance.catalog).count()

		ccvtotal = CompanyCatalogView.objects.filter(catalog=instance.catalog).aggregate(Sum('clicks')).get('clicks__sum', 0)
		if ccvtotal is None:
			ccvtotal = 0

		logger.info(str(ccvtotal))

		if ccvtotal in [50,100,150,200,250,300,350,400,450,500]:
			company = instance.catalog.company
			companiesarr = []
			if instance.catalog.view_permission == "public":
				companiesarr.extend(CatalogSeller.objects.filter(catalog=instance.catalog, status="Enable").values_list('selling_company',flat=True))
			else:
				companiesarr.append(company.id)

			#user_ids = CompanyUser.objects.filter(company=company, user__groups__name="administrator").values_list('user', flat=True)
			user_ids = CompanyUser.objects.filter(company__in=companiesarr, user__groups__name="administrator").values_list('user', flat=True)

			message = notificationTemplates("company_catalog_view_times")% (instance.catalog.title, ccvtotal)
			logger.info("in company_catalog_view send notification")
			# if settings.TASK_QUEUE_METHOD == 'celery':
			# 	logger.info("in company_catalog_view send notification celery")
			# 	notificationSend.apply_async((user_ids, "Your "+str(instance.catalog.title)+" catalog was viewed "+str(ccvtotal)+" times", {"push_id": instance.id, "notId":instance.id, "push_type":"catalog", "image":instance.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url, "company_image":"", "title":"Catalog Views", "name":str(instance.catalog.title), "table_id": instance.catalog.id}), expires=datetime.now() + timedelta(days=2))
			# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			# 	logger.info("in company_catalog_view send notification djangoQ")
			# 	task_id = async(
			# 		'api.tasks.notificationSend',
			# 		user_ids, "Your "+str(instance.catalog.title)+" catalog was viewed "+str(ccvtotal)+" times", {"push_id": instance.id, "notId":instance.id, "push_type":"catalog", "image":instance.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url, "company_image":"", "title":"Catalog Views", "name":str(instance.catalog.title), "table_id": instance.catalog.id}
			# 	)
			sendNotifications(user_ids, message, {"push_id": instance.id, "notId":instance.id, "push_type":"catalog", "image":instance.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url, "company_image":"", "title":"Catalog Views", "name":str(instance.catalog.title), "table_id": instance.catalog.id})

			if ccvtotal in [50,100,150,200]:
				#to send sms
				template = None
				if ccvtotal in [50,100,200]:
					century = "Half-Century"
					if ccvtotal == 50:
						century = "Half-Century"
					elif ccvtotal == 100:
						century = "Century"
					elif ccvtotal == 200:
						century = "Double-Century"

					template = smsTemplates("catalogviewed")% (century, str(instance.catalog.title), ccvtotal)

				if ccvtotal in [150]:
					template = smsTemplates("catalogviewed_2")% (str(instance.catalog.title), ccvtotal)

				print template
				if template:
					phone_number = UserProfile.objects.filter(user__in=user_ids).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
					unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
					phone_number = list(set(phone_number) - set(unsubscribed_number))
					print phone_number
					smsSend(phone_number, template, True)

		#msg to share by company
		if Push_User.objects.filter(catalog=instance.catalog, buying_company=instance.company).exclude(push__company=instance.catalog.company).exists():
			print "received catalog viewed"
			shares_companies = Push_User.objects.filter(catalog=instance.catalog, buying_company=instance.company).exclude(push__company=instance.catalog.company).values_list('push__company', flat=True)
			for shares_company in shares_companies:
				print "shares_company=",shares_company

				push_ids = Push.objects.filter(company=shares_company, shared_catalog=instance.catalog).values_list('id', flat=True)

				buying_companies = Push_User.objects.filter(push__in=push_ids).values_list('buying_company', flat=True)

				ccvtotal = CompanyCatalogView.objects.filter(catalog=instance.catalog, company__in=buying_companies).aggregate(Sum('clicks')).get('clicks__sum', 0)
				if ccvtotal is None:
					ccvtotal = 0

				logger.info(str(ccvtotal))

				if ccvtotal in [50,100,150,200,250,300,350,400,450,500]:
					company = shares_company
					user_ids = CompanyUser.objects.filter(company=company, user__groups__name="administrator").values_list('user', flat=True)

					message = notificationTemplates("company_catalog_view_times_2")% (instance.catalog.title, ccvtotal)
					logger.info("in company_catalog_view send notification")
					# if settings.TASK_QUEUE_METHOD == 'celery':
					# 	logger.info("in company_catalog_view send notification celery")
					# 	notificationSend.apply_async((user_ids, "Your "+str(instance.catalog.title)+" catalog has been viewed "+str(ccvtotal)+" times", {"push_id": instance.id, "notId":instance.id, "push_type":"catalog", "image":instance.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url, "company_image":"", "title":"Catalog Views", "name":str(instance.catalog.title), "table_id": instance.catalog.id}), expires=datetime.now() + timedelta(days=2))
					# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
					# 	logger.info("in company_catalog_view send notification djangoQ")
					# 	task_id = async(
					# 		'api.tasks.notificationSend',
					# 		user_ids, "Your "+str(instance.catalog.title)+" catalog has been viewed "+str(ccvtotal)+" times", {"push_id": instance.id, "notId":instance.id, "push_type":"catalog", "image":instance.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url, "company_image":"", "title":"Catalog Views", "name":str(instance.catalog.title), "table_id": instance.catalog.id}
					# 	)
					sendNotifications(user_ids, message, {"push_id": instance.id, "notId":instance.id, "push_type":"catalog", "image":instance.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url, "company_image":"", "title":"Catalog Views", "name":str(instance.catalog.title), "table_id": instance.catalog.id})

	except Exception as e:
		logger.info("in company_catalog_view Exception")
		logger.info(str(e))
		pass
#commented by gaurav
#post_save.connect(company_catalog_view, sender = CompanyCatalogView, dispatch_uid = 'company_catalog_view_unique')


class Product(models.Model):
	title = models.CharField(max_length = 100, default=None, blank = True, null = True)
	#catalog = models.ManyToManyField(Catalog, related_name = 'products')#, blank=True
	catalog = models.ForeignKey(Catalog, related_name = 'products', default=None, blank = True, null = True)
	sku = models.CharField(max_length = 100, default=None, blank = True, null = True)#, unique=True
	fabric = models.TextField(blank = True, null = True)
	work = models.TextField(blank = True, null = True)
	price = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'), blank = True, null = True)
	#image_small = models.ImageField(upload_to='product_image', null=True, blank=True)
	image = VersatileImageField(
		upload_to='product_image/',
		ppoi_field='image_ppoi'
	)
	image_ppoi = PPOIField()

	is_hidden = models.BooleanField(default=False)

	deleted = models.BooleanField(default=False)
	objects = SoftDeleteManager()
	all_objects = models.Manager()

	mirror = models.ForeignKey('self', related_name = 'product_mirror', default=None, blank = True, null = True, on_delete=models.SET_NULL)

	public_price = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))

	sort_order = models.PositiveIntegerField(default=0)

	created_at = models.DateField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)

	weight = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	box_volumetric_dimension = models.CharField(max_length = 100, default=None, blank = True, null = True)

	single_piece_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)


	'''image_small_thumbnail = ProcessedImageField(upload_to='product_image',
										   processors=[ResizeToFill(400,600)],
										   format='JPEG')
	image_small_thumbnail2 = ImageSpecField(source='image_small_thumbnail',
									  processors=[ResizeToFill(100, 50)],
									  format='JPEG',
									  options={'quality': 30})'''

	def __init__(self, *args, **kwargs):
		super(Product, self).__init__(*args, **kwargs)
		self.old_deleted = self.deleted

	def save(self, *args, **kwargs):
		'''if self.deleted == True or self.is_hidden == True: #if self.deleted != self.old_deleted:
			Push_User_Product.all_objects.filter(product=self.id).update(deleted=self.deleted)'''

		self.title = self.title.title()
		if self.sku is not None and self.sku != "":
			if "img" in self.sku.lower() or "undefined" in self.sku.lower() or "jpg" in self.sku.lower() or "png" in self.sku.lower():
				self.sku = None
			else:
				self.sku = re.sub(r"^\W+", "", self.sku)
				self.sku = self.sku.lstrip('0')
		# else:
		# 	self.sku = str(self.sort_order)

		'''print "==save=="
		if not self.id:
		#if self.image_small:
			# Have to save the image (and imagefield) first
			super(Product, self).save(*args, **kwargs)
			# obj is being created for the first time - resize
			resized = get_thumbnail(self.image_small, '300x300', quality=40, format='JPEG')
			# Manually reassign the resized image to the image field
			self.image_small.save(resized.name, ContentFile(resized.read()), True)'''

		# if self.single_piece_price is None and (self.catalog.single_piece_price is not None or self.catalog.single_piece_price_percentage is not None):
		if self.catalog.single_piece_price is not None or self.catalog.single_piece_price_percentage is not None:
			final_price = self.public_price
			if self.catalog.view_permission == "push":
				final_price = self.price
			add_price = 0
			if self.catalog.single_piece_price:
				add_price += self.catalog.single_piece_price
			if self.catalog.single_piece_price_percentage:
				add_price += final_price * self.catalog.single_piece_price_percentage / 100
			logger.info("product model save() product.id = %s, add_price = %s" % (self.id, add_price))
			self.single_piece_price = final_price + add_price

		super(Product, self).save(*args, **kwargs)

	'''def delete(self, *args, **kwargs):
		self.deleted = True
		self.save()'''

	def product_likes(self):
		totalLikes = ProductLike.objects.filter(product=self.id).count()
		return totalLikes

	def __unicode__(self):
		return 'id = %s : sku = %s' % (self.id, self.sku)
		#if self.catalog is not None:
		#	return '%s : %s' % (self.sku, self.catalog.title)
		#else:
	class Meta:
		index_together = [
			["id", "catalog"],
		]
	'''def image_small_url(self):
		return '%s%s' % (settings.MEDIA_URL, self.image_small)'''
	'''class Meta:
		ordering = ('title',)
		#unique_together = ('title', 'catalog')
		#unique_together = (('sku', 'catalog__brand__name'),)'''

def product_on_create(sender, instance, **kwargs):
	if kwargs['created']:
		total_products = Product.objects.filter(catalog=instance.catalog).count()
		#print "product public"
		#print total_products

		if instance.catalog.view_permission == "public" and total_products == 1:
			todayDate = date.today()

			cat_ids = Product.objects.filter(catalog__company=instance.catalog.company, catalog__view_permission="public", created_at=todayDate).values_list('catalog', flat=True)
			cat_ids = Product.objects.filter(catalog__company=instance.catalog.company, catalog__view_permission="public", created_at__lt=todayDate, catalog__in=cat_ids).values_list('catalog', flat=True)
			today_pub_product_upload_total = Product.objects.filter(catalog__company=instance.catalog.company, catalog__view_permission="public", created_at=todayDate).exclude(catalog__in=cat_ids).count()

			logger.info("product_on_create view_permission=public catalog id = %s"% (instance.catalog.id))
			#notification to followers
			catalog = instance.catalog
			companyids = CompanyBrandFollow.objects.filter(brand=catalog.brand).values_list('company', flat=True).distinct()
			users = CompanyUser.objects.filter(company__in = companyids, user__groups__name="administrator").exclude(company=instance.catalog.company).values_list('user', flat=True).distinct()
			users = list(users)
			companyImage = catalog.brand.image.thumbnail[settings.MEDIUM_IMAGE].url
			pushImage = catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
			#message = "View your followed brand "+instance.brand.name+"'s new catalog"
			#message = catalog.brand.name+" has added catalog "+catalog.title

			# message = catalog.company.name+" just added "+catalog.title+" catalog of "+catalog.brand.name+" Brand"
			message = notificationTemplates("catalog_added")% (catalog.company.name, catalog.title, catalog.brand.name)
			# if settings.TASK_QUEUE_METHOD == 'celery':
			# 	notificationSend.apply_async((users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id), "other_para":{"not_action_1":"catalog_view"} }), expires=datetime.now() + timedelta(days=2))
			# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			# 	task_id = async(
			# 		'api.tasks.notificationSend',
			# 		users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id), "other_para":{"not_action_1":"catalog_view"} }
			# 	)
			sendNotifications(users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id), "other_para":{"not_action_1":"catalog_view"} })


			#notification to buyers

			#for 1'st product upload need to send notification
			#if Catalog.objects.filter(company=instance.catalog.company, view_permission="public", created_at=todayDate).count() == 1:
			logger.info("product_on_create view_permission=public today_pub_product_upload_total = %s"% (today_pub_product_upload_total))
			if today_pub_product_upload_total == 1:
				logger.info("product_on_create view_permission=public catalog id = %s, sending notifications to my all buyers"% (instance.catalog.id))
				buyers = Buyer.objects.filter(selling_company=instance.catalog.company, status="approved").exclude(buying_company__in=companyids).values_list('buying_company', flat=True)
				users = CompanyUser.objects.filter(company__in = buyers, user__groups__name="administrator").exclude(company=instance.catalog.company).values_list('user', flat=True).distinct()
				users = list(users)

				# message = instance.catalog.company.name+" just uploaded a catalog "+catalog.title
				message = notificationTemplates("catalog_added_2")% (instance.catalog.company.name, catalog.title)
				# if settings.TASK_QUEUE_METHOD == 'celery':
				# 	notificationSend.apply_async((users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id)}), expires=datetime.now() + timedelta(days=2))
				# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				# 	task_id = async(
				# 		'api.tasks.notificationSend',
				# 		users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id)}
				# 	)
				sendNotifications(users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id)})

				excludeusers = GCMDevice.objects.filter(user__in=users, active=True).values_list('user', flat=True).distinct()
				logger.info("product_on_create view_permission=public catalog id = %s, sending notifications to my all buyers, excludeusers = %s"% (instance.catalog.id, excludeusers))

				unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
				smsUser = UserProfile.objects.filter(user__in=users).exclude(user__in=excludeusers)
				smsurl = 'https://app.wishbooks.io/m?type=catalog&id='+str(instance.catalog.id)

				for userPObj in smsUser:
					if "+91" not in userPObj.country.phone_code:
						continue

					phone_number = [str(userPObj.country.phone_code)+str(userPObj.phone_number)]
					phone_number = list(set(phone_number) - set(unsubscribed_number))

					if len(phone_number) == 0:
						continue

					otp = getLastOTP(userPObj)
					usersmsurl = smsurl + '&m='+str(userPObj.phone_number)+'&o='+str(otp)
					#time.sleep(2)
					usersmsurl = urlShortener(usersmsurl)

					template = smsTemplates("public_catalog")% (instance.catalog.company.name, instance.catalog.title, usersmsurl)
					#smsSend(phone_number, template, True)
					logger.info("in_queue smsSendTextNationPromotional")
					if settings.TASK_QUEUE_METHOD == 'celery':
						smsSendTextNationPromotional.apply_async((phone_number, template, True), expires=datetime.now() + timedelta(days=2))
					elif settings.TASK_QUEUE_METHOD == 'djangoQ':
						if isScheduledTime():
							schedule('api.tasks.smsSendTextNationPromotional',
								phone_number, template, True,
								schedule_type=Schedule.ONCE,
								next_run=getScheduledTime(),
								q_options={'broker': priority_broker}
							)
						else:
							task_id = async(
								'api.tasks.smsSendTextNationPromotional',
								phone_number, template, True
							)

		set_total_products_uploaded(instance.catalog)

	catalogEAVProductset(instance.catalog)

	if instance.catalog.view_permission == "public":
		try:
			obj = CatalogIndex.get(id=instance.catalog.id, ignore=404)
			logger.info("Product model product_on_create CatalogIndex = %s"% (obj))
			if obj:
				min_price = Product.objects.filter(catalog=instance.catalog).aggregate(Min('public_price')).get('public_price__min', 0)
				max_price = Product.objects.filter(catalog=instance.catalog).aggregate(Max('public_price')).get('public_price__max', 0)
				if min_price is None:
					min_price = 0
				if max_price is None:
					max_price = 0
				obj.update(min_price=min_price, max_price=max_price)
		except Exception as e:
			if settings.DEBUG==False and "conflict" not in str(e):
				mail_status = send_mail("product_on_create", "Error = "+str(e)+", Catalog ID = "+str(instance.catalog.id), "tech@wishbook.io", ["tech@wishbook.io"])
				logger.info(str(mail_status))
			pass

	if instance.sku is not None and instance.sku != "":
		if Product.objects.filter(sku=instance.sku, catalog = instance.catalog).exclude(Q(deleted=True) | Q(id=instance.id)).exists():
			instance.sku = instance.sku+str(instance.sort_order)
			instance.save()
	else:
		instance.sku = str(instance.sort_order)
		instance.save()

post_save.connect(product_on_create, sender = Product, dispatch_uid = 'product_on_create_unique')


@receiver(post_delete, sender=Product)
def product_post_delete(sender, instance, **kwargs):
	try:
		set_total_products_uploaded(instance.catalog)
	except Exception as e:
		pass


class CompanyProductView(models.Model):#not using
	company = models.ForeignKey(Company)
	product = models.ForeignKey(Product)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('company', 'product')

class ProductEAVFlat(models.Model):
	product = models.OneToOneField(Product)
	category = models.ForeignKey(Category, default=None, blank = True, null = True)
	catalog = models.ForeignKey(Catalog, default=None, blank = True, null = True)
	fabric = models.CharField(max_length = 100, default=None, blank = True, null = True)
	work = models.CharField(max_length = 100, default=None, blank = True, null = True)
	fabric_text = models.CharField(max_length = 100, default=None, blank = True, null = True)
	work_text = models.CharField(max_length = 100, default=None, blank = True, null = True)
	#stitching_type = models.CharField(max_length = 100, default=None, blank = True, null = True) #enum choice
	#number_pcs_design_per_set = models.CharField(max_length = 250, default=None, blank = True, null = True) #textbox
	#size = models.CharField(max_length = 100, default=None, blank = True, null = True) #dropdown
	#size_mix = models.CharField(max_length = 100, default=None, blank = True, null = True) #textbox

class CatalogEAVFlat(models.Model):
	catalog = models.OneToOneField(Catalog)

	title = models.CharField(max_length = 100, blank = True, null = True)
	brand = models.ForeignKey(Brand, default=None, blank = True, null = True)
	view_permission = models.CharField(choices=CATALOG_PERMISSION, default='push', max_length=20)
	category = models.ForeignKey(Category, default=None, blank = True, null = True)
	sell_full_catalog = models.BooleanField(default=False)

	fabric = models.CharField(max_length = 250, default=None, blank = True, null = True)
	work = models.CharField(max_length = 250, default=None, blank = True, null = True)
	# style = models.CharField(max_length = 250, default=None, blank = True, null = True)
	fabric_value = models.CharField(max_length = 250, default=None, blank = True, null = True)
	work_value = models.CharField(max_length = 250, default=None, blank = True, null = True)
	# style_value = models.CharField(max_length = 250, default=None, blank = True, null = True)

	min_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	max_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)

	stitching_type = models.CharField(max_length = 250, default=None, blank = True, null = True) #enum choice
	number_pcs_design_per_set = models.CharField(max_length = 250, default=None, blank = True, null = True) #textbox
	size = models.CharField(max_length = 250, default=None, blank = True, null = True) #dropdown
	size_value = models.CharField(max_length = 250, default=None, blank = True, null = True)
	size_mix = models.CharField(max_length = 250, default=None, blank = True, null = True) #textbox

	style = models.CharField(max_length = 250, default=None, blank = True, null = True) #enum choice

	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateField(auto_now=True)

	def __unicode__(self):
		return '%s : %s' % (self.title, self.view_permission)

class ProductLike(models.Model):
	user = models.ForeignKey('auth.User')
	product = models.ForeignKey(Product)

	#def __unicode__(self):
	#	return '%s : %s' % (self.user.username, self.product)

	class Meta:
		unique_together = ('user', 'product')
		index_together = [
			["user", "product"],
		]

class CatalogList(models.Model):
	name = models.CharField(max_length = 100)
	catalogs = models.ManyToManyField(Catalog, related_name = 'catalog_list')
	user = models.ForeignKey('auth.User')

	def __unicode__(self):
		#return '%s : %s' % (self.name, self.user.username)
		return '%s' % (self.name)

	class Meta:
		unique_together = ('name', 'user')

class WbCoupon(models.Model):
	name = models.CharField(max_length = 100)
	discount_type = models.CharField(choices=WB_COUPON, max_length=20)
	value = models.DecimalField(max_digits=19 , decimal_places=2)
	valid_till = models.DateField()
	num_uses = models.PositiveIntegerField(default=0)


class Cart(models.Model):
	user = models.ForeignKey('auth.User')
	order_number = models.CharField(max_length=50, blank = True, null = True)
	buying_company = models.ForeignKey(Company, related_name = 'cart_buying_company')

	processing_status = models.CharField(choices=SALES_ORDER_PROCESSING_STATUS, default='Cart', blank = True, null=True, max_length=50)

	payment_details = models.TextField(blank = True, null = True)
	payment_date = models.DateField(blank = True, null = True)
	broker_company = models.ForeignKey(Company, related_name = 'cart_broker_company', default=None, blank = True, null = True)
	brokerage_fees = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))

	preffered_shipping_provider = models.CharField(choices=SHIPPING_PROVIDER, default='Buyer Suggested', null=True, max_length=20)
	buyer_preferred_logistics = models.CharField(max_length=250, default=None, blank = True, null = True)

	ship_to = models.ForeignKey(Address, default=None, blank = True, null = True)
	shipping_charges = models.DecimalField(max_digits=19 , decimal_places=2, default=Decimal('0.00'), blank = True, null = True)

	order_type = models.CharField(choices=ORDER_TYPE, default='Prepaid', max_length=20)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	payment_method = models.CharField(choices=PAYMENT_MODE, max_length=20, default=None, blank = True, null = True)

	total_qty = models.IntegerField(default=0)
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	paid_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	pending_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=20, default='Pending')
	taxes = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	total_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2) # amount+taxes+shipping_charges-discount

	seller_discount = models.DecimalField(default=Decimal('0.00'), blank=True, null=True, max_digits=19, decimal_places=2)

	created_type = models.CharField(choices=CART_CREATED_TYPE, max_length=20, default="Cart", blank = True, null = True)
	cart_status = models.CharField(choices=CART_STATUS, max_length=20, default="Created", blank = True, null = True)

	def __init__(self, *args, **kwargs):
		super(Cart, self).__init__(*args, **kwargs)
		self.old_cart_status = self.cart_status
		self.old_order_type = self.order_type

	def save(self, *args, **kwargs):
		pk_value = self.pk

		if (pk_value is None or self.old_cart_status != self.cart_status) and self.cart_status == "Converted":
			from api.v1.order.functions import *
			converCartToOrder(self)

		# if self.old_order_type != self.order_type and self.order_type == "Credit" and self.processing_status == "Pending":
		# 	from api.v1.order.functions import *
		# 	converCartToOrder(self)

		super(Cart, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s : %s : %s'% (self.id, self.order_number, self.created)

	def total_products(self):
		totalProducts = self.items.all().aggregate(Sum('quantity')).get('quantity__sum', 0)
		if totalProducts is None:
			totalProducts = 0
		return totalProducts

class SalesOrder(models.Model):
	user = models.ForeignKey('auth.User')
	order_number = models.CharField(max_length=50, blank = True, null = True) #buyer_ref
	seller_ref = models.CharField(max_length=50, blank = True, null = True)
	seller_company = models.ForeignKey(Company, related_name = 'selling_order')
	company = models.ForeignKey(Company, related_name = 'buying_order')#buyer_company
#	total_rate = models.DecimalField(max_digits=19, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))]) # can be done by aggregator. this should be removed
	created_at = models.DateTimeField(auto_now_add=True)
	date = models.DateField(auto_now=True)
	time = models.DateTimeField(auto_now=True)
	processing_status = models.CharField(choices=SALES_ORDER_PROCESSING_STATUS, default='Pending', null=True, max_length=50)
	customer_status = models.CharField(choices=SALES_ORDER_CUSTOMER_STATUS, default='Pending', max_length=20) #not using
	sales_image = models.ImageField(upload_to='order', null=True, blank=True)
	purchase_image = models.ImageField(upload_to='order', null=True, blank=True)
	note = models.TextField(blank = True, null = True)
	tracking_details = models.TextField(blank = True, null = True)
	supplier_cancel = models.TextField(blank = True, null = True)
	buyer_cancel = models.TextField(blank = True, null = True)
	payment_details = models.TextField(blank = True, null = True)
	payment_date = models.DateField(blank = True, null = True)

	dispatch_date = models.DateField(blank = True, null = True)

	broker_company = models.ForeignKey(Company, related_name = 'broker_company', default=None, blank = True, null = True)
	brokerage_fees = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))
#	catalog = models.PositiveIntegerField(default=0)

	sales_image_2 = models.ImageField(upload_to='order', null=True, blank=True)
	sales_image_3 = models.ImageField(upload_to='order', null=True, blank=True)

	sales_reference_id = models.IntegerField(blank = True, null = True)
	purchase_reference_id = models.IntegerField(blank = True, null = True)

	#backorder = models.BooleanField(default=False)
	backorders = models.ManyToManyField('self', blank = True)

	is_supplier_approved = models.BooleanField(default=True)
	tranferred_to = models.ForeignKey('self', blank=True, null=True, related_name='tranferred_order')
	wb_coupon = models.ForeignKey(WbCoupon, default=None, blank = True, null = True)

	buying_company_name = models.CharField(max_length=250, default=None, blank = True, null = True)
	preffered_shipping_provider = models.CharField(choices=SHIPPING_PROVIDER, default='Buyer Suggested', null=True, max_length=20)
	buyer_preferred_logistics = models.CharField(max_length=250, default=None, blank = True, null = True)

	ship_to = models.ForeignKey(Address, default=None, blank = True, null = True)
	shipping_charges = models.DecimalField(max_digits=19 , decimal_places=2, default=Decimal('0.00'), blank = True, null = True)

	transaction_type = models.CharField(choices=TRANSACTION_TYPE, default='Sale Purchase', max_length=50)
	cancelled_by = models.CharField(choices=CANCELLED_BY, default=None, blank = True, null = True, max_length=20)
	seller_cancellation_reason = models.CharField(choices=SELLER_CANCEL_REASON, default=None, blank = True, null = True, max_length=30)

	order_type = models.CharField(choices=ORDER_TYPE, default='Prepaid', max_length=20)

	visible_to_supplier = models.BooleanField(default=True)
	visible_to_buyer = models.BooleanField(default=True)

	approximate_order = models.BooleanField(default=False)

	created_by = CreatingUserField(related_name = "created_salesorders")
	modified_by = LastUserField(related_name = "modified_salesorders")
	audit_log = AuditLog()

	amount = models.DecimalField(default=Decimal('0.00'), blank=True, null=True, max_digits=19, decimal_places=2)
	seller_extra_discount_percentage = models.DecimalField(default=Decimal('0.00'), blank=True, null=True, max_digits=19, decimal_places=2)
	cart = models.ForeignKey(Cart, default=None, blank = True, null = True)

	source_type = models.CharField(choices=SOURCE_TYPE, default='Marketplace', max_length=50)

	processing_note = models.TextField(blank = True, null = True)


	def __init__(self, *args, **kwargs):
		super(SalesOrder, self).__init__(*args, **kwargs)
		self.old_processing_status = self.processing_status
		self.old_customer_status = self.customer_status
		self.old_seller_extra_discount_percentage = self.seller_extra_discount_percentage

	def save(self, *args, **kwargs):
		pk_value = self.pk
		if self.pk:
			logger.info("salesorder model in save update")
			if self.customer_status == "Paid":
				if self.old_customer_status != self.customer_status and self.customer_status == "Cancelled":
					print "in old_customer_status Cancelled"
					crObj, created = OrderRating.objects.get_or_create(order=self)
					crObj.seller_rating=5
					crObj.buyer_rating=0
					crObj.save()
					print crObj
				if self.old_processing_status != self.processing_status and self.processing_status == "Cancelled":
					print "in old_processing_status Cancelled"
					crObj, created = OrderRating.objects.get_or_create(order=self)
					crObj.seller_rating=0
					crObj.buyer_rating=5
					crObj.save()
					print crObj
		else:
			#create in save
			logger.info("salesorder model in save create")
			if self.brokerage_fees == Decimal('0.00'):
				buyerObj = Buyer.objects.filter(selling_company=self.seller_company, buying_company=self.company).last()
				if buyerObj:
					self.brokerage_fees = buyerObj.brokerage_fees

		buyerObj = Buyer.objects.filter(selling_company=self.seller_company, buying_company=self.company).last()
		if buyerObj:
			self.buying_company_name = buyerObj.buying_company_name
		else:
			self.buying_company_name = self.company.name

		if self.customer_status == "Paid" and self.processing_status == "Draft":
			self.processing_status = "Pending"

		if self.order_type == "Prepaid" and self.payment_details is not None:
			paydetail = self.payment_details.lower()
			if "credit" in paydetail:# or "neft" in paydetail or "other" in paydetail or "cheque" in paydetail:
				self.order_type = "Credit"

		if self.old_processing_status == "Draft" and self.processing_status == "Cancelled":
			self.visible_to_supplier = False
			if self.source_type == "Saas" and self.order_type == "Credit": #for csv only
				self.visible_to_supplier = True
				self.visible_to_buyer = False

		if self.old_processing_status == "Cart" and self.processing_status == "Cancelled":
			self.visible_to_supplier = False
			self.visible_to_buyer = False

		if self.old_processing_status == "Field Verification Pending" and self.processing_status == "Pending":
			self.company.location_verified = True
			self.company.save()

		super(SalesOrder, self).save(*args, **kwargs)

		#using for webapp in sales order creation as status is accepted
		logger.info("old_processing_status = %s, processing_status = %s"% (str(self.old_processing_status), str(self.processing_status)))
		if self.processing_status == "Accepted" and (pk_value is None or self.old_processing_status != self.processing_status):
			from api.common_functions import orderFinalizeNotification
			orderFinalizeNotification(self)

		if self.source_type == "Marketplace" and self.cart is None:
			jsonarr = {}
			jsonarr['order_number'] = self.order_number
			jsonarr['table_id'] = self.id
			if self.processing_status == "Pending" and (pk_value is None or self.old_processing_status != self.processing_status):
				logger.info("salesorder model sending notification processing_status=Pending")
				# ~ if self.user.companyuser.company == self.company
				if self.user.companyuser.company == self.company or self.user.companyuser.company == self.seller_company:
					#created by buyer
					jsonarr['status'] = self.processing_status
					jsonarr['title'] = "Sales Order "+str(self.processing_status)

					jsonarr['company_info'] = self.company.name+', '+self.company.city.city_name+', '+self.company.state.state_name
					jsonarr['order_url'] = 'https://app.wishbooks.io/m?type=sales&id='+str(self.id)

					broker_users = []
					if self.broker_company is not None:
						broker_users=CompanyUser.objects.filter(company=self.broker_company).values_list('user', flat=True).distinct()

					user1 = self.seller_company.company_users.values_list('user', flat=True)
					user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

					sendAllTypesMessage("salesorder_pending", user1, jsonarr)
				#else:
				# ~ elif self.user.companyuser.company == self.seller_company:
					# ~ jsonarr['status'] = self.processing_status
					jsonarr['title'] = "Purchase Order "+str(self.processing_status)

					# ~ broker_users = []
					# ~ if self.broker_company is not None:
						# ~ broker_users=CompanyUser.objects.filter(company=self.broker_company).values_list('user', flat=True).distinct()

					user1 = self.company.company_users.values_list('user', flat=True)
					user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

					sendAllTypesMessage("purchaseorder_pending", user1, jsonarr)
				elif self.broker_company is not None:
					print "broker pending notification"
					jsonarr['broker_name'] = self.broker_company.name
					jsonarr['notId'] = self.id

					user1 = self.seller_company.company_users.values_list('user', flat=True)
					user1 = User.objects.filter(id__in=user1, groups__name="administrator")

					sendAllTypesMessage("salesorder_broker", user1, jsonarr)

					user1 = self.company.company_users.values_list('user', flat=True)
					user1 = User.objects.filter(id__in=user1, groups__name="administrator")

					sendAllTypesMessage("purchaseorder_broker", user1, jsonarr)

			# ~ paydetail = self.payment_details.lower()
			# ~ if self.order_type == "Prepaid" and ("credit" in paydetail or "neft" in paydetail or "other" in paydetail or "cheque" in paydetail):
				# ~ self.order_type = "Credit"
				# ~ self.save()
		if self.old_seller_extra_discount_percentage != self.seller_extra_discount_percentage and self.seller_extra_discount_percentage > Decimal('0.00'):
			logger.info("salesorder model sending notification old_seller_extra_discount_percentage")

			jsonarr = {}
			jsonarr['order_number'] = self.order_number
			jsonarr['table_id'] = self.id
			jsonarr['status'] = self.processing_status
			jsonarr['title'] = "Discount on Purchase Order"
			jsonarr['order_url'] = 'https://app.wishbooks.io/m?type=purchase&id='+str(self.id)
			jsonarr['push_type'] = "promotional"

			#message = "Discount of "+ str(self.seller_extra_discount_percentage) +"% has been given by your supplier. Finalize your order"
			discount_percent = getOrderCCDiscount(self)
			discount_percent = discount_percent + self.seller_extra_discount_percentage
			# message = "Woohoo! Seller has added "+ str(self.seller_extra_discount_percentage) +"% discount on your order "+ str(self.order_number) +". Now total discount is "+ str(discount_percent) +"%. Place the order now!"
			message = notificationTemplates("seller_order_extra_discount")% (self.seller_extra_discount_percentage, self.order_number, discount_percent)

			broker_users = []
			if self.broker_company is not None:
				broker_users=CompanyUser.objects.filter(company=self.broker_company).values_list('user', flat=True).distinct()

			user1 = self.company.company_users.values_list('user', flat=True)
			user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

			sendNotifications(user1, message, jsonarr)

	def payment_status(self):
		status = ""
		invoices = self.invoice_set.all() #should be order by id
		#print "models invoices ==", invoices
		invoices_count = invoices.count()
		if invoices_count == 0:
			status = "Pending"
		elif invoices_count == 1:
			#~ status = self.invoice_set.first().payment_status
			status = invoices[0].payment_status
			# ~ if self.invoice_set.first().payment_status == "Paid":
				# ~ status = "Paid"
			# ~ else:
				# ~ status = "Pending"
		else:
			paid = 0
			partiallypaid = 0
			pending = 0
			last_paid_invoice_pending_amount = None
			for invoice in invoices:
				if invoice.payment_status == "Paid":
					paid += 1
					last_paid_invoice_pending_amount = invoice.pending_amount
				elif invoice.payment_status == "Partially Paid":
					partiallypaid += 1
				else:
					pending += 1
			if paid == invoices_count:
				status = "Paid"
			elif pending == invoices_count:
				status = "Pending"
			else:
				# lastpaidinvoice = invoices.filter(payment_status="Paid").order_by('id').last()
				# if lastpaidinvoice.pending_amount < float(1):
				if last_paid_invoice_pending_amount is not None and last_paid_invoice_pending_amount < float(1):
					status = "Paid"
				else:
					status = "Partially Paid"

		return status

	def total_item(self):
		return self.items.count()
	def total_products(self):
		# totalProducts = self.items.all().aggregate(Sum('quantity')).get('quantity__sum', 0)
		# if totalProducts is None:
		# 	totalProducts = 0
		# return totalProducts
		totalProducts = 0
		for it in self.items.all():
			totalProducts += it.quantity
		return totalProducts
	def total_pending_quantity(self):
		# soiQty = self.items.all().aggregate(Sum('pending_quantity')).get('pending_quantity__sum', 0)
		# if soiQty is None:
		# 	soiQty = 0
		# return soiQty
		soiQty = 0
		for it in self.items.all():
			soiQty += it.pending_quantity
		return soiQty
	def total_rate(self):
		rate = Decimal(0.0)
		for it in self.items.all():
			#if(it.rate):
			try:
				rate += it.rate*it.quantity
			except Exception:
				pass
			#else:
			#	rate += it.product.price*it.quantity
		return rate

	def __unicode__(self):
		#return '%s : %s : %s : %s'% (self.seller_company.name, self.company.name, self.order_number, self.date)
		return '%s : %s : %s'% (self.id, self.order_number, self.date)

	class Meta:
		#ordering = ('id',)
		index_together = [
			["user", "company"],
		]

@receiver(post_save, sender=SalesOrder)
def sales_order_postsave(sender, instance, **kwargs):
	if instance.order_number is None or instance.order_number == "":
		instance.order_number = instance.id
		instance.save()

# can be done using manytomany field using an intermediate model ("through" attribute)
class SalesOrderItem(models.Model):
	sales_order = models.ForeignKey(SalesOrder, related_name='items',  default=None )
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField(default=1)
	rate = models.DecimalField(max_digits=19 , decimal_places=2, null=True)#, validators=[MinValueValidator(Decimal('0.01'))]
	pending_quantity = models.PositiveIntegerField(default=0)
	invoiced_qty = models.PositiveIntegerField(default=0)
	dispatched_qty = models.PositiveIntegerField(default=0)
	canceled_qty = models.PositiveIntegerField(default=0)

	packing_type = models.CharField(choices=PACKING_TYPE, max_length=20, default=None, blank = True, null = True)
	note = models.TextField(blank = True, null = True)

	is_full_catalog = models.BooleanField(default=False)

	def __unicode__(self):
		#return '%s' % (self.product.title)
		return '%s' % (self.id)

	class Meta:
		unique_together = ('sales_order', 'product', 'packing_type')
		index_together = [
			["id", "sales_order"],
		]

class SalesOrderInternal(models.Model):
	salesorder = models.OneToOneField(SalesOrder)
	last_modified_by = models.ForeignKey(User, default=None, blank = True, null = True)
	internal_remark = models.TextField(blank = True, null = True)

class Dispatch(models.Model):
	sales_order = models.ForeignKey(SalesOrder, related_name='dispatch',  default=None )
	date = models.DateField(blank = True, null = True)
	dispatch_details = models.TextField(blank = True, null = True)
	status = models.CharField(choices=DISPATCH_STATUS, default='Dispatched', max_length=20)

class DispatchItem(models.Model):
	sales_order_item = models.ForeignKey(SalesOrderItem, related_name='dispatch_item',  default=None )
	quantity = models.PositiveIntegerField(default=1)

class Selection(models.Model):
	user = models.ForeignKey('auth.User')
	name = models.CharField(max_length=100)
	products = models.ManyToManyField(Product)
	thumbnail = models.ImageField(upload_to='selection_image', null=True, blank=True)
	buyable = models.BooleanField(default=True)

	deleted = models.BooleanField(default=False)
	objects = SoftDeleteManager()
	all_objects = models.Manager()

	'''def save(self, *args, **kwargs):
		if self.deleted == True: #if self.deleted != self.old_deleted:
			#Product.all_objects.filter(selection=self.id).update(deleted=self.deleted)
			Push_User.all_objects.filter(selection=self.id).update(deleted=self.deleted)
			Push_User_Product.all_objects.filter(selection=self.id).update(deleted=self.deleted)

		super(Selection, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self.deleted = True
		self.save()'''

	def image(self):
		image = ""

		if self.products.exists():
			product = self.products.first()
			image = product.image.thumbnail[settings.MEDIUM_IMAGE].url

		'''if Brand.objects.filter(company=self.user.companyuser.company).exists():
			brandObj = Brand.objects.filter(company=self.user.companyuser.company).first()
			image=brandObj.image.thumbnail[settings.MEDIUM_IMAGE].url
		elif BrandDistributor.objects.filter(company=self.user.companyuser.company).exclude(brand__isnull=True).exists():
			brandObj = BrandDistributor.objects.filter(company=self.user.companyuser.company).first()
			image=brandObj.brand.first().image.thumbnail[settings.MEDIUM_IMAGE].url'''

		return image

	def __unicode__(self):
		#return '%s : %s'% (self.user.username, self.name)
		return '%s : %s'% (self.id, self.name)

	class Meta:
		#ordering = ('name',)
		unique_together = ('name', 'user')
		index_together = [
			["user", "id"],
		]

class ChannelType(models.Model):
	name = models.CharField(max_length = 20)
	credential_format = models.CharField(max_length = 20)
	file_format = models.CharField(max_length = 20)

	def __unicode__(self):
		return str(self.name)
	class Meta:
		ordering = ('name',)

class Channel(models.Model):
	channel_type = models.ForeignKey(ChannelType)
	name = models.CharField(max_length = 20)

	def __unicode__(self):
		return str(self.name)
	class Meta:
		ordering = ('name',)



class BuyerSegmentation(models.Model):
	segmentation_name = models.CharField(max_length = 50)
	#condition = models.TextField(default = 0)
	state = models.ManyToManyField(State, blank=True)
	city = models.ManyToManyField(City, blank=True)
	category = models.ManyToManyField(Category, blank=True)
	#active_buyers = models.PositiveIntegerField(default=0)
	last_generated = models.DateTimeField(auto_now=True)
	company = models.ForeignKey(Company)
	#group_type = models.CharField(choices=GROUP_TYPE, max_length=20)
	group_type = models.ManyToManyField(GroupType, blank=True)

	applozic_id = models.IntegerField(blank = True, null = True)
	buyer_grouping_type = models.CharField(choices=BUYER_GROUPING_TYPE, max_length=50, default='Location Wise')
	buyers = models.ManyToManyField(Company, related_name = 'group_buyers', blank=True)

	def active_buyers(self):
		if self.buyer_grouping_type == "Location Wise":
			group_type = self.group_type.values_list('id', flat=True)

			if self.city.count() == 0:
				city = City.objects.all().values_list('id', flat=True)
			else:
				city = self.city.values_list('id', flat=True)
			if self.category.count() == 0:
				category = Category.objects.all().values_list('id', flat=True)
			else:
				category = self.category.values_list('id', flat=True)

			###companyIds = Branch.objects.filter(Q(city__in=city)).values_list('company', flat=True)

			totalUser = Buyer.objects.filter(Q(selling_company = self.company, status='approved', buying_company__city__in=city, buying_company__category__in=category, group_type__in=group_type) | Q(buying_company__in=self.buyers.all())).values_list('buying_company', flat=True).distinct().count()

			#totalUser = CompanyUser.objects.filter(company__in=buyerIds, user__groups__name="administrator").values_list('user', flat=True).distinct().count()
		else:
			totalUser = self.buyers.count()
		return totalUser

	def save(self, *args, **kwargs):
		'''if self.pk is None:
			user = CompanyUser.objects.filter(company=self.company).first().user
			r = chat_create_group({"ofUserId":user.username, "groupName":user.username+" "+self.segmentation_name, "groupMemberList":[], "type":"5"})
			r = r.json()
			print r
			self.applozic_id = r["response"]["id"]'''

		self.segmentation_name = self.segmentation_name.title()
		super(BuyerSegmentation, self).save(*args, **kwargs)



	def __unicode__(self):
		return '%s' % (self.segmentation_name)

	class Meta:
		unique_together = ('segmentation_name', 'company')


class AssignGroups(models.Model):
	user = models.OneToOneField(User)
	groups = models.ManyToManyField(BuyerSegmentation)


class Push(models.Model):
	date = models.DateField(auto_now_add=True)
	time = models.DateTimeField(auto_now_add=True)
	push_type = models.CharField(choices=PUSH_TYPE, default='buyers', max_length=20)
	push_downstream = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')
	status = models.CharField(choices=PUSH_STATUS, default='In Progress', max_length=20)
	message = models.TextField(blank = True, null = True)
	buyer_segmentation = models.ForeignKey(BuyerSegmentation, related_name = 'push_buyer_segmentation', default=None, blank = True, null = True)
	single_company_push = models.ForeignKey(Company, related_name='single_push', default=None, blank = True, null = True)
	company = models.ForeignKey(Company)
	user = models.ForeignKey('auth.User')
	to_show = models.CharField(choices=YES_OR_NO, default='yes', max_length=10)
	sms = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')
	whatsapp = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')
	email = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')

	change_price_add = models.IntegerField(blank = True, null = True) #percentage add/remove
	change_price_fix = models.IntegerField(blank = True, null = True) #fix amount for all product
	change_price_add_amount = models.IntegerField(blank = True, null = True) #amount add/remove

	exp_desp_date = models.DateField(blank = True, null = True)

	shared_catalog = models.ForeignKey(Catalog, default=None, blank = True, null = True)

	expiry_date = models.DateTimeField(blank = True, null = True)

	def save(self, *args, **kwargs):
		if self.pk is None and self.expiry_date is None:
			todayDate = date.today()
			self.expiry_date = todayDate + timedelta(days=self.company.default_catalog_lifetime)
		print "push self.expiry_date", self.expiry_date

		super(Push, self).save(*args, **kwargs)

	def direct_users(self):
		buyers = Buyer.objects.filter(selling_company=self.company, status="approved").values_list('buying_company', flat=True)
		total_users = Push_User.all_objects.filter(push=self.id, buying_company__in=buyers).values_list('buying_company', flat=True).distinct().count()
		return total_users

	def total_users(self):
		total_users = Push_User.all_objects.filter(push=self.id).order_by('buying_company').values_list('buying_company', flat=True).distinct().count()
		return total_users

	def total_products_viewed(self):
		global buyers
		global pushUser
		pushUser = Push_User.all_objects.filter(push=self.id).select_related('catalog','selection').first()
		buyers = Push_User.all_objects.filter(push=self.id).order_by('buying_company').values_list('buying_company', flat=True).distinct()
		total_viewed = 0
		if pushUser and pushUser.catalog:
			total_viewed = CompanyProductView.objects.filter(product__in=pushUser.catalog.products.all(), company__in=buyers).count()
		#total_viewed = CompanyProductFlat.objects.filter(push_reference=self.id, is_viewed='yes').count()
		return total_viewed

	def total_viewed(self):
		global buyers
		global pushUser

		pushUser = Push_User.all_objects.filter(push=self.id).select_related('catalog','selection').first()
		buyers = Push_User.all_objects.filter(push=self.id).order_by('buying_company').values_list('buying_company', flat=True).distinct()
		total_viewed = 0
		if pushUser and pushUser.catalog:
			#total_viewed = CompanyCatalogView.objects.filter(catalog=pushUser.catalog, company__in=buyers).count()
			total_viewed = CompanyCatalogView.objects.filter(catalog=pushUser.catalog, company__in=buyers).aggregate(Sum('clicks')).get('clicks__sum', 0)
			if total_viewed is None:
				total_viewed = 0

		#total_viewed = Push_User.all_objects.filter(push=self.id, is_viewed='yes').count()
		return total_viewed



	def total_products(self):
		global pushUser

		'''catelog_ids = Push_Catalog.objects.filter(push=self.id).values_list('catalog', flat=True)
		selection_ids = Push_Selection.objects.filter(push=self.id).values_list('selection', flat=True)

		total_catelog_product = Product.objects.filter(Q(catalog__in=catelog_ids)).values_list('id', flat=True).count()
		total_selection_product = Selection.objects.filter(Q(id__in=selection_ids)).values_list('products', flat=True).count()

		total_products = total_catelog_product + total_selection_product

		return total_products'''

		'''totalProduct = 0
		pushUser = Push_User.all_objects.filter(push=self.id).select_related('catalog','selection').first()
		if pushUser:#Push_User.all_objects.filter(push=self.id).exists():
			#pushUser = Push_User.all_objects.filter(push=self.id).first()
			totalProduct = Push_User_Product.all_objects.filter(push=self.id, user=pushUser.user).values('product').distinct().count()
		'''

		totalProduct = PushSellerPrice.objects.filter(push=self.id).values_list('product', flat=True).distinct().count()

		return totalProduct

	def push_amount(self):
		#pushUserProductCount = CompanyProductFlat.objects.filter(push_reference=self.id, is_viewed='yes').count()

		return 0 #pushUserProductCount


	def title(self):
		global pushUser
		#pushUser = Push_User.all_objects.filter(push=self.id).select_related('catalog','selection').first()
		title = ""
		if pushUser:#Push_User.all_objects.filter(push=self.id).exists():
			#pushUser = Push_User.all_objects.filter(push=self.id).first()
			if pushUser.catalog is not None:
				title = pushUser.catalog.title
			elif pushUser.selection is not None:
				title = pushUser.selection.name
		return title

	def image(self):
		'''image = ""
		if Push_Catalog.objects.filter(push=self.id).exists():
			image = Push_Catalog.objects.filter(push=self.id)[0].catalog.thumbnail.url
		elif Push_Selection.objects.filter(push=self.id).exists():
			image = Push_Selection.objects.filter(push=self.id)[0].selection.products.all()[0].image.url
		return image'''
		global pushUser
		image = ""
		if pushUser:
			if pushUser.catalog:
				image = pushUser.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
			elif pushUser.selection:
				try:
					image = pushUser.selection.products.first().image.thumbnail[settings.MEDIUM_IMAGE].url
				except Exception:
					pass

		'''pushUserProduct = CompanyProductFlat.objects.filter(push_reference=self.id).first()
		if pushUserProduct:
			if pushUserProduct.catalog:
				image = pushUserProduct.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
			else:
				image = pushUserProduct.product.image.thumbnail[settings.MEDIUM_IMAGE].url'''
		return image

	def __unicode__(self):
		#return '%s : %s : %s : %s' % (self.company.name, self.buyer_segmentation.segmentation_name, self.message, self.date)
		return '%s : %s : %s' % (self.id, self.message, self.date)
	class Meta:
		index_together = [
			["company", "buyer_segmentation"],
		]
	'''class Meta:
		ordering = ('id',)'''

class Push_User(models.Model):
	push = models.ForeignKey(Push, related_name='push_users', default=None)
	user = models.ForeignKey(User, default=None, null=True, blank=True)
	is_viewed = models.CharField(choices=YES_OR_NO, default='no', max_length=5)
	selection = models.ForeignKey(Selection, related_name='push_user_selection_id', default=None, blank = True, null = True)
	catalog = models.ForeignKey(Catalog, related_name='push_user_catalog_id', default=None, blank = True, null = True)
	total_price = models.DecimalField(max_digits=19, decimal_places=2, db_index=True) #user's buying price

	selling_company = models.ForeignKey(Company, related_name = 'selling_companies_push', default=None, blank = True, null = True)
	buying_company = models.ForeignKey(Company, related_name = 'buying_companies_push', default=None, blank = True, null = True)
	selling_price = models.DecimalField(max_digits=19, decimal_places=2) #original price

	sms = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')
	whatsapp = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')
	email = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')

	full_catalog_orders_only = models.BooleanField(default=False)


	deleted = models.BooleanField(default=False)
	objects = SoftDeleteManager()
	all_objects = models.Manager()

	supplier_disabled = models.BooleanField(default=False)
	buyer_disabled = models.BooleanField(default=False)
	expiry_date = models.DateTimeField(blank = True, null = True)

	def save(self, *args, **kwargs):
		if self.pk is None and self.expiry_date is None:
			self.expiry_date = self.push.expiry_date
		#print "push_user self.expiry_date", self.expiry_date

		super(Push_User, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self.deleted = True
		self.save()
		#Push_User_Product.objects.filter(push=self.push, user=self.user, selling_company=self.selling_company, buying_company=self.buying_company).update(deleted=True)

	def __unicode__(self):
		#return '%s : %s' % (self.push, self.user)
		return '%s' % (self.id)

	class Meta:
		index_together = [
			["id", "buying_company"],
			["buying_company", "selling_company"],
			["user", "catalog"],
			["user", "selection"],
			["push", "selling_company"],
			["catalog", "selling_company"],
			["buying_company", "push", "user"],
			["buying_company", "catalog", "push"],
			["buying_company", "selection", "push"],
			["selling_company", "catalog", "push"],
			["selling_company", "user", "catalog"],
			["selling_company", "user", "selection"],

		]
		#ordering = ('user',)

class PushSellerPrice(models.Model):
	push = models.ForeignKey(Push)
	selling_company = models.ForeignKey(Company)
	product = models.ForeignKey(Product)
	price = models.DecimalField(max_digits=19, decimal_places=2)
	created_at = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return str(self.price)
	class Meta:
		unique_together = ('push', 'selling_company', 'product')
		index_together = [
			["push", "selling_company"],
			["push", "selling_company", "product"],
		]

class Push_User_Product(models.Model):
	push = models.ForeignKey(Push)
	user = models.ForeignKey(User)
	selection = models.ForeignKey(Selection, related_name='pup_selection', default=None, blank = True, null = True)
	catalog = models.ForeignKey(Catalog, related_name='pup_catalog', default=None, blank = True, null = True)
	product = models.ForeignKey(Product, related_name='pup_product')
	sku = models.CharField(max_length = 20)
	price = models.DecimalField(max_digits=19, decimal_places=2) #user's buying price
	is_viewed = models.CharField(choices=YES_OR_NO, default='no', max_length=5)

	selling_company = models.ForeignKey(Company, related_name = 'selling_companies_product', default=None, blank = True, null = True)
	buying_company = models.ForeignKey(Company, related_name = 'buying_companies_product', default=None, blank = True, null = True)
	selling_price = models.DecimalField(max_digits=19, decimal_places=2) #original price

	sms = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')
	whatsapp = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')
	email = models.CharField(choices=YES_OR_NO, max_length = 5, default='yes')

	viewed_date = models.DateField(blank = True, null = True)

	deleted = models.BooleanField(default=False)
	objects = SoftDeleteManager()
	all_objects = models.Manager()

	'''def save(self, *args, **kwargs):
		if self.is_viewed == 'yes':
			self.viewed_date = date.today()

		super(Push_User_Product, self).save(*args, **kwargs)'''

	def delete(self, *args, **kwargs):
		self.deleted = True
		self.save()

	def __unicode__(self):
		#return '%s : %s' % (self.user, self.product.title)
		return '%s : %s' % (self.id, self.sku)


	'''class Meta:
		index_together = [
			["buying_company", "product"],
			["user", "product"],
			["user", "selling_company"],
			["push", "user", "catalog"],
			["push", "user", "selection"],
			["id", "buying_company"],
			["push", "selling_company", "is_viewed"],

		]
	'''
	'''class Meta:
		ordering = ('push',)'''

'''
class Push_Result(models.Model):
	push = models.ForeignKey(Push, related_name='push_result', default=None)
	num_people_targeted = models.PositiveIntegerField(default=0)
	num_app_users = models.PositiveIntegerField(default=0)
	num_product_views = models.PositiveIntegerField(default=0)

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('push',)
'''
class Push_Catalog(models.Model):
	push = models.ForeignKey(Push, related_name='push_catalog', default=None)
	catalog = models.ForeignKey(Catalog, related_name='push_catalog_id', default=None)

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('push',)


class Push_Product(models.Model):
	push = models.ForeignKey(Push)
	product = models.ForeignKey(Product, related_name='push_product_id', default=None)

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('push',)

class Push_Selection(models.Model):
	push = models.ForeignKey(Push, related_name='push_selection', default=None)
	selection = models.ForeignKey(Selection, related_name='push_selection_id', default=None)

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('push',)

class Export(models.Model):
	channel = models.ForeignKey(Channel)
	date = models.DateField()
	time = models.DateTimeField()

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('id',)

class Export_Result(models.Model):
	export = models.ForeignKey(Export)
	file_path = models.CharField(max_length = 20)

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('export',)

class Export_Catalog(models.Model):
	export = models.ForeignKey(Export)
	catalog = models.ForeignKey(Catalog)

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('export_id',)

class Export_Product(models.Model):
	export = models.ForeignKey(Export)
	product = models.ForeignKey(Product)

	def __unicode__(self):
		return str(self.id)
	class Meta:
		ordering = ('export_id',)

class Invite(models.Model):
	company = models.ForeignKey(Company)
	relationship_type = models.CharField(choices=RELATIONSHIP_TYPE, default='None', max_length=20)
	date = models.DateField(auto_now=True)
	time = models.DateTimeField(auto_now=True)
	user = models.ForeignKey('auth.User')

	def __unicode__(self):
		return '%s : %s'% (self.id, self.relationship_type)
	'''class Meta:
		ordering = ('id',)'''

class Invitee(models.Model):
	invite = models.ForeignKey(Invite, default=None, null=True, blank=True)
	#invitee_number = models.PositiveIntegerField()
	country = models.ForeignKey(Country, related_name='invitee_country', default=1)
	invitee_number = models.CharField(max_length=13)#validators=[phone_regex],
	invitee_company = models.CharField(max_length = 100, null=True, blank=True)
	invitee_name = models.CharField(max_length = 100)
	status = models.CharField(choices=INVITE_STATUS, default='invited', max_length=20)
	registered_user = models.ForeignKey(User, default=None, null=True, blank=True)
	invite_type = models.CharField(choices=INVITE_TYPE, default='userinvitation', max_length=20)
	invitation_type = models.CharField(choices=INVITATION_TYPE, max_length=20)
	###group_type = models.ForeignKey(GroupType)

	def __unicode__(self):
		return '%s : %s' % (self.id, self.invitee_number)
	class Meta:
		index_together = [
			["invite", "country"],
		]

class Warehouse(models.Model):
	company = models.ForeignKey(Company)
	name = models.CharField(max_length=100)
	supplier = models.ManyToManyField(Company, related_name = 'suppliers', blank=True)
	salesmen = models.ManyToManyField(User, blank=True)

	def __unicode__(self):
		return '%s : %s'% (self.id, self.name)

class Logistics(models.Model):
	name = models.CharField(max_length=250)

	def __unicode__(self):
		return '%s : %s'% (self.id, self.name)

class Buyer(models.Model):
	selling_company = models.ForeignKey(Company, related_name = 'selling_companies', default=None, blank = True, null = True)
	buying_company = models.ForeignKey(Company, related_name = 'buying_companies', default=None, blank = True, null = True)
	status = models.CharField(choices=BUYER_STATUS, max_length=50)
	fix_amount = models.DecimalField(max_digits=19 , decimal_places=2, default=Decimal('0.00'))
	percentage_amount = models.DecimalField(max_digits=19 , decimal_places=2, default=Decimal('0.00'))
	invitee = models.ForeignKey(Invitee, related_name = 'invitee_id', default=None, blank = True, null = True)
	#group_type = models.CharField(choices=GROUP_TYPE, max_length=20)
	group_type = models.ForeignKey(GroupType, blank = True, null = True)

	payment_duration = models.IntegerField(default=0)
	discount = models.DecimalField(max_digits=10 , decimal_places=2, default=None, blank = True, null = True)
	cash_discount = models.DecimalField(max_digits=10 , decimal_places=2, default=None, blank = True, null = True)

	credit_limit = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))

	broker_company = models.ForeignKey(Company, related_name = 'broker_companies', default=None, blank = True, null = True)
	brokerage_fees = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))

	warehouse = models.ForeignKey(Warehouse, default=None, blank = True, null = True)
	is_visible = models.BooleanField(default=False)

	supplier_approval = models.BooleanField(default=False)
	buyer_approval = models.BooleanField(default=False)

	preferred_logistics = models.ForeignKey(Logistics, default=None, blank = True, null = True)
	buyer_type = models.CharField(choices=BUYER_TYPE, max_length=20, default='Relationship')
	details = models.TextField(blank=True, null=True)

	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)
	created_at = models.DateField(auto_now_add=True)

	created_type = models.CharField(choices=BUYER_TYPE, max_length=20, default='Relationship')

	enquiry_catalog = models.ForeignKey(Catalog, default=None, blank = True, null = True)
	enquiry_item_type = models.CharField(choices=ENQUIRY_ITEM_TYPE, max_length=20, default=None, blank = True, null = True)
	enquiry_quantity = models.IntegerField(default=0)

	buying_company_name = models.CharField(max_length=250, default=None, blank = True, null = True)
	buying_person_name = models.CharField(max_length=250, default=None, blank = True, null = True)
	supplier_person_name = models.CharField(max_length=250, default=None, blank = True, null = True)

	refer_userinvitation_id = models.IntegerField(default=None, blank = True, null = True)

	modified = models.DateTimeField(auto_now=True)


	def __init__(self, *args, **kwargs):
		super(Buyer, self).__init__(*args, **kwargs)
		self.old_status = self.status

	def final_discount(self):
		global cbg
		cbg = None
		if self.selling_company is not None and self.status.lower() == "rejected":
			cbg = CompanyBuyerGroup.objects.filter(company=self.selling_company, buyer_type="Public").first()
			if cbg:
				return cbg.discount
		if self.discount is None or self.discount < Decimal('0.01'):
			if self.selling_company is not None and self.group_type is not None:
				buyer_type = companyBuyerGroupType(self.group_type.name)
				cbg = CompanyBuyerGroup.objects.filter(company=self.selling_company, buyer_type=buyer_type).first()
				if cbg:
					return cbg.discount
			elif self.selling_company is not None and self.status.lower() != "approved":
				cbg = CompanyBuyerGroup.objects.filter(company=self.selling_company, buyer_type="Public").first()
				if cbg:
					return cbg.discount
		if self.discount is None:
			return Decimal('0.00')

		return self.discount

	def final_cash_discount(self):
		if self.selling_company is not None and self.status.lower() == "rejected":
			cbg = CompanyBuyerGroup.objects.filter(company=self.selling_company, buyer_type="Public").first()
			if cbg:
				return cbg.cash_discount
		if self.cash_discount is None or self.cash_discount < Decimal('0.01'):
			if self.selling_company is not None and self.group_type is not None:
				buyer_type = companyBuyerGroupType(self.group_type.name)
				cbg = CompanyBuyerGroup.objects.filter(company=self.selling_company, buyer_type=buyer_type).first()
				if cbg:
					return cbg.cash_discount
			elif self.selling_company is not None and self.status.lower() != "approved":
				cbg = CompanyBuyerGroup.objects.filter(company=self.selling_company, buyer_type="Public").first()
				if cbg:
					return cbg.cash_discount
		if self.cash_discount is None:
			return Decimal('0.00')

		return self.cash_discount

	def save(self, *args, **kwargs):
		print "=============================Buyer - def save(==================================", self.id
		if self.selling_company is not None and self.status not in ["supplier_registrationpending","supplier_pending","rejected"]:
			self.supplier_approval = True
		if self.buying_company  is not None and self.status not in ["buyer_registrationpending","buyer_pending","rejected"]:
			self.buyer_approval = True

		if self.status != self.old_status or self.pk is None:
			if self.status == "approved":
				#groupObjs = BuyerSegmentation.objects.filter(Q(company=self.selling_company, group_type=self.group_type, buyer_grouping_type="Location Wise") | Q(company=self.selling_company, buyer_grouping_type="Custom", buyers=self.buying_company)).exclude(applozic_id__isnull=True)
				groupApplozicIds = BuyerSegmentation.objects.filter(Q(company=self.selling_company, group_type=self.group_type, buyer_grouping_type="Location Wise") | Q(company=self.selling_company, buyer_grouping_type="Custom", buyers=self.buying_company)).exclude(applozic_id__isnull=True).values_list('applozic_id', flat=True).distinct()
				groupApplozicIds = list(groupApplozicIds)
				userIds = CompanyUser.objects.filter(company=self.buying_company).values_list('user__username', flat=True).distinct()
				userIds = list(userIds)

				ofUserId = self.selling_company.chat_admin_user.username #CompanyUser.objects.filter(company=self.selling_company).values_list('user__username', flat=True).first()

				if len(userIds) > 0:
					chat_add_members_in_groups({'clientGroupIds':groupApplozicIds, 'userIds':userIds, 'ofUserId':str(ofUserId)})
				'''for groupObj in groupObjs:
					chat_add_members_in_groups({'clientGroupIds':[str(groupObj.applozic_id)], 'userIds':userIds, 'ofUserId':str(ofUserId)})
					for userId in userIds:
						r = chat_add_member_in_group({'clientGroupId':str(groupObj.applozic_id), 'userId':str(userId), 'ofUserId':str(ofUserId)})'''

				if self.selling_company.buyers_assigned_to_salesman == True and self.selling_company.salesman_mapping == "Location":
					slObjs = SalesmanLocation.objects.filter(Q(salesman__companyuser__company=self.selling_company, state=self.buying_company.state) & (Q(city=self.buying_company.city) | Q(city__isnull=True)))
					for slObj in slObjs:
						bsObj, created = BuyerSalesmen.objects.get_or_create(salesman=slObj.salesman)
						bsObj.buyers.add(self.buying_company.id)
						bsObj.save()

			if self.status == "rejected":
				#groupObjs = BuyerSegmentation.objects.filter(Q(company=self.selling_company, group_type=self.group_type, buyer_grouping_type="Location Wise") | Q(company=self.selling_company, buyer_grouping_type="Custom", buyers=self.buying_company)).exclude(applozic_id__isnull=True)
				groupApplozicIds = BuyerSegmentation.objects.filter(Q(company=self.selling_company, group_type=self.group_type, buyer_grouping_type="Location Wise") | Q(company=self.selling_company, buyer_grouping_type="Custom", buyers=self.buying_company)).exclude(applozic_id__isnull=True).values_list('applozic_id', flat=True).distinct()
				groupApplozicIds = list(groupApplozicIds)
				userIds = CompanyUser.objects.filter(company=self.buying_company).values_list('user__username', flat=True).distinct()
				userIds = list(userIds)

				ofUserId = self.selling_company.chat_admin_user.username #CompanyUser.objects.filter(company=self.selling_company).values_list('user__username', flat=True).first()

				if len(userIds) > 0:
					chat_remove_members_from_groups({'clientGroupIds':groupApplozicIds, 'userIds':userIds, 'ofUserId':str(ofUserId)})
				'''for groupObj in groupObjs:
					chat_remove_members_from_groups({'clientGroupIds':[str(groupObj.applozic_id)], 'userIds':userIds, 'ofUserId':str(ofUserId)})
					for userId in userIds:
						r = chat_remove_member_from_group({'clientGroupId':str(groupObj.applozic_id), 'userId':str(userId), 'ofUserId':str(ofUserId)})'''

				if self.selling_company.buyers_assigned_to_salesman == True and self.selling_company.salesman_mapping == "Location":
					slObjs = SalesmanLocation.objects.filter(Q(salesman__companyuser__company=self.selling_company, state=self.buying_company.state) & (Q(city=self.buying_company.city) | Q(city__isnull=True)))
					for slObj in slObjs:
						bsObj, created = BuyerSalesmen.objects.get_or_create(salesman=slObj.salesman)
						bsObj.buyers.remove(self.buying_company.id)
						bsObj.save()

				groupObjs = BuyerSegmentation.objects.filter(company=self.selling_company, buyers=self.buying_company)#buyer_grouping_type="Custom",
				for groupObj in groupObjs:
					print "to remove buyers"
					groupObj.buyers.remove(self.buying_company.id)
					groupObj.save()

				# #changes for companyproductflat table
				# #CompanyProductFlat.objects.filter(selling_company=self.selling_company, buying_company=self.buying_company).delete()
				# #Push_User.objects.filter(selling_company=self.selling_company, buying_company=self.buying_company).delete()
				# #commented below logic because server goes down on reject request. ex. supplier trivenisaree reject
				# suppliers = Buyer.objects.filter(buying_company=self.buying_company, status="approved").exclude(selling_company=self.selling_company).values_list('selling_company', flat=True)
				# catalogIds = CompanyProductFlat.objects.filter(selling_company=self.selling_company, buying_company=self.buying_company).exclude(catalog__isnull=True).values_list('catalog', flat=True)
				# print "catalogIds"
				# print catalogIds
				# for catalogId in catalogIds:
				# 	print "catalogId"
				# 	print catalogId
				#
				# 	pushUserObjId = Push_User.objects.filter(selling_company__in=suppliers, buying_company=self.buying_company, catalog=catalogId).values('buying_company','catalog','selling_company').annotate(Max('id')).values('id__max')
				# 	pushUser = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first()
				# 	if pushUser:
				# 		cpfObjs = CompanyProductFlat.objects.filter(selling_company=self.selling_company, buying_company=self.buying_company, catalog=catalogId)
				# 		for cpfObj in cpfObjs:
				# 			print "CompanyProductFlat id===="
				# 			print cpfObj.id
				# 			cpfObj.selling_company = pushUser.selling_company
				# 			pspObj = PushSellerPrice.objects.filter(selling_company=pushUser.selling_company, product=cpfObj.product, push=pushUser.push).first()
				# 			if pspObj:
				# 				cpfObj.final_price = pspObj.price
				#
				# 				print "final_price========"
				# 				print pspObj.price
				#
				# 				buyerObj = Buyer.objects.filter(selling_company=pushUser.selling_company, buying_company=self.buying_company, status="approved").first()
				# 				sellPrice = (pspObj.price+buyerObj.fix_amount) + ((pspObj.price*buyerObj.percentage_amount)/100)
				# 				print "sellPrice========"
				# 				print sellPrice
				# 				cpfObj.selling_price = sellPrice
				#
				# 			cpfObj.save()
				# 	else:
				# 		CompanyProductFlat.objects.filter(selling_company=self.selling_company, buying_company=self.buying_company, catalog=catalogId).delete()
				# Push_User.objects.filter(selling_company=self.selling_company, buying_company=self.buying_company).delete()
				# #end changes for companyproductflat table


		if self.buyer_type == "Enquiry" and self.status in ["approved", "rejected"]:
			self.buyer_type = "Relationship"

		'''user = self.request.user
		if not user.is_staff and self.status == "rejected":
			print "not user.is_staff"
			company = user.companyuser.company
			if self.selling_company == company:
				print "sel00"
				self.supplier_approval = False
			elif self.buying_company == company:
				print "buy11"
				self.buyer_approval = False'''
		if self.buying_company and self.buying_company.name_updated:
			self.buying_company_name = self.buying_company.name

		return super(Buyer, self).save(*args, **kwargs)

	def __unicode__(self):
		#if self.selling_company is not None and self.buying_company is not None:
		#	return '%s : %s' % (self.selling_company.name, self.buying_company.name)
		return '%s' % (self.id)

	class Meta:
		#ordering = ('id',)
		unique_together = ('selling_company', 'buying_company')
		index_together = [
			["selling_company", "buying_company"],
			["selling_company", "group_type"],
			["selling_company", "buying_company", "group_type"],
		]


class Message(models.Model):
	sender_user = models.ForeignKey(User, related_name='sender_set')
	body = models.TextField(max_length=160)
	receiver_user = models.ForeignKey(User, related_name='receiver_set')
	datetime = models.DateTimeField(auto_now=True)
	subject = models.CharField(max_length=20)
	mtype = models.CharField(choices=MESSAGE_TYPE, max_length=20, blank=True)
	status = models.CharField(choices=MESSAGE_STATUS, default='unread', max_length=20)

	def __unicode__(self):
		return str(self.subject)
	class Meta:
		ordering = ('datetime',)

def message_init(sender, instance, **kwargs):
	if kwargs['created']:
		MessageFolder(message=instance, folder='inbox').save()
		MessageFolder(message=instance, folder='sent').save()
post_save.connect(message_init, sender=Message, dispatch_uid='message_init_unique')

# def send_notification(sender, instance, **kwargs):
# 	devices = GCMDevice.objects.all()
# 	devices.send_message("You've got mail")
# 	devices.send_message(None, extra={"foo": "bar"})

# post_save.connect(send_notification, sender = Message, dispatch_uid = 'send_notification_unique')

class MessageFolder(models.Model):
	message = models.ForeignKey(Message, related_name='message_folder_set')
	folder = models.CharField(choices=MESSAGE_FOLDER, default='', max_length=20)
	# status = models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.folder)
	class Meta:
		ordering = ('folder',)

class Meeting(models.Model):
	salesorder = models.ManyToManyField(SalesOrder, related_name='meeting', blank=True)
	user = models.ForeignKey('auth.User')
	company = models.ForeignKey(Company, related_name = 'meeting_user_company', default=None, blank = True, null = True)
	buying_company_ref = models.ForeignKey(Company, related_name = 'meeting_buying_company', default=None, blank = True, null = True)
	start_datetime = models.DateTimeField()
	end_datetime = models.DateTimeField(blank=True, null=True)
	duration = models.DurationField(blank=True, null=True)
	start_lat = models.FloatField()
	start_long = models.FloatField()
	end_lat = models.FloatField(blank=True, null=True)
	end_long = models.FloatField(blank=True, null=True)
	status = models.CharField(choices=MEETING_STATUS, default='pending', max_length=20)
	note = models.TextField(blank = True, null = True)
	purpose = models.CharField(max_length=200, null=True, blank=True)
	buyer_name_text = models.CharField(max_length=200, null=True, blank=True)

	location_address = models.TextField(default=None, blank = True, null = True)
	location_city = models.CharField(max_length=250, default=None, blank = True, null = True)
	location_state = models.CharField(max_length=250, default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def total_products(self):
		if self.end_datetime is not None and self.buying_company_ref is not None:
			salesorders = SalesOrder.objects.filter(created_at__lte=self.end_datetime+timedelta(minutes=5), created_at__gte=self.start_datetime-timedelta(minutes=5), user=self.user, company=self.buying_company_ref).values_list('id', flat=True)
			salesorders = list(salesorders)

			#totalProducts = SalesOrderItem.objects.filter(sales_order=self.salesorder.all()).aggregate(Sum('quantity')).get('quantity__sum', 0)
			totalProducts = SalesOrderItem.objects.filter(sales_order__in=salesorders).aggregate(Sum('quantity')).get('quantity__sum', 0)
			if totalProducts is None:
				totalProducts = 0
			return totalProducts
		else:
			return 0

	def __unicode__(self):
		return '%s : %s'% (self.id, self.start_datetime)

	def save(self, *args, **kwargs):
		if self.end_datetime:
			self.duration = self.end_datetime-self.start_datetime
		if self.buyer_name_text == "" and self.note != "":
			self.buyer_name_text = self.note

		if self.buying_company_ref:
			if self.buying_company_ref.address:
				self.buying_company_ref.address.latitude=self.start_lat
				self.buying_company_ref.address.longitude=self.start_long
				self.buying_company_ref.address.save()

		return super(Meeting, self).save(*args, **kwargs)

class Language(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=50)

	def save(self, *args, **kwargs):
		self.name = self.name.title()
		super(Language, self).save(*args, **kwargs)

	def __unicode__(self):
		return '%s' % (self.name)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	alternate_email = models.EmailField(blank=True)
	country = models.ForeignKey(Country, related_name='user_country', default=1)
	phone_number = models.CharField(max_length=13)#, unique=True, validators=[phone_regex],
	phone_number_verified = models.CharField(choices=YES_OR_NO, default='no', max_length=10)
	whatsapp_verified = models.CharField(choices=YES_OR_NO, default='no', max_length=10)
	user_image = models.ImageField(upload_to='user_image', null=True, blank=True)
	tnc_agreed = models.BooleanField(default=True)
	warehouse = models.ForeignKey(Warehouse, default=None, blank = True, null = True)
	#company_name = models.CharField(max_length = 30, blank=True)
	#invite_id = models.PositiveIntegerField(blank=True, null=True)
	is_profile_set = models.BooleanField(default=True)
	first_login = models.DateTimeField(null=True, blank=True)
	browser_notification_disable = models.BooleanField(default=False)
	last_login_platform = models.CharField(choices=LOGIN_PLATFORM, max_length=20, default=None, blank = True, null = True)

	is_password_set = models.BooleanField(default=False)
	user_approval_status = models.CharField(choices=APPROVAL_STATUS, max_length=20, default="Approved")

	language = models.ForeignKey(Language, default=2, blank = True, null = True)
	send_sms_to_contacts = models.BooleanField(default=True)

	company_name = models.CharField(max_length = 100, default=None, blank = True, null = True)

	sugar_crm_user_id = models.CharField(max_length=250, default=None, blank = True, null = True)

	modified = models.DateTimeField(auto_now=True)

	uninstall_date  = models.DateField(blank = True, null = True)

	def __unicode__(self):
		return '%s : %s' % (self.id, self.phone_number)

	def user_image_url(self):
		return '%s%s' % (settings.MEDIA_URL, self.user_image)

	class Meta:
		index_together = [
			["user", "country"],
		]

def create_user_profile(sender, instance, **kwargs):
	if kwargs['created']:
		UserProfile(user=instance).save()
		#UserProfile.objects.get_or_create(user=instance)
		if settings.DEBUG == False:
			user_to_crm(instance.id,created = True)

	user = User.objects.get(pk=instance.id)
	print "in create_user_profile password is set=", instance.has_usable_password()
	user.userprofile.is_password_set = instance.has_usable_password()
	user.userprofile.save()

post_save.connect(create_user_profile, sender = User, dispatch_uid = 'create_user_profile_unique')

'''class Invoice(models.Model):
	company = models.ForeignKey(Company, related_name = 'invoice_company')
	charges_amount = models.PositiveIntegerField(blank=True, null=True)
	credit_amount = models.PositiveIntegerField(blank=True, null=True)
	net_value = models.PositiveIntegerField(blank=True, null=True)
	payment_status = models.CharField(choices=INVOICE_STATUS, default='pending', max_length=20)
	payment_datetime = models.DateTimeField(null=True, blank=True)
	start_date = models.DateField()
	end_date = models.DateField()
	push = models.ManyToManyField(Push)

	def __unicode__(self):
		return '%s : %s'% (self.id, self.start_date)

class InvoiceCredit(models.Model):
	company = models.ForeignKey(Company, related_name = 'invoice_credit_company')
	credit_amount = models.PositiveIntegerField()
	created_date = models.DateTimeField(auto_now=True)
	expire_date = models.DateField()

	def __unicode__(self):
		return '%s : %s'% (self.id, self.credit_amount)'''

class WishbookInvoice(models.Model):
	company = models.ForeignKey(Company)
	billed_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	balance_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	discount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	status = models.CharField(choices=INVOICE_STATUS, default='pending', max_length=20)

	start_date = models.DateField()
	end_date = models.DateField()

	def __unicode__(self):
		return '%s'% (self.id)

class WishbookInvoiceItem(models.Model):
	company = models.ForeignKey(Company)
	invoice = models.ForeignKey(WishbookInvoice, default=None, blank=True, null=True)

	start_date = models.DateField()
	end_date = models.DateField()

	item_type = models.CharField(max_length=200)

	qty = models.PositiveIntegerField(blank=True, null=True)
	rate = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)

	def __unicode__(self):
		return '%s'% (self.id)

class WishbookCredit(models.Model):
	company = models.ForeignKey(Company)
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	balance_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	expire_date = models.DateField()

	def __unicode__(self):
		return '%s'% (self.id)

class WishbookInvoiceCredit(models.Model):
	invoice = models.ForeignKey(WishbookInvoice)
	credit = models.ForeignKey(WishbookCredit)
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)

	def __unicode__(self):
		return '%s'% (self.id)

class WishbookPayment(models.Model):
	company = models.ForeignKey(Company)
	instrument = models.CharField(max_length=200)
	date = models.DateField()
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	detail = models.CharField(max_length=200)

	def __unicode__(self):
		return '%s'% (self.id)

class WishbookInvoicePayment(models.Model):
	invoice = models.ForeignKey(WishbookInvoice)
	payment = models.ForeignKey(WishbookPayment)
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)

	def __unicode__(self):
		return '%s'% (self.id)

class RegistrationOTP(models.Model):
	country = models.ForeignKey(Country, related_name='otp_country', default=1)
	phone_number = models.CharField(max_length=13)#, unique=True, validators=[phone_regex],
	otp = models.PositiveIntegerField()
	created_date = models.DateTimeField(auto_now=True)
	is_verified = models.CharField(choices=YES_OR_NO, default='no', max_length=10)

	def __unicode__(self):
		return '%s : %s'% (self.phone_number, self.otp)

class ImageTest(models.Model):
	images = VersatileImageField(
		upload_to='images_test/',
		ppoi_field='images_ppoi'
	)
	image_optional = VersatileImageField(
		upload_to='images_test/',
		blank=True,
		placeholder_image=OnStoragePlaceholderImage(
			path='placeholder.gif'
		)
	)
	images_ppoi = PPOIField()
	##history = HistoricalRecords()
	deleted = models.BooleanField(default=False)

	objects = SoftDeleteManager()
	all_objects = models.Manager()

	created_by = CreatingUserField(related_name = "created_categories")
	created_with_session_key = CreatingSessionKeyField()
	audit_log = AuditLog()

	#objects = models.Manager()
	#all_objects = SoftDeleteManager()
	def delete(self, *args, **kwargs):
		self.deleted = True
		self.save()
	def __init__(self, *args, **kwargs):
		#print "ImageTest __init__", args, kwargs
		super(ImageTest, self).__init__(*args, **kwargs)
		self.old_deleted = self.deleted
	def save(self, **kwargs):
		if self.deleted != self.old_deleted:
			print "deleted changed - was : %s - now : %s" %(self.old_deleted, self.deleted)
		super(ImageTest, self).save(**kwargs)

class PromotionalNotification(models.Model):
	title = models.CharField(max_length=200)
	#category = models.ManyToManyField(Category, blank=True)
	state = models.ManyToManyField(State, blank=True)
	city = models.ManyToManyField(City, blank=True)
	user = models.ManyToManyField(User, blank=True)
	text = models.TextField()

	manufacturer = models.BooleanField(default=False)
	wholesaler_distributor = models.BooleanField(default=False)
	retailer = models.BooleanField(default=False)
	online_retailer_reseller = models.BooleanField(default=False)
	broker = models.BooleanField(default=False)
	company_type_not_selected = models.BooleanField(default=False)

	image = models.ImageField(upload_to='promotional_notification', default=None, null=True, blank=True)

	app_version = models.CharField(max_length=250, default=None, blank = True, null = True)
	last_login_platform = models.CharField(choices=LOGIN_PLATFORM, max_length=20, default=None, blank = True, null = True)
	deep_link = models.URLField(default=None, blank = True, null = True)

class UpdateNotification(models.Model):
	title = models.CharField(max_length=200)
	text = models.TextField()
	update_for = models.CharField(choices=UPDATE_FOR, default='Android', max_length=30)
	app_version_code = models.PositiveIntegerField()

class Stock(models.Model):
	warehouse = models.ForeignKey(Warehouse, default=None, blank=True, null=True)
	company = models.ForeignKey(Company, default=None, blank=True, null=True)
	#brand = models.ForeignKey(Brand, default=None, blank=True, null=True)
	#catalog = models.ForeignKey(Catalog, default=None, blank=True, null=True)
	product = models.ForeignKey(Product)
	in_stock = models.IntegerField(default=0)
	available = models.IntegerField(default=0)
	blocked = models.IntegerField(default=0)
	open_sale = models.IntegerField(default=0)
	open_purchase = models.IntegerField(default=0)

	def __unicode__(self):
		return '%s : %s'% (self.id, self.in_stock)

	def save(self, *args, **kwargs):
		if self.company is None and self.warehouse is not None:
			self.company = self.warehouse.company
		return super(Stock, self).save(*args, **kwargs)

	class Meta:
		unique_together = ('warehouse', 'product',)
		index_together = [
			["warehouse", "product"],
		]

class WarehouseStock(models.Model):
	warehouse = models.ForeignKey(Warehouse)
	product = models.ForeignKey(Product)
	in_stock = models.IntegerField(default=0)
	def __unicode__(self):
		return '%s : %s'% (self.id, self.in_stock)

	class Meta:
		unique_together = ('warehouse', 'product',)
		index_together = [
			["warehouse", "product"],
		]

class OpeningStock(models.Model):
	warehouse = models.ForeignKey(Warehouse, default=None, blank=True, null=True)
	company = models.ForeignKey(Company, default=None, blank=True, null=True)
	#created_at = models.DateTimeField(auto_now_add=True)
	date = models.DateField()
	remark = models.CharField(max_length=200, blank = True, null = True)
	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)
	upload_file = models.FileField(upload_to='opening_stock_upload_file', null=True, blank=True)
	error_file = models.FileField(upload_to='opening_stock_error_file', null=True, blank=True)

	def __unicode__(self):
		return '%s'% (self.date)

	def save(self, *args, **kwargs):
		if self.company is None and self.warehouse is not None:
			self.company = self.warehouse.company
		return super(OpeningStock, self).save(*args, **kwargs)

class OpeningStockQty(models.Model):
	opening_stock = models.ForeignKey(OpeningStock, blank = True, null = True) #set null for bulk create from OpeningStock
	product = models.ForeignKey(Product)
	in_stock = models.IntegerField(default=0)

	def __unicode__(self):
		return '%s'% (self.in_stock)

class InventoryAdjustment(models.Model):
	warehouse = models.ForeignKey(Warehouse, default=None, blank=True, null=True)
	company = models.ForeignKey(Company, default=None, blank=True, null=True)
	#created_at = models.DateTimeField(auto_now_add=True)
	date = models.DateField()
	remark = models.CharField(max_length=200, blank = True, null = True)
	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)
	upload_file = models.FileField(upload_to='adjustment_stock_upload_file', null=True, blank=True)
	error_file = models.FileField(upload_to='adjustment_stock_error_file', null=True, blank=True)

	def __unicode__(self):
		return '%s'% (self.date)

	def save(self, *args, **kwargs):
		if self.company is None and self.warehouse is not None:
			self.company = self.warehouse.company
		return super(InventoryAdjustment, self).save(*args, **kwargs)

class InventoryAdjustmentQty(models.Model):
	inventory_adjustment = models.ForeignKey(InventoryAdjustment, blank = True, null = True) #set null for bulk create from InventoryAdjustment
	product = models.ForeignKey(Product)
	quantity = models.IntegerField(default=0)
	adjustment_type = models.CharField(choices=ADJUSTMENT_QTY_STATUS, max_length=20)
	to_warehouse = models.ForeignKey(Warehouse, default=None, blank = True, null = True)

	def __unicode__(self):
		return '%s'% (self.quantity)

class ProductStatus(models.Model):
	company = models.ForeignKey(Company)
	product = models.ForeignKey(Product)
	status = models.CharField(choices=ENABLE_DISABLE, default='Disable', max_length=20)
	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		index_together = [
			["company", "product"],
		]

class CatalogSelectionStatus(models.Model):
	company = models.ForeignKey(Company)
	catalog = models.ForeignKey(Catalog, default=None, blank = True, null = True)
	selection = models.ForeignKey(Selection, default=None, blank = True, null = True)
	status = models.CharField(choices=ENABLE_DISABLE, default='Disable', max_length=20)
	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		index_together = [
			["company", "catalog"],
			["company", "selection"],
		]

@receiver(post_save, sender=CatalogSelectionStatus)
def catalog_selection_status_postsave(sender, instance, **kwargs):
	print "catalog_selection_status_postsave"
	if instance.status == "Disable":
		print "Disable"
		users = UserWishlist.objects.filter(catalog=instance.catalog).values_list('user', flat=True)
		users = list(users)
		if len(users) > 0:
			print "wishlist noti"
			notify = True
			if instance.catalog.view_permission == "public":
				dtnow = datetime.now()
				if CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow, catalog=instance.catalog).exists():
					notify = False

			if notify:
				print "notify true"
				#companyImage = instance.catalog.brand.image.thumbnail[settings.MEDIUM_IMAGE].url
				pushImage = instance.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
				jsondata = {"push_id": int(instance.catalog.id),"notId":int(instance.catalog.id),"push_type":"catalog","image":pushImage, "company_image":"", "title":instance.catalog.title, "name":instance.catalog.title, "table_id": int(instance.catalog.id)}
				# message = instance.catalog.title+" catalog from your Wishlist is now out-of-stock."
				message = notificationTemplates("wishlist_catalog_disable")% (instance.catalog.title)
				# if settings.TASK_QUEUE_METHOD == 'celery':
				# 	notificationSend.apply_async((users, message, jsondata), expires=datetime.now() + timedelta(days=2))
				# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				# 	task_id = async(
				# 		'api.tasks.notificationSend',
				# 		users, message, jsondata
				# 	)
				sendNotifications(users, message, jsondata)

class App(models.Model):
	name = models.CharField(max_length=100, unique=True)
	api_min_version = models.CharField(max_length=100)
	api_max_version = models.CharField(max_length=100)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.name)

class AppInstance(models.Model):
	app = models.ForeignKey(App, related_name = 'instance_app')
	company = models.ForeignKey(Company, related_name = 'instance_company')
	account_url = models.TextField(blank = True, null = True)
	#user = models.ForeignKey(User, related_name = 'instance_user')

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.id)

	class Meta:
		unique_together = ('app', 'company')

class SKUMap(models.Model):
	app_instance = models.ForeignKey(AppInstance)
	product = models.ForeignKey(Product, default=None, blank = True, null = True)
	external_sku = models.CharField(max_length=100, blank = True, null = True)
	catalog = models.ForeignKey(Catalog, default=None, blank = True, null = True)
	external_catalog = models.CharField(max_length=100, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.external_sku)

	class Meta:
		#unique_together = ('app_instance', 'product')
		#unique_together = ('app_instance', 'external_sku')
		unique_together = ('app_instance', 'product', 'catalog')

		#index_together = [
		#	["product", "app_instance"],
		#]

class Barcode(models.Model):
	warehouse = models.ForeignKey(Warehouse)
	product = models.ForeignKey(Product)
	barcode = models.CharField(max_length=200, unique=True)
	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)

	def __unicode__(self):
		return '%s' % (self.barcode)
	class Meta:
		index_together = [
			["warehouse", "product"],
		]

class CompanyProductFlat(models.Model):
	product = models.ForeignKey(Product)
	buying_company = models.ForeignKey(Company, related_name = 'cpf_buying_company')
	final_price = models.DecimalField(max_digits=19, decimal_places=2) #buying price for buying company
	selling_price = models.DecimalField(max_digits=19, decimal_places=2)
	selection = models.ForeignKey(Selection, default=None, blank = True, null = True)
	catalog = models.ForeignKey(Catalog, default=None, blank = True, null = True)
	selling_company = models.ForeignKey(Company, related_name = 'cpf_selling_company')
	push_reference = models.ForeignKey(Push, default=None, blank = True, null = True)

	#status = models.CharField(choices=ENABLE_DISABLE, default='Enable', max_length=20)
	is_disable = models.BooleanField(default=False)
	like = models.BooleanField(default=False)
	is_salable = models.BooleanField(default=False)
	is_viewed = models.CharField(choices=YES_OR_NO, default='no', max_length=5)

	def __unicode__(self):
		return '%s : %s'% (self.id, self.product.id)

	class Meta:
		index_together = [
			["buying_company", "selection"],
			["buying_company", "catalog"],
			["product", "catalog", "buying_company"],
			["product", "selection", "buying_company"],
			["buying_company", "selling_company", "catalog"],
			["buying_company", "selling_company", "selection"],
			["product", "buying_company", "selling_company", "catalog"],
			["product", "buying_company", "selling_company", "selection"],

		]

class UnsubscribedNumber(models.Model):
	country = models.ForeignKey(Country)
	phone_number = models.CharField(max_length=13)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class SmsTransaction(models.Model):
	created_at = models.DateField(auto_now_add=True)
	total_sent = models.IntegerField(default=0)
	provider = models.CharField(max_length=50)

	class Meta:
		unique_together = ('created_at', 'provider')

class SmsError(models.Model):
	created_at = models.DateField(auto_now_add=True)
	sms_text = models.TextField() #models.CharField(max_length=250)
	mobile_no = models.CharField(max_length=15)
	is_sent = models.BooleanField(default=False)
	provider = models.CharField(max_length=50)
	error_text = models.CharField(max_length=250)

class Attendance(models.Model):
	user = models.ForeignKey('auth.User')
	company = models.ForeignKey(Company, related_name = 'attendance_user_company', default=None, blank = True, null = True)
	date_time = models.DateTimeField()
	action = models.CharField(choices=ATTENDANCE_ACTION, max_length=20)
	att_lat = models.FloatField(blank=True, null=True)
	att_long = models.FloatField(blank=True, null=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class CompanyAccount(models.Model):
	company = models.ForeignKey(Company)
	buyer_company = models.ForeignKey(Company, related_name = 'buyer')
	mapped_accout_ref = models.CharField(max_length=100)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class CronHistory(models.Model):
	cron_type = models.CharField(max_length=100)
	time = models.DateTimeField()


class CompanyKycTaxation(models.Model):
	company = models.OneToOneField(Company, related_name = 'kyc')
	pan = models.CharField(max_length=20, blank = True, null = True)
	gstin = models.CharField(max_length=20, blank = True, null = True)
	arn = models.CharField(max_length=20, blank = True, null = True)
	add_gst_to_price = models.BooleanField(default=True)

	company_type = models.CharField(choices=COMPANY_KYC_TYPE, max_length=50, default=None, blank = True, null = True)
	is_completed = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.company.name)

class SolePropreitorshipKYC(models.Model):
	company = models.OneToOneField(Company)
	#proprietor = models.CharField(max_length=250)
	full_name = models.CharField(max_length=250, blank=True, null=True)
	father_name = models.CharField(max_length=250, blank=True, null=True)
	spouse_name = models.CharField(max_length=250, blank=True, null=True)
	birth_date = models.DateField(blank = True, null = True)
	gender = models.CharField(choices=KYC_GENDER, max_length=20, blank=True, null=True)
	email = models.CharField(max_length = 255, blank=True, null=True)
	mobile_no = models.CharField(max_length=15, blank=True, null=True)
	pan_card = models.CharField(max_length= 15, blank=True, null=True)
	aadhar_card = models.CharField(max_length= 15, blank=True, null=True)
	address = models.TextField(blank=True, null=True)
	pincode = models.IntegerField(blank=True, null=True)
	state = models.CharField(max_length=50, blank=True, null=True)
	city = models.CharField(max_length=100, blank=True, null=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class CompanyCreditRating(models.Model):
	company = models.OneToOneField(Company)
	bureau_score = models.PositiveIntegerField(blank=True, null=True)
	bank_data_source = models.CharField(choices=BANK_DATA_SOURCE, max_length=50, blank = True, null = True)
	bank_statement_pdf =  models.FileField(upload_to='bank_statement_pdf', blank = True, null = True)
	bank_monthly_transaction_6m = models.PositiveIntegerField(blank=True, null=True)
	bank_average_balance_6m = models.PositiveIntegerField(blank=True, null=True)
	bank_check_bounces_6m = models.PositiveIntegerField(blank=True, null=True)
	salary = models.PositiveIntegerField(blank=True, null=True)
	gst_credit_rating = models.PositiveIntegerField(blank=True, null=True)
	average_payment_duration = models.CharField(choices=AVERAGE_PAYMENT_DURATION, max_length=20, default = None, blank = True, null = True)
	average_gr_rate = models.CharField(choices=AVERAGE_GR_RATE, max_length=20, default = None, blank = True, null = True)
	rating = models.CharField(choices=CREDIT_RATING, max_length=20, default="Unrated")

	bureau_report_rating = models.CharField(choices=REPORT_RATING, max_length=20, default = None, blank = True, null = True)
	financial_statement_rating = models.CharField(choices=REPORT_RATING, max_length=20, default = None, blank = True, null = True)

	bureau_type = models.CharField(choices=BUREAU_TYPE, max_length=20, default = None, blank = True, null = True)
	bureau_status = models.CharField(choices=BUREAU_STATUS, max_length=50, default = None, blank = True, null = True)
	bureau_xml = models.TextField(blank = True, null = True)
	bureau_order_id = models.CharField(max_length=250, default=None, blank = True, null = True)
	bureau_report_id = models.CharField(max_length=250, default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s : %s'% (self.id, self.bureau_score)

@receiver(post_save, sender=CompanyCreditRating)
def companycreditrating_postsave(sender, instance, **kwargs):
	if instance.bureau_score is not None and instance.bureau_score >= 700 and instance.rating != "Good":
		instance.rating = "Good"
		instance.save()
	elif instance.bureau_score is not None and instance.bureau_score > 0 and instance.bureau_score < 700 and instance.rating != "Poor":
		instance.rating = "Poor"
		instance.save()
	elif (instance.bureau_score is None or instance.bureau_score == 0) and instance.rating != "Unrated":
		instance.rating = "Unrated"
		instance.save()


class UserCreditSubmission(models.Model):
	company = models.ForeignKey(Company)
	bureau_score = models.PositiveIntegerField(blank=True, null=True)
	bank_data_source = models.CharField(choices=BANK_DATA_SOURCE, max_length=50, blank = True, null = True)
	bank_statement_pdf =  models.FileField(upload_to='bank_statement_pdf', blank = True, null = True)
	bank_monthly_transaction_6m = models.PositiveIntegerField(blank=True, null=True)
	bank_average_balance_6m = models.PositiveIntegerField(blank=True, null=True)
	bank_check_bounces_6m = models.PositiveIntegerField(blank=True, null=True)
	salary = models.PositiveIntegerField(blank=True, null=True)
	gst_credit_rating = models.PositiveIntegerField(blank=True, null=True)
	average_payment_duration = models.CharField(choices=AVERAGE_PAYMENT_DURATION, max_length=20, default = None, blank = True, null = True)
	average_gr_rate = models.CharField(choices=AVERAGE_GR_RATE, max_length=20, default = None, blank = True, null = True)
	rating = models.CharField(choices=CREDIT_RATING, max_length=20, default="Unrated")

	bureau_report_rating = models.CharField(choices=REPORT_RATING, max_length=20, default = None, blank = True, null = True)
	financial_statement_rating = models.CharField(choices=REPORT_RATING, max_length=20, default = None, blank = True, null = True)

	bureau_type = models.CharField(choices=BUREAU_TYPE, max_length=20, default = None, blank = True, null = True)
	bureau_status = models.CharField(choices=BUREAU_STATUS, max_length=50, default = None, blank = True, null = True)
	bureau_xml = models.TextField(blank = True, null = True)
	bureau_order_id = models.CharField(max_length=250, default=None, blank = True, null = True)
	bureau_report_id = models.CharField(max_length=250, default=None, blank = True, null = True)

	user = models.ForeignKey(User)

	created = models.DateTimeField(auto_now_add=True)


class CreditReference(models.Model):
	selling_company = models.ForeignKey(Company, related_name = 'selling_companies_cr')
	buying_company = models.ForeignKey(Company, related_name = 'buying_companies_cr')
	transaction_on_credit = models.BooleanField(default=False)
	number_transactions = models.PositiveIntegerField(blank=True, null=True)#per month
	transaction_value = models.CharField(choices=TRANSACTION_VALUE, max_length=50, default=None, blank = True, null = True)
	average_payment_duration = models.CharField(choices=AVERAGE_PAYMENT_DURATION, max_length=50, default=None, blank = True, null = True)
	average_gr_rate = models.CharField(choices=AVERAGE_GR_RATE, max_length=50, default=None, blank = True, null = True)
	remarks = models.TextField(blank = True, null = True)

	duration_of_work = models.CharField(choices=DURATION_OF_WORK, max_length=50, default=None, blank = True, null = True)

	buyer_requested = models.BooleanField(default=False)
	supplier_responded = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __init__(self, *args, **kwargs):
		super(CreditReference, self).__init__(*args, **kwargs)
		self.old_buyer_requested = self.buyer_requested
		self.old_supplier_responded = self.supplier_responded

	def save(self, *args, **kwargs):
		pk_value = self.pk

		super(CreditReference, self).save(*args, **kwargs)

		if (self.old_buyer_requested != self.buyer_requested or pk_value is None) and self.buyer_requested == True:
			notjson = {"notId": self.pk, "push_type":"credit_reference_buyer_requested", "company_id":self.buying_company.id, "table_id":self.pk, "title":"Buyer feedback request"}
			# message = str(self.buying_company.name)+" has requested you to rate them on the basis of their transaction history with your company. It will help them with getting the credit."
			message = notificationTemplates("credit_reference_rate_request")% (self.buying_company.name)
			user_ids = CompanyUser.objects.filter(company=self.selling_company).values_list('user', flat=True)
			# if settings.TASK_QUEUE_METHOD == 'celery':
			# 	notificationSend.apply_async((user_ids, message, notjson), expires=datetime.now() + timedelta(days=2))
			# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			# 	task_id = async(
			# 		'api.tasks.notificationSend',
			# 		user_ids, message, notjson
			# 	)
			sendNotifications(user_ids, message, notjson)

		'''if (self.old_supplier_responded != self.supplier_responded or pk_value is None) and self.supplier_responded == True:
			notjson = {"notId": self.pk, "push_type":"credit_reference_supplier_responded", "company_id":self.selling_company.id, "table_id":self.pk, "title":"Seller response"}
			message = "Seller feedback received"
			user_ids = CompanyUser.objects.filter(company=self.buying_company).values_list('user', flat=True)
			if settings.TASK_QUEUE_METHOD == 'celery':
				notificationSend.apply_async((user_ids, message, notjson), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
					'api.tasks.notificationSend',
					user_ids, message, notjson
				)
		'''

	class Meta:
		unique_together = ('selling_company', 'buying_company')


'''
@receiver(post_save, sender=CreditReference)
def credit_reference_postsave(sender, instance, **kwargs):
	if kwargs['created']:
		print "credit_reference_postsave created postsave"
		if instance.buyer_requested:
'''


class TaxType(models.Model):
	name = models.CharField(max_length=100)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.name)

class TaxCode(models.Model):
	tax_type = models.ForeignKey(TaxType)
	tax_code = models.CharField(max_length=50)
	tax_code_type = models.CharField(choices=TAX_CODE_TYPE, max_length=50)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.tax_code)

class TaxClass(models.Model):
	tax_code = models.ForeignKey(TaxCode)
	tax_name = models.CharField(max_length=50)
	from_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	to_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	location_type = models.CharField(choices=LOCATION_TYPE, max_length=50)
	percentage = models.DecimalField(max_digits=19, decimal_places=2)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		#return '%s : %s : %s : %s : %s : %s'% (self.tax_code.tax_code, self.tax_name, self.from_price, self.to_price, self.location_type, self.percentage)
		#return '%s' % (self.tax_name)
		return '%s : %s : %s : %s'% (self.id, self.tax_name, self.location_type, self.percentage)

class CategoryTaxClass(models.Model):
	category = models.ForeignKey(Category)
	#tax_class = models.ForeignKey(TaxClass)
	tax_classes = models.ManyToManyField(TaxClass)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.category.category_name)

class Invoice(models.Model):
	order = models.ForeignKey(SalesOrder)
	datetime = models.DateTimeField(auto_now_add=True)
	total_qty = models.IntegerField(default=0)
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	paid_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	pending_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=20, default='Pending')
	taxes = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	total_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2) # shipping_charges+taxes+shipping_charges-discount
	invoice_number = models.CharField(max_length=250, default=None, blank = True, null = True)
	status = models.CharField(choices=ORDER_INVOICE_STATUS, default='Invoiced', null=True, max_length=20)

	wb_coupon = models.ForeignKey(WbCoupon, default=None, blank = True, null = True)
	seller_discount = models.DecimalField(default=None, blank=True, null=True, max_digits=19, decimal_places=2)
	wb_coupon_discount = models.DecimalField(default=None, blank=True, null=True, max_digits=19, decimal_places=2)

	preffered_shipping_provider = models.CharField(choices=SHIPPING_PROVIDER, default='Buyer Suggested', null=True, max_length=20)
	buyer_preferred_logistics = models.CharField(max_length=250, default=None, blank = True, null = True)
	shipping_charges = models.DecimalField(max_digits=19 , decimal_places=2, default=Decimal('0.00'), blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if self.shipping_charges < Decimal('0.01'):
			self.preffered_shipping_provider = self.order.preffered_shipping_provider
			self.buyer_preferred_logistics = self.order.buyer_preferred_logistics
			self.shipping_charges = self.order.shipping_charges
		return super(Invoice, self).save(*args, **kwargs)

	'''def total_item(self):
		return self.invoiceitem_set.count()'''

	def total_tax_value_1(self):
		total = 0
		for item in self.items.all():
			total += item.tax_value_1
		return total

	def total_tax_value_2(self):
		total = 0
		for item in self.items.all():
			total += item.tax_value_2
		return total

	def tax_class_1(self):
		try:
			#itemObj = self.items.first()
			itemObj = self.items.all()[0]
			if itemObj and itemObj.tax_class_1:
				return itemObj.tax_class_1.tax_name
		except Exception as e:
			pass
		return None

	def tax_class_2(self):
		try:
			#itemObj = self.items.first()
			itemObj = self.items.all()[0]
			if itemObj and itemObj.tax_class_2:
				return itemObj.tax_class_2.tax_name
			return None
		except Exception as e:
			pass
		return None

	def __unicode__(self):
		#return '%s' % (self.order)
		return '%s : %s'% (self.id, self.invoice_number)

@receiver(post_save, sender=Invoice)
def invoice_postsave(sender, instance, **kwargs):
	if instance.invoice_number is None or instance.invoice_number == "":
		instance.invoice_number = instance.id
		instance.save()

class InvoiceItem(models.Model):
	invoice = models.ForeignKey(Invoice, blank = True, null = True, related_name = 'items')
	order_item = models.ForeignKey(SalesOrderItem)
	qty = models.IntegerField(default=0)
	#tax_code_1 = models.ForeignKey(TaxCode, default=None, blank = True, null = True, related_name = 'tax_code_1')
	tax_class_1 = models.ForeignKey(TaxClass, default=None, blank = True, null = True, related_name = 'tax_class_1')
	tax_value_1 = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))
	#tax_code_2 = models.ForeignKey(TaxCode, default=None, blank = True, null = True, related_name = 'tax_code_2')
	tax_class_2 = models.ForeignKey(TaxClass, default=None, blank = True, null = True, related_name = 'tax_class_2')
	tax_value_2 = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))
	rate = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	total_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	discount = models.DecimalField(default=Decimal('0.00'), blank=True, null=True, max_digits=19, decimal_places=2)

	def __unicode__(self):
		return '%s' % (self.invoice)

class Payment(models.Model):
	mode = models.CharField(choices=PAYMENT_MODE, max_length=20)
	by_company = models.ForeignKey(Company, related_name = 'payment_by')
	to_company = models.ForeignKey(Company, related_name = 'payment_to')
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	status = models.CharField(choices=PAYMENT_STATUS, max_length=20)
	details = models.TextField(blank=True, null=True)

	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)

	datetime = models.DateTimeField(auto_now_add=True)
	transaction_reference = models.TextField(blank=True, null=True)
	invoice = models.ManyToManyField(Invoice, related_name = 'payments', default=None)

	released_to_seller = models.BooleanField(default=False)
	release_instrument = models.CharField(choices=RELEASE_INSTRUMENT, max_length=20, default=None, blank = True, null = True)
	release_instrument_inumber = models.CharField(max_length=250, default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s : %s : %s'% (self.id, self.amount, self.status)

class PaymentInvoice(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	transaction_reference = models.TextField(blank=True, null=True)
	invoice = models.ForeignKey(Invoice)
	#payment = models.ForeignKey(Payment)
	amount = models.DecimalField(max_digits=19, decimal_places=2)

class Shipment(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	invoice = models.ForeignKey(Invoice)
	mode = models.CharField(max_length=250, default=None, blank = True, null = True)
	tracking_number = models.CharField(max_length=250, default=None, blank = True, null = True)
	details = models.TextField(blank=True, null=True)
	transporter_courier = models.CharField(max_length=250, default=None, blank = True, null = True)
	logistics_provider = models.CharField(max_length=250, default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class UserSendNotification(models.Model):
	user = models.ForeignKey(User)
	created_at = models.DateField(auto_now_add=True)
	send_sms = models.IntegerField(default=0)
	send_chat = models.IntegerField(default=0)
	send_gcm = models.IntegerField(default=0)

	class Meta:
		unique_together = ('user', 'created_at')

class Jobs(models.Model):
	user = models.ForeignKey(User)
	company = models.ForeignKey(Company)
	job_type = models.CharField(choices=JOB_TYPE, max_length=50)
	upload_file = models.FileField(upload_to='jobs_upload_file', null=True, blank=True)
	error_file = models.FileField(upload_to='jobs_error_file', null=True, blank=True)
	status = models.CharField(choices=JOBS_STATUS, max_length=50)
	completed_rows = models.IntegerField(default=0)
	total_rows = models.IntegerField(default=0)
	start_time = models.DateTimeField(blank=True, null=True)
	end_time = models.DateTimeField(blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True)
	error_details = models.TextField(blank = True, null = True)
	exception_details = models.TextField(blank = True, null = True)

	action_note = models.CharField(max_length=250, default=None, blank = True, null = True)

class Promotion(models.Model):
	image = VersatileImageField(
		upload_to='promotion_image/',
		ppoi_field='image_ppoi'
	)
	image_ppoi = PPOIField()
	landing_page_type = models.CharField(choices=LANDING_PAGE_TYPE, max_length=50)
	landing_page = models.CharField(max_length=100, blank = True, null = True)
	start_date = models.DateField(blank = True, null = True)
	end_date = models.DateField(blank = True, null = True)
	status = models.CharField(choices=ENABLE_DISABLE, max_length=50)
	active = models.CharField(max_length=50, blank = True, null = True)
	show_on_webapp = models.BooleanField(default=False)

	manufacturer = models.BooleanField(default=False)
	#wholesaler_distributor = models.BooleanField(default=False)
	wholesaler = models.BooleanField(default=False)
	retailer = models.BooleanField(default=False)
	#online_retailer_reseller = models.BooleanField(default=False)
	broker = models.BooleanField(default=False)

	language = models.ManyToManyField(Language, blank=True)

	campaign_name = models.CharField(max_length=100, default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s'% (self.id)

class PaidClient(models.Model):
	company = models.ForeignKey(Company)

	def __unicode__(self):
		return '%s' % (self.company.name)

class CompanyRating(models.Model):
	company = models.OneToOneField(Company)
	seller_score = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'), blank = True, null = True)
	buyer_score = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'), blank = True, null = True)
	total_seller_rating = models.PositiveIntegerField(default=0)
	total_buyer_rating = models.PositiveIntegerField(default=0)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.id)

class OrderRating(models.Model):
	order = models.OneToOneField(SalesOrder)
	seller_rating = models.DecimalField(max_digits=4, decimal_places=2, default=None, blank = True, null = True)#filled by buyer
	buyer_rating = models.DecimalField(max_digits=4, decimal_places=2, default=None, blank = True, null = True)#filled by supplier
	seller_remark = MultiSelectField(choices=SELLER_REMARK, blank = True, null = True)
	seller_remark_other = models.TextField(blank=True, null=True)
	buyer_remark = MultiSelectField(choices=BUYER_REMARK, blank = True, null = True)
	buyer_remark_other = models.TextField(blank=True, null=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.id)

	def __init__(self, *args, **kwargs):
		super(OrderRating, self).__init__(*args, **kwargs)
		self.old_seller_rating = self.seller_rating
		self.old_buyer_rating = self.buyer_rating

	def save(self, *args, **kwargs):
		if self.pk is None:
			print "created"
			super(OrderRating, self).save(*args, **kwargs)

			if self.seller_rating:
				company = self.order.seller_company
				sellercrObj, created = CompanyRating.objects.get_or_create(company=company)
				print ("old seller score")
				print sellercrObj.seller_score

				if self.seller_rating >= float(4):
					sellercrObj.seller_score = ((sellercrObj.seller_score * sellercrObj.total_seller_rating) + 1 )/(sellercrObj.total_seller_rating +1)
				else:
					sellercrObj.seller_score = ((sellercrObj.seller_score * sellercrObj.total_seller_rating) )/(sellercrObj.total_seller_rating +1)

				print ("new seller score")
				print sellercrObj.seller_score
				sellercrObj.total_seller_rating += 1
				sellercrObj.save()

				'''total_raws = OrderRating.objects.filter(order__seller_company=company).count()

				total_rating = OrderRating.objects.filter(order__seller_company=company, seller_rating__gte = float(4)).exclude(seller_rating__isnull=True).aggregate(Sum('seller_rating')).get('seller_rating__sum', 0)
				if total_rating is None:
					total_rating = 0
				print total_rating
				print total_raws

				sellercrObj.seller_score = total_rating / total_raws
				sellercrObj.save()
				print sellercrObj.seller_score'''

			if self.buyer_rating:
				company = self.order.company
				buyercrObj, created = CompanyRating.objects.get_or_create(company=company)
				print ("old buyer score")
				print buyercrObj.buyer_score

				if self.buyer_rating >= float(4):
					buyercrObj.buyer_score = ((buyercrObj.buyer_score * buyercrObj.total_buyer_rating) + 1 )/(buyercrObj.total_buyer_rating +1)
				else:
					buyercrObj.buyer_score = ((buyercrObj.buyer_score * buyercrObj.total_buyer_rating) )/(buyercrObj.total_buyer_rating +1)

				print ("new buyer score")
				print buyercrObj.buyer_score
				buyercrObj.total_buyer_rating += 1
				buyercrObj.save()
		else:
			if self.seller_rating == float(5):
				self.seller_remark = []

			if self.buyer_rating == float(5):
				self.buyer_remark = []

			print "updated"
			super(OrderRating, self).save(*args, **kwargs)

			if self.seller_rating is not None and self.seller_rating != self.old_seller_rating:
				company=self.order.seller_company
				sellercrObj, created = CompanyRating.objects.get_or_create(company=company)
				print ("old seller score")
				print sellercrObj.seller_score

				if self.old_seller_rating is not None:
					total_highest_rating = OrderRating.objects.filter(seller_rating__gte=4, order__seller_company=company).exclude(seller_rating__isnull=True).count()
					total_rating = OrderRating.objects.filter(order__seller_company=company).exclude(seller_rating__isnull=True).count()
					sellercrObj.seller_score = float(total_highest_rating) / float(total_rating)
					sellercrObj.save()
				else:
					if self.seller_rating >= float(4):
						sellercrObj.seller_score = ((sellercrObj.seller_score * sellercrObj.total_seller_rating) + 1 )/(sellercrObj.total_seller_rating +1)
					else:
						sellercrObj.seller_score = ((sellercrObj.seller_score * sellercrObj.total_seller_rating) )/(sellercrObj.total_seller_rating +1)

					print ("new seller score")
					print sellercrObj.seller_score
					sellercrObj.total_seller_rating += 1
					sellercrObj.save()


			if self.buyer_rating is not None and self.buyer_rating != self.old_buyer_rating:
				company=self.order.company
				buyercrObj, created = CompanyRating.objects.get_or_create(company=company)
				print ("old buyer score")
				print buyercrObj.buyer_score

				if self.old_buyer_rating is not None:
					total_highest_rating = OrderRating.objects.filter(buyer_rating__gte=4, order__company=company).exclude(buyer_rating__isnull=True).count()
					total_rating = OrderRating.objects.filter(order__company=company).exclude(buyer_rating__isnull=True).count()
					buyercrObj.buyer_score = float(total_highest_rating) / float(total_rating)
					buyercrObj.save()
				else:
					if self.buyer_rating >= float(4):
						buyercrObj.buyer_score = ((buyercrObj.buyer_score * buyercrObj.total_buyer_rating) + 1 )/(buyercrObj.total_buyer_rating +1)
					else:
						buyercrObj.buyer_score = ((buyercrObj.buyer_score * buyercrObj.total_buyer_rating) )/(buyercrObj.total_buyer_rating +1)

					print ("new buyer score")
					print buyercrObj.buyer_score
					buyercrObj.total_buyer_rating += 1
					buyercrObj.save()

		#super(OrderRating, self).save(*args, **kwargs)
'''
@receiver(post_save, sender=OrderRating)
def orderrating__post_save(sender, instance, created, *args, **kwargs):
	if created:
		# new
		print "created"
		print instance
		if instance.seller_rating:
			sellercrObj = CompanyRating.objects.get_or_create(company=instance.order.seller_company)
			sellercrObj.total_seller_rating += 1

			sellercrObj.save()


		if instance.buyer_rating:
			buyercrObj = CompanyRating.objects.get_or_create(company=instance.order.company)
			buyercrObj.total_buyer_rating += 1

			buyercrObj.save()


	elif not created:
		# updated
		print "updated"
		print instance
'''

class ApprovedCredit(models.Model):
	company = models.ForeignKey(Company)
	lender_company = models.CharField(choices=LENDER_COMPANY, max_length=50)
	total_limit = models.DecimalField(max_digits=19, decimal_places=2)
	minimum_order_value = models.DecimalField(max_digits=19, decimal_places=2)
	used_limit = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))
	available_limit = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self.available_limit = self.total_limit - self.used_limit
		return super(ApprovedCredit, self).save(*args, **kwargs)

class Loan(models.Model):
	company = models.ForeignKey(Company)
	approved_credit = models.ForeignKey(ApprovedCredit)
	order = models.ForeignKey(SalesOrder)
	status = models.CharField(choices=LOAN_STATUS, max_length=50)

class PaymentMethod(models.Model):
	name = models.CharField(max_length=200)
	payment_type = models.CharField(choices=PAYMENT_METHOD_TYPE, max_length=50)
	display_name = models.CharField(max_length=200)
	status = models.CharField(choices=ENABLE_DISABLE, default='Enable', max_length=20)

class PincodeZone(models.Model):
	city = models.ForeignKey(City)
	pincode = models.IntegerField()
	zone = models.CharField(max_length=200)
	is_servicable = models.BooleanField(default=True)
	cod_available = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s : %s : %s'% (self.id, self.pincode, self.is_servicable)

class Config(models.Model):
	key = models.CharField(max_length=250, unique=True)
	value = models.CharField(max_length=250)
	display_text = models.TextField(blank=True, null=True)
	visible_on_frontend = models.BooleanField(default=False)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class BrokeragePayment(models.Model):
	company = models.ForeignKey(Company, related_name = 'brokeragepaymentcompanies')
	selling_company = models.ForeignKey(Company, related_name = 'brokeragepaymentsellingcompanies')
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	payment_date = models.DateField()
	payment_method = models.CharField(choices=PAYMENT_MODE, max_length=20)
	payment_details = models.TextField(blank = True, null = True)

class BrokerageOrderFee(models.Model):
	order = models.ForeignKey(SalesOrder)
	selling_company = models.ForeignKey(Company)
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	brokerage_payment = models.ForeignKey(BrokeragePayment)

class UserPlatformInfo(models.Model):
	user = models.OneToOneField(User)
	platform = models.CharField(max_length=250, blank = True, null = True)
	app_version = models.CharField(max_length=250, blank = True, null = True)
	app_version_code = models.CharField(max_length=250, blank = True, null = True)
	device_model = models.CharField(max_length=250, blank = True, null = True)
	brand = models.CharField(max_length=250, blank = True, null = True)
	operating_system = models.CharField(max_length=250, blank = True, null = True)
	operating_system_version = models.CharField(max_length=250, blank = True, null = True)
	screen_width = models.CharField(max_length=250, blank = True, null = True)
	screen_height = models.CharField(max_length=250, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s : %s : %s'% (self.id, self.app_version, self.app_version_code)

class CashbackRule(models.Model):
	seller = models.ForeignKey(Company)
	payment_type = models.CharField(choices=PAYMENT_METHOD_TYPE, max_length=50)
	shipping_status = models.CharField(choices=SHIPPING_STATUS, max_length=20, default='Pending')
	payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=20, default='Pending')
	expire_date = models.DateField()
	times_per_buyer = models.IntegerField(default=1)

class Cashback(models.Model):
	sales_order = models.ForeignKey(SalesOrder)
	cashback_rule = models.ForeignKey(CashbackRule)
	buyer = models.ForeignKey(Company)
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	status = models.CharField(choices=CASHBACK_STATUS, default='Pending', max_length=20)

class CompanySellsToState(models.Model):
	company = models.ForeignKey(Company, related_name = 'companysellstostate')
	intermediate_buyer = models.ForeignKey(Company, related_name = 'intermediatecompanysellstostate', default=None, blank = True, null = True)
	state = models.ForeignKey(State)

	class Meta:
		unique_together = ('company', 'intermediate_buyer', 'state')

class CatalogSeller(models.Model):
	catalog = models.ForeignKey(Catalog)
	selling_company = models.ForeignKey(Company)
	selling_type = models.CharField(choices=CATALOG_TYPE, max_length=20, default='Public')
	buyer_segmentation = models.ForeignKey(BuyerSegmentation, default=None, blank = True, null = True)
	sell_full_catalog = models.BooleanField(default=False)
	full_catalog_price = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank = True, null = True)
	status = models.CharField(choices=ENABLE_DISABLE, max_length=20, default='Enable')
	expiry_date = models.DateTimeField(blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('catalog', 'selling_company', 'selling_type')

	def __init__(self, *args, **kwargs):
		super(CatalogSeller, self).__init__(*args, **kwargs)
		self.old_expiry_date = self.expiry_date

	def __unicode__(self):
		return '%s : %s : %s'% (self.id, self.status, self.expiry_date)

	def save(self, *args, **kwargs):
		print 'class catalogseller: save:'
		super(CatalogSeller, self).save(*args, **kwargs)
		#import pdb; pdb.set_trace()
		if self.old_expiry_date != self.expiry_date:

			if self.catalog.company == self.selling_company:
				print "class catalogseller: save: update catalogseller expire date = "
				Catalog.objects.filter(id=self.catalog.id, company=self.catalog.company).update(expiry_date = self.expiry_date)
				CatalogSeller.objects.filter(selling_company = self.catalog.company, catalog = self.catalog).exclude(id = self.id).update(expiry_date = self.expiry_date)


def catalog_seller_sort_order(sender, instance, **kwargs):
	print "models: class catalogseller: in catalog_seller_sort_order"
	if kwargs['created']:
		if instance.catalog.company != instance.selling_company and instance.status == "Enable" and instance.selling_company.id != 148:
			# ~ catalogObj = Catalog.objects.last()
			# ~ instance.catalog.sort_order = catalogObj.id + 1
			# ~ instance.catalog.save()

			catalog = instance.catalog
			companyImage = catalog.brand.image.thumbnail[settings.MEDIUM_IMAGE].url
			pushImage = catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url


			logger.info("catalog_seller_sort_order view_permission=public catalog id = %s notification to followers of my state"% (instance.catalog.id))
			#notification to followers
			state = instance.selling_company.address.state
			print "state==",state
			companyids = CompanyBrandFollow.objects.filter(brand=catalog.brand, company__state=state).values_list('company', flat=True).distinct()
			users = CompanyUser.objects.filter(company__in = companyids, user__groups__name="administrator").exclude(company=instance.selling_company).values_list('user', flat=True).distinct()
			users = list(users)
			statecity = ""
			if instance.selling_company.address:
				statecity += " from "+instance.selling_company.address.city.city_name
				statecity += ", "+instance.selling_company.address.state.state_name
			# message = instance.selling_company.name+statecity+" is also selling "+catalog.title+" catalog of "+catalog.brand.name+" brand"
			message = notificationTemplates("catalog_become_seller")% (instance.selling_company.name+statecity, catalog.title, catalog.brand.name)
			# if settings.TASK_QUEUE_METHOD == 'celery':
			# 	notificationSend.apply_async((users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id), "other_para":{"not_action_1":"catalog_view"} }), expires=datetime.now() + timedelta(days=2))
			# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			# 	task_id = async(
			# 		'api.tasks.notificationSend',
			# 		users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id), "other_para":{"not_action_1":"catalog_view"} }
			# 	)
			sendNotifications(users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id), "other_para":{"not_action_1":"catalog_view"} })


			logger.info("catalog_seller_sort_order in create catalog id = %s, selling_company = %s sending notifications to my all buyers"% (instance.catalog.id, instance.selling_company.id))
			buyers = Buyer.objects.filter(selling_company=instance.selling_company, status="approved").values_list('buying_company', flat=True)
			users = CompanyUser.objects.filter(company__in = buyers, user__groups__name="administrator").exclude(company=instance.selling_company).values_list('user', flat=True).distinct()
			users = list(users)
			#message = instance.selling_company.name+" just uploaded a catalog "+catalog.title
			# if settings.TASK_QUEUE_METHOD == 'celery':
			# 	notificationSend.apply_async((users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id)}), expires=datetime.now() + timedelta(days=2))
			# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			# 	task_id = async(
			# 		'api.tasks.notificationSend',
			# 		users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id)}
			# 	)
			sendNotifications(users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":pushImage, "company_image":companyImage, "title":catalog.title, "name":catalog.title, "table_id": int(catalog.id)})

			excludeusers = GCMDevice.objects.filter(user__in=users, active=True).values_list('user', flat=True).distinct()
			logger.info("catalog_seller_sort_order in create catalog id = %s, sending notifications to my all buyers, excludeusers = %s"% (instance.catalog.id, excludeusers))

			unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
			smsUser = UserProfile.objects.filter(user__in=users).exclude(user__in=excludeusers)
			smsurl = 'https://app.wishbooks.io/m?type=catalog&id='+str(instance.catalog.id)

			for userPObj in smsUser:
				if "+91" not in userPObj.country.phone_code:
					continue

				phone_number = [str(userPObj.country.phone_code)+str(userPObj.phone_number)]
				phone_number = list(set(phone_number) - set(unsubscribed_number))

				if len(phone_number) == 0:
					continue

				otp = getLastOTP(userPObj)
				usersmsurl = smsurl + '&m='+str(userPObj.phone_number)+'&o='+str(otp)
				#time.sleep(2)
				usersmsurl = urlShortener(usersmsurl)

				template = smsTemplates("public_catalog")% (instance.selling_company.name, instance.catalog.title, usersmsurl)
				#smsSend(phone_number, template, True)
				logger.info("in_queue smsSendTextNationPromotional")
				if settings.TASK_QUEUE_METHOD == 'celery':
					smsSendTextNationPromotional.apply_async((phone_number, template, True), expires=datetime.now() + timedelta(days=2))
				elif settings.TASK_QUEUE_METHOD == 'djangoQ':
					if isScheduledTime():
						schedule('api.tasks.smsSendTextNationPromotional',
							phone_number, template, True,
							schedule_type=Schedule.ONCE,
							next_run=getScheduledTime(),
							q_options={'broker': priority_broker}
						)
					else:
						task_id = async(
							'api.tasks.smsSendTextNationPromotional',
							phone_number, template, True
						)

	#update seller of catalog in catalogindex
	try:
		obj = CatalogIndex.get(id=instance.catalog.id, ignore=404)
		logger.info("CatalogSeller model CatalogIndex = %s"% (obj))
		if obj:
			#seller_names = CatalogSeller.objects.filter(catalog=catalog_obj, selling_type="Public", status="Enable").values_list('selling_company__name', flat=True)
			seller_names =  get_catalog_sellers_names(instance.catalog)#common_functions
			logger.info("CatalogSeller model CatalogIndex seller_names = %s"% (seller_names))
			if len(seller_names) > 0:
				catalog_suggest=obj.catalog_suggest
				# print(catalog_suggest)
				if instance.catalog.company.name not in catalog_suggest:
					catalog_suggest.append(instance.catalog.company.name)
				#WB-1610 : Django: If someone changes company name - then all catalog entries for that company in elastic search should be updated
				obj.update(sellers=list(seller_names), company=instance.catalog.company.name, catalog_suggest=catalog_suggest)#,
			else:
				obj.delete()
	except Exception as e:
		logger.info(e)
		if settings.DEBUG==False:
			mail_status = send_mail("catalog_seller_sort_order", "Error = "+str(e)+", Catalog ID = "+str(instance.catalog.id), "tech@wishbook.io", ["tech@wishbook.io"])
			logger.info(str(mail_status))
		pass


post_save.connect(catalog_seller_sort_order, sender = CatalogSeller, dispatch_uid = 'catalog_seller_sort_order_unique')

class UserReview(models.Model):
	image = VersatileImageField(
		upload_to='userreview_image/',
		ppoi_field='image_ppoi'
	)
	image_ppoi = PPOIField()
	status = models.CharField(choices=ENABLE_DISABLE, max_length=50)
	language = models.ManyToManyField(Language, blank=True)

class PromotionalTag(models.Model):
	image = VersatileImageField(
		upload_to='userreview_image/',
		ppoi_field='image_ppoi'
	)
	image_ppoi = PPOIField()
	status = models.CharField(choices=ENABLE_DISABLE, max_length=20, default='Enable')
	url = models.URLField(blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

#added by jay
class PreDefinedFilter(models.Model):
	name = models.CharField(max_length=100)
	category = models.ForeignKey(Category)
	status = models.CharField(choices=ENABLE_DISABLE, max_length=20, default='Enable')
	url = models.URLField(blank = True, null = True)
	created = models.DateTimeField(auto_now_add=True)
	sort_order =  models.PositiveIntegerField(default=0)

@receiver(post_save, sender=PreDefinedFilter)
def predefinedfilter_postsave(sender, instance, **kwargs):
	if kwargs['created']:
		print "created predefinedfilter_postsave"
		instance.sort_order = instance.id
		instance.save()

class UserWishlist(models.Model):
	user = models.ForeignKey('auth.User')
	catalog = models.ForeignKey(Catalog)
	created = models.DateTimeField(auto_now_add=True)


class UserContact(models.Model):
	user = models.ForeignKey('auth.User')
	name = models.CharField(max_length=100)
	number = models.CharField(max_length=15)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('user', 'number')

	def __unicode__(self):
		return '%s : %s' % (self.id, self.number)

class SearchQuery(models.Model):
	user = models.ForeignKey('auth.User')
	params = models.CharField(max_length=250)
	request_for = models.CharField(max_length=100)
	use_count = models.PositiveIntegerField(default=0)
	result_count = models.PositiveIntegerField(default=0)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('user', 'params', 'request_for')

RELATIONSHIP_TYPE = (('Enquiry','Enquiry'), ('Buyer','Buyer'), ('Supplier','Supplier'))
ACTION_TYPE = (('Call','Call'), ('Chat','Chat'))

class ActionLog(models.Model):
	user = models.ForeignKey('auth.User')
	recipient_company = models.ForeignKey(Company)
	relationship_type = models.CharField(choices=RELATIONSHIP_TYPE, max_length=20)
	action_type = models.CharField(choices=ACTION_TYPE, max_length=20)

	created = models.DateTimeField(auto_now_add=True)

class UserSavedFilter(models.Model):
	user = models.ForeignKey('auth.User')
	title = models.CharField(max_length=100)
	sub_text = models.CharField(max_length=200, blank = True, null = True)
	params = models.TextField()

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class AppVersion(models.Model):
	version_code = models.CharField(max_length=100, blank = True, null = True)
	update = models.BooleanField(default=False)
	force_update = models.BooleanField(default=False)
	platform = models.CharField(choices=APP_PLATFORM, max_length=100)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class DiscountRule(models.Model):
	name = models.CharField(max_length=100, blank = True, null = True)
	selling_company = models.ForeignKey(Company)
	discount_type = models.CharField(choices=CATALOG_TYPE, max_length=20, default="Public")
	all_brands = models.BooleanField(default=True)
	cash_discount = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))
	credit_discount = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))

	brands = models.ManyToManyField(Brand, blank=True)
	buyer_segmentations = models.ManyToManyField(BuyerSegmentation, blank=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.id)


class Marketing(models.Model):
	campaign_name = models.CharField(max_length=250)
	campaign_text = models.CharField(max_length=500) #title - notification title and sms message
	campaign_html = models.TextField(blank = True, null = True) #message - notification message and facebook msg

	to = models.CharField(choices=MARKETING_TO, max_length=50)
	state = models.ManyToManyField(State, blank=True)
	city = models.ManyToManyField(City, blank=True)
	specific_no_file = models.FileField(upload_to='marketing_files', null=True, blank=True)

	company_number_type_all = models.BooleanField(default=False)
	company_number_type_retailers = models.BooleanField(default=False)
	company_number_type_wholesalers_agents = models.BooleanField(default=False)
	company_number_type_manufactures = models.BooleanField(default=False)

	company_number_type_online_retailer_reseller = models.BooleanField(default=False)
	company_number_type_broker = models.BooleanField(default=False)

	company_number_type_guestusers = models.BooleanField(default=False)
	company_number_type_inphonebook = models.BooleanField(default=False)

	by_sms = models.BooleanField(default=False)
	by_facebook_notifications = models.BooleanField(default=False)
	by_in_app_notifications = models.BooleanField(default=False)
	by_audio_call = models.BooleanField(default=False)
	login_url_in_sms = models.BooleanField(default=False)
	image = models.ImageField(upload_to='marketing_images', default=None, null=True, blank=True)

	app_version = models.CharField(max_length=250, default=None, blank = True, null = True)
	last_login_platform = models.CharField(choices=LOGIN_PLATFORM, max_length=20, default=None, blank = True, null = True)
	deep_link = models.URLField(default=None, blank = True, null = True)

	test_users = models.ManyToManyField(User, blank=True, related_name="test_users")
	categories = models.ManyToManyField(Category, related_name = "marketings", blank=True)

	minimum_category_views = models.PositiveIntegerField(default=0)
	append_deeplink_insms = models.BooleanField(default=False)

	user = models.ForeignKey('auth.User')
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s' % (self.id)
'''
#@receiver(m2m_changed, sender=Marketing.test_users.through)
@receiver(post_save, sender=Marketing)
def marketing_postsave(sender, instance, **kwargs):
	print "kwargs    kwargs    ===", kwargs
	if kwargs['created']:
		print "created Marketing postsave start"

		if settings.TASK_QUEUE_METHOD == 'celery':
			startMarketing.apply_async((instance.id), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			if isScheduledTime():
				schedule('api.tasks.startMarketing',
					instance.id,
					schedule_type=Schedule.ONCE,
					next_run=getScheduledTime(),
					q_options={'broker': priority_broker}
				)
			else:
				schedule('api.tasks.startMarketing',
					instance.id,
					schedule_type=Schedule.ONCE,
					next_run=datetime.now()+timedelta(seconds=10),
					q_options={'broker': priority_broker}
				)

		print "created Marketing postsave end"
'''


'''class DiscountRuleBrand(models.Model):
	discount_rule = models.ForeignKey(DiscountRule)
	brand = models.ForeignKey(Brand)

	def __unicode__(self):
		return '%s' % (self.id)

class DiscountRuleBuyerGroup(models.Model):
	discount_rule = models.ForeignKey(DiscountRule)
	buyer_group = models.ForeignKey(BuyerSegmentation)

	def __unicode__(self):
		return '%s' % (self.id)'''

class CatalogEnquiry(models.Model):
	enquiry_type = models.CharField(choices=ENQUIRY_TYPE, max_length=20, default=None, blank = True, null = True)
	catalog = models.ForeignKey(Catalog)
	selling_company = models.ForeignKey(Company, related_name = 'ce_selling_companies')
	buying_company = models.ForeignKey(Company, related_name = 'ce_buying_companies')
	status = models.CharField(choices=CATALOG_ENQUIRY_STATUS, max_length=30, default="Created")
	text = models.TextField(blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True)
	item_type = models.CharField(choices=ENQUIRY_ITEM_TYPE, max_length=20, default=None, blank = True, null = True)
	item_quantity = models.IntegerField(default=0)

	applogic_conversation_id = models.CharField(max_length = 250, default=None, blank = True, null = True)

	modified = models.DateTimeField(auto_now=True)

	sugar_crm_lead_id = models.CharField(max_length=250, default=None, blank = True, null = True)

#update enquiry to sugar_crm
def enquiry_to_crm(sender, instance, **kwargs):
	if kwargs['created']:
		if settings.DEBUG == False:
			enquiry_to_crm_q(instance.id,created=True)

post_save.connect(enquiry_to_crm,CatalogEnquiry,dispatch_uid = 'sugar_enquiry_update')

class SellerPolicy(models.Model):
	company = models.ForeignKey(Company)
	policy_type = models.CharField(choices=POLICY_TYPE, max_length=20)
	policy = models.TextField()

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class MobileStateMapping(models.Model):
	state = models.ForeignKey(State)
	mobile_no_start_with = models.CharField(max_length = 5, unique=True)

	def __unicode__(self):
		return '%s' % (self.id)

class UserCampaignClick(models.Model):
	user = models.ForeignKey(User)
	campaign = models.CharField(max_length=250)
	created_at = models.DateTimeField(auto_now_add=True)

class SellerStatistic(models.Model):
	company = models.OneToOneField(Company)
	name = models.CharField(max_length = 100, blank = True, null = True)
	wishbook_salesman = models.TextField(blank = True, null = True)
	company_type = models.TextField(blank = True, null = True)
	city = models.CharField(max_length = 100, blank = True, null = True)
	phone_number = models.CharField(max_length=13, blank = True, null = True)
	last_login = models.DateTimeField(null=True, blank=True)

	#30 days
	catalogs_uploaded = models.IntegerField(blank = True, null = True)
	total_catalog_seller = models.IntegerField(blank = True, null = True)
	total_enabled_catalog = models.IntegerField(blank = True, null = True)
	last_catalog_upload_date = models.DateField(null=True, blank=True)
	last_catalog_seller_date = models.DateField(null=True, blank=True)
	last_catalog_or_seller_name = models.CharField(max_length = 250, blank = True, null = True)

	#30 days
	total_enquiry_received = models.IntegerField(blank = True, null = True)
	total_enquiry_converted = models.IntegerField(blank = True, null = True)
	total_enquiry_pending = models.IntegerField(blank = True, null = True)
	total_enquiry_values = models.IntegerField(blank = True, null = True)
	handling_time = models.DurationField(blank=True, null=True)

	#30 days
	total_order_values = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))
	total_pending_order_values = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))
	total_prepaid_order_values = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))
	total_prepaid_cancelled_order_values = models.DecimalField(max_digits=19, decimal_places=2, default=Decimal('0.00'))
	avg_dispatch_time = models.DurationField(blank=True, null=True)

	enquiry_not_handled = models.IntegerField(blank = True, null = True)
	total_pending_order = models.IntegerField(blank = True, null = True)
	prepaid_order_cancellation_rate = models.CharField(max_length = 100, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)


class Story(models.Model):
	name = models.CharField(max_length=250)
	image = VersatileImageField(
		upload_to='story_image/',
		ppoi_field='image_ppoi'
	)
	image_ppoi = PPOIField()
	catalogs = models.ManyToManyField(Catalog, blank=True)
	deep_link = models.URLField(default=None, blank = True, null = True)

	is_disable = models.BooleanField(default=False)
	sort_order =  models.PositiveIntegerField(default=0)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

@receiver(post_save, sender=Story)
def story_postsave(sender, instance, **kwargs):
	if kwargs['created']:
		print "created story_postsave"
		instance.sort_order = instance.id
		instance.save()

	urlPath = "story_"+str(instance.id)
	cache.delete(urlPath)

class ApiSalesorderauditlogentry(models.Model):
	id = models.IntegerField()
	order_number = models.CharField(max_length=50, blank=True, null=True)
	seller_ref = models.CharField(max_length=50, blank=True, null=True)
	created_at = models.DateTimeField()
	date = models.DateField()
	time = models.DateTimeField()
	processing_status = models.CharField(max_length=20, blank=True, null=True)
	customer_status = models.CharField(max_length=20)
	sales_image = models.CharField(max_length=100, blank=True, null=True)
	purchase_image = models.CharField(max_length=100, blank=True, null=True)
	note = models.TextField(blank=True, null=True)
	tracking_details = models.TextField(blank=True, null=True)
	supplier_cancel = models.TextField(blank=True, null=True)
	buyer_cancel = models.TextField(blank=True, null=True)
	payment_details = models.TextField(blank=True, null=True)
	payment_date = models.DateField(blank=True, null=True)
	dispatch_date = models.DateField(blank=True, null=True)
	brokerage_fees = models.DecimalField(max_digits=19, decimal_places=2)
	sales_image_2 = models.CharField(max_length=100, blank=True, null=True)
	sales_image_3 = models.CharField(max_length=100, blank=True, null=True)
	sales_reference_id = models.IntegerField(blank=True, null=True)
	purchase_reference_id = models.IntegerField(blank=True, null=True)
	is_supplier_approved = models.IntegerField()
	buying_company_name = models.CharField(max_length=250, blank=True, null=True)
	preffered_shipping_provider = models.CharField(max_length=20, blank=True, null=True)
	buyer_preferred_logistics = models.CharField(max_length=250, blank=True, null=True)
	shipping_charges = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)
	transaction_type = models.CharField(max_length=50)
	cancelled_by = models.CharField(max_length=20, blank=True, null=True)
	seller_cancellation_reason = models.CharField(max_length=30, blank=True, null=True)
	action_id = models.AutoField(primary_key=True)
	action_date = models.DateTimeField()
	action_type = models.CharField(max_length=1)
	action_user = models.ForeignKey('auth.User', blank=True, null=True, related_name = 'aso_action_user')
	broker_company = models.ForeignKey(Company, blank=True, null=True, related_name = 'aso_broker_company')
	company = models.ForeignKey(Company, related_name = 'aso_company')
	created_by = models.ForeignKey('auth.User', blank=True, null=True, related_name = 'aso_created_by')
	modified_by = models.ForeignKey('auth.User', blank=True, null=True, related_name = 'aso_modified_by')
	seller_company = models.ForeignKey(Company, related_name = 'aso_seller_company')
	ship_to = models.ForeignKey(Address, blank=True, null=True, related_name = 'aso_ship_to')
	tranferred_to = models.ForeignKey(SalesOrder, blank=True, null=True, related_name = 'aso_tranferred_to')
	user = models.ForeignKey('auth.User', related_name = 'aso_user')
	wb_coupon = models.ForeignKey(WbCoupon, blank=True, null=True, related_name = 'aso_wb_coupon')
	order_type = models.CharField(max_length=20)
	visible_to_buyer = models.IntegerField()
	visible_to_supplier = models.IntegerField()
	approximate_order = models.IntegerField()
	amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)
	seller_extra_discount_percentage = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)
	cart = models.ForeignKey(Cart, blank=True, null=True, related_name = 'aso_cart')
	source_type = models.CharField(max_length=50)
	processing_note = models.TextField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'api_salesorderauditlogentry'
		verbose_name = 'Sales Order Log Entry'
		verbose_name_plural = 'Sales Order Log Entry'

class ViewFollower(models.Model):
	user = models.OneToOneField(User)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, related_name='items',  default=None)
	selling_company = models.ForeignKey(Company, related_name = 'cartitem_selling_company')
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	quantity = models.PositiveIntegerField(default=1)
	rate = models.DecimalField(max_digits=19 , decimal_places=2, null=True)#, validators=[MinValueValidator(Decimal('0.01'))]

	packing_type = models.CharField(choices=PACKING_TYPE, max_length=20, default=None, blank = True, null = True)
	note = models.TextField(blank = True, null = True)

	tax_class_1 = models.ForeignKey(TaxClass, default=None, blank = True, null = True, related_name = 'cartitem_tax_class_1')
	tax_value_1 = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))
	tax_class_2 = models.ForeignKey(TaxClass, default=None, blank = True, null = True, related_name = 'cartitem_tax_class_2')
	tax_value_2 = models.DecimalField(max_digits=10 , decimal_places=2, default=Decimal('0.00'))

	amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	total_amount = models.DecimalField(blank=True, null=True, max_digits=19, decimal_places=2)
	discount = models.DecimalField(default=Decimal('0.00'), blank=True, null=True, max_digits=19, decimal_places=2)
	discount_percent = models.DecimalField(default=Decimal('0.00'), blank=True, null=True, max_digits=19, decimal_places=2)

	is_full_catalog = models.BooleanField(default=False)

	def __unicode__(self):
		return '%s : %s : %s'% (self.id, self.quantity, self.rate)

class CartPayment(models.Model):
	mode = models.CharField(choices=PAYMENT_MODE, max_length=20)
	cart = models.ForeignKey(Cart)
	amount = models.DecimalField(max_digits=19, decimal_places=2)
	status = models.CharField(choices=PAYMENT_STATUS, max_length=20)
	payment_details = models.TextField(blank=True, null=True)

	user = models.ForeignKey('auth.User', default=None, blank = True, null = True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class CompanyCreditAprovedLine(models.Model):
	company =  models.ForeignKey(Company, related_name = 'credit_line')
	nbfc_partner = models.CharField(choices=NBFC_PARTNER, max_length=30, default='Indifi', blank=True, null=True) #enum choice
	approved_line = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank=True, null=True)
	available_line = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank=True, null=True)
	used_line = models.DecimalField(max_digits=19, decimal_places=2, default=None, blank=True, null=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '%s : %s '% (self.company.name, self.available_line)

	class Meta:
		unique_together = ('company', 'nbfc_partner',)

class CompanyBankDetails(models.Model):
	company = models.OneToOneField(Company, related_name = 'bankdetail')
	account_name = models.CharField(max_length=100, default=None, blank=True, null=True)
	account_number = models.BigIntegerField(default=None, blank = True, null = True)
	bank_name = models.CharField(max_length=100, default=None, blank=True, null=True)
	ifsc_code = models.CharField(max_length=20, default=None, blank=True, null=True)#,  validators=[alphanumeric_ifsc]
	account_type = models.CharField(choices=ACCOUNT_TYPE, max_length=20, default=None, blank=True, null=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

class ShipRocketApiLog(models.Model):
	"""docstring for ShipRocketApiLog.
		it will store ship rocket order id and awb number label url,
		manifest_url and invoice_url and api response.
	"""
	SHIP_ACCESS_TYPE		=	(('CREATE','CREATE'),
								 ('AWB','AWB'),
								 ('PICKUP','PICKUP')
								)
	SHIP_STATUS_TYPE		=	(('SUCCESS','SUCCESS'),
								 ('FAILED','FAIELD'),
								)

	provider_access_type 	=	models.CharField(choices=SHIP_ACCESS_TYPE, max_length=20, default=None, blank=True, null=True)
	api_provider 			=	models.CharField(max_length=50,default="ShipRocket",blank=True,null=True)
	provider_order_id 		=	models.CharField(max_length=50,blank=True,null=True)
	provider_shipment_id 	=	models.CharField(max_length=50,blank=True,null=True)
	provider_label_url 		=	models.URLField(blank = True, null = True, max_length=250)
	provider_manifest_url 	=	models.URLField(blank = True, null = True, max_length=250)
	provider_invoice_url   	=	models.URLField(blank = True, null = True, max_length=250)
	provider_api_response	=	models.TextField(blank=True, null=True)
	provider_awb_number		=	models.CharField(max_length=50,blank=True, null=True)
	provider_status      	=	models.CharField(choices=SHIP_STATUS_TYPE, max_length=20, default=None, blank=True, null=True)
	wishbook_order_ids		=   models.CharField(max_length=50,blank=True, null=True)

	def __unicode__(self):
		return '%s : %s : %s'% (self.wishbook_order_ids,self.provider_access_type, self.provider_status)

#salesorder wishbook discount, company add available total_wbmoney_points
# class WBMoneyRule(models.Model):
# 	label = models.CharField(max_length=200, unique=True)
# 	points = models.PositiveIntegerField(default=0)
# 	details = models.TextField(default=None, blank = True, null = True)
#
# 	created = models.DateTimeField(auto_now_add=True)
# 	modified = models.DateTimeField(auto_now=True)
#
# class WBMoneyEarning(models.Model):
# 	company = models.ForeignKey(Company, related_name = 'wb_money')
# 	wb_money_rule = models.ForeignKey(WBMoneyRule, related_name = 'wb_money')
# 	points = models.PositiveIntegerField(default=0)
#
# 	created = models.DateTimeField(auto_now_add=True)
# 	# modified = models.DateTimeField(auto_now=True)
