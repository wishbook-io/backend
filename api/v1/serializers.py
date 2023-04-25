from rest_framework import fields, serializers
from api.models import *
from api.common_functions import *

from django.contrib.auth.models import User, Group
from rest_framework import permissions
from django.conf import settings

from rest_framework.validators import UniqueTogetherValidator
import logging
logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _
import datetime
from versatileimagefield.serializers import VersatileImageFieldSerializer

import json
import ast

from django.db.models import Sum, Min, Max, Count
from datetime import datetime, date, time, timedelta

from django.core.exceptions import ObjectDoesNotExist

import random


from api.v0.notifications import *
from notifier.shortcuts import send_notification
#from notifier.shortcuts import create_notification
from api.v0.notifier_backend import *

from django.db.models import Value
from django.db.models.functions import Concat

from rest_framework.authtoken.models import Token

from django_q.tasks import async, result

from api.common_functions import handel_catalog_eav
from django_q.brokers import get_broker
priority_broker_trivenilabs = get_broker('trivenilabs')

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
	"""
	A ModelSerializer that takes an additional `fields` argument that
	controls which fields should be displayed.
	"""

	def __init__(self, *args, **kwargs):
		# Instantiate the superclass normally
		#fields = kwargs.pop('fields', None)
		super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

		fields = self.context['request'].query_params.get('fields')
		if fields:
			fields = fields.split(',')
			# Drop any fields that are not specified in the `fields` argument.
			allowed = set(fields)
			existing = set(self.fields.keys())
			for field_name in existing - allowed:
				self.fields.pop(field_name)

class UserProfileSerializer(serializers.ModelSerializer):
	otp = serializers.CharField(required=False)
	class Meta:
		model = UserProfile
		fields = ('alternate_email','country','phone_number', 'phone_number_verified', 'user_image', 'tnc_agreed', 'otp', 'warehouse', 'browser_notification_disable', 'user_approval_status', 'is_profile_set', 'language')
		read_only_fields = ('is_profile_set')

class CompanyTypeSerializer(serializers.ModelSerializer):
	name = serializers.CharField(source='company.name', read_only=True)
	city = serializers.CharField(source='company.city', read_only=True)
	phone_number = serializers.CharField(source='company.phone_number', read_only=True)

	def update(self, instance, validated_data):
		instance.manufacturer = validated_data.get('manufacturer', instance.manufacturer)
		instance.wholesaler_distributor = validated_data.get('wholesaler_distributor', instance.wholesaler_distributor)
		instance.retailer = validated_data.get('retailer', instance.retailer)
		instance.online_retailer_reseller = validated_data.get('online_retailer_reseller', instance.online_retailer_reseller)
		instance.broker = validated_data.get('broker', instance.broker)

		instance.save()

		instance.company.company_type_filled = True

		if instance.manufacturer is True and instance.wholesaler_distributor is False and instance.retailer is False and instance.online_retailer_reseller is False and instance.broker is False:

			instance.company.connections_preapproved = False
			instance.company.push_downstream = 'no'

		instance.company.save()

		return instance

	class Meta:
		model = CompanyType

class CompanyUserSerializer(serializers.ModelSerializer):
	username = serializers.CharField(source='user.username', read_only=True)
	companyname = serializers.CharField(source='company.name', read_only=True)
	company_type = serializers.CharField(source='company.company_type', read_only=True)
	brand_added_flag = serializers.CharField(source='company.brand_added_flag', read_only=True)
	deputed_to_name = serializers.CharField(source='deputed_to.name', read_only=True)
	total_my_catalogs = serializers.SerializerMethodField()
	total_brand_followers = serializers.SerializerMethodField()
	company_group_flag = CompanyTypeSerializer(read_only=True, source='company.company_group_flag')
	address = serializers.IntegerField(source='company.address.id', read_only=True)

	class Meta:
		model = CompanyUser
		extra_kwargs = {
			"user": {
				"validators": [],
			},
			"company": {
				"validators": [],
			},
		}
		# fields = ('id', 'first_name', 'last_name', 'company', 'relationship_type', 'username')

	def create(self, validated_data):
		user = self.context['request'].user
		if CompanyUser.objects.filter(user=user).exists():
			companyUser = CompanyUser.objects.filter(user=user).first()
		else:
			companyUser = CompanyUser.objects.create(**validated_data)
		return companyUser

	def get_total_my_catalogs(self, obj):
		#total = Catalog.objects.filter(company=obj.company).count()
		total = myCatalogs(obj.company)
		return total

	def get_total_brand_followers(self, obj):
		#bids = Brand.objects.filter(Q(company = obj.company) | Q(manufacturer_company = obj.company)).values_list('id', flat=True)
		bids = Brand.objects.filter(Q(manufacturer_company=obj.company) | Q(Q(company=obj.company) & Q(manufacturer_company__isnull=True))).values_list('id', flat=True)
		total = CompanyBrandFollow.objects.filter(brand__in=bids).values_list('company', flat=True).distinct().count()
		return total

class UserSerializer(serializers.ModelSerializer):
	#phone_nos = UserNumberSerializer(many=True, read_only=True)
	userprofile = UserProfileSerializer()
	#companyuser = CompanyUserSerializer(read_only=True)
	companyuser = serializers.SerializerMethodField()
	companyid = serializers.CharField(required=False)
	deputed_to = serializers.CharField(required=False)

	#groups = GroupSerializer(many=True)
	#user_group = serializers.CharField(write_only=True)
	'''def __init__(self, *args, **kwargs):
		super(UserSerializer, self).__init__(*args, **kwargs)
		self.fields['username'].error_messages.update({
			'unique': 'Username is already taken'
		})'''
	def get_companyuser(self, obj):
		try:
			serializer = CompanyUserSerializer(instance=obj.companyuser)
			return serializer.data
		except Exception as e:
			address_id = None
			address = Address.objects.filter(user=obj).first()
			if address:
				address_id = address.id
			else:
				cObj = Company.objects.filter(id=1).first()
				if cObj and cObj.address:
					address_id = cObj.address.id
			return {"id":0,"username":obj.username,"companyname":"Guest","company_type":"nonmanufacturer","brand_added_flag":"no","deputed_to_name":None,"total_my_catalogs":0,"total_brand_followers":0,"company_group_flag":{"id":0,"name":"Guest","city":"Surat","phone_number":"7212451426","manufacturer":False,"wholesaler_distributor":False,"retailer":True,"online_retailer_reseller":False,"broker":False,"company":1},"address":address_id,"company":1,"deputed_from":None,"user":obj.id,"deputed_to":None}

	class Meta:
		model = User
		fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'companyuser', 'userprofile', 'password', 'companyid', 'date_joined', 'last_login', 'is_active', 'is_staff', 'deputed_to')# 'user_group',
		'''error_messages = {
			'username': {
				'unique':'Username is already taken.',
			},
		}'''

		##for custom validation message using def validate_username(self, data):
		extra_kwargs = {
			"username": {
				"validators": [],
			},
			'password': {'write_only': True},
			###'password': {'write_only': True},
		}
	def validate_username(self, data):
		#user=self.context['request'].user
		#company = user.companyuser.company

		if self.instance is None:
			if User.objects.filter(username=data).exists():
				raise serializers.ValidationError('Username is already taken.')
		else:
			if User.objects.filter(username=data).exclude(id=self.instance.id).exists():
				raise serializers.ValidationError('Username is already taken.')

		return data

	'''def to_internal_value(self, data):
		print "to_internal_value"
		print data
		username = data.get('username')
		print username
		if User.objects.filter(username=username).exists():
			raise serializers.ValidationError({"username":"Username is already taken."})

		return data'''

	def update(self, instance, validated_data):
		print "in user update "
		userprofile_exist = validated_data.get('userprofile', None)
		print userprofile_exist
		if userprofile_exist is not None:
			userprofile_data = validated_data.pop('userprofile')
			print "before phone"
			phoneNumber = userprofile_data.get('phone_number', None)
			country = userprofile_data.get('country', instance.userprofile.country)
			if phoneNumber is not None and UserProfile.objects.filter(phone_number=phoneNumber, country=country).exclude(user=instance.id).exists():
				print "IN phone"
				raise serializers.ValidationError({"phone_number":"User is registered with this number"})
			print "after phone"

		instance.username = validated_data.get('username', instance.username)
		instance.first_name = validated_data.get('first_name', instance.first_name)
		instance.last_name = validated_data.get('last_name', instance.last_name)
		instance.email = validated_data.get('email', instance.email)
		instance.groups = validated_data.get('groups', instance.groups.all())
		instance.is_active = validated_data.get('is_active', instance.is_active)
		'''password = validated_data.get('password', instance.password)
		if password is not None:
			print "password="
			print password
			instance.set_password(password)'''
		instance.save()

		deputed_to = validated_data.get('deputed_to', None)

		if userprofile_exist is not None:
			#instance.userprofile.user_approval_status = userprofile_data.get('user_approval_status', instance.userprofile.user_approval_status)
			new_user_approval_status = userprofile_data.get('user_approval_status', instance.userprofile.user_approval_status)
			if instance.userprofile.user_approval_status != new_user_approval_status:
				instance.userprofile.user_approval_status = new_user_approval_status
				if new_user_approval_status == "Approved":
					rno = random.randrange(100000, 999999, 1)
					image = settings.MEDIA_URL+"logo-single.png"

					message = notificationTemplates("user_profile_approved")
					sendNotifications([instance.id], message, {"notId": rno, "title":"Account Approved", "push_type":"promotional", "image":image})

					Token.objects.filter(user=instance).delete()

			instance.userprofile.language = userprofile_data.get('language', instance.userprofile.language)
			instance.userprofile.alternate_email = userprofile_data.get('alternate_email', instance.userprofile.alternate_email)
			instance.userprofile.browser_notification_disable = userprofile_data.get('browser_notification_disable', instance.userprofile.browser_notification_disable)
			#instance.userprofile.phone_number = userprofile_data.get('phone_number', instance.userprofile.phone_number)
			#instance.userprofile.country = userprofile_data.get('country', instance.userprofile.country)
			instance.userprofile.save()

			old_phone_number = instance.userprofile.phone_number
			old_country = instance.userprofile.country
			phone_number = userprofile_data.get('phone_number', None)
			country = userprofile_data.get('country', None)
			otp = userprofile_data.get('otp', None)

			if phone_number is not None and country is not None and (old_phone_number != phone_number or old_country != country):
				if not is_phone_number_available(country, phone_number, True):
					raise serializers.ValidationError({"phone_number":"Phone number already exists. Please choose another phone number"})
				print "in send otp"
				if otp is not None:
					if RegistrationOTP.objects.filter(phone_number=phone_number, country=country).exists():
							registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-id').first()

							if str(registrationOtp.otp) == otp:
								registrationOtp.is_verified = "yes"
								registrationOtp.save()

								instance.userprofile.phone_number = phone_number
								instance.userprofile.save()

								full_mobile_number = str(country.phone_code)+str(phone_number)
								verifyMSG91OTP(full_mobile_number, otp)

								try:
									if instance.companyuser is not None:
										company = instance.companyuser.company
										makeBuyerSupplierFromInvitee(registrationOtp.phone_number, registrationOtp.country, company)
								except ObjectDoesNotExist:
									pass
							else:
								raise serializers.ValidationError({"otp":"Please enter valid OTP"})
								#return Response({"success": "OTP is valid"})
					else:
						raise serializers.ValidationError({"otp":"Please enter valid OTP"})

				else:
					print "in send otp else"
					#country = Country.objects.get(pk=country)

					'''otpno = random.randrange(100000, 999999, 1)
					sendOTP(str(country.phone_code)+str(phone_number), str(otpno))

					registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otpno, country=country)'''
					checkAndSendOTP(phone_number, country)

		login_user=self.context['request'].user
		login_company = get_user_company(login_user) #login_user.companyuser.company
		if login_company is not None:
			companyUser, created = CompanyUser.objects.get_or_create(user=instance, company=login_company)
			if deputed_to is not None:
				companyUser.deputed_to = Company.objects.get(pk=deputed_to)
			else:
				companyUser.deputed_to = None
			companyUser.save()

		return instance
	def create(self, validated_data):
		userprofile_data = validated_data.pop('userprofile')
		print "before phone"
		phoneNumber = userprofile_data.get('phone_number', None)
		country = userprofile_data.get('country', Country.objects.get(pk=1))

		if phoneNumber is not None and UserProfile.objects.filter(phone_number=phoneNumber, country=country).exists():
			raise serializers.ValidationError({"phone_number":"User is registered with this number"})
		print "after phone"
		user_group = validated_data.pop('groups')

		password = validated_data.pop('password')

		companyId = validated_data.pop('companyid', None)
		deputed_to = validated_data.pop('deputed_to', None)

		print "pass"
		usr = User.objects.create(**validated_data)
		usr.set_password(password)
		usr.groups = user_group#[users_group]
		usr.save()

		print "save"

		UserProfile.objects.filter(user=usr).update(**userprofile_data)

		login_user=self.context['request'].user
		login_company = get_user_company(login_user) #login_user.companyuser.company

		invited_from = 'Wishbook'
		if login_company:
			invited_from = login_company.name #'Wishbook'
		if companyId is not None:
			company=Company.objects.get(pk=companyId)
			companyUser = CompanyUser.objects.get_or_create(company=company, user=usr)
			invited_from = company.name

		#sendInvite(str(country.phone_code)+str(phoneNumber), str(self.context['request'].user.username))
		logger.info(str("in UserSerializer oncreate send user_detail sms start"))
		otp = random.randrange(100000, 999999, 1)
		registrationOtp = RegistrationOTP.objects.create(phone_number=phoneNumber, otp=otp, country=country)
		smsurl = 'https://app.wishbooks.io/?m='+str(phoneNumber)+'&o='+str(otp)+'&c='+str(country.id)
		smsurl = urlShortener(smsurl)
		template = smsTemplates("user_detail")% (invited_from, smsurl, phoneNumber, password)
		logger.info(str(template))
		usernumber = str(country.phone_code)+str(phoneNumber)
		smsSend([usernumber], template, True, True)
		sendOTP(usernumber, otp)
		logger.info(str("in UserSerializer oncreate send user_detail sms end"))

		if login_company:
			companyUser, created = CompanyUser.objects.get_or_create(user=usr, company=login_company)

			##start make default buyer/supplier
			makeBuyerSupplierFromInvitee(phoneNumber, country, login_company)
			##end make default buyer/supplier

		if deputed_to is not None:
			companyUser.deputed_to = Company.objects.get(pk=deputed_to)
			companyUser.save()

		return usr


class CompanyKycTaxationSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)

	class Meta:
		model = CompanyKycTaxation

class CompanySerializer(serializers.ModelSerializer):
	users = serializers.SerializerMethodField('get_usr')
	admin = serializers.CharField(required=False)
	chat_user = serializers.CharField(source='chat_admin_user.username', read_only=True)
	company_group_flag = CompanyTypeSerializer(read_only=True)
	#kyc_gstin = serializers.CharField(source='kyc.gstin', read_only=True)
	state_name = serializers.CharField(source='state.state_name', read_only=True)
	city_name = serializers.CharField(source='city.city_name', read_only=True)

	first_name = serializers.CharField(required=False)
	last_name = serializers.CharField(required=False)

	class Meta:
		model = Company
		fields = ('id', 'users', 'chat_user', 'name', 'push_downstream', 'street_address', 'pincode', 'phone_number', 'email', 'website', 'note',
		'status', 'company_type', 'thumbnail', 'brand_added_flag', 'discovery_ok', 'connections_preapproved', 'no_suppliers', 'no_buyers', 'have_salesmen',
		'sell_all_received_catalogs', 'sell_shared_catalogs', 'newsletter_subscribe', 'sms_buyers_on_overdue', 'company_type_filled', 'city', 'state',
		'country', 'chat_admin_user', 'category', 'admin', 'buyers_assigned_to_salesman', 'salesman_mapping', 'company_group_flag', 'state_name', 'city_name',
		'default_catalog_lifetime', 'is_profile_set', 'refered_by', 'first_name', 'last_name', 'paytm_country', 'paytm_phone_number')

	def create(self, validated_data):
		category = validated_data.pop('category')

		if not(category):
			category = Category.objects.values_list('id', flat=True)

		company = Company.objects.create(**validated_data)

		company.category.add(*category)
		company.save()
		branch = Branch.objects.get_or_create(company = company, name="Main Branch - "+company.name, street_address=company.street_address, city=company.city, state=company.state, phone_number=company.phone_number)# ,

		user=self.context['request'].user
		companyUser = CompanyUser.objects.get_or_create(user=user, company=company)

		return company

	#short code to update serializer
	def update(self, instance, validated_data):
		user=self.context['request'].user
		print validated_data

		first_name = validated_data.pop('first_name', None)
		last_name = validated_data.pop('last_name', None)
		email = validated_data.get('email', None)

		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()

		if first_name:
			user.first_name = first_name
		if last_name:
			user.last_name = last_name
		if email:
			if User.objects.filter(email=email).exclude(id=user.id).exists() == False:
				user.email = email
		if first_name or last_name or email:
			user.save()

		return instance

	def validate(self, data):
		user=self.context['request'].user

		if self.instance is None:
			if CompanyUser.objects.filter(user=user).exists():
				raise serializers.ValidationError({'name': 'You are not allow to create new company'})

		return data

	def get_usr(self, obj):
		return list(CompanyUser.objects.filter(company=obj.id).values_list('user__username', flat=True))

class StateSerializer(serializers.ModelSerializer):
	class Meta:
		model = State

class CitySerializer(serializers.ModelSerializer):
	state_name = serializers.CharField(source='state.state_name', read_only=True)
	class Meta:
		model = City

class GetBranchSerializer(serializers.ModelSerializer):
	city = CitySerializer()
	state = StateSerializer()
	'''state = serializers.SerializerMethodField()
	def get_state(self, obj):
		ser = StateSerializer(instance=obj.address.state, context={'request': self.context['request']})
		return ser.data

	city = serializers.SerializerMethodField()
	def get_city(self, obj):
		ser = CitySerializer(instance=obj.address.city, context={'request': self.context['request']})
		return ser.data'''

	class Meta:
		model = Branch

class AddressSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	is_default = serializers.SerializerMethodField(required=False, read_only=True)

	def get_is_default(self, obj):
		if Company.objects.filter(address=obj).exists():
			return True
		return False

	class Meta:
		model = Address

class GetAddressSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	is_default = serializers.SerializerMethodField()

	def get_is_default(self, obj):
		if Company.objects.filter(address=obj).exists():
			return True
		return False

	class Meta:
		model = Address
		depth = 1

class SalesOrderItemSerializer(serializers.ModelSerializer):
	product_title = serializers.CharField(source='product.title', read_only=True)
	product_catalog = serializers.CharField(source='product.catalog.title', read_only=True)
	product_sku = serializers.CharField(source='product.sku', read_only=True)
	product_image = serializers.CharField(source='product.image.thumbnail.150x210', read_only=True)
	product_category = serializers.CharField(source='product.catalog.category.category_name', read_only=True)
	class Meta:
		model = SalesOrderItem
		validators = []
		'''extra_kwargs = {
			"sales_order": {
				"validators": [],
			},
			"product": {
				"validators": [],
			},
		}'''

class BuyerSalesOrderListSerializer(serializers.ListSerializer):
	def to_representation(self, obj):
		query = obj#.all()

		user = self.context['request'].user
		if user.is_authenticated():
			if user.groups.filter(name="administrator").exists():
				company = user.companyuser.company
				query = obj.filter(seller_company=company).distinct().order_by('-id')
			else:
				query = obj.filter(user=user).distinct().order_by('-id')
		else:
			query = obj.none()

		return super(BuyerSalesOrderListSerializer, self).to_representation(query)


class BuyerSalesOrderSerializer(serializers.ModelSerializer):
	items = SalesOrderItemSerializer(many=True, read_only=True)
	company_name = serializers.CharField(source='company.name', read_only=True)
	seller_company_name = serializers.CharField(source='seller_company.name', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	images = serializers.SerializerMethodField()
	def get_images(self, obj):
		images = []
		catalogs = obj.items.all().values_list('product__catalog', flat=True)
		catalogs = Catalog.objects.filter(id__in=catalogs)
		for catalog in catalogs:
			images.append(catalog.thumbnail.thumbnail[settings.SMALL_IMAGE].url)
		return images

	class Meta:
		model = SalesOrder
		list_serializer_class = BuyerSalesOrderListSerializer
		fields = ('id', 'order_number', 'company', 'total_rate', 'date', 'time', 'processing_status', 'customer_status', 'user','items','sales_image','purchase_image', 'company_name', 'seller_company', 'seller_company_name', 'note', 'total_products', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'images', 'payment_status')

class SellerSalesOrderListSerializer(serializers.ListSerializer):
	def to_representation(self, obj):
		query = obj#.all()

		user = self.context['request'].user
		if user.is_authenticated():
			if user.groups.filter(name="administrator").exists():
				company = get_user_company(user) #user.companyuser.company
				query = obj.filter(company=company).distinct().order_by('-id')
			else:
				query = obj.filter(user=user).distinct().order_by('-id')
		else:
			query = obj.none()

		return super(SellerSalesOrderListSerializer, self).to_representation(query)


class SellerSalesOrderSerializer(serializers.ModelSerializer):
	items = SalesOrderItemSerializer(many=True, read_only=True)
	company_name = serializers.CharField(source='company.name', read_only=True)
	seller_company_name = serializers.CharField(source='seller_company.name', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	images = serializers.SerializerMethodField()
	def get_images(self, obj):
		images = []
		catalogs = obj.items.all().values_list('product__catalog', flat=True)
		catalogs = Catalog.objects.filter(id__in=catalogs)
		for catalog in catalogs:
			images.append(catalog.thumbnail.thumbnail[settings.SMALL_IMAGE].url)
		return images

	class Meta:
		model = SalesOrder
		list_serializer_class = SellerSalesOrderListSerializer
		fields = ('id', 'order_number', 'company', 'total_rate', 'date', 'time', 'processing_status', 'customer_status', 'user','items','sales_image','purchase_image', 'company_name', 'seller_company', 'seller_company_name', 'note', 'total_products', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'images', 'payment_status')

class MeetingListSerializer(serializers.ListSerializer):

	def to_representation(self, obj):
		query = obj#.all()

		user = self.context['request'].user

		try:
			if user.is_authenticated() and user.companyuser.company is not None:
				if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					query = obj.filter(user__companyuser__company=company).distinct().order_by('-id')
				else:
					query = obj.filter(user=user).distinct().order_by('-id')
		except ObjectDoesNotExist:
			return obj.none()

		return super(MeetingListSerializer, self).to_representation(query)

class MeetingSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)#add user on create
	duration = serializers.CharField(read_only=True)
	buying_company_name = serializers.CharField(source='buying_company_ref.name', read_only=True)

	salesorder = serializers.SerializerMethodField()

	def get_salesorder(self, obj):
		if obj.end_datetime is not None and obj.buying_company_ref is not None:
			salesorders = SalesOrder.objects.filter(created_at__lte=obj.end_datetime+timedelta(minutes=5), created_at__gte=obj.start_datetime-timedelta(minutes=5), user=obj.user, company=obj.buying_company_ref).values_list('id', flat=True)
			salesorders = list(salesorders)
			return salesorders
		else:
			return []

	'''def to_representation(self, obj):
		query = obj#.all()
		print obj
		user = self.context['request'].user

		try:
			if user.is_authenticated() and user.companyuser.company is not None:
				if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					query = obj.filter(user__companyuser__company=company).distinct().order_by('-id')
				else:
					query = obj.filter(user=user).distinct().order_by('-id')
		except ObjectDoesNotExist:
			return obj.none()

		return super(MeetingSerializer, self).to_representation(query)'''
	class Meta:
		model = Meeting
		#list_serializer_class = MeetingListSerializer
		readonly_fields = ("duration",)
		fields = ('id', 'user', 'duration', 'buying_company_name', 'start_datetime', 'end_datetime', 'start_lat', 'start_long', 'end_lat', 'end_long', 'status', 'buying_company_ref', 'salesorder', 'total_products', 'note', 'purpose', 'company', 'buyer_name_text')


class GetCompanySerializer(serializers.ModelSerializer):
	branches = GetBranchSerializer(many=True, read_only=True)
	buying_order = BuyerSalesOrderSerializer(many=True, read_only=True)##My Sales
	selling_order = SellerSalesOrderSerializer(many=True, read_only=True)##My buy
	meeting_buying_company = MeetingSerializer(many=True, read_only=True)

	chat_user = serializers.CharField(source='chat_admin_user.username', read_only=True)

	users = serializers.SerializerMethodField('get_usr')

	address = GetAddressSerializer()

	def get_usr(self, obj):
		return list(CompanyUser.objects.filter(company=obj.id).values_list('user__username', flat=True))

	thumbnail = serializers.SerializerMethodField('get_image')
	def get_image(self, obj):
		image = None
		if obj.thumbnail:
			image = obj.thumbnail.url
		else:
			if Brand.objects.filter(company=obj.id).exists():
				brand = Brand.objects.filter(company=obj.id).first()
				image = brand.image.thumbnail[settings.SMALL_SQR_IMAGE].url
		return image
	class Meta:
		model = Company

class BrandSerializer(serializers.ModelSerializer):
	name = serializers.CharField()
	image = VersatileImageFieldSerializer(
		sizes='brand_image'
	)

	total_catalogs = serializers.SerializerMethodField()
	is_followed = serializers.SerializerMethodField()

	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	company_id = serializers.ReadOnlyField(source='company.id', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)


	def validate_name(self, data):
		if self.instance is None:
			if Brand.objects.filter(name=data).exists():
				raise serializers.ValidationError(data+' brand already exists.')
		else:
			if Brand.objects.filter(name=data).exclude(id=self.instance.id).exists():
				raise serializers.ValidationError(data+' brand already exists.')

		return data

	def get_total_catalogs(self, obj):
		dtnow = datetime.now()
		# ~ cids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow, catalog__brand=obj).values_list('catalog', flat=True).distinct()
		# ~ total = Product.objects.filter(catalog__view_permission="public", catalog__in=cids).values_list('catalog', flat=True).distinct().count()
		total = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow, catalog__brand=obj, catalog__view_permission="public", catalog__total_products_uploaded__gt=0).values_list('catalog', flat=True).distinct().count()
		return total
		'''
		global currentUserCompany
		currentUser = self.context['request'].user
		total = 0

		currentUserCompany = get_user_company(currentUser) #currentUser.companyuser.company
		disableCatalogIds = getDisableCatalogIds(currentUserCompany)#self.context['disableCatalogIds'] #

		if currentUser.groups.filter(name="salesperson").exists():
			sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()

			catalogsIds = Push_User.objects.filter(buying_company=currentUserCompany, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
			catalogsIds = list(catalogsIds)

			catalogsIds = Push_User.objects.filter(selling_company=currentUserCompany, catalog__in=catalogsIds).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
			catalogsIds = list(catalogsIds)

			total = Catalog.objects.filter((Q(company=currentUserCompany) | Q(id__in=catalogsIds)) & Q(brand=obj) ).exclude(id__in=disableCatalogIds).distinct().count()
		elif currentUserCompany is None:#for guest user
			dtnow = datetime.now()
			cids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow, catalog__brand=obj).values_list('catalog', flat=True).distinct()
			total = Product.objects.filter(catalog__view_permission="public", catalog__in=cids).values_list('catalog', flat=True).distinct().count()
		elif is_manufacturer(currentUserCompany.company_group_flag):
			total = Catalog.objects.filter(company=currentUserCompany, brand=obj).exclude(id__in=disableCatalogIds).count()
		else:
			sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()
			catalogsIds = Push_User.objects.filter(buying_company=currentUserCompany, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
			catalogsIds = list(catalogsIds)
			total = Catalog.objects.filter((Q(company=currentUserCompany) | Q(id__in=catalogsIds) | Q(view_permission="public", supplier_disabled=False)) & Q(brand=obj) ).exclude(id__in=disableCatalogIds).distinct().count()
		return total
		'''

	def get_is_followed(self, obj):
		#global currentUserCompany
		currentUser = self.context['request'].user
		currentUserCompany = get_user_company(currentUser)

		cbf = CompanyBrandFollow.objects.filter(brand=obj, company=currentUserCompany).first()
		if cbf:
			return cbf.id
		return None


	class Meta:
		model = Brand
		fields = ('id', 'name', 'company', 'company_id', 'image', 'total_catalogs', 'is_followed', 'user')

class BrandDistributorSerializer(serializers.ModelSerializer):
	class Meta:
		model = BrandDistributor

class GetBrandDistributorSerializer(serializers.ModelSerializer):
	brand = BrandSerializer(many=True)
	class Meta:
		model = BrandDistributor

class BrandDiscountRuleSerializer(serializers.ModelSerializer):
	discount_rules = serializers.SerializerMethodField()
	def get_discount_rules(self, obj):
		user=self.context['request'].user
		company = get_user_company(user)

		drObj = DiscountRule.objects.filter(selling_company=company, brands=obj).last()
		jsondata = {}
		if drObj:
			jsondata['cash_discount'] = drObj.cash_discount
			jsondata['credit_discount'] = drObj.credit_discount

		return jsondata

	class Meta:
		model = Brand
		fields = ('id', 'name', 'discount_rules', )

class CatalogUploadOptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = CatalogUploadOption

'''class JSONSerializerField(serializers.Field):
	""" Serializer for JSONField -- required to make field writable"""
	def to_internal_value(self, data):
		print "to_internal_value"
		return data
	def to_representation(self, value):
		print "to repres"
		return value'''

class CatalogSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	category_name = serializers.ReadOnlyField(source='category.category_name', read_only=True)
	#picasa_url = serializers.ReadOnlyField(read_only=True)
	#picasa_id = serializers.ReadOnlyField(read_only=True)
	thumbnail = VersatileImageFieldSerializer(
		sizes='catalog_image'
	)
	full_catalog_orders_only = serializers.SerializerMethodField()
	exp_desp_date = serializers.SerializerMethodField('get_expdespdate')

	brand_name = serializers.ReadOnlyField(source='brand.name', read_only=True)
	brand_image = serializers.SerializerMethodField()
	#is_brand_followed = serializers.SerializerMethodField()

	is_disable = serializers.SerializerMethodField('get_disable')
	# exp_desp_date = serializers.SerializerMethodField('get_despdate')

	max_sort_order = serializers.SerializerMethodField()
	price_range = serializers.SerializerMethodField()

	supplier = serializers.SerializerMethodField()
	supplier_name = serializers.SerializerMethodField()
	supplier_chat_user = serializers.SerializerMethodField()
	is_trusted_seller = serializers.SerializerMethodField()
	supplier_id = serializers.SerializerMethodField()
	supplier_details = serializers.SerializerMethodField()
	supplier_company_rating = serializers.SerializerMethodField()

	is_supplier_approved = serializers.SerializerMethodField()
	public_count = serializers.SerializerMethodField()
	push_id = serializers.SerializerMethodField()
	is_viewed = serializers.SerializerMethodField()

	supplier_disabled = serializers.SerializerMethodField()
	buyer_disabled = serializers.SerializerMethodField()

	type = serializers.SerializerMethodField()
	total_products = serializers.SerializerMethodField()

	is_owner = serializers.SerializerMethodField()



	eav = serializers.JSONField(required=False, write_only=True) #serializers.CharField(required=False) #JSONSerializerField() #binary=True,

	def create(self, validated_data):
		eav_insert = validated_data.pop('eav', None)

		catalog = Catalog.objects.create(**validated_data)

		# eav.register(Catalog)

		if eav_insert is not None and eav_insert != "":
			logger.info("CatalogSerializer create eav_insert = %s" % (eav_insert))
			eav_insert = json.loads(eav_insert)
			logger.info("json loads eav_insert = %s" % (eav_insert))

			handel_catalog_eav(catalog, eav_insert)

			# for key, value in eav_insert.items():
			# 	logger.info("catalog serializer create eav array key = %s ,value = %s"% (key, value))
			# 	if isinstance(value, list):
			# 		#logger.info("in isinstance(value, list)")
			# 		for subdata in value:
			# 			enumValue = EnumValue.objects.filter(value=subdata).first()
			# 			if enumValue:
			# 				setattr( catalog.eav, key, enumValue)
			# 				catalog.save()
			# 	else:
			# 		enumValue = EnumValue.objects.filter(value=value).first()
			# 		if enumValue is not None and key not in ["other"]:
			# 			#logger.info("in if enumValue")
			# 			setattr( catalog.eav, key, enumValue)
			# 			catalog.save()
			# 		else:
			# 			#logger.info("in last setattr( catalog.eav, key, value)")
			# 			#set text value
			# 			setattr( catalog.eav, key, value)
			# 			catalog.save()
		# catalogEAVset(catalog)
		return catalog

	def update(self, instance, validated_data):
		eav_insert = validated_data.pop('eav', None)

		instance.title = validated_data.get('title', instance.title)
		instance.brand = validated_data.get('brand', instance.brand)
		instance.thumbnail = validated_data.get('thumbnail', instance.thumbnail)
		instance.view_permission = validated_data.get('view_permission', instance.view_permission)
		instance.category = validated_data.get('category', instance.category)
		instance.company = validated_data.get('company', instance.company)
		instance.sell_full_catalog = validated_data.get('sell_full_catalog', instance.sell_full_catalog)
		instance.mirror = validated_data.get('mirror', instance.mirror)
		instance.expiry_date = validated_data.get('expiry_date', instance.expiry_date)
		instance.default_product_weight = validated_data.get('default_product_weight', instance.default_product_weight)
		#instance.single_piece_price = validated_data.get('single_piece_price', instance.single_piece_price)
		instance.deleted = validated_data.get('deleted', instance.deleted)
		instance.catalog_type = validated_data.get('catalog_type', instance.catalog_type)

		if validated_data.get('single_piece_price', None) or validated_data.get('single_piece_price_percentage', None):
			instance.single_piece_price = validated_data.get('single_piece_price', None)
			instance.single_piece_price_percentage = validated_data.get('single_piece_price_percentage', None)

		instance.dispatch_date = validated_data.get('dispatch_date', instance.dispatch_date)
		instance.save()

		# eav.register(Catalog)

		if eav_insert is not None and eav_insert != "":
			logger.info("CatalogSerializer update eav_insert = %s" % (eav_insert))
			eav_insert = json.loads(eav_insert)
			logger.info("json loads eav_insert = %s" % (eav_insert))

			from eav.models import Attribute, Value as EavValue
			from django.contrib.contenttypes.models import ContentType
			#ct = ContentType.objects.get(id=26)
			ct = ContentType.objects.get(id=25)

			all_attributes = []

			for key, value in eav_insert.items():
				logger.info("catalog serializer update eav array key = %s ,value = %s"% (key, value))

				attribute = Attribute.objects.get(name=key)
				all_attributes.append(attribute)
				final_ev = []
				eavvalues = EavValue.objects.filter(entity_ct=ct, entity_id=instance.id, attribute=attribute)
				#print eavvalues

				if isinstance(value, list):
					for subdata in value:
						enumValue = EnumValue.objects.filter(value=subdata).first()
						if enumValue:
							setattr( instance.eav, key, enumValue)
							instance.save()
							final_ev.append(enumValue)
				else:
					enumValue = EnumValue.objects.filter(value=value).first()
					if enumValue is not None and key not in ["other"]:
						setattr( instance.eav, key, enumValue)
						instance.save()
						final_ev.append(enumValue)
					else:
						#set text value
						setattr( instance.eav, key, value)
						instance.save()
				eavvalues.exclude(value_enum__in=final_ev).delete()
			#to delete fields which is not posted
			EavValue.objects.filter(entity_ct=ct, entity_id=instance.id).exclude(attribute__in=all_attributes).delete()
		catalogEAVset(instance)
		instance.save()
		return instance

	def validate(self, data):
		user=self.context['request'].user
		company = user.companyuser.company
		brand_distributor = BrandDistributor.objects.filter(company=company).order_by('brand').values_list('brand', flat=True).distinct()
		brands = Brand.objects.filter(Q(company=company) | Q(id__in=brand_distributor)).values_list('id', flat=True).distinct()

		if data.get('brand', None) != None and not user.is_staff:
			if data['brand'].id not in brands:
				raise serializers.ValidationError({"brand":"Select valid brand"})

		if data.get('title', None) != None:
			if self.instance is None:
				#~ if Catalog.objects.filter(title=data['title'], company=company).exists():
				if Catalog.objects.filter(Q(title=data['title'], brand=data['brand']) | Q(title=data['title'], company=company)).exists():
					raise serializers.ValidationError({"title":"Catalog already exists with the same title. Please change the title"})
			else:
				#~ if Catalog.objects.filter(title=data['title'], company=company).exclude(id=self.instance.id).exists():
				if Catalog.objects.filter(Q(title=data['title'], brand=data['brand']) | Q(title=data['title'], company=company)).exclude(id=self.instance.id).exists():
					raise serializers.ValidationError({"title":"Catalog already exists with the same title. Please change the title"})
					#raise serializers.ValidationError({"title":"title should be unique"})
		#company.id not in settings.PAID_CLIENTS
		if PaidClient.objects.filter(company=company).exists() == False and Catalog.objects.filter(created_at=date.today(), company=company).count() >= settings.MAX_CATALOG_UPLOAD_LIMIT and self.instance is None:
			msg = "Currently you are using Trial Version and you have reached the daily "+str(settings.MAX_CATALOG_UPLOAD_LIMIT)+" catalog limit. Please upgrade to a paid plan."
			raise serializers.ValidationError({"catalog":msg})

		return data

	def get_brand_image(self, obj):
		return obj.brand.image.thumbnail[settings.SMALL_SQR_IMAGE].url

	'''def get_is_brand_followed(self, obj):
		global user
		global currentUserCompany

		user=self.context['request'].user
		currentUserCompany = user.companyuser.company

		cbf = CompanyBrandFollow.objects.filter(brand=obj.brand, company=currentUserCompany).first()
		if cbf:
			return cbf.id
		return None'''

	'''def get_full_catalog_orders_only(self, obj):
		global currentUserCompany
		global pushUserObj
		global user
		global cpfObj

		viewType = self.context['request'].query_params.get('view_type', None)

		pushUserObj = None

		user=self.context['request'].user
		currentUserCompany = get_user_company(user) #user.companyuser.company

		sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()
		cpfObj = CompanyProductFlat.objects.filter(catalog=obj, buying_company=currentUserCompany, is_disable=False, selling_company__in=list(sellingCompanyObj)).select_related('push_reference', 'selling_company').last()

		if cpfObj:
			pushUserObj = Push_User.objects.filter(buying_company=currentUserCompany, catalog=obj, push=cpfObj.push_reference).last()

		if viewType is not None and viewType.lower()=="myreceived":
			if pushUserObj:
				return pushUserObj.full_catalog_orders_only
			else:
				return obj.sell_full_catalog
		elif obj.view_permission.lower()=="public":
			return obj.sell_full_catalog
		elif obj.company == currentUserCompany:
			return obj.sell_full_catalog
		else:
			if pushUserObj:
				return pushUserObj.full_catalog_orders_only
			else:
				return obj.sell_full_catalog'''

	def get_expdespdate(self, obj):
		global currentUserCompany
		global pushUserObj
		global user
		global cpfObj

		viewType = self.context['request'].query_params.get('view_type', None)

		pushUserObj = None

		user=self.context['request'].user
		currentUserCompany = get_user_company(user) #user.companyuser.company

		sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()
		cpfObj = CompanyProductFlat.objects.filter(catalog=obj, buying_company=currentUserCompany, is_disable=False, selling_company__in=list(sellingCompanyObj)).select_related('push_reference', 'selling_company').last()

		if cpfObj:
			pushUserObj = Push_User.objects.filter(buying_company=currentUserCompany, catalog=obj, push=cpfObj.push_reference).last()

		if cpfObj and cpfObj.push_reference.exp_desp_date is not None:
			return str(cpfObj.push_reference.exp_desp_date)
		else:
			return None

	def get_disable(self, obj): #NOT using
		global currentUserCompany
		status = False
		if CatalogSelectionStatus.objects.filter(company=currentUserCompany, catalog=obj, status="Disable").exists():
			status = True
		return status

	# def get_despdate(self, obj):
	# 	global cpfObj
	# 	if cpfObj and cpfObj.push_reference.exp_desp_date is not None:
	# 		return str(cpfObj.push_reference.exp_desp_date)
	# 	else:
	# 		return None

	def get_max_sort_order(self, obj):
		global product_minmax
		# max_order = Product.objects.filter(catalog=obj).aggregate(Max('sort_order')).get('sort_order__max', 0)
		product_minmax = Product.objects.filter(catalog=obj).aggregate(max_sort_order=Max('sort_order'), min_public_price=Min('public_price'), max_public_price=Max('public_price'), min_price=Min('price'), max_price=Max('price'))
		max_order = product_minmax['max_sort_order']
		if max_order is None:
			max_order = 0
		return max_order

	def get_price_range(self, obj):
		global currentUserCompany
		global viewType
		global product_minmax

		min_price = None
		max_price = None

		viewType = self.context['request'].query_params.get('view_type', None)
		if viewType and viewType.lower()=="myreceived":
			# min_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Min('final_price')).get('final_price__min', 0)
			# max_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Max('final_price')).get('final_price__max', 0)
			cpf_minmax = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(min_final_price=Min('final_price'), max_final_price=Max('final_price'))
			min_price = cpf_minmax['min_final_price']
			max_price = cpf_minmax['max_final_price']
		elif obj.view_permission.lower()=="public":
			#print obj.catalogeavflat
			# min_price = Product.objects.filter(catalog=obj).aggregate(Min('public_price')).get('public_price__min', 0)
			# max_price = Product.objects.filter(catalog=obj).aggregate(Max('public_price')).get('public_price__max', 0)
			###minmax = Product.objects.filter(catalog=obj).aggregate(min_price=Min('public_price'), max_price=Max('public_price'))
			min_price = product_minmax['min_public_price']
			max_price = product_minmax['max_public_price']
		elif obj.company == currentUserCompany:
			# min_price = Product.objects.filter(catalog=obj).aggregate(Min('price')).get('price__min', 0)
			# max_price = Product.objects.filter(catalog=obj).aggregate(Max('price')).get('price__max', 0)
			min_price = product_minmax['min_price']
			max_price = product_minmax['max_price']
		else:
			# min_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Min('final_price')).get('final_price__min', 0)
			# max_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Max('final_price')).get('final_price__max', 0)
			cpf_minmax = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(min_final_price=Min('final_price'), max_final_price=Max('final_price'))
			min_price = cpf_minmax['min_final_price']
			max_price = cpf_minmax['max_final_price']

		if min_price is None:
			min_price = 0
		if max_price is None:
			max_price = 0

		if min_price == max_price:
			return str(int(min_price))
		else:
			return str(int(min_price))+"-"+str(int(max_price))

	def get_supplier(self, obj):
		global user
		global currentUserCompany
		global supplierObj
		global cpfObj
		global isPublicCatalog
		global catalgsellerObjs
		global viewType
		global csFirstObj

		supplierObj = None
		isPublicCatalog = False
		catalgsellerObjs = None
		csFirstObj = None

		try:
			#if obj.view_permission.lower()=="public":
			#	supplierObj = obj.company
			#	return obj.company.id
			#else:
			if user.groups.filter(name="salesperson").exists():
				supplierObj = currentUserCompany
				return currentUserCompany.id
			#~ elif cpfObj:
				#~ supplierObj = cpfObj.selling_company
				#~ return supplierObj.id
			elif viewType and viewType.lower()=="myreceived" and cpfObj:
				supplierObj = cpfObj.selling_company
				return supplierObj.id
			elif obj.view_permission.lower()=="public":
				isPublicCatalog = True
				dtnow = datetime.now()
				catalgsellerObjs = CatalogSeller.objects.filter(catalog=obj, selling_type="Public", status="Enable", expiry_date__gt=dtnow).order_by('-selling_company__trusted_seller','id')

				# csFirstObj = catalgsellerObjs.first()
				# if csFirstObj:
				# 	supplierObj = csFirstObj.selling_company
				# 	return supplierObj.id
				if catalgsellerObjs:
					for catalgsellerObj in catalgsellerObjs:
						csFirstObj = catalgsellerObj
						supplierObj = csFirstObj.selling_company
						return supplierObj.id
			elif cpfObj:
				supplierObj = cpfObj.selling_company
				return supplierObj.id
			return None
		except Exception as e:
			#print obj
			logger.info("get_supplier "+str(e))
			return None

	def get_full_catalog_orders_only(self, obj):
		global pushUserObj
		global csFirstObj
		global catalgsellerObjs
		global isPublicCatalog

		viewType = self.context['request'].query_params.get('view_type', None)

		# ~ if pushUserObj:
			# ~ return pushUserObj.full_catalog_orders_only
		# ~ else:
			# ~ return obj.sell_full_catalog

		if viewType is not None and viewType.lower()=="myreceived":
			if pushUserObj:
				return pushUserObj.full_catalog_orders_only
			else:
				return obj.sell_full_catalog
		elif isPublicCatalog:
			## return obj.sell_full_catalog
			# if csFirstObj:
			# 	return csFirstObj.sell_full_catalog
			if catalgsellerObjs:
				temp_flag = True
				for catalgsellerObj in catalgsellerObjs:
					if catalgsellerObj.sell_full_catalog is False:
						temp_flag = False
						break
				return temp_flag
			else:
				return obj.sell_full_catalog
		elif obj.company == currentUserCompany:
			return obj.sell_full_catalog
		elif pushUserObj:
			return pushUserObj.full_catalog_orders_only
		else:
			return obj.sell_full_catalog

	def get_supplier_name(self, obj):
		global supplierObj

		if supplierObj:
			return supplierObj.name
		return supplierObj

	def get_supplier_chat_user(self, obj):
		global supplierObj
		if supplierObj:
			if supplierObj.chat_admin_user:
				return supplierObj.chat_admin_user.username
		return supplierObj

	def get_is_trusted_seller(self, obj):
		global supplierObj
		if supplierObj:
			return supplierObj.trusted_seller
		return False

	def get_supplier_id(self, obj):
		global currentUserCompany
		global supplierObj

		buyerObj = Buyer.objects.filter(selling_company=supplierObj, buying_company=currentUserCompany, status="approved").values_list('id', flat=True).first()
		if buyerObj:
			return buyerObj
		else:
			return None

	def get_supplier_details(self, obj):
		global supplierObj
		global currentUserCompany
		global isPublicCatalog
		global catalgsellerObjs

		jsondata = {}

		jsondata['i_am_selling_this'] = False
		if CatalogSeller.objects.filter(catalog=obj, selling_type="Public", selling_company=currentUserCompany).exists():
			jsondata['i_am_selling_this'] = True
		if obj.view_permission == "push":
			jsondata['i_am_selling_this'] = True

		if isPublicCatalog:
			jsondata['total_suppliers'] = catalgsellerObjs.count()
		if supplierObj:

			near_me = self.context['request'].query_params.get('near_me', 'false')
			if near_me is not None and near_me.lower() == "true":
				jsondata['near_by_sellers'] = CompanySellsToState.objects.filter(company=supplierObj, state=currentUserCompany.address.state).exclude(intermediate_buyer__isnull=True).count()
			#jsondata['city_name'] = supplierObj.address.city.city_name
		return jsondata

	def get_supplier_company_rating(self, obj):
		global supplierObj
		if supplierObj:
			if CompanyRating.objects.filter(company=supplierObj.id).exists():
				serializer = GetCompanyRatingSerializer(instance=supplierObj.companyrating, context={'request': self.context['request']})
				return serializer.data
		return {}

	def get_is_supplier_approved(self, obj):
		global user
		global currentUserCompany
		if Buyer.objects.filter(selling_company=obj.company, buying_company=currentUserCompany, status="approved").exists():
			return True
		else:
			return False

	def get_public_count(self, obj):
		return 0
		# if obj.view_permission.lower() == "public":
		# 	ccvclicks = CompanyCatalogView.objects.filter(catalog=obj).aggregate(Sum('clicks')).get('clicks__sum', 0)
		# 	if ccvclicks is None:
		# 		ccvclicks = 0
		# 	return ccvclicks
		# else:
		# 	return 0

	def get_push_id(self, obj):
		global cpfObj
		if cpfObj and cpfObj.push_reference is not None:
			return cpfObj.push_reference.id
		else:
			return None

	def get_supplier_disabled(self, obj):
		global currentUserCompany
		global pushUserObj
		global isPublicCatalog
		global catalgsellerObjs
		global viewType
		global csFirstObj

		if viewType and viewType.lower()=="myreceived" and pushUserObj:
			return pushUserObj.supplier_disabled
		#~ if pushUserObj:
			#~ return pushUserObj.supplier_disabled
		elif isPublicCatalog:
			#print "catalgsellerObjs", catalgsellerObjs
			try:
				# if catalgsellerObjs.first().status == "Disable":
				if csFirstObj.status == "Disable":
					return True
			except Exception as e:
				return True
		elif obj.company == currentUserCompany:
			return obj.supplier_disabled
		elif pushUserObj:
			return pushUserObj.supplier_disabled

		'''tempPUObj = Push_User.objects.filter(buying_company=currentUserCompany, catalog=obj).first()
		if tempPUObj:
			return tempPUObj.supplier_disabled'''
		return False

	def get_buyer_disabled(self, obj):
		global currentUserCompany
		global pushUserObj
		global viewType
		'''tempPUObj = Push_User.objects.filter(buying_company=currentUserCompany, catalog=obj).first()
		if tempPUObj:
			return tempPUObj.buyer_disabled
		else:
			if obj.supplier_disabled==True and obj.company==currentUserCompany:
				return True
			else:
				return False
		'''
		if viewType and viewType.lower()=="myreceived" and pushUserObj:
			return pushUserObj.buyer_disabled
		#~ if pushUserObj:
			#~ return pushUserObj.buyer_disabled
		elif CatalogSeller.objects.filter(selling_company=currentUserCompany, status="Disable", catalog=obj).exists():
			return True
		elif obj.supplier_disabled==True and obj.company==currentUserCompany:
			return True
		elif pushUserObj:
			return pushUserObj.buyer_disabled
		else:
			return False

	def get_is_viewed(self, obj):
		global pushUserObj
		global currentUserCompany

		status = "no"
		if obj.company == currentUserCompany:
			status = "yes"
		else:
			if pushUserObj:
				status = pushUserObj.is_viewed
		return status

	def get_type(self, obj):
		return "catalog"

	def get_total_products(self, obj):
		# global currentUserCompany
		# disableProductsIds = ProductStatus.objects.filter(product__catalog=obj, status='Disable', company=currentUserCompany).values_list('product', flat=True)
		# total = obj.products.all().exclude(id__in=disableProductsIds).count()
		# return total
		return obj.total_products_uploaded

	def get_is_owner(self, obj):
		global currentUserCompany
		if obj.company == currentUserCompany:
			return True

		return False

	class Meta:
		model = Catalog
		fields = ('id', 'brand', 'title', 'thumbnail', 'view_permission', 'category', 'category_name', 'company', 'sell_full_catalog', 'exp_desp_date', 'brand_name', 'brand_image', 'is_disable', 'created_at', 'is_product_price_null', 'max_sort_order', 'price_range', 'supplier', 'full_catalog_orders_only', 'supplier_name', 'is_supplier_approved', 'public_count', 'supplier_chat_user', 'push_id', 'is_viewed', 'type', 'is_trusted_seller', 'supplier_id', 'supplier_details', 'supplier_company_rating', 'supplier_disabled', 'buyer_disabled', 'total_products', 'expiry_date', 'default_product_weight', 'is_owner', 'eav', 'deleted', 'single_piece_price', 'single_piece_price_percentage', 'dispatch_date', 'catalog_type') #, 'is_hidden' 'picasa_url', 'picasa_id', 'is_brand_followed',

	'''def __init__(self, *args, **kwargs):
		super(CatalogSerializer, self).__init__(*args, **kwargs)

		request = kwargs['context']['request']

		if request.method == 'GET':
			self.fields['brand'] = BrandSerializer()'''

class GetNestedCatalogSerializer(serializers.ModelSerializer):
	brand = BrandSerializer()

	class Meta:
		model = Catalog
		fields = ('id', 'title', 'brand')

class GetCompanyRatingSerializer(serializers.ModelSerializer):
	seller_score = serializers.SerializerMethodField()
	buyer_score = serializers.SerializerMethodField()

	def get_seller_score(self, obj):
		return obj.seller_score*5

	def get_buyer_score(self, obj):
		return obj.buyer_score*5

	class Meta:
		model = CompanyRating

class SellerPolicySerializer(serializers.ModelSerializer):
	class Meta:
		model = SellerPolicy

class GetCatalogSerializer(serializers.ModelSerializer):
	brand = BrandSerializer()

	push_user_id = serializers.SerializerMethodField('get_pushuser')
	total_products = serializers.SerializerMethodField('get_totalproduct')
	full_catalog_orders_only = serializers.SerializerMethodField()
	is_disable = serializers.SerializerMethodField('get_disable')
	is_viewed = serializers.SerializerMethodField('get_viewed')
	exp_desp_date = serializers.SerializerMethodField('get_expdespdate')

	max_sort_order = serializers.SerializerMethodField()

	thumbnail = VersatileImageFieldSerializer(
		sizes='catalog_image'
	)
	price_range = serializers.SerializerMethodField()
	single_piece_price_range = serializers.SerializerMethodField()

	supplier = serializers.SerializerMethodField()
	supplier_name = serializers.SerializerMethodField()
	supplier_chat_user = serializers.SerializerMethodField()
	is_trusted_seller = serializers.SerializerMethodField()
	is_supplier_approved = serializers.SerializerMethodField()
	supplier_id = serializers.SerializerMethodField()
	supplier_company_rating = serializers.SerializerMethodField()
	supplier_details = serializers.SerializerMethodField()
	#suppliers = serializers.SerializerMethodField()

	supplier_disabled = serializers.SerializerMethodField()
	buyer_disabled = serializers.SerializerMethodField()

	eavdata = serializers.SerializerMethodField()

	#products = serializers.SerializerMethodField('get_prdct')
	products = serializers.SerializerMethodField()
	category_name = serializers.CharField(source='category.category_name', read_only=True)

	is_addedto_wishlist = serializers.SerializerMethodField()
	enquiry_id = serializers.SerializerMethodField()

	def get_eavdata(self, obj):
		global catalogeav
		catalogeav = getCatalogEAV(obj, "allInJson")
		return catalogeav

	#def get_prdct(self, obj):
	def get_products(self, obj):
		#print "in get_products"
		global user
		global totalProduct
		global pushUserObj
		global currentUserCompany
		global cpfObj
		global catalogeav
		global viewType

		barcode = self.context['request'].query_params.get('barcode', None)
		warehouse = self.context['request'].query_params.get('warehouse', None)
		viewType = self.context['request'].query_params.get('view_type', None)

		totalProduct = 0
		pushUserObj = None
		cpfObj = None

		user = self.context['request'].user
		currentUserCompany=get_user_company(user) #user.companyuser.company

		if obj.company == currentUserCompany:
			is_same_company = True
		else:
			is_same_company = False

		products = []
		sellingCompanyObj = []

		# WB-2287 # if viewType=received but buying comapny didn't receive that catalog so we need to change that view_type to public if catalog is public
		if (viewType and "received" in viewType) and not CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj, is_disable=False).exists():
			if obj.view_permission.lower() == "public":
				viewType = "public"

		#sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()
		if (viewType and "received" in viewType) or (obj.view_permission.lower() != "public" and is_same_company != True):
			#elif CompanyProductFlat.objects.filter(buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, catalog=obj, is_disable=False).exists():
			sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()
			productsIds = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, catalog=obj, is_disable=False).values_list('product', flat=True)
			#print "received productsIds", productsIds
			products = obj.products.filter(id__in=productsIds).order_by('-catalog','sort_order','id')#.values_list('id', flat=True)
		elif obj.view_permission.lower() == "public":
			products = obj.products.all().order_by('-catalog','sort_order','id')
			disableProductsIds = ProductStatus.objects.filter(product__in=products, status='Disable', company=obj.company).values_list('product', flat=True)
			#print "disableProductsIds", disableProductsIds
			products = products.exclude(id__in=disableProductsIds)
			#print "public start"
		elif is_same_company:
			products = obj.products.all().order_by('-catalog','sort_order','id')
			#print "products", products

		resProducts = []

		catalogserializer = GetNestedCatalogSerializer(instance=obj, context={'request': self.context['request']})

		#fabric = getCatalogEAV(obj, "fabricInString")
		#work = getCatalogEAV(obj, "workInString")
		fabric = work = None
		if "fabric" in catalogeav.keys():
			fabric = ", ".join(catalogeav["fabric"])
		if "work" in catalogeav.keys():
			work = ", ".join(catalogeav["work"])

		for product in products:
			totalProduct += 1

			#fabricworkjson = getEAVFabricWork(product, "BothInJson")
			#print "fabricworkjson", fabricworkjson

			resProduct = {}
			resProduct['id'] = product.id
			resProduct['sku'] = product.sku
			resProduct['title'] = product.title
			resProduct['fabric'] = fabric #fabricworkjson['fabric'] #product.fabric
			resProduct['work'] = work #fabricworkjson['work'] #product.work
			resProduct['price'] = product.price
			resProduct['public_price'] = product.public_price
			resProduct['single_piece_price'] = product.single_piece_price

			resProduct['catalog'] = catalogserializer.data

			if barcode is not None and barcode.lower() == 'true' and warehouse is not None:
				barcodeObj = Barcode.objects.filter(warehouse=warehouse, product=product.id).first()
				if barcodeObj:
					resProduct['barcode'] = barcodeObj.barcode

			resProduct['image'] = {}
			try:
				resProduct['image']['thumbnail_small'] = product.image.thumbnail[settings.SMALL_IMAGE].url
				resProduct['image']['thumbnail_medium'] = product.image.thumbnail[settings.LARGE_IMAGE].url
			except Exception:
				logger.info("Exception : in product image. product ID = ")
				logger.info(str(product.id))
				pass

			resProduct['push_user_product_id'] = None

			if (viewType and "received" in viewType) or (obj.view_permission.lower() != "public" and is_same_company != True):
				#elif CompanyProductFlat.objects.filter(product=product, buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, catalog=obj, is_disable=False).exists():
				cpfObj = CompanyProductFlat.objects.filter(product=product, buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, catalog=obj, is_disable=False).select_related('selling_company', 'push_reference').last()

				resProduct['final_price'] = cpfObj.final_price
				resProduct['selling_price'] = cpfObj.selling_price

				resProduct['is_disable'] = cpfObj.is_disable

				#pupid = Push_User_Product.objects.filter(product=product, buying_company=currentUserCompany, selling_company=cpfObj.selling_company, catalog=obj, push=cpfObj.push_reference, user=user).values_list('id', flat=True).last()
				#print "received productsIds"
				#if pupid:
				#	resProduct['push_user_product_id'] = pupid
				resProduct['push_user_product_id'] = cpfObj.id

				resProduct['delete_allowed'] = False
			elif obj.view_permission.lower() == "public":
				resProduct['final_price'] = product.public_price
				resProduct['selling_price'] = product.public_price

				resProduct['delete_allowed'] = True
				#print "public"
				resProduct['is_disable'] = False
				if ProductStatus.objects.filter(company=currentUserCompany, product=product, status="Disable").exists():
					resProduct['is_disable'] = True
			elif is_same_company:
				resProduct['final_price'] = product.price
				resProduct['selling_price'] = product.price

				resProduct['delete_allowed'] = True

				# ~ if CompanyProductFlat.objects.filter(product=product.id).exists():
					# ~ resProduct['delete_allowed'] = False

				resProduct['is_disable'] = False
				if ProductStatus.objects.filter(company=currentUserCompany, product=product, status="Disable").exists():
					resProduct['is_disable'] = True

			resProduct['product_like_id'] = None

			# ~ plObj = ProductLike.objects.filter(user=user, product=product.id).values_list('id', flat=True).last()
			# ~ if plObj:
				# ~ resProduct['product_like_id'] = plObj

			resProduct['product_likes'] = 0 #ProductLike.objects.filter(product=product.id).count()

			resProducts.append(resProduct)

		if cpfObj:
			pushUserObj = Push_User.objects.filter(buying_company=currentUserCompany, catalog=obj, push=cpfObj.push_reference).last()

		return resProducts

	#category = serializers.SerializerMethodField('get_catgry')
	#def get_catgry(self, obj):
	#	return [obj.category.id]

	def get_totalproduct(self, obj):
		global totalProduct
		return totalProduct
		#return obj.total_products_uploaded

	def get_pushuser(self, obj):
		global pushUserObj
		if pushUserObj:
			return pushUserObj.id
		else:
			return None



	def get_disable(self, obj):
		global currentUserCompany
		status = False
		if CatalogSelectionStatus.objects.filter(company=currentUserCompany, catalog=obj, status="Disable").exists():
			status = True
		return status

	def get_viewed(self, obj):
		global currentUserCompany
		global catalogCompany
		global pushUserObj
		catalogCompany = obj.company

		status = "no"
		# ~ if catalogCompany==currentUserCompany:
			# ~ status = "yes"
		# ~ else:
			# ~ if pushUserObj:
				# ~ status = pushUserObj.is_viewed
		return status

	def get_expdespdate(self, obj):
		global pushUserObj
		# ~ if pushUserObj is not None and pushUserObj.push.exp_desp_date is not None:
			# ~ return str(pushUserObj.push.exp_desp_date)
		# ~ else:
			# ~ return None
		return None

	def get_max_sort_order(self, obj):
		global product_minmax
		# max_order = Product.objects.filter(catalog=obj).aggregate(Max('sort_order')).get('sort_order__max', 0)
		product_minmax = Product.objects.filter(catalog=obj).aggregate(max_sort_order=Max('sort_order'), min_public_price=Min('public_price'), max_public_price=Max('public_price'), min_price=Min('price'), max_price=Max('price'))
		max_order = product_minmax['max_sort_order']
		if max_order is None:
			max_order = 0
		return max_order

	def get_price_range(self, obj):
		global currentUserCompany
		global viewType
		global product_minmax
		min_price = None
		max_price = None

		#if viewType and viewType=="myreceived":
		if viewType and "received" in viewType:
			# min_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Min('final_price')).get('final_price__min', 0)
			# max_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Max('final_price')).get('final_price__max', 0)
			cpf_minmax = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(min_final_price=Min('final_price'), max_final_price=Max('final_price'))
			min_price = cpf_minmax['min_final_price']
			max_price = cpf_minmax['max_final_price']
		elif obj.view_permission.lower()=="public":
			# min_price = Product.objects.filter(catalog=obj).aggregate(Min('public_price')).get('public_price__min', 0)
			# max_price = Product.objects.filter(catalog=obj).aggregate(Max('public_price')).get('public_price__max', 0)
			###minmax = Product.objects.filter(catalog=obj).aggregate(min_price=Min('public_price'), max_price=Max('public_price'))
			min_price = product_minmax['min_public_price']
			max_price = product_minmax['max_public_price']
		elif obj.company == currentUserCompany:
			# min_price = Product.objects.filter(catalog=obj).aggregate(Min('price')).get('price__min', 0)
			# max_price = Product.objects.filter(catalog=obj).aggregate(Max('price')).get('price__max', 0)
			min_price = product_minmax['min_price']
			max_price = product_minmax['max_price']
		else:
			# min_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Min('final_price')).get('final_price__min', 0)
			# max_price = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(Max('final_price')).get('final_price__max', 0)
			cpf_minmax = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, catalog=obj).aggregate(min_final_price=Min('final_price'), max_final_price=Max('final_price'))
			min_price = cpf_minmax['min_final_price']
			max_price = cpf_minmax['max_final_price']

		if min_price is None:
			min_price = 0
		if max_price is None:
			max_price = 0

		if min_price == max_price:
			return str(int(min_price))
		else:
			return str(int(min_price))+"-"+str(int(max_price))

	def get_single_piece_price_range(self, obj):
		global currentUserCompany
		global viewType

		# min_price = Product.objects.filter(catalog=obj).aggregate(Min('single_piece_price')).get('single_piece_price__min', 0)
		# max_price = Product.objects.filter(catalog=obj).aggregate(Max('single_piece_price')).get('single_piece_price__max', 0)

		minmax = Product.objects.filter(catalog=obj).aggregate(min_price=Min('single_piece_price'), max_price=Max('single_piece_price'))
		min_price = minmax['min_price']
		max_price = minmax['max_price']

		if min_price == max_price:
			if min_price:
				return str(int(min_price))
			return min_price
		else:
			return str(int(min_price))+"-"+str(int(max_price))

	def get_supplier(self, obj):
		global user
		global currentUserCompany
		global supplierObj
		global cpfObj
		global isPublicCatalog
		global catalgsellerObjs
		global viewType
		global csFirstObj

		supplierObj = None
		isPublicCatalog = False
		catalgsellerObjs = None
		csFirstObj = None

		try:
			#if obj.view_permission.lower()=="public":
			#	supplierObj = obj.company
			#	return obj.company.id
			#else:
			if user.groups.filter(name="salesperson").exists():
				supplierObj = currentUserCompany
				return currentUserCompany.id
			#~ elif cpfObj:
				#~ supplierObj = cpfObj.selling_company
				#~ return supplierObj.id
			#elif viewType and viewType=="myreceived" and cpfObj:
			elif viewType and "received" in viewType and cpfObj:
				supplierObj = cpfObj.selling_company
				return supplierObj.id
			elif obj.view_permission.lower()=="public":
				isPublicCatalog = True
				dtnow = datetime.now()
				catalgsellerObjs = CatalogSeller.objects.filter(catalog=obj, selling_type="Public", status="Enable", expiry_date__gt=dtnow).order_by('-selling_company__trusted_seller','id')

				# csFirstObj = catalgsellerObjs.first()
				# if csFirstObj:
				# 	supplierObj = csFirstObj.selling_company
				# 	return supplierObj.id
				if catalgsellerObjs:
					for catalgsellerObj in catalgsellerObjs:
						csFirstObj = catalgsellerObj
						supplierObj = csFirstObj.selling_company
						return supplierObj.id
			elif cpfObj:
				supplierObj = cpfObj.selling_company
				return supplierObj.id
			return None
		except Exception as e:
			logger.info("get_supplier "+str(e))
			return None

	def get_full_catalog_orders_only(self, obj):
		global pushUserObj
		global csFirstObj
		global catalgsellerObjs
		global isPublicCatalog

		viewType = self.context['request'].query_params.get('view_type', None)

		# ~ if pushUserObj:
			# ~ return pushUserObj.full_catalog_orders_only
		# ~ else:
			# ~ return obj.sell_full_catalog

		if viewType is not None and viewType.lower()=="myreceived":
			if pushUserObj:
				return pushUserObj.full_catalog_orders_only
			else:
				return obj.sell_full_catalog
		elif isPublicCatalog:
			## return obj.sell_full_catalog
			# if csFirstObj:
			# 	return csFirstObj.sell_full_catalog
			if catalgsellerObjs:
				temp_flag = True
				for catalgsellerObj in catalgsellerObjs:
					if catalgsellerObj.sell_full_catalog is False:
						temp_flag = False
						break
				return temp_flag
			else:
				return obj.sell_full_catalog
		elif obj.company == currentUserCompany:
			return obj.sell_full_catalog
		elif pushUserObj:
			return pushUserObj.full_catalog_orders_only
		else:
			return obj.sell_full_catalog

	def get_supplier_name(self, obj):
		global supplierObj

		if supplierObj:
			supplierObj = Company.objects.select_related('chat_admin_user', 'companyrating', 'address__state', 'address__city').prefetch_related('sellerpolicy_set').get(pk=supplierObj.pk)
			return supplierObj.name
		return supplierObj

	def get_supplier_chat_user(self, obj):
		global supplierObj
		if supplierObj:
			if supplierObj.chat_admin_user:
				return supplierObj.chat_admin_user.username
		return supplierObj

	def get_is_trusted_seller(self, obj):
		global supplierObj
		if supplierObj:
			return supplierObj.trusted_seller
		return False

	def get_is_supplier_approved(self, obj):
		global user
		global currentUserCompany
		if Buyer.objects.filter(selling_company=obj.company, buying_company=currentUserCompany, status="approved").exists():
			return True
		else:
			return False

	def get_supplier_id(self, obj):
		global currentUserCompany
		global supplierObj

		buyerObj = Buyer.objects.filter(selling_company=supplierObj, buying_company=currentUserCompany, status="approved").values_list('id', flat=True).first()
		if buyerObj:
			return buyerObj
		else:
			return None

	def get_supplier_company_rating(self, obj):
		global supplierObj
		if supplierObj:
			if CompanyRating.objects.filter(company=supplierObj.id).exists():
				serializer = GetCompanyRatingSerializer(instance=supplierObj.companyrating, context={'request': self.context['request']})
				return serializer.data
		return {}

	def get_supplier_details(self, obj):
		global supplierObj
		global currentUserCompany
		global isPublicCatalog
		global catalgsellerObjs

		jsondata = {}

		jsondata['i_am_selling_this'] = False
		if CatalogSeller.objects.filter(catalog=obj, selling_type="Public", selling_company=currentUserCompany).exists():
			jsondata['i_am_selling_this'] = True
		if obj.view_permission == "push":
			jsondata['i_am_selling_this'] = True

		if isPublicCatalog:
			jsondata['total_suppliers'] = catalgsellerObjs.count()
			#jsondata['i_am_selling_this'] = catalgsellerObjs.filter(selling_company=currentUserCompany).exists()
		if supplierObj:
			jsondata['state_name'] = supplierObj.address.state.state_name
			jsondata['city_name'] = supplierObj.address.city.city_name

			serializer = SellerPolicySerializer(instance=supplierObj.sellerpolicy_set.all(), many=True)
			jsondata['seller_policy'] = serializer.data

		return jsondata

	'''def get_suppliers(self, obj):
		global currentUserCompany
		global supplierObj
		global isPublicCatalog
		global catalgsellerObjs

		jsonarr = []
		#csObjs = CatalogSeller.objects.filter(catalog=obj, status="Enable")
		if isPublicCatalog == True:
			for csObj in catalgsellerObjs:
				jsondata = {}
				jsondata['company_id'] = csObj.selling_company.id
				jsondata['name'] = csObj.selling_company.name
				jsondata['chat_user'] = None
				if csObj.selling_company.chat_admin_user:
					jsondata['chat_user'] = csObj.selling_company.chat_admin_user.username
				jsondata['trusted_seller'] = csObj.selling_company.trusted_seller

				jsondata['relation_id'] = None
				buyer_table_id = Buyer.objects.filter(selling_company=csObj.selling_company, buying_company=currentUserCompany, status="approved").values_list('id', flat=True).first()
				if buyer_table_id:
					jsondata['relation_id'] = buyer_table_id

				jsondata['seller_score'] = None
				crObj = CompanyRating.objects.filter(company=csObj.selling_company).first()
				if crObj:
					jsondata['seller_score'] = crObj.seller_score*5

				jsondata['state_name'] = csObj.selling_company.address.state.state_name
				jsondata['city_name'] = csObj.selling_company.address.city.city_name


				jsonarr.append(jsondata)
		return jsonarr'''

	def get_supplier_disabled(self, obj):
		global currentUserCompany
		global pushUserObj
		global isPublicCatalog
		global catalgsellerObjs
		global viewType
		global csFirstObj

		if viewType and viewType.lower()=="myreceived" and pushUserObj:
			return pushUserObj.supplier_disabled
		#~ if pushUserObj:
			#~ return pushUserObj.supplier_disabled
		elif isPublicCatalog:
			#print "catalgsellerObjs", catalgsellerObjs
			try:
				# if catalgsellerObjs.first().status == "Disable":
				if csFirstObj.status == "Disable":
					return True
			except Exception as e:
				return True
		elif obj.company == currentUserCompany:
			return obj.supplier_disabled
		elif pushUserObj:
			return pushUserObj.supplier_disabled

		'''tempPUObj = Push_User.objects.filter(buying_company=currentUserCompany, catalog=obj).first()
		if tempPUObj:
			return tempPUObj.supplier_disabled'''
		return False

	def get_buyer_disabled(self, obj):
		global currentUserCompany
		global pushUserObj
		global viewType
		'''tempPUObj = Push_User.objects.filter(buying_company=currentUserCompany, catalog=obj).first()
		if tempPUObj:
			return tempPUObj.buyer_disabled
		else:
			if obj.supplier_disabled==True and obj.company==currentUserCompany:
				return True
			else:
				return False
		'''
		#if viewType and viewType=="myreceived" and pushUserObj:
		if viewType and "received" in viewType and pushUserObj:
			return pushUserObj.buyer_disabled
		#~ if pushUserObj:
			#~ return pushUserObj.buyer_disabled
		elif CatalogSeller.objects.filter(selling_company=currentUserCompany, status="Disable", catalog=obj).exists():
			return True
		elif obj.supplier_disabled==True and obj.company==currentUserCompany:
			return True
		elif pushUserObj:
			return pushUserObj.buyer_disabled
		else:
			return False



	def get_is_addedto_wishlist(self, obj):
		global user
		if user.is_authenticated():
			wishlist = UserWishlist.objects.filter(user=user, catalog=obj).first()
			if wishlist:
				return wishlist.id

		return None

	def get_enquiry_id(self, obj):
		global user
		global currentUserCompany
		global supplierObj

		ceObj = CatalogEnquiry.objects.filter(selling_company=supplierObj, buying_company=currentUserCompany, catalog=obj).first()
		if ceObj:
			return ceObj.id

		return None

	'''def __init__(self, *args, **kwargs):
		super(GetCatalogSerializer, self).__init__(*args, **kwargs)

		#request = kwargs['context']['request']
		request = self.context
		print request

		if request.method == 'GET':
			self.fields['brand'] = BrandSerializer()'''

	class Meta:
		model = Catalog
		fields = ('id', 'brand', 'title', 'thumbnail', 'view_permission', 'category', 'eavdata', 'products', 'company', 'total_products', 'push_user_id', 'sell_full_catalog', 'is_disable', 'is_viewed', 'exp_desp_date', 'is_product_price_null', 'max_sort_order', 'price_range', 'single_piece_price_range', 'supplier', 'full_catalog_orders_only', 'supplier_name', 'is_supplier_approved', 'supplier_chat_user', 'is_trusted_seller', 'supplier_id', 'supplier_company_rating', 'supplier_details', 'supplier_disabled', 'buyer_disabled', 'category_name', 'is_addedto_wishlist', 'expiry_date', 'created_at', 'enquiry_id', 'single_piece_price', 'single_piece_price_percentage', 'dispatch_date')	#, 'filter_products', 'is_hidden'

class ProductListSerializer(serializers.ListSerializer):

	def to_representation(self, obj):
		global currentUser
		global currentUserCompany

		currentUser = self.context['request'].user

		viewType = self.context['request'].query_params.get('view_type', None)
		price = self.context['request'].query_params.get('price', None)

		try:
			currentUserCompany = currentUser.companyuser.company
			if currentUser.groups.filter(name="salesperson").exists():
				#pushUserProductId = Push_User_Product.objects.filter(selling_company=currentUserCompany).values_list('product', flat=True).distinct()
				pushUserProductId = CompanyProductFlat.objects.filter(selling_company=currentUserCompany).values_list('product', flat=True).distinct()
				sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()

				if price is not None:
					productsIds = CompanyProductFlat.objects.filter((Q(product__in=pushUserProductId) & Q(buying_company=currentUserCompany) & Q(selling_company__in=sellingCompanyObj) & Q(is_disable=False)) & (Q(final_price=price) | Q(selling_price=price))).values_list('product', flat=True).distinct()
					query = obj.filter(Q(catalog__company=currentUserCompany, price=price) | Q(id__in=productsIds)).distinct().order_by('-catalog','sort_order','id')#order_by('-id')
				else:
					productsIds = CompanyProductFlat.objects.filter(product__in=pushUserProductId, buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, is_disable=False).values_list('product', flat=True).distinct()
					query = obj.filter(Q(catalog__company=currentUserCompany) | Q(id__in=productsIds)).distinct().order_by('-catalog','sort_order','id')

			#elif currentUserCompany.company_type.lower() == "manufacturer" or (viewType is not None and viewType.lower()=="myproducts"):
			elif is_manufacturer(currentUserCompany.company_group_flag) or (viewType is not None and viewType.lower()=="myproducts"):
				if price is not None:
					query = obj.filter(catalog__company=currentUserCompany, price=price).distinct().order_by('-catalog','sort_order','id')
				else:
					query = obj.filter(catalog__company=currentUserCompany).distinct().order_by('-catalog','sort_order','id')

			else:
				sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()

				if price is not None:
					productsIds = CompanyProductFlat.objects.filter((Q(buying_company=currentUserCompany) & Q(selling_company__in=sellingCompanyObj) & Q(is_disable=False)) & (Q(final_price=price) | Q(selling_price=price))).values_list('product', flat=True)
					query = obj.filter(Q(catalog__company=currentUserCompany, price=price) | Q(id__in=productsIds)).distinct().order_by('-catalog','sort_order','id')
				else:
					productsIds = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, is_disable=False).values_list('product', flat=True)
					query = obj.filter(Q(catalog__company=currentUserCompany) | Q(id__in=productsIds)).distinct().order_by('-catalog','sort_order','id')

		except ObjectDoesNotExist:
			return obj.none()

		return super(ProductListSerializer, self).to_representation(query)

class ProductSerializer(serializers.ModelSerializer):
	image = VersatileImageFieldSerializer(
		sizes='product_image'
	)
	eav = serializers.CharField(required=False)

	barcode = serializers.SerializerMethodField()

	fabric = serializers.SerializerMethodField()
	work = serializers.SerializerMethodField()

	def get_barcode(self, obj):
		user=self.context['request'].user
		currentUserCompany = user.companyuser.company
		barcodeObj = Barcode.objects.filter(warehouse__company=currentUserCompany, product=obj).first()
		if barcodeObj:
			return barcodeObj.barcode
		else:
			return None

	def create(self, validated_data):
		#eav_insert = validated_data.pop('eav', None)
		if validated_data.get('sort_order', None) is None:
			max_order = Product.objects.filter(catalog=validated_data.get('catalog')).aggregate(Max('sort_order')).get('sort_order__max', 0)
			if max_order is None:
				max_order = 0
			validated_data['sort_order'] = max_order+1

		product = Product.objects.create(**validated_data)

		#eav.register(Product)
		'''######V1
		if settings.DEBUG == True:
			if product.fabric is not None and EnumGroup.objects.filter(Q(name='fabric') | Q(name='fabric_text')).exists():
				if not EnumGroup.objects.filter(name='fabric', enums__value=product.fabric).exists():
					if not EnumValue.objects.filter(value=product.fabric).exists():
						EnumValue.objects.create(value=product.fabric)
					enumGroupObj = EnumGroup.objects.get(name='fabric')
					enumValueObj = EnumValue.objects.get(value=product.fabric)
					enumGroupObj.enums.add(enumValueObj)

				product.eav.fabric = EnumValue.objects.get(value=product.fabric)
				product.eav.fabric_text = product.fabric

			if product.work is not None and EnumGroup.objects.filter(Q(name='work') | Q(name='work_text')).exists():
				if not EnumGroup.objects.filter(name='work', enums__value=product.work).exists():
					if not EnumValue.objects.filter(value=product.work).exists():
						EnumValue.objects.create(value=product.work)
					enumGroupObj = EnumGroup.objects.get(name='work')
					enumValueObj = EnumValue.objects.get(value=product.work)
					enumGroupObj.enums.add(enumValueObj)

				product.eav.work = EnumValue.objects.get(value=product.work)
				product.eav.work_text = product.work
			product.save()
		else:'''

		'''
		#last version but need to move catalog eav
		##Full EAV multiple save is done
		from eav.models import Attribute, Value as EavValue
		from django.contrib.contenttypes.models import ContentType

		ct = ContentType.objects.get(id=26)

		if product.fabric:
			fabrics = list(product.fabric.strip().replace(', ',',').split(','))
			#print fabrics

			attribute = Attribute.objects.get(name="fabric")
			for fabric in fabrics:
				#print fabric
				if fabric.strip() == "":
					continue
				ev = EnumValue.objects.filter(value=fabric.strip()).first()
				#print ev
				if ev:
					EavValue.objects.create(entity_ct=ct, entity_id=product.id, value_enum=ev, attribute=attribute)
				else:
					if product.eav.fabric_text:
						product.eav.fabric_text += ", "+fabric.strip()
					else:
						product.eav.fabric_text = fabric.strip()
			if 'Other' in fabrics:
				fabrics.remove('Other')
			product.fabric = ','.join(fabrics)

		if product.work:
			works = list(product.work.strip().replace(', ',',').split(','))
			#print works

			attribute = Attribute.objects.get(name="work")
			for work in works:
				#print work
				if work.strip() == "":
					continue
				ev = EnumValue.objects.filter(value=work.strip()).first()
				#print ev
				if ev:
					EavValue.objects.create(entity_ct=ct, entity_id=product.id, value_enum=ev, attribute=attribute)
				else:
					if product.eav.work_text:
						product.eav.work_text += ", "+work.strip()
					else:
						product.eav.work_text = work.strip()
			if 'Other' in works:
				works.remove('Other')
			product.work = ','.join(works)

		product.save()
		productEAVset(product)
		'''

		'''
		######V2
		##Full EAV multiple save is done
		from eav.models import Attribute, Value as EavValue
		from django.contrib.contenttypes.models import ContentType

		fabrics = list(product.fabric.split(','))
		works = list(product.work.split(','))

		ct = ContentType.objects.get(id=26)
		attribute = Attribute.objects.get(name="fabric")
		for fabric in fabrics:
			EavValue.objects.create(entity_ct=ct, entity_id=product.id, value_enum=EnumValue.objects.get(id=fabric), attribute=attribute)
			#product.eav.fabric = EnumValue.objects.get(id=fabric)
			#product.save()
		attribute = Attribute.objects.get(name="work")
		for work in works:
			EavValue.objects.create(entity_ct=ct, entity_id=product.id, value_enum=EnumValue.objects.get(id=work), attribute=attribute)
			#product.eav.work = EnumValue.objects.get(id=work)
			#product.save()
		'''


		'''
		#last version but need to move catalog eav
		if eav_insert is not None and eav_insert != "":

			eav_insert = ast.literal_eval(eav_insert)

			for data in eav_insert:
				logger.info("product create eav array key = %s ,value = %s"% (data[0], data[1]))
				if "," in data[1]:
					dataarr = list(data[1].strip().replace(', ',',').split(','))
					for subdata in dataarr:
						enumValue = EnumValue.objects.filter(value=subdata).first()
						if enumValue:
							setattr( product.eav, data[0], enumValue)
							product.save()
				else:
					enumValue = EnumValue.objects.filter(value=data[1]).first()
					if enumValue:
						setattr( product.eav, data[0], enumValue)
						product.save()
					else:
						#set text value
						setattr( product.eav, data[0], data[1])'''
		return product

	def update(self, instance, validated_data):
		#eav_insert = validated_data.pop('eav', None)

		instance.sku = validated_data.get('sku', instance.sku)
		instance.title = validated_data.get('title', instance.title)
		instance.fabric = validated_data.get('fabric', instance.fabric)
		instance.price = validated_data.get('price', instance.price)
		instance.public_price = validated_data.get('public_price', instance.public_price)
		instance.work = validated_data.get('work', instance.work)
		instance.image = validated_data.get('image', instance.image)

		instance.catalog = validated_data.get('catalog', instance.catalog)
		instance.save()

		#eav.register(Product)

		'''######V2
		if settings.DEBUG == True:
			if instance.fabric is not None and EnumGroup.objects.filter(Q(name='fabric') | Q(name='fabric_text')).exists():
				if not EnumGroup.objects.filter(name='fabric', enums__value=instance.fabric).exists():
					if not EnumValue.objects.filter(value=instance.fabric).exists():
						EnumValue.objects.create(value=instance.fabric)
					enumGroupObj = EnumGroup.objects.get(name='fabric')
					enumValueObj = EnumValue.objects.get(value=instance.fabric)
					enumGroupObj.enums.add(enumValueObj)

				instance.eav.fabric = EnumValue.objects.get(value=instance.fabric)
				instance.eav.fabric_text = instance.fabric

			if instance.work is not None and EnumGroup.objects.filter(Q(name='work') | Q(name='work_text')).exists():
				if not EnumGroup.objects.filter(name='work', enums__value=instance.work).exists():
					if not EnumValue.objects.filter(value=instance.work).exists():
						EnumValue.objects.create(value=instance.work)
					enumGroupObj = EnumGroup.objects.get(name='work')
					enumValueObj = EnumValue.objects.get(value=instance.work)
					enumGroupObj.enums.add(enumValueObj)

				instance.eav.work = EnumValue.objects.get(value=instance.work)
				instance.eav.work_text = instance.work
		else:'''

		'''
		#last version but need to move catalog eav
		##Full EAV multiple save is done
		from eav.models import Attribute, Value as EavValue
		from django.contrib.contenttypes.models import ContentType

		ct = ContentType.objects.get(id=26)

		if instance.fabric:
			fabrics = list(instance.fabric.strip().replace(', ',',').split(','))
			#print fabrics

			attribute = Attribute.objects.get(name="fabric")
			instance.eav.fabric_text = None

			final_ev = []
			eavvalues = EavValue.objects.filter(entity_ct=ct, entity_id=instance.id, attribute=attribute)
			for fabric in fabrics:
				#print fabric
				if fabric.strip() == "":
					continue
				ev = EnumValue.objects.filter(value=fabric.strip()).first()
				#print ev
				if ev:
					if not eavvalues.filter(value_enum=ev).exists():
						EavValue.objects.create(entity_ct=ct, entity_id=instance.id, value_enum=ev, attribute=attribute)
					final_ev.append(ev)
				else:
					if instance.eav.fabric_text:
						instance.eav.fabric_text += ", "+fabric.strip()
					else:
						instance.eav.fabric_text = fabric.strip()
			EavValue.objects.filter(entity_ct=ct, entity_id=instance.id, attribute=attribute).exclude(value_enum__in=final_ev).delete()
			if 'Other' in fabrics:
				fabrics.remove('Other')
			instance.fabric = ','.join(fabrics)

		if instance.work:
			works = list(instance.work.strip().replace(', ',',').split(','))
			#print works

			attribute = Attribute.objects.get(name="work")
			instance.eav.work_text = None

			final_ev = []
			eavvalues = EavValue.objects.filter(entity_ct=ct, entity_id=instance.id, attribute=attribute)
			for work in works:
				#print work
				if work.strip() == "":
					continue
				ev = EnumValue.objects.filter(value=work.strip()).first()
				#print ev
				if ev:
					if not eavvalues.filter(value_enum=ev).exists():
						EavValue.objects.create(entity_ct=ct, entity_id=instance.id, value_enum=ev, attribute=attribute)
					final_ev.append(ev)
				else:
					if instance.eav.work_text:
						instance.eav.work_text += ", "+work.strip()
					else:
						instance.eav.work_text = work.strip()
			EavValue.objects.filter(entity_ct=ct, entity_id=instance.id, attribute=attribute).exclude(value_enum__in=final_ev).delete()
			if 'Other' in works:
				works.remove('Other')
			instance.work = ','.join(works)

		instance.save()
		productEAVset(instance)

		if eav_insert is not None and eav_insert != "":
			eav_insert = ast.literal_eval(eav_insert)

			for data in eav_insert:
				logger.info("product update eav array key = %s ,value = %s"% (data[0], data[1]))
				attribute = Attribute.objects.get(name=data[0])
				final_ev = []
				eavvalues = EavValue.objects.filter(entity_ct=ct, entity_id=instance.id, attribute=attribute)

				if "," in data[1]:
					dataarr = list(data[1].strip().replace(', ',',').split(','))
					for subdata in dataarr:
						enumValue = EnumValue.objects.filter(value=subdata).first()
						if enumValue:
							setattr( instance.eav, data[0], enumValue)
							instance.save()
							final_ev.append(enumValue)
				else:
					enumValue = EnumValue.objects.filter(value=data[1]).first()
					if enumValue:
						setattr( instance.eav, data[0], enumValue)
						instance.save()
						final_ev.append(enumValue)
					else:
						#set text value
						setattr( instance.eav, data[0], data[1])
				eavvalues.exclude(value_enum__in=final_ev).delete()'''

		return instance

	def get_fabric(self, obj):
		return getCatalogEAV(obj.catalog, "fabricInString")

	def get_work(self, obj):
		return getCatalogEAV(obj.catalog, "workInString")

	def validate(self, data):
		user=self.context['request'].user
		company = user.companyuser.company
		companyCatalog = Catalog.objects.filter(company=company).order_by('id').values_list('id', flat=True).distinct()

		if data.get('catalog', None) != None:
			catalogObj = data['catalog']
			if catalogObj.id not in companyCatalog and not user.is_staff:
				raise serializers.ValidationError({"catalog":"Select valid catalog"})

			# if data.get('sku', None) != None and data.get('sku', None) != "":
			# 	if self.instance is None:
			# 		# if Product.objects.filter(sku=data['sku'], catalog__brand=catalogObj.brand, catalog__company=company).exclude(deleted=True).exists():
			# 		# 	raise serializers.ValidationError({"sku":"sku should be unique"})
			#  	# else:
			# 		# if Product.objects.filter(sku=data['sku'], catalog__brand=catalogObj.brand, catalog__company=company).exclude(Q(deleted=True) | Q(id=self.instance.id)).exists():
			# 		# 	raise serializers.ValidationError({"sku":"sku should be unique"})
			# 		if Product.objects.filter(sku=data['sku'], catalog = catalogObj).exclude(deleted=True).exists():
			# 			raise serializers.ValidationError({"sku":"sku should be unique across the catalog"})

			if catalogObj.view_permission == "public":
				public_price = data.get('public_price', None)
				if public_price is None or public_price <= 100:
					raise serializers.ValidationError({"public_price":"public price must be more than 100"})


		'''if data.get('eav', None) != None:
			eav_insert = data.get('eav', None)
			eav_insert = ast.literal_eval(eav_insert)

			catalogObj = data['catalog']

			requireAttribute = CategoryEavAttribute.objects.filter(category=catalogObj.category, is_required=True).values_list('attribute__name', flat=True).distinct()

			eavKey = []
			for eavdata in eav_insert:
				eavKey.append(eavdata[0])

			for eavdata in requireAttribute:
				if not eavdata in eavKey:
					raise serializers.ValidationError({"eav":"Enter this EAV key : "+eavdata})'''

		price = data.get('price', None)
		if price is None or price <= 100:
			raise serializers.ValidationError({"price":"price must be more than 100"})

		return data

	class Meta:
		model = Product
		list_serializer_class = ProductListSerializer
		fields = ('id', 'sku', 'title', 'fabric', 'price', 'work', 'catalog', 'image', 'eav', 'barcode', 'public_price', 'sort_order')

class SelectionPOSProductSerializer(serializers.ModelSerializer):
	image = VersatileImageFieldSerializer(
		sizes=[('thumbnail_small', 'thumbnail__150x210')]#'product_image'
	)
	class Meta:
		model = Product
		fields = ('id', 'sku', 'title', 'price', 'image')



class GetProductSerializer(serializers.ModelSerializer):

	image = VersatileImageFieldSerializer(
		sizes='product_image'
	)

	final_price = serializers.SerializerMethodField('get_finalprice') ##my purchase price
	selling_price = serializers.SerializerMethodField('get_sellprice') ## my sell price
	push_user_product_id = serializers.SerializerMethodField('get_pushuserproduct')
	product_like_id = serializers.SerializerMethodField('get_productlike')
	delete_allowed = serializers.SerializerMethodField('get_deleteallowed')
	is_disable = serializers.SerializerMethodField('get_disable')

	#eav = serializers.SerializerMethodField('get_eavdata')

	catalog = GetNestedCatalogSerializer()#serializers.SerializerMethodField('get_catlg')
	barcode = serializers.SerializerMethodField()

	fabric = serializers.SerializerMethodField()
	work = serializers.SerializerMethodField()

	def get_barcode(self, obj):
		global currentUserCompany
		barcodeObj = Barcode.objects.filter(warehouse__company=currentUserCompany, product=obj).first()
		if barcodeObj:
			return barcodeObj.barcode
		else:
			return None

	def get_catlg(self, obj):
		serializer = GetNestedCatalogSerializer(instance=obj.catalog, context={'request': self.context['request']})
		return [serializer.data]

	#~ def get_eavdata(self, obj):
		#~ return getEAVFabricWork(obj, "all")

	def get_finalprice(self, obj):
		global currentUser
		global currentUserCompany
		global catalogCompany
		global cpfObj
		currentUser = self.context['request'].user
		currentUserCompany = currentUser.companyuser.company
		catalogCompany = obj.catalog.company

		finalPrice = None

		if catalogCompany==currentUserCompany:
			finalPrice = obj.price
		else:
			sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()
			cpfObj = CompanyProductFlat.objects.filter(product=obj, buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, is_disable=False).select_related('selling_company', 'push_reference').last()
			if cpfObj:
				finalPrice = cpfObj.final_price

		return finalPrice


	def get_sellprice(self, obj):
		global currentUser
		global currentUserCompany
		global catalogCompany
		global cpfObj

		sellPrice = None
		if catalogCompany==currentUserCompany:
			sellPrice = obj.price
		else:
			if cpfObj:
				sellPrice = cpfObj.selling_price

		return sellPrice


	def get_pushuserproduct(self, obj):
		global currentUser
		global currentUserCompany
		global catalogCompany

		global cpfObj
		pushUserId = None
		if catalogCompany==currentUserCompany:
			pushUserId = None
		else:
			if cpfObj:
				#pushUserId = Push_User_Product.objects.filter(product=obj, buying_company=currentUserCompany, selling_company=cpfObj.selling_company, push=cpfObj.push_reference, user=currentUser).values_list('id', flat=True).last()
				pushUserId = cpfObj.id

		return pushUserId

	def get_productlike(self, obj):
		global currentUser
		productLike = ProductLike.objects.filter(user=currentUser, product=obj.id).values_list('id', flat=True).last()

		return productLike

	def get_deleteallowed(self, obj):
		delete_allowed = True

		# ~ if CompanyProductFlat.objects.filter(product = obj.id).exists():
			# ~ delete_allowed = False
		return delete_allowed

	def get_disable(self, obj):
		global currentUserCompany
		status = ProductStatus.objects.filter(company=currentUserCompany, product=obj.id, status="Disable").exists()

		return status

	def get_fabric(self, obj):
		#return getEAVFabricWork(obj, "fabric")
		return getCatalogEAV(obj.catalog, "fabricInString")

	def get_work(self, obj):
		#return getEAVFabricWork(obj, "work")
		return getCatalogEAV(obj.catalog, "workInString")


	class Meta:
		model = Product
		list_serializer_class = ProductListSerializer
		fields = ('id', 'sku', 'title', 'fabric', 'work', 'catalog', 'image', 'final_price', 'selling_price', 'price', 'push_user_product_id', 'product_likes', 'product_like_id', 'delete_allowed', 'is_disable', 'barcode')#'eav',

class GetBuyerDetailSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
	selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)
	buying_company_chat_user = serializers.ReadOnlyField(source='buying_company.chat_admin_user.username', read_only=True)
	buying_company_phone_number = serializers.ReadOnlyField(source='buying_company.phone_number', read_only=True)
	invitee_name = serializers.ReadOnlyField(source='invitee.invitee_name', read_only=True)
	invitee_phone_number = serializers.ReadOnlyField(source='invitee.invitee_number', read_only=True)
	group_type_name = serializers.ReadOnlyField(source='group_type.name', read_only=True)

	discount = serializers.SerializerMethodField()
	cash_discount = serializers.SerializerMethodField()

	def get_discount(self, obj):
		return obj.final_discount()
		'''global cbg
		cbg = None
		if obj.discount is None:
			if obj.selling_company is not None and obj.group_type is not None:
				buyer_type = companyBuyerGroupType(obj.group_type.name)
				cbg = CompanyBuyerGroup.objects.filter(company=obj.selling_company, buyer_type=buyer_type).first()
				if cbg:
					return cbg.discount
		return obj.discount'''

	def get_cash_discount(self, obj):
		return obj.final_cash_discount()
		'''global cbg
		if obj.cash_discount is None:
			if cbg:
				return cbg.cash_discount
		return obj.cash_discount'''

	class Meta:
		model = Buyer

class BuyerSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
	selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)#add user on create
	#buying_company_name = serializers.ReadOnlyField(source='buying_company.name', read_only=True)
	buying_company_chat_user = serializers.ReadOnlyField(source='buying_company.chat_admin_user.username', read_only=True)
	buying_company_phone_number = serializers.ReadOnlyField(source='buying_company.phone_number', read_only=True)
	invitee_name = serializers.ReadOnlyField(source='invitee.invitee_name', read_only=True)
	invitee_phone_number = serializers.ReadOnlyField(source='invitee.invitee_number', read_only=True)
	group_type_name = serializers.ReadOnlyField(source='group_type.name', read_only=True)

	def get_name(self, obj):
		name = None
		if obj.buying_company is not None:
			name = obj.buying_company.name
		else:
			name = obj.invitee.invitee_name

		return name

	def update(self, instance, validated_data):
		newStatus = validated_data.get('status', None)
		oldStatus = instance.status
		buyerType = instance.buyer_type

		instance.status = validated_data.get('status', instance.status)
		instance.fix_amount = validated_data.get('fix_amount', instance.fix_amount)
		instance.percentage_amount = validated_data.get('percentage_amount', instance.percentage_amount)

		instance.group_type = validated_data.get('group_type', instance.group_type)

		instance.payment_duration = validated_data.get('payment_duration', instance.payment_duration)
		instance.discount = validated_data.get('discount', instance.discount)
		instance.cash_discount = validated_data.get('cash_discount', instance.cash_discount)
		instance.credit_limit = validated_data.get('credit_limit', instance.credit_limit)

		instance.broker_company = validated_data.get('broker_company', instance.broker_company)
		instance.brokerage_fees = validated_data.get('brokerage_fees', instance.brokerage_fees)
		instance.details = validated_data.get('details', instance.details)

		instance.buying_company_name = validated_data.get('buying_company_name', instance.buying_company_name)
		instance.buying_person_name = validated_data.get('buying_person_name', instance.buying_person_name)
		instance.supplier_person_name = validated_data.get('supplier_person_name', instance.supplier_person_name)

		user=self.context['request'].user
		senderCompany = user.companyuser.company
		receiverCompany = None
		requestType = None
		if instance.selling_company == senderCompany:
			receiverCompany = instance.buying_company
			if buyerType == "Relationship":
				requestType = "buyer"
			else:
				requestType = "buyer_enquiry"
		elif instance.buying_company == senderCompany:
			receiverCompany = instance.selling_company
			if buyerType == "Relationship":
				requestType = "supplier"
			else:
				requestType = "supplier_enquiry"

		if instance.status.lower() == "rejected":
			if instance.selling_company == senderCompany:
				if instance.buyer_approval != False:
					instance.supplier_approval = False
			elif instance.buying_company == senderCompany:
				if instance.supplier_approval != False:
					instance.buyer_approval = False

		instance.save()

		if newStatus is not None and oldStatus != newStatus and newStatus.lower() == "approved":
			print "pushOnApproves"
			shareOnApproves(instance.selling_company, instance.buying_company)
		print "before if newStatus"
		print newStatus
		if newStatus is not None and oldStatus != newStatus and newStatus.lower() in ["approved", "rejected", "pending references", "transferred", "references filled"]:
			print "after if newStatus"
			if receiverCompany:
				print "if receivercompany"
				user1 = CompanyUser.objects.filter(company=receiverCompany).values_list('user', flat=True)
				user1 = User.objects.filter(id__in=user1, groups__name="administrator")
				company_image = None
				if senderCompany.thumbnail:
					company_image = senderCompany.thumbnail.url
				elif Brand.objects.filter(company=senderCompany).exists():
					brandObj = Brand.objects.filter(company=senderCompany).only('image').first()
					if brandObj:
						company_image = brandObj.image.thumbnail[settings.MEDIUM_IMAGE].url
				username = CompanyUser.objects.filter(company=senderCompany).values_list('user__username', flat=True).first()
				jsonarr = {}
				jsonarr['company_name'] = senderCompany.name
				jsonarr['table_id'] = instance.id
				jsonarr['notId'] = instance.id
				jsonarr['push_type'] = requestType
				jsonarr['company_id'] = senderCompany.id
				if requestType=="buyer" or requestType=="buyer_enquiry":
					title = "Supplier Request"
				else:
					title = "Buyer Request"
				jsonarr['title'] = title
				jsonarr['company_image'] = company_image
				jsonarr['username'] = username
				jsonarr['status'] = newStatus
				jsonarr['buyer_type'] = buyerType

				sendAllTypesMessage("buyersupplier_status", user1, jsonarr)


		return instance

	def validate(self, data):
		status = data.get('status', None)
		group_type = data.get('group_type', None)
		if status is not None and status.lower() == "approved" and self.instance is not None:
			user=self.context['request'].user
			company = user.companyuser.company
			if self.instance.selling_company == company:
				if self.instance.buyer_approval == False:
					raise serializers.ValidationError({'buying_company': 'Buyer has already responded'})
			elif self.instance.buying_company == company:
				if self.instance.supplier_approval == False:
					raise serializers.ValidationError({'selling_company': 'Supplier has already responded'})

			if self.instance.group_type is None and group_type is None:
				raise serializers.ValidationError({'group_type': 'Select Group Type'})

		return data

	class Meta:
		model = Buyer

class GroupTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = GroupType

class CountrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Country

class BSInviteeSerializer(serializers.ModelSerializer):
	country = CountrySerializer()
	class Meta:
		model = Invitee
		#depth = 1

class GetBuyerSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
	buying_company = GetCompanySerializer()
	invitee = BSInviteeSerializer()
	group_type = GroupTypeSerializer()

	discount = serializers.SerializerMethodField()
	cash_discount = serializers.SerializerMethodField()
	credit_reference = serializers.SerializerMethodField()

	details = serializers.SerializerMethodField()

	def get_discount(self, obj):
		return obj.final_discount()

	def get_cash_discount(self, obj):
		return obj.final_cash_discount()

	def get_credit_reference(self, obj):
		crObj = CreditReference.objects.filter(selling_company=obj.selling_company, buying_company=obj.buying_company).first()
		jsondata = {}
		jsondata["id"] = None
		if crObj:
			jsondata["id"] = crObj.id
		return jsondata

	def get_details(self, obj):
		if obj.details is None:
			return ""
		return obj.details

	class Meta:
		model = Buyer
		fields = ('id', 'buying_company', 'broker_company', 'brokerage_fees', 'status', 'fix_amount', 'percentage_amount', 'invitee', 'group_type', 'payment_duration', 'discount', 'cash_discount', 'credit_limit', 'buyer_type', 'details', 'buying_company_name', 'buying_person_name', 'supplier_person_name', 'created_at', 'credit_reference')

class CatalogListSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def validate(self, data):
		user=self.context['request'].user
		company = user.companyuser.company

		if data.get('name', None) != None:
			if self.instance is None:
				if CatalogList.objects.filter(name=data['name'], user=user).exists():
					raise serializers.ValidationError({'name': 'This catalog list already exists'})
			else:
				if CatalogList.objects.filter(name=data['name'], user=user).exclude(id=self.instance.id).exists():
					raise serializers.ValidationError({'name': 'This catalog list already exists'})

		if data.get('catalogs', None) != None:
			for catalog in data['catalogs']:
				if Catalog.objects.filter(id=catalog.id,company=company).exists() == False:
					if user.groups.filter(name="salesperson").exists():
						if Push_User.objects.filter(selling_company=company,catalog=catalog).exists() == False:
							raise serializers.ValidationError({'catalogs': 'Select valid catalog'})
					else:
						if Push_User.objects.filter(buying_company=company,catalog=catalog).exists() == False:
							raise serializers.ValidationError({'catalogs': 'Select valid catalog'})

		return data

	class Meta:
		model = CatalogList

class GetCatalogListSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	catalogs = GetCatalogSerializer(many=True)
	class Meta:
		model = CatalogList

class SupplierSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
	buying_company = serializers.ReadOnlyField(source='buying_company.name', read_only=True)#add user on create
	selling_company_name = serializers.ReadOnlyField(source='selling_company.name', read_only=True)
	selling_company_chat_user = serializers.ReadOnlyField(source='selling_company.chat_admin_user.username', read_only=True)
	selling_company_phone_number = serializers.ReadOnlyField(source='selling_company.phone_number', read_only=True)
	invitee_name = serializers.ReadOnlyField(source='invitee.invitee_name', read_only=True)
	invitee_phone_number = serializers.ReadOnlyField(source='invitee.invitee_number', read_only=True)
	group_type_name = serializers.ReadOnlyField(source='group_type.name', read_only=True)

	discount = serializers.SerializerMethodField()
	cash_discount = serializers.SerializerMethodField()

	def get_discount(self, obj):
		return obj.final_discount()
		'''global cbg
		cbg = None
		if obj.discount is None:
			if obj.selling_company is not None and obj.group_type is not None:
				buyer_type = companyBuyerGroupType(obj.group_type.name)
				cbg = CompanyBuyerGroup.objects.filter(company=obj.selling_company, buyer_type=buyer_type).first()
				if cbg:
					return cbg.discount
		return obj.discount'''

	def get_cash_discount(self, obj):
		return obj.final_cash_discount()
		'''global cbg
		if obj.cash_discount is None:
			if cbg:
				return cbg.cash_discount
		return obj.cash_discount'''

	def update(self, instance, validated_data):
		newStatus = validated_data.get('status', None)
		oldStatus = instance.status
		buyerType = instance.buyer_type

		instance.status = validated_data.get('status', instance.status)
		instance.fix_amount = validated_data.get('fix_amount', instance.fix_amount)
		instance.percentage_amount = validated_data.get('percentage_amount', instance.percentage_amount)

		instance.group_type = validated_data.get('group_type', instance.group_type)

		instance.broker_company = validated_data.get('broker_company', instance.broker_company)
		instance.brokerage_fees = validated_data.get('brokerage_fees', instance.brokerage_fees)

		instance.warehouse = validated_data.get('warehouse', instance.warehouse)
		instance.is_visible = validated_data.get('is_visible', instance.is_visible)

		instance.details = validated_data.get('details', instance.details)

		user=self.context['request'].user
		senderCompany = user.companyuser.company
		receiverCompany = None
		requestType = None
		if instance.selling_company == senderCompany:
			receiverCompany = instance.buying_company
			if buyerType == "Relationship":
				requestType = "buyer"
			else:
				requestType = "buyer_enquiry"
		elif instance.buying_company == senderCompany:
			receiverCompany = instance.selling_company
			if buyerType == "Relationship":
				requestType = "supplier"
			else:
				requestType = "supplier_enquiry"

		if instance.status.lower() == "rejected":
			if instance.selling_company == senderCompany:
				if instance.buyer_approval != False:
					instance.supplier_approval = False
			elif instance.buying_company == senderCompany:
				if instance.supplier_approval != False:
					instance.buyer_approval = False

		instance.save()

		if newStatus is not None and oldStatus != newStatus and newStatus.lower() == "approved":
			print "shareOnApproves"
			shareOnApproves(instance.selling_company, instance.buying_company)

		print "before if newStatus"
		print newStatus
		if newStatus is not None and oldStatus != newStatus and newStatus.lower() in ["approved", "rejected", "pending references", "transferred", "references filled"]:
			print "after if newStatus"
			if receiverCompany:
				print "if receivercompany"
				user1 = CompanyUser.objects.filter(company=receiverCompany).values_list('user', flat=True)
				user1 = User.objects.filter(id__in=user1, groups__name="administrator")
				company_image = None
				if senderCompany.thumbnail:
					company_image = senderCompany.thumbnail.url
				elif Brand.objects.filter(company=senderCompany).exists():
					brandObj = Brand.objects.filter(company=senderCompany).only('image').first()
					if brandObj:
						company_image = brandObj.image.thumbnail[settings.MEDIUM_IMAGE].url
				username = CompanyUser.objects.filter(company=senderCompany).values_list('user__username', flat=True).first()
				jsonarr = {}
				jsonarr['company_name'] = senderCompany.name
				jsonarr['table_id'] = instance.id
				jsonarr['notId'] = instance.id
				jsonarr['push_type'] = requestType
				jsonarr['company_id'] = senderCompany.id
				if requestType=="buyer" or requestType=="buyer_enquiry":
					title = "Supplier Request"
				else:
					title = "Buyer Request"
				jsonarr['title'] = title
				jsonarr['company_image'] = company_image
				jsonarr['username'] = username
				jsonarr['status'] = newStatus
				jsonarr['buyer_type'] = buyerType

				sendAllTypesMessage("buyersupplier_status", user1, jsonarr)

		return instance

	def validate(self, data):
		status = data.get('status', None)
		if status is not None and status.lower() == "approved" and self.instance is not None:
			user=self.context['request'].user
			company = user.companyuser.company
			if self.instance.selling_company == company:
				if self.instance.buyer_approval == False:
					raise serializers.ValidationError({'buying_company': 'Buyer has already responded'})
			elif self.instance.buying_company == company:
				if self.instance.supplier_approval == False:
					raise serializers.ValidationError({'selling_company': 'Supplier has already responded'})
		return data

	class Meta:
		model = Buyer

class GetCompanyForSupplierSerializer(serializers.ModelSerializer):
	branches = GetBranchSerializer(many=True, read_only=True)
	#buying_order = BuyerSalesOrderSerializer(many=True, read_only=True)##My Sales
	selling_order = SellerSalesOrderSerializer(many=True, read_only=True)##My buy
	#meeting_buying_company = MeetingSerializer(many=True, read_only=True)

	chat_user = serializers.CharField(source='chat_admin_user.username', read_only=True)

	users = serializers.SerializerMethodField('get_usr')
	address = GetAddressSerializer()

	seller_policy = SellerPolicySerializer(many=True, read_only=True, source="sellerpolicy_set")

	def get_usr(self, obj):
		return list(CompanyUser.objects.filter(company=obj.id).values_list('user__username', flat=True))

	thumbnail = serializers.SerializerMethodField('get_image')
	def get_image(self, obj):
		image = None
		if obj.thumbnail:
			image = obj.thumbnail.url
		else:
			if Brand.objects.filter(company=obj.id).exists():
				brand = Brand.objects.filter(company=obj.id).first()
				image = brand.image.thumbnail[settings.SMALL_SQR_IMAGE].url
		return image
	class Meta:
		model = Company
		fields = ('id', 'chat_user', 'name', 'push_downstream', 'street_address', 'pincode', 'phone_number', 'email', 'website', 'note',
		'status', 'company_type', 'thumbnail',
		'city', 'state', 'country', 'branches', 'selling_order', 'users', 'address', 'seller_policy')


class GetSupplierSerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
	selling_company = GetCompanyForSupplierSerializer()
	invitee = BSInviteeSerializer()
	group_type = GroupTypeSerializer()

	credit_reference = serializers.SerializerMethodField()
	def get_credit_reference(self, obj):
		crObj = CreditReference.objects.filter(selling_company=obj.selling_company, buying_company=obj.buying_company).first()
		jsondata = {}
		jsondata["id"] = None
		if crObj:
			jsondata["id"] = crObj.id
		return jsondata

	class Meta:
		model = Buyer
		fields = ('id', 'selling_company', 'broker_company', 'brokerage_fees', 'status', 'fix_amount', 'percentage_amount', 'invitee', 'group_type', 'warehouse', 'is_visible', 'supplier_person_name', 'credit_reference')

class MeetingListSerializer(serializers.ListSerializer):
	def to_representation(self, obj):
		query = obj

		user = self.context['request'].user

		try:
			if user.is_authenticated() and user.companyuser.company is not None:
				if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					query = obj.filter(Q(user__companyuser__company=company) | Q(user__companyuser__deputed_to=company)).distinct().order_by('-id')
				else:
					query = obj.filter(user=user).distinct().order_by('-id')
		except ObjectDoesNotExist:
			return obj.none()

		return super(MeetingListSerializer, self).to_representation(query)

class MeetingSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	duration = serializers.CharField(read_only=True)
	buying_company_name = serializers.CharField(source='buying_company_ref.name', read_only=True)

	salesorder = serializers.SerializerMethodField()

	def get_salesorder(self, obj):
		if obj.end_datetime is not None and obj.buying_company_ref is not None:
			salesorders = SalesOrder.objects.filter(created_at__lte=obj.end_datetime+timedelta(minutes=5), created_at__gte=obj.start_datetime-timedelta(minutes=5), user=obj.user, company=obj.buying_company_ref).values_list('id', flat=True)
			salesorders = list(salesorders)
			return salesorders
		else:
			return []

	buyer_table_id = serializers.SerializerMethodField()

	def get_buyer_table_id(self, obj):
		user=self.context['request'].user
		selling_company = None
		if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
			selling_company = user.companyuser.deputed_to
		else:
			selling_company=obj.company
		if selling_company and obj.buying_company_ref:
			buyerObj = Buyer.objects.filter(selling_company=obj.company, buying_company=obj.buying_company_ref, status="approved").values_list('id', flat=True).first()
			if buyerObj:
				return buyerObj
			else:
				return None
		else:
			return None

	class Meta:
		model = Meeting
		#~ list_serializer_class = MeetingListSerializer
		readonly_fields = ("duration",)
		fields = ('id', 'user', 'duration', 'buying_company_name', 'start_datetime', 'end_datetime', 'start_lat', 'start_long', 'end_lat', 'end_long', 'status', 'buying_company_ref', 'salesorder', 'total_products', 'note', 'purpose', 'company', 'buyer_table_id', 'buyer_name_text')

'''class SalesOrderItemSerializer(serializers.ModelSerializer):
	product_title = serializers.CharField(source='product.title', read_only=True)
	product_sku = serializers.CharField(source='product.sku', read_only=True)
	product_image = serializers.CharField(source='product.image.thumbnail.150x210', read_only=True)
	class Meta:
		model = SalesOrderItem'''

class GetSalesOrderSerializer(serializers.ModelSerializer):
	company_name = serializers.CharField(source='company.name', read_only=True)
	company_address = serializers.CharField(source='company.street_address', read_only=True)
	company_state_city = serializers.SerializerMethodField()
	company_number = serializers.SerializerMethodField()
	seller_company_name = serializers.CharField(source='seller_company.name', read_only=True)
	seller_company_address = serializers.CharField(source='seller_company.street_address', read_only=True)
	seller_company_state_city = serializers.SerializerMethodField()
	seller_company_number = serializers.SerializerMethodField()
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	broker_company_name = serializers.CharField(source='broker_company.name', read_only=True)
	ship_to = GetAddressSerializer(required=False)
	buyer_table_id = serializers.SerializerMethodField()
	images = serializers.SerializerMethodField()
	brokerage = serializers.SerializerMethodField()
	buyer_credit_rating = serializers.SerializerMethodField()

	def get_buyer_table_id(self, obj):
		try:
			user=self.context['request'].user
			selling_company = None
			company = user.companyuser.company
			if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
				selling_company = user.companyuser.deputed_to
			elif obj.broker_company == company:
				selling_company = company
			else:
				selling_company=obj.seller_company
			if selling_company and obj.company:
				buyerObj = Buyer.objects.filter(selling_company=selling_company, buying_company=obj.company, status="approved").values_list('id', flat=True).first()
				if buyerObj:
					return buyerObj
				else:
					return None
			else:
				return None
		except Exception:
			return None

	def get_company_state_city(self, obj):
		cityname = "-"
		statename = "-"
		if obj.company.city:
			cityname = obj.company.city.city_name
		if obj.company.state:
			statename = obj.company.state.state_name

		return cityname+", "+statename

	def get_seller_company_state_city(self, obj):
		cityname = "-"
		statename = "-"
		if obj.seller_company.city:
			cityname = obj.seller_company.city.city_name
		if obj.seller_company.state:
			statename = obj.seller_company.state.state_name

		return cityname+", "+statename

	def get_company_number(self, obj):
		return obj.company.country.phone_code+obj.company.phone_number

	def get_seller_company_number(self, obj):
		return obj.seller_company.country.phone_code+obj.seller_company.phone_number

	def get_images(self, obj):
		images = []
		if obj.items.count() <= 2:
			items = obj.items.all()
			for item in items:
				images.append(item.product.image.thumbnail[settings.SMALL_IMAGE].url)
		else:
			# catalogs = obj.items.all().values_list('product__catalog', flat=True)
			# catalogs = Catalog.objects.filter(id__in=catalogs)
			# for catalog in catalogs:
			# 	images.append(catalog.thumbnail.thumbnail[settings.SMALL_IMAGE].url)
			temp_catalog_id = []
			items = obj.items.all()
			for item in items:
				if item.product.catalog_id in temp_catalog_id:
					continue
				temp_catalog_id.append(item.product.catalog_id)
				temp_image = item.product.catalog.thumbnail.thumbnail[settings.SMALL_IMAGE].url
				images.append(temp_image)
		return images

	def get_brokerage(self, obj):
		return obj.total_rate() * obj.brokerage_fees / 100

	def get_buyer_credit_rating(self, obj):
		# ccrObj = CompanyCreditRating.objects.filter(company=obj.company).first()
		# if ccrObj:
		# 	return ccrObj.rating
		# return "Unrated"
		try:
			return obj.company.companycreditrating.rating
		except Exception:
			pass
		return "Unrated"

	class Meta:
		model = SalesOrder
		fields = ('id', 'order_number', 'company', 'total_rate', 'created_at', 'date', 'time', 'processing_status', 'customer_status', 'user','sales_image','purchase_image', 'company_name', 'seller_company', 'seller_company_name', 'note', 'total_products', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'broker_company', 'brokerage_fees', 'broker_company_name', 'items', 'sales_image_2', 'sales_image_3', 'buyer_table_id', 'company_address', 'seller_company_address', 'company_state_city', 'seller_company_state_city', 'company_number', 'seller_company_number', 'is_supplier_approved', 'payment_status', 'buying_company_name', 'preffered_shipping_provider', 'buyer_preferred_logistics', 'ship_to', 'shipping_charges', 'images', 'brokerage', 'buyer_credit_rating', 'seller_extra_discount_percentage', 'order_type')

class InvoiceItemSerializer(serializers.ModelSerializer):
	def create(self, validated_data):
		invoice = validated_data.get('invoice')
		order_item = validated_data.get('order_item')
		qty = validated_data.get('qty')

		#initObj = InvoiceItem.objects.create(invoice=invoice, order_item=order_item, qty=qty)
		initObj = InvoiceItem.objects.create(**validated_data)

		try:
			initObj.order_item.invoiced_qty = initObj.order_item.invoiced_qty+qty
			initObj.order_item.pending_quantity -= qty
			initObj.order_item.save()
		except Exception as e:
			logger.info("InvoiceItemSerializer create Exception = %s"% (str(e)))
			pass

		return initObj

	class Meta:
		model = InvoiceItem

class TaxClassSerializer(serializers.ModelSerializer):
	class Meta:
		model = TaxClass
		depth = 1

class ShipmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Shipment

class GetInvoiceItemSerializer(serializers.ModelSerializer):
	order_item = SalesOrderItemSerializer(required=False)
	tax_class_1 = TaxClassSerializer()
	tax_class_2 = TaxClassSerializer()
	class Meta:
		model = InvoiceItem



class PaymentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Payment

class GetInvoiceSerializer(serializers.ModelSerializer):
	items = GetInvoiceItemSerializer(many=True,  required=False)
	order = GetSalesOrderSerializer(required=False)
	shipments = ShipmentSerializer(source="shipment_set", required=False, many=True)
	payments = PaymentSerializer(required=False, many=True)

	kyc = serializers.SerializerMethodField()
	def get_kyc(self, obj):
		jsondata = {}

		kycObj = CompanyKycTaxation.objects.filter(company=obj.order.seller_company).first()
		kycser = CompanyKycTaxationSerializer(instance=kycObj)
		jsondata['seller_kyc'] =  kycser.data

		kycObj = CompanyKycTaxation.objects.filter(company=obj.order.company).first()
		kycser = CompanyKycTaxationSerializer(instance=kycObj)
		jsondata['buyer_kyc'] =  kycser.data

		return jsondata

	class Meta:
		model = Invoice
		#depth = 1
		fields = ('id', 'order', 'datetime', 'total_qty', 'amount', 'paid_amount', 'pending_amount', 'payment_status', 'taxes', 'total_amount', 'status', 'items', 'invoice_number', 'shipments', 'payments', 'seller_discount', 'wb_coupon', 'wb_coupon_discount', 'tax_class_1', 'tax_class_2', 'total_tax_value_1', 'total_tax_value_2', 'preffered_shipping_provider', 'buyer_preferred_logistics', 'shipping_charges', 'kyc')

class GetSalesOrderInvoiceSerializer(serializers.ModelSerializer):
	items = GetInvoiceItemSerializer(many=True,  required=False)
	shipments = ShipmentSerializer(source="shipment_set", required=False, many=True)
	payments = PaymentSerializer(required=False, many=True)

	class Meta:
		model = Invoice
		fields = ('id', 'order', 'datetime', 'total_qty', 'amount', 'paid_amount', 'pending_amount', 'payment_status', 'taxes', 'total_amount', 'items', 'invoice_number', 'shipments', 'payments', 'status', 'seller_discount', 'wb_coupon', 'wb_coupon_discount', 'tax_class_1', 'tax_class_2', 'total_tax_value_1', 'total_tax_value_2', 'preffered_shipping_provider', 'buyer_preferred_logistics', 'shipping_charges')

class GetExpandSalesOrderSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	buyer_table_id = serializers.SerializerMethodField()
	ship_to = GetAddressSerializer(required=False)
	invoice = GetSalesOrderInvoiceSerializer(source="invoice_set", many=True,  required=False)
	#items = SalesOrderItemSerializer(many=True,  required=False)
	company_name = serializers.CharField(source='company.name', read_only=True)
	company_number = serializers.SerializerMethodField()
	seller_company_name = serializers.CharField(source='seller_company.name', read_only=True)

	brokerage = serializers.SerializerMethodField()
	buyer_credit_rating = serializers.SerializerMethodField()

	seller_chat_user = serializers.ReadOnlyField(source='seller_company.chat_admin_user.username', read_only=True)
	buyer_chat_user = serializers.ReadOnlyField(source='company.chat_admin_user.username', read_only=True)
	broker_company_name = serializers.CharField(source='broker_company.name', read_only=True)

	def get_buyer_table_id(self, obj):
		user=self.context['request'].user
		selling_company = None
		company = user.companyuser.company
		if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
			selling_company = user.companyuser.deputed_to
		elif obj.broker_company == company:
			selling_company = company
		else:
			selling_company=obj.seller_company
		if selling_company and obj.company:
			buyerObj = Buyer.objects.filter(selling_company=selling_company, buying_company=obj.company, status="approved").values_list('id', flat=True).first()
			if buyerObj:
				return buyerObj
			else:
				return None
		else:
			return None

	def get_company_number(self, obj):
		return obj.company.country.phone_code+obj.company.phone_number

	def get_brokerage(self, obj):
		return obj.total_rate() * obj.brokerage_fees / 100

	def get_buyer_credit_rating(self, obj):
		# ccrObj = CompanyCreditRating.objects.filter(company=obj.company).first()
		# if ccrObj:
		# 	return ccrObj.rating
		# return "Unrated"
		try:
			return obj.company.companycreditrating.rating
		except Exception:
			pass
		return "Unrated"

	class Meta:
		model = SalesOrder
		fields = ('id', 'order_number', 'company', 'total_rate', 'created_at', 'date', 'time', 'processing_status', 'customer_status', 'user','sales_image','purchase_image', 'seller_company', 'note', 'total_products', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'broker_company', 'brokerage_fees', 'items', 'sales_image_2', 'sales_image_3', 'buyer_table_id', 'is_supplier_approved', 'invoice', 'company_name', 'seller_company_name', 'total_pending_quantity', 'payment_status', 'buying_company_name', 'company_number', 'buyer_preferred_logistics', 'preffered_shipping_provider', 'ship_to', 'brokerage', 'seller_chat_user', 'buyer_chat_user', 'buyer_credit_rating', 'broker_company_name', 'seller_extra_discount_percentage', 'order_type')



class InvoiceSerializer(serializers.ModelSerializer):
	invoiceitem_set = InvoiceItemSerializer(many=True,  required=False)
	created_from_csv = serializers.BooleanField(required=False)
	discount_from_csv = serializers.DecimalField(max_digits=10 , decimal_places=2, required=False)

	def validate(self, data):
		#user=self.context['request'].user

		order = data.get('order', None)
		if order is not None and order.processing_status == "Cancelled":
			raise serializers.ValidationError({"processing_status":"This order was Calcelled."})

		return data

	def create(self, validated_data):
		#iaqs = [InventoryAdjustmentQty(**item) for item in validated_data]
		#return InventoryAdjustmentQty.objects.bulk_create(iaqs)

		order_id = validated_data.get('order')

		created_from_csv = validated_data.pop('created_from_csv', False)
		discount_from_csv = validated_data.pop('discount_from_csv', None)

		logger.info("InvoiceSerializer created_from_csv = %s"% (created_from_csv))
		if created_from_csv == False:
			invoicestodelete = Invoice.objects.filter(order=order_id, status="Invoiced", payment_status__in=["Pending", "Cancelled"]) #.delete()
			for invoiced in invoicestodelete:
				invoiceitems = invoiced.items.all()
				for invoiceitem in invoiceitems:
					invoiceitem.order_item.pending_quantity += invoiceitem.qty
					invoiceitem.order_item.invoiced_qty -= invoiceitem.qty
					invoiceitem.order_item.save()
				invoiced.delete()

		invoiceitems = validated_data.pop('invoiceitem_set')
		logger.info("InvoiceSerializer validated_data = %s"% (validated_data))
		invoiceObj = Invoice.objects.create(**validated_data)
		logger.info("InvoiceSerializer invoiceObj = %s"% (invoiceObj))

		# logger.info("InvoiceSerializer buyoncredit = %s"% (buyoncredit))
		'''if invoiceObj.order.processing_status != "Dispatched" and invoiceObj.order.processing_status == "Accepted":
			invoiceObj.order.processing_status="In Progress"
			invoiceObj.order.save()'''
		if invoiceObj.order.processing_status == "Dispatched":
			invoiceObj.status = "Dispatched"


		res = []

		totalqty = 0
		invoice_amount = Decimal(0.0)

		taxes = Decimal(0.0)
		total_amount = Decimal(0.0)

		total_seller_discount = Decimal(0.0)

		discount_percent = getOrderCCDiscount(invoiceObj.order)
		discount_percent = discount_percent + invoiceObj.order.seller_extra_discount_percentage
		logger.info("InvoiceSerializer seller discount + discount_percent = %s"% (discount_percent))
		# first_discount_percent = invoiceObj.order.seller_extra_discount_percentage
		# logger.info("InvoiceSerializer first_discount_percent = %s"% (first_discount_percent))

		if discount_from_csv:
			discount_percent = discount_from_csv #discount_percent + discount_from_csv
			logger.info("InvoiceSerializer discount_from_csv final = %s"% (discount_percent))
			# first_discount_percent = discount_from_csv
			# logger.info("InvoiceSerializer discount_from_csv final = %s"% (first_discount_percent))

		is_cash_discount = getIsCashDiscount(invoiceObj.order)

		for item in invoiceitems:
			logger.info("InvoiceSerializer invoiceitems loop = %s"% (item))
			order_item = item.pop('order_item')
			invoice = invoiceObj

			# discount_percent = Decimal(0.0)
			# if discount_from_csv is None:
			# 	second_discount_percent = getSupplierRelDiscountV2(invoiceObj.order.seller_company, invoiceObj.order.company, is_cash_discount, order_item.product)
			# 	discount_percent = first_discount_percent + second_discount_percent
			# else:
			# 	discount_percent = first_discount_percent

			logger.info("InvoiceSerializer invoiceitems loop = %s, discount_percent = %s" % (item, discount_percent))

			qty = item.pop('qty')

			totalqty += int(qty)
			try:
				#invoice_amount += order_item.rate*order_item.quantity
				invoice_amount += order_item.rate*qty
			except Exception:
				pass

			item_total_amount = Decimal(0.0)
			jsondata = {'invoice':invoiceObj.id, 'order_item':order_item.id, 'qty':qty, 'rate':order_item.rate, 'amount':order_item.rate*qty}
			item_total_amount = order_item.rate*qty

			count = 1

			taxObjs = getTaxClassObj(invoiceObj.order.seller_company, invoiceObj.order.company, order_item.product.catalog.category, order_item.rate)
			logger.info("InvoiceSerializer create taxObjs = %s"% (str(taxObjs)))

			if discount_percent is None:
				discount_percent = Decimal(0.0)

			item_price = order_item.rate*qty
			item_discount = item_price * discount_percent / 100
			item_price -= item_discount
			item_total_amount -= item_discount
			total_seller_discount += item_discount

			for taxObj in taxObjs:
				print taxObj
				if count == 1:
					#tax_value_1= (order_item.rate*order_item.quantity * taxObj.percentage)/100
					tax_value_1= (item_price * taxObj.percentage)/100
					jsondata['tax_value_1'] = round(tax_value_1, 2)
					jsondata['tax_class_1'] = taxObj.id
					item_total_amount += tax_value_1
					taxes += tax_value_1

				elif count == 2:
					#tax_value_2 = (order_item.rate*order_item.quantity * taxObj.percentage)/100
					tax_value_2 = (item_price * taxObj.percentage)/100
					jsondata['tax_value_2'] = round(tax_value_2, 2)
					jsondata['tax_class_2'] = taxObj.id
					item_total_amount += tax_value_2
					taxes += tax_value_2

				count += 1
			jsondata['total_amount'] = round(item_total_amount, 2)
			jsondata['discount'] = round(item_discount, 2)
			#gst
			logger.info("InvoiceSerializer create jsondata = %s"% (str(jsondata)))
			initser = InvoiceItemSerializer(data=jsondata)
			if initser.is_valid():
				logger.info("InvoiceSerializer create jsondata save() is_valid true")
				initser.save()
			else:
				logger.info("InvoiceSerializer create jsondata error = %s"% (str(initser.errors)))

		if totalqty != invoiceObj.order.total_products():
			invoiceObj.order.processing_status="In Progress"
			invoiceObj.order.save()

		invoiceObj.seller_discount = total_seller_discount

		logger.info("InvoiceSerializer invoiceObj.seller_discount = %s"% (invoiceObj.seller_discount))
		invoiceObj.total_qty = totalqty
		invoiceObj.amount = invoice_amount
		invoiceObj.paid_amount = Decimal(0.0)

		invoiceObj.taxes = taxes
		#final_amount = invoice_amount + taxes - invoiceObj.seller_discount + invoiceObj.shipping_charges
		final_amount = invoice_amount + taxes
		if invoiceObj.seller_discount is not None:
			final_amount -= invoiceObj.seller_discount
		if invoiceObj.shipping_charges is not None:
			final_amount += invoiceObj.shipping_charges
		invoiceObj.total_amount = final_amount
		invoiceObj.pending_amount = final_amount

		invoiceObj.save()

		'''order = invoiceObj.order
		serializer = SalesOrderSerializer(order, data={'processing_status': 'Dispatched'}, context={'request': self.context['request']}, partial=True)
		if serializer.is_valid():
			serializer.save()'''

		return invoiceObj

	def update(self, instance, validated_data):
		logger.info("update invoice ser")

		oldStatus = instance.status
		newStatus = validated_data.get('status', None)

		instance.total_qty = validated_data.get('total_qty', instance.total_qty)
		instance.amount = validated_data.get('amount', instance.amount)
		instance.paid_amount = validated_data.get('paid_amount', instance.paid_amount)
		instance.pending_amount = validated_data.get('pending_amount', instance.pending_amount)
		instance.payment_status = validated_data.get('payment_status', instance.payment_status)
		instance.taxes = validated_data.get('taxes', instance.taxes)
		instance.total_amount = validated_data.get('total_amount', instance.total_amount)
		instance.invoice_number = validated_data.get('invoice_number', instance.invoice_number)
		instance.status = validated_data.get('status', instance.status)

		instance.wb_coupon = validated_data.get('wb_coupon', instance.wb_coupon)
		instance.seller_discount = validated_data.get('seller_discount', instance.seller_discount)
		instance.wb_coupon_discount = validated_data.get('wb_coupon_discount', instance.wb_coupon_discount)
		instance.preffered_shipping_provider = validated_data.get('preffered_shipping_provider', instance.preffered_shipping_provider)
		instance.buyer_preferred_logistics = validated_data.get('buyer_preferred_logistics', instance.buyer_preferred_logistics)
		instance.shipping_charges = validated_data.get('shipping_charges', instance.shipping_charges)

		instance.save()

		if newStatus is not None and oldStatus != newStatus and newStatus == "Cancelled":
			seller_warehouse = Warehouse.objects.filter(company=instance.order.seller_company).first()
			seller_company = instance.order.seller_company
			buyer_warehouse = Warehouse.objects.filter(company=instance.order.company).first()
			buyer_company = instance.order.company

			items = SalesOrderItem.objects.filter(sales_order=instance.order.id)
			for item in items:
				invoiceitemObj = InvoiceItem.objects.filter(invoice=instance, order_item=item).first()
				if invoiceitemObj:
					if Stock.objects.filter(company=seller_company, product=item.product).exists():
						seller_stock = Stock.objects.get(company=seller_company, product=item.product)

						seller_stock.available = seller_stock.available + max((invoiceitemObj.qty - seller_stock.open_sale), 0)
						seller_stock.blocked = min(seller_stock.in_stock, (seller_stock.open_sale + seller_stock.blocked - invoiceitemObj.qty))
						seller_stock.open_sale = max((seller_stock.open_sale + seller_stock.blocked - invoiceitemObj.qty - seller_stock.in_stock), 0)

						seller_stock.save()

					if Stock.objects.filter(company=buyer_company, product=item.product).exists():
						buyer_stock = Stock.objects.get(company=buyer_company, product=item.product)

						buyer_stock.open_purchase = max(buyer_stock.open_purchase - invoiceitemObj.qty, 0)
						buyer_stock.save()

					item.canceled_qty += invoiceitemObj.qty
					item.save()

			if instance.total_qty == instance.order.total_products():
				instance.order.processing_status="Cancelled"
				instance.order.save()

		return instance

	class Meta:
		model = Invoice
		fields = ('id', 'order', 'datetime', 'total_qty', 'amount', 'paid_amount', 'pending_amount', 'payment_status', 'invoiceitem_set', 'invoice_number', 'taxes', 'total_amount', 'status', 'seller_discount', 'wb_coupon', 'wb_coupon_discount', 'tax_class_1', 'tax_class_2', 'total_tax_value_1', 'total_tax_value_2', 'preffered_shipping_provider', 'buyer_preferred_logistics', 'shipping_charges', 'created_from_csv', 'discount_from_csv')

class SalesOrderSerializer(serializers.ModelSerializer):
	items = SalesOrderItemSerializer(many=True)
	company_name = serializers.CharField(source='company.name', read_only=True)
	seller_company_name = serializers.CharField(source='seller_company.name', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	broker_company_name = serializers.CharField(source='broker_company.name', read_only=True)

	catalog = serializers.IntegerField(required=False, allow_null=True)
	selection = serializers.IntegerField(required=False, allow_null=True)

	#just for getting warehouse id
	warehouse = serializers.IntegerField(write_only=True, required=False, allow_null=True)

	tracking_details = serializers.CharField(required=False)
	mode = serializers.CharField(required=False)
	tracking_number = serializers.CharField(required=False)
	transporter_courier = serializers.CharField(required=False)

	userid = serializers.CharField(required=False)

	def validate(self, data):
		print "in SalesOrderSerializer validate"
		try:
			user=self.context['request'].user
		except Exception as e:
			print "SalesOrderSerializer request Exception ", e
			userid = data['userid']
			print userid
			user = User.objects.get(pk=userid)
		currentUserCompany = get_user_company(user) #user.companyuser.company
		if currentUserCompany is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		if self.instance is None:
			seller_company = data['seller_company']
			company = data['company']

			if seller_company == company:
				#raise serializers.ValidationError({"company":"Buyer and Seller must be different"})
				raise serializers.ValidationError({"company":"Can not create an order to your own company"})

			if data.get('catalog', None) != None:
				if CatalogSelectionStatus.objects.filter(company=seller_company, catalog=data['catalog'], status="Disable").exists():
					raise serializers.ValidationError({"catalog":"Catalog has been disabled by supplier"})

			if data.get('selection', None) != None:
				if CatalogSelectionStatus.objects.filter(company=seller_company, selection=data['selection'], status="Disable").exists():
					raise serializers.ValidationError({"selection":"Selection has been disabled by supplier"})

			if data.get('order_number', None) != None:
				if (currentUserCompany == seller_company and SalesOrder.objects.filter(order_number=data['order_number'], seller_company=seller_company).exists()) or (currentUserCompany == company and SalesOrder.objects.filter(order_number=data['order_number'], company=company).exists()):
					raise serializers.ValidationError({"order_number":"Order number already exists."}) #on changing this error message must need to changes salesordercsv import task with same message
			#raise serializers.ValidationError({"order_number":"1212312"})
			if data.get('items', None) != None:
				items = data['items']
				productsIds = []
				lastcatalog = None

				productIdArr = []
				productNameArr = []
				productSKUArr = []
				rateNameArr = []
				for item in items:
					productsIds.append(item['product'].id)
					lastcatalog = item['product'].catalog
					'''if item['quantity'] > 0 and ProductStatus.objects.filter(company=seller_company, product=item['product'], status="Disable").exists():
						productIdArr.append(item['product'].id)
						productNameArr.append(item['product'].title)
						productSKUArr.append(item['product'].sku)'''

					if item['rate'] < Decimal('0.01'):
						rateNameArr.append(item['product'].title)

				#if len(productIdArr) > 0:
				#	raise serializers.ValidationError({"product":"Some of your products have been disabled by supplier. Please delete them.", "disable_products":productSKUArr})

				if len(rateNameArr) > 0:
					if currentUserCompany == company and lastcatalog is not None:
						users = CompanyUser.objects.filter(company=seller_company, user__groups__name="administrator").values_list('user', flat=True)
						users = list(users)
						print users
						rno = random.randrange(100000, 999999, 1)
						image = lastcatalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
						catalogtitles = Product.objects.filter(id__in=productsIds).values_list('catalog__title', flat=True).distinct()
						catalogtitles = ", ".join(catalogtitles)

						message = notificationTemplates("update_catalog_price_order")% (catalogtitles)
						# if settings.TASK_QUEUE_METHOD == 'celery':
						# 	task_id = notificationSend.apply_async((users, "A buyer could not create a purchase order for your catalog "+str(catalogtitles)+" because you have not updated the price. Please update the price of your catalog.", {"notId": rno, "title":"Update price", "push_type":"promotional", "image":image, "table_id": lastcatalog.id}), expires=datetime.now() + timedelta(days=2))
						# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
						# 	task_id = async(
						# 		'api.tasks.notificationSend',
						# 		users, "A buyer could not create a purchase order for your catalog "+str(catalogtitles)+" because you have not updated the price. Please update the price of your catalog.", {"notId": rno, "title":"Update price", "push_type":"promotional", "image":image, "table_id": lastcatalog.id}
						# 	)
						# print task_id
						sendNotifications(users, message, {"notId": rno, "title":"Update price", "push_type":"promotional", "image":image, "table_id": lastcatalog.id})
					raise serializers.ValidationError({"product":"You cannot order catalogs with item prices as Zero"})

		if self.instance:
			if self.instance.processing_status == "Cancelled":
				raise serializers.ValidationError({"processing_status":"This order was Calcelled."})

		return data

	def create(self, validated_data):
		logger.info("create v1 SalesOrderSerializer")
		items = validated_data.pop('items')

		if 'catalog' in validated_data:
			validated_data.pop('catalog')
		if 'selection' in validated_data:
			validated_data.pop('selection')
		if 'userid' in validated_data:
			validated_data.pop('userid')

		##validated_data['customer_status'] = "Pending"

		salesorder = SalesOrder.objects.create(**validated_data)

		if salesorder.company == salesorder.user.companyuser.company and salesorder.broker_company is None:
			buyerObj = Buyer.objects.filter(selling_company=salesorder.seller_company, buying_company=salesorder.company).first()
			if buyerObj is not None and buyerObj.broker_company is not None:
				salesorder.broker_company = buyerObj.broker_company
				salesorder.save()

		for item in items:
			if item['quantity'] > 0 and not ProductStatus.objects.filter(company=salesorder.seller_company, product=item['product'], status="Disable").exists():
				packing_type = item.get('packing_type', None)
				note = item.get('note', None)
				is_full_catalog = item.get('is_full_catalog', False)
				print "packing_type="
				print packing_type
				print note
				salesitem = SalesOrderItem.objects.get_or_create(product=item['product'], quantity=item['quantity'], rate=item['rate'],sales_order = salesorder, pending_quantity=item['quantity'], note=note, packing_type=packing_type, is_full_catalog=is_full_catalog)

		return salesorder

	def update(self, instance, validated_data):
		logger.info("update SalesOrderSerializer =======================================>>>>>>>>>>>>>>>>")
		newStatus = validated_data.get('processing_status', None)
		oldStatus = instance.processing_status

		newCStatus = validated_data.get('customer_status', None)
		oldCStatus = instance.customer_status

		newShippingCharge = validated_data.get('shipping_charges', None)
		oldShippingCharge = instance.shipping_charges

		buyer_warehouse = validated_data.get('warehouse', None)

		instance.processing_status = validated_data.get('processing_status', instance.processing_status)
		instance.customer_status = validated_data.get('customer_status', instance.customer_status)
		instance.note = validated_data.get('note', instance.note)
		instance.tracking_details = validated_data.get('tracking_details', instance.tracking_details)
		instance.supplier_cancel = validated_data.get('supplier_cancel', instance.supplier_cancel)
		instance.buyer_cancel = validated_data.get('buyer_cancel', instance.buyer_cancel)
		instance.payment_details = validated_data.get('payment_details', instance.payment_details)
		instance.preffered_shipping_provider = validated_data.get('preffered_shipping_provider', instance.preffered_shipping_provider)
		instance.buyer_preferred_logistics = validated_data.get('buyer_preferred_logistics', instance.buyer_preferred_logistics)
		instance.ship_to = validated_data.get('ship_to', instance.ship_to)
		instance.shipping_charges = validated_data.get('shipping_charges', instance.shipping_charges)
		instance.transaction_type = validated_data.get('transaction_type', instance.transaction_type)
		instance.source_type = validated_data.get('source_type', instance.source_type)
		instance.order_type = validated_data.get('order_type', instance.order_type)
		instance.seller_extra_discount_percentage = validated_data.get('seller_extra_discount_percentage', instance.seller_extra_discount_percentage)

		if validated_data.get('payment_date', None) is not None:
			instance.payment_date = validated_data.get('payment_date', instance.payment_date)
		if validated_data.get('dispatch_date', None) is not None:
			instance.dispatch_date = validated_data.get('dispatch_date', instance.dispatch_date)

		if validated_data.get('sales_image', None) is not None:
			instance.sales_image = validated_data.get('sales_image', instance.sales_image)
		if validated_data.get('purchase_image', None) is not None:
			instance.purchase_image = validated_data.get('purchase_image', instance.purchase_image)

		instance.save()

		#on update shipping charges and provider
		if oldShippingCharge is None:
			oldShippingCharge = Decimal('0.00')
		if newShippingCharge is not None and oldShippingCharge != newShippingCharge:
			diffamt = Decimal(newShippingCharge) - Decimal(oldShippingCharge)
			logger.info("diffamt = %s"% (str(diffamt)))
			invoices = Invoice.objects.filter(order=instance, status="Invoiced")
			for invoice in invoices:
				print invoice
				invoice.preffered_shipping_provider = instance.preffered_shipping_provider
				invoice.buyer_preferred_logistics = instance.buyer_preferred_logistics
				invoice.shipping_charges = newShippingCharge
				invoice.total_amount += diffamt
				invoice.pending_amount += diffamt
				invoice.save()

		#to update product items in order
		items = validated_data.get('items', [])
		print items
		if len(items) > 0:
			itemsIds = SalesOrderItem.objects.filter(sales_order = instance).values_list('id', flat=True)
			itemsIds = list(itemsIds)
			print "itemsIds-----", itemsIds
			for item in items:
				if item['quantity'] > 0 and not ProductStatus.objects.filter(company=instance.seller_company, product=item['product'], status="Disable").exists():
					packing_type = item.get('packing_type', None)
					note = item.get('note', None)

					if SalesOrderItem.objects.filter(product=item['product'],sales_order = instance).exists():
						print "order item update"
						soiObj = SalesOrderItem.objects.filter(product=item['product'],sales_order = instance).last()
						soiObj.quantity=item['quantity']
						soiObj.rate=item['rate']
						soiObj.pending_quantity=item['quantity']
						soiObj.note=note
						soiObj.packing_type=packing_type
						soiObj.save()
						itemsIds.remove(soiObj.id)
					else:
						print "order item create"
						salesitem = SalesOrderItem.objects.get_or_create(product=item['product'], quantity=item['quantity'], rate=item['rate'],sales_order = instance, pending_quantity=item['quantity'], note=note, packing_type=packing_type)
			print "itemsIds------", itemsIds
			SalesOrderItem.objects.filter(id__in=itemsIds).delete()


		jsonarr = {}
		jsonarr['order_number'] = instance.order_number
		jsonarr['table_id'] = instance.id

		if newStatus is not None and oldStatus != newStatus and newStatus in ["Dispatched", "In Progress", "Accepted", "Cancelled", "Closed"] and oldStatus not in ["Draft", "Cart"] and instance.source_type == "Marketplace":
			#for buyer notification
			jsonarr['status'] = newStatus
			jsonarr['title'] = "Purchase Order "+str(newStatus)
			jsonarr['order_url'] = str(settings.GLOBAL_SITE_URL)+'?type=purchase&id='+str(instance.id)

			broker_users = []
			if instance.broker_company is not None:
				broker_users=CompanyUser.objects.filter(company=instance.broker_company).values_list('user', flat=True).distinct()

			#deputed_users = CompanyUser.objects.filter(company=instance.company, deputed_from=instance.seller_company).values_list('user', flat=True).distinct()

			user1 = instance.company.company_users.values_list('user', flat=True)
			user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

			# send_notification('order-status', user1, jsonarr)
			sendAllTypesMessage("send_order_status", user1, jsonarr)

		if newStatus is not None and oldStatus != newStatus and newStatus in ["Cancelled", "Delivered"] and oldStatus not in ["Draft", "Cart"] and instance.source_type == "Marketplace":
			#for supplier notification. supplier can't see draft order.
			jsonarr['status'] = newStatus
			jsonarr['title'] = "Sales Order "+str(newStatus)
			jsonarr['order_url'] = str(settings.GLOBAL_SITE_URL)+'?type=sales&id='+str(instance.id)

			broker_users = []
			if instance.broker_company is not None:
				broker_users=CompanyUser.objects.filter(company=instance.broker_company).values_list('user', flat=True).distinct()

			#deputed_users = CompanyUser.objects.filter(company=instance.company, deputed_from=instance.seller_company).values_list('user', flat=True).distinct()

			user1 = instance.seller_company.company_users.values_list('user', flat=True)
			user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

			# send_notification('order-status', user1, jsonarr)
			sendAllTypesMessage("send_order_status", user1, jsonarr)

		if newCStatus is not None and oldCStatus != newCStatus and newCStatus in ["Paid", "Payment Confirmed", "Cancelled"] and oldStatus not in ["Draft", "Cart"] and instance.source_type == "Marketplace":
			#for supplier notification.
			jsonarr['status'] = newCStatus
			jsonarr['title'] = "Sales Order "+str(newStatus)
			jsonarr['order_url'] = str(settings.GLOBAL_SITE_URL)+'?type=sales&id='+str(instance.id)

			broker_users = []
			if instance.broker_company is not None:
				broker_users=CompanyUser.objects.filter(company=instance.broker_company).values_list('user', flat=True).distinct()

			#deputed_users = CompanyUser.objects.filter(company=instance.company, deputed_from=instance.seller_company).values_list('user', flat=True).distinct()

			user1 = instance.seller_company.company_users.values_list('user', flat=True)
			user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

			# send_notification('order-status', user1, jsonarr)
			sendAllTypesMessage("send_order_status", user1, jsonarr)



		if newStatus is not None and oldStatus != newStatus and newStatus == "Accepted":
			seller_warehouse = Warehouse.objects.filter(company=instance.seller_company).first()
			seller_company = instance.seller_company

			items = SalesOrderItem.objects.filter(sales_order=instance.id)
			for item in items:
				if not Stock.objects.filter(company=seller_company, product=item.product).exists():
					Stock.objects.create(company=seller_company, product=item.product)
				seller_stock = Stock.objects.get(company=seller_company, product=item.product)

				available = seller_stock.available
				blocked = seller_stock.blocked
				in_stock = seller_stock.in_stock
				open_sale = seller_stock.open_sale

				seller_stock.available = max((available - min(available, item.quantity)), 0)
				seller_stock.blocked = blocked + min(available, item.quantity)
				seller_stock.open_sale = open_sale + max(item.quantity - available, 0)

				seller_stock.save()

		if newStatus is not None and oldStatus != newStatus and newStatus == "Dispatched":
			seller_warehouse = Warehouse.objects.filter(company=instance.seller_company).first()
			seller_company = instance.seller_company

			invoice_status = "Pending"
			if instance.customer_status == "Paid":
				invoice_status = "Paid"
			jsondata={'order':instance.id, 'total_qty':instance.total_products(), 'amount':instance.total_rate(), 'paid_amount':0, 'pending_amount':0, 'payment_status':invoice_status, 'status':'Dispatched'}
			invoiceitem_set = []

			items = SalesOrderItem.objects.filter(sales_order=instance.id)
			for item in items:
				if Stock.objects.filter(company=seller_company, product=item.product).exists():
					seller_stock = Stock.objects.get(company=seller_company, product=item.product)

					seller_stock.in_stock = max(seller_stock.in_stock - item.quantity, 0)
					seller_stock.blocked = max(seller_stock.blocked - item.quantity, 0)
					seller_stock.open_sale = max(seller_stock.open_sale - item.quantity, 0)

					seller_stock.save()

				invoiceitem_set.append({"order_item":item.id, "qty":item.quantity})

				item.dispatched_qty += item.quantity
				#item.pending_quantity -= item.quantity
				item.save()

			jsondata['invoiceitem_set'] = invoiceitem_set
			invser = InvoiceSerializer(data=jsondata)
			if invser.is_valid():
				print "invser InvoiceSerializer save for looppp"
				invoiceObj = invser.save()
				print "shipmentObj================"
				tracking_details = validated_data.get('tracking_details', instance.tracking_details)
				mode = validated_data.get('mode', None)
				tracking_number = validated_data.get('tracking_number', None)
				transporter_courier = validated_data.get('transporter_courier', None)

				shipmentObj = Shipment.objects.create(invoice=invoiceObj, details=tracking_details, mode=mode, tracking_number=tracking_number, transporter_courier=transporter_courier)
				print shipmentObj
			else:
				print invser.errors


		if newStatus is not None and oldStatus != newStatus and newStatus == "Delivered":
			buyer_company = instance.company

			#items = SalesOrderItem.objects.filter(sales_order=instance.id)
			items = InvoiceItem.objects.filter(invoice__order=instance.id, invoice__status="Dispatched")
			for item in items:
				if Stock.objects.filter(company=buyer_company, product=item.order_item.product).exists():
					#buyer_stock = Stock.objects.get(company=buyer_company, product=item.product)
					buyer_stock = Stock.objects.get(company=buyer_company, product=item.order_item.product)
					print ("in stock")
					print (buyer_stock)
					#if buyer_stock.blocked < buyer_stock.open_sale:
					#	buyer_stock.blocked = buyer_stock.blocked + min((buyer_stock.open_sale - buyer_stock.blocked), buyer_stock.in_stock)
					buyer_stock.available = max((buyer_stock.in_stock + item.qty - (buyer_stock.open_sale+buyer_stock.blocked)), 0)
					buyer_stock.blocked = min((buyer_stock.open_sale + buyer_stock.blocked), (buyer_stock.in_stock + item.qty))
					buyer_stock.in_stock = buyer_stock.in_stock + item.qty
					buyer_stock.open_purchase = max(buyer_stock.open_purchase - item.qty, 0)
					buyer_stock.open_sale = max(buyer_stock.open_sale - item.qty, 0)

					buyer_stock.save()

			if buyer_warehouse is not None and Warehouse.objects.filter(pk=buyer_warehouse).exists():
				buyer_warehouse = Warehouse.objects.get(pk=buyer_warehouse)
				if buyer_warehouse:
					for item in items:
						warehousestock, created = WarehouseStock.objects.get_or_create(warehouse=buyer_warehouse, product=item.order_item.product)
						warehousestock.in_stock = warehousestock.in_stock + item.qty
						warehousestock.save()

			invoices = Invoice.objects.filter(order=instance.id, status="Dispatched")
			for invoice in invoices:
				invoice.status = "Delivered"
				invoice.save()
			#else:
			#	buyer_warehouse = Warehouse.objects.filter(company=instance.company).first()

			soiQty = SalesOrderItem.objects.filter(sales_order=instance.id).aggregate(Sum('pending_quantity')).get('pending_quantity__sum', 0)
			if soiQty is None:
				soiQty = 0

			print "////////////////////////////soiQty=",soiQty
			if soiQty > 0:
				instance.processing_status = oldStatus
				print "///////////oldStatus=",oldStatus
				print "///////////instance.processing_status=",instance.processing_status
				instance.save()


		if (newStatus is not None and oldStatus != newStatus and newStatus == "Cancelled") or (newCStatus is not None and oldCStatus != newCStatus and newCStatus == "Cancelled"):
			seller_warehouse = Warehouse.objects.filter(company=instance.seller_company).first()
			seller_company = instance.seller_company
			buyer_warehouse = Warehouse.objects.filter(company=instance.company).first()
			buyer_company = instance.company

			invoices = Invoice.objects.filter(order=instance.id)
			for invoice in invoices:
				invoice.status = "Cancelled"
				invoice.save()

			items = SalesOrderItem.objects.filter(sales_order=instance.id)
			for item in items:
				if Stock.objects.filter(company=seller_company, product=item.product).exists():
					seller_stock = Stock.objects.get(company=seller_company, product=item.product)


					seller_stock.available = seller_stock.available + max((item.quantity - seller_stock.open_sale), 0)
					seller_stock.blocked = min(seller_stock.in_stock, (seller_stock.open_sale + seller_stock.blocked - item.quantity))
					seller_stock.open_sale = max((seller_stock.open_sale + seller_stock.blocked - item.quantity - seller_stock.in_stock), 0)

					seller_stock.save()

				if Stock.objects.filter(company=buyer_company, product=item.product).exists():
					buyer_stock = Stock.objects.get(company=buyer_company, product=item.product)

					buyer_stock.open_purchase = max(buyer_stock.open_purchase - item.quantity, 0)
					buyer_stock.save()

				item.canceled_qty += item.quantity
				item.save()

		if newStatus is not None and oldStatus != newStatus and newStatus == "Closed":
			seller_warehouse = Warehouse.objects.filter(company=instance.seller_company).first()
			seller_company = instance.seller_company
			buyer_warehouse = Warehouse.objects.filter(company=instance.company).first()
			buyer_company = instance.company

			items = SalesOrderItem.objects.filter(sales_order=instance.id)
			for item in items:
				if Stock.objects.filter(company=seller_company, product=item.product).exists():
					seller_stock = Stock.objects.get(company=seller_company, product=item.product)


					seller_stock.available = seller_stock.available + max((item.pending_quantity - seller_stock.open_sale), 0)
					seller_stock.blocked = min(seller_stock.in_stock, (seller_stock.open_sale + seller_stock.blocked - item.pending_quantity))
					seller_stock.open_sale = max((seller_stock.open_sale + seller_stock.blocked - item.pending_quantity - seller_stock.in_stock), 0)

					seller_stock.save()

				if Stock.objects.filter(company=buyer_company, product=item.product).exists():
					buyer_stock = Stock.objects.get(company=buyer_company, product=item.product)

					buyer_stock.open_purchase = max(buyer_stock.open_purchase - item.pending_quantity, 0)
					buyer_stock.save()

				item.canceled_qty += item.pending_quantity
				item.save()

		#logic for buy on credit
		payment_details = ""
		if instance.payment_details:
			payment_details = instance.payment_details.lower()

		if newStatus is not None and oldStatus != newStatus and newStatus == "Pending" and "buy on credit" in payment_details:
			jsondata={'order':instance.id}
			invoiceitem_set = []
			items = SalesOrderItem.objects.filter(sales_order=instance.id)

			for item in items:
				invoiceitem_set.append({"order_item":item.id, "qty":item.quantity})

			jsondata['invoiceitem_set'] = invoiceitem_set

			invser = InvoiceSerializer(data=jsondata)
			if invser.is_valid():
				print "invser InvoiceSerializer save for looppp"
				invoiceObj = invser.save()
			else:
				print invser.errors

			#for supplier notification.
			jsonarr['title'] = "Sales Order on Credit"

			broker_users = []
			if instance.broker_company is not None:
				broker_users=CompanyUser.objects.filter(company=instance.broker_company).values_list('user', flat=True).distinct()

			#deputed_users = CompanyUser.objects.filter(company=instance.company, deputed_from=instance.seller_company).values_list('user', flat=True).distinct()

			user1 = instance.seller_company.company_users.values_list('user', flat=True)
			user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

			# send_notification('order-status', user1, jsonarr)
			sendAllTypesMessage("send_order_on_credit", user1, jsonarr)

		return instance

	class Meta:
		model = SalesOrder
		fields = ('id', 'order_number', 'company', 'total_rate', 'date', 'time', 'processing_status', 'warehouse', 'customer_status', 'user','sales_image','purchase_image', 'company_name', 'seller_company', 'seller_company_name', 'note', 'total_products', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'broker_company', 'brokerage_fees', 'broker_company_name', 'catalog', 'selection', 'items', 'backorders', 'sales_image_2', 'sales_image_3', 'is_supplier_approved', 'mode', 'tracking_number', 'transporter_courier', 'preffered_shipping_provider', 'buyer_preferred_logistics', 'ship_to', 'shipping_charges', 'userid', 'transaction_type', 'source_type', 'order_type', 'cart', 'seller_extra_discount_percentage')


class ProductLikeSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def validate(self, data):
		user=self.context['request'].user


		if data.get('product', None) != None:
			if self.instance is None:
				if ProductLike.objects.filter(product=data['product'], user=user).exists():
					raise serializers.ValidationError({'product': 'This product already liked'})
			else:
				if ProductLike.objects.filter(product=data['product'], user=user).exclude(id=self.instance.id).exists():
					raise serializers.ValidationError({'product': 'This product already liked'})

		return data

	class Meta:
		model = ProductLike

class SelectionSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def create(self, validated_data):
		products = validated_data.pop('products', None)

		selection = Selection.objects.create(**validated_data)

		selection.products = products

		user=self.context['request'].user
		company = user.companyuser.company
		selection.buyable=True
		for product in products:
			if Product.objects.filter(id=product.id,catalog__company=company).exists() == False:
				'''if Push_User_Product.objects.filter(buying_company=company, product=product).exists():#user=user
					pushIds=Push_User_Product.objects.filter(buying_company=company, product=product).values_list('push', flat=True).distinct()#user=user
					if Push_User.objects.filter(buying_company=company, push__in=pushIds, full_catalog_orders_only=True).exists():#user=user
						selection.buyable=False'''
				if CompanyProductFlat.objects.filter(buying_company=company, product=product).exists():
					pushIds=CompanyProductFlat.objects.filter(buying_company=company, product=product).values_list('push_reference', flat=True).distinct()#user=user
					if Push_User.objects.filter(buying_company=company, push__in=pushIds, full_catalog_orders_only=True).exists():#user=user
						selection.buyable=False

		selection.save()


		return selection

	def update(self, instance, validated_data):
		instance.name = validated_data.get('name', instance.name)
		instance.products = validated_data.get('products', instance.products)
		instance.thumbnail = validated_data.get('thumbnail', instance.thumbnail)

		user=self.context['request'].user
		company = user.companyuser.company
		instance.buyable=True

		for product in instance.products.all():
			if Product.objects.filter(id=product.id,catalog__company=company).exists() == False:
				'''if Push_User_Product.objects.filter(buying_company=company, product=product).exists():#user=user
					pushIds=Push_User_Product.objects.filter(buying_company=company, product=product).values_list('push', flat=True).distinct()#user=user
					if Push_User.objects.filter(buying_company=company, push__in=pushIds, full_catalog_orders_only=True).exists():#user=user
						instance.buyable=False'''
				if CompanyProductFlat.objects.filter(buying_company=company, product=product).exists():
					pushIds=CompanyProductFlat.objects.filter(buying_company=company, product=product).values_list('push_reference', flat=True).distinct()#user=user
					if Push_User.objects.filter(buying_company=company, push__in=pushIds, full_catalog_orders_only=True).exists():#user=user
						instance.buyable=False

		instance.save()

		return instance

	def validate(self, data):
		user=self.context['request'].user
		company = user.companyuser.company

		if data.get('name', None) != None:
			if self.instance is None:
				if Selection.objects.filter(name=data['name'], user=user).exists():
					raise serializers.ValidationError({'name': 'This selection already exists. Please enter a different name'})
			else:
				if Selection.objects.filter(name=data['name'], user=user).exclude(id=self.instance.id).exists():
					raise serializers.ValidationError({'name': 'This selection already exists. Please enter a different name'})

		if data.get('products', None) != None:
			for product in data['products']:
				if Product.objects.filter(id=product.id,catalog__company=company).exists() == False:
					#if Push_User_Product.objects.filter(buying_company=company, product=product).exists() == False:
					if CompanyProductFlat.objects.filter(buying_company=company, product=product).exists() == False:
						raise serializers.ValidationError({'products': 'Select valid product'})

		return data

	class Meta:
		model = Selection
		fields = ('id', 'user', 'name', 'products', 'thumbnail')

class GetSelectionSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	push_user_id = serializers.SerializerMethodField('get_pushuser')
	is_disable = serializers.SerializerMethodField('get_disable')
	exp_desp_date = serializers.SerializerMethodField('get_expdespdate')

	def get_pushuser(self, obj):
		global pushUserObj
		global user
		global company
		pushUserObj = None
		pushUserId = None

		user = self.context['request'].user
		company = user.companyuser.company
		pushUserId = None
		if user.is_authenticated():
			if obj.user==user:
				pushUserId = None
			else:
				if user.groups.filter(name="salesperson").exists():
					pushUserId = None
				else:
					'''pushUserObjId = Push_User.objects.filter(buying_company=company, selection=obj.id).values('buying_company','selection','selling_company').annotate(Max('id')).values('id__max')#user=user
					pushUserObj = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first()
					pushUserId = pushUserObj.id'''

					cpfObj = CompanyProductFlat.objects.filter(buying_company=company, selection=obj.id).select_related('push_reference').last() #, is_disable=False
					if cpfObj:
						pushUserObj = Push_User.objects.filter(buying_company=company, push=cpfObj.push_reference, selection=obj.id).first()
						if pushUserObj:
							pushUserId = pushUserObj.id

		return pushUserId

	def get_disable(self, obj):
		global user
		global company
		#user = self.context['request'].user
		#company = user.companyuser.company

		status = False
		if CatalogSelectionStatus.objects.filter(company=company, selection=obj.id, status="Disable").exists():
			status = True
		return status

	def get_expdespdate(self, obj):
		global pushUserObj
		if pushUserObj is not None and pushUserObj.push.exp_desp_date is not None:
			return str(pushUserObj.push.exp_desp_date)
		else:
			return None

	class Meta:
		model = Selection
		fields = ('id', 'user', 'name', 'products', 'image', 'push_user_id', 'buyable', 'is_disable', 'exp_desp_date')

class GetSelectionWithProductSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	push_user_id = serializers.SerializerMethodField('get_pushuser')
	is_disable = serializers.SerializerMethodField('get_disable')
	exp_desp_date = serializers.SerializerMethodField('get_expdespdate')

	products = serializers.SerializerMethodField('get_prdct')
	def get_prdct(self, obj):
		global pushUserObj
		global currentUserCompany
		pushUserObj = None

		user = self.context['request'].user
		currentUserCompany=user.companyuser.company

		if obj.user.companyuser.company == currentUserCompany:
			products = obj.products.all().order_by('id')
		else:
			sellingCompanyObj = Buyer.objects.filter(buying_company=currentUserCompany, status="approved").values_list('selling_company', flat=True).distinct()
			productsIds = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, selection=obj, is_disable=False).values_list('product', flat=True)

			products = obj.products.filter(id__in=productsIds).order_by('id')#.values_list('id', flat=True)

		resProducts = []

		cpfObj = None

		for product in products:
			resProduct = {}
			resProduct['id'] = product.id
			resProduct['sku'] = product.sku
			resProduct['title'] = product.title
			resProduct['fabric'] = product.fabric
			resProduct['work'] = product.work
			resProduct['price'] = product.price

			resProduct['image'] = {}
			resProduct['image']['thumbnail_small'] = product.image.thumbnail[settings.SMALL_IMAGE].url
			resProduct['image']['thumbnail_medium'] = product.image.thumbnail[settings.LARGE_IMAGE].url

			resProduct['push_user_product_id'] = None

			if obj.user.companyuser.company == currentUserCompany:
				resProduct['final_price'] = product.price
				resProduct['selling_price'] = product.price

				resProduct['delete_allowed'] = True
				#if Push_User_Product.objects.filter(product=product.id).exists():
				if CompanyProductFlat.objects.filter(product=product.id).exists():
					resProduct['delete_allowed'] = False

				resProduct['is_disable'] = False
				if ProductStatus.objects.filter(company=currentUserCompany, product=product, status="Disable").exists():
					resProduct['is_disable'] = True
			else:
				cpfObj = CompanyProductFlat.objects.filter(product=product, buying_company=currentUserCompany, selling_company__in=sellingCompanyObj, selection=obj, is_disable=False).select_related('selling_company', 'push_reference').last()

				resProduct['final_price'] = cpfObj.final_price
				resProduct['selling_price'] = cpfObj.selling_price

				resProduct['is_disable'] = cpfObj.is_disable

				'''pupid = Push_User_Product.objects.filter(product=product, buying_company=currentUserCompany, selling_company=cpfObj.selling_company, selection=obj, push=cpfObj.push_reference, user=user).values_list('id', flat=True).last()

				if pupid:
					resProduct['push_user_product_id'] = pupid'''
				resProduct['push_user_product_id'] = cpfObj.id
				resProduct['delete_allowed'] = False

			resProduct['product_like_id'] = None

			# ~ plObj = ProductLike.objects.filter(user=user, product=product.id).values_list('id', flat=True).last()
			# ~ if plObj:
				# ~ resProduct['product_like_id'] = plObj

			resProduct['product_likes'] = 0 #ProductLike.objects.filter(product=product.id).count()

			resProducts.append(resProduct)

		if cpfObj:
			pushUserObj = Push_User.objects.filter(buying_company=currentUserCompany, selection=obj, push=cpfObj.push_reference).last()

		return resProducts

	def get_pushuser(self, obj):
		global pushUserObj
		if pushUserObj:
			return pushUserObj.id
		else:
			return None

	def get_disable(self, obj):
		global currentUserCompany

		status = False
		if CatalogSelectionStatus.objects.filter(company=currentUserCompany, selection=obj.id, status="Disable").exists():
			status = True
		return status

	def get_expdespdate(self, obj):
		global pushUserObj
		if pushUserObj is not None and pushUserObj.push.exp_desp_date is not None:
			return str(pushUserObj.push.exp_desp_date)
		else:
			return None

	class Meta:
		model = Selection
		fields = ('id', 'user', 'name', 'products', 'image', 'push_user_id', 'buyable', 'is_disable', 'exp_desp_date')

def pushOnApproves(selling_company, buying_company):
	logger.info("== pushOnApproves() == /V1/ folder ")
	logger.info("In pushOnApproves for buyer start at "+str(datetime.now()))
	logger.info(str(selling_company.name))
	logger.info(str(buying_company.name))

	buyerRef = Buyer.objects.filter(selling_company = selling_company, buying_company=buying_company).select_related('group_type').first()

	sellingPushes = Push.objects.filter(Q(company=selling_company, to_show='yes', buyer_segmentation__group_type=buyerRef.group_type) & Q(Q(buyer_segmentation__city__isnull=True, buyer_segmentation__category__isnull=True) | Q(buyer_segmentation__city=buying_company.city, buyer_segmentation__category=buying_company.category.all()))).values_list('id', flat=True).distinct()

	catalogArr = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).exclude(catalog__isnull=True).values('catalog').annotate(Max('id')).values('id__max')#.distinct().values_list('id', flat=True)
	#print catalogArr
	selectinArr = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).exclude(selection__isnull=True).values('selection').annotate(Max('id')).values('id__max')#.distinct().values_list('id', flat=True)
	#print selectinArr
	sellPushUsers = Push_User.objects.filter(Q(id__in=catalogArr) | Q(id__in=selectinArr)).values_list('id', flat=True).distinct()

	pushUserObj = None
	sellCompUser = CompanyUser.objects.filter(company = selling_company, user__groups__name="administrator").select_related('user').first()
	selluser = sellCompUser.user
	print "selluser==="
	print selluser
	if selling_company.push_downstream.lower() == 'yes':
		logger.info("In pushOnApproves Downstream = yes")
		pushUserObj = Push_User.objects.filter(Q(buying_company=selling_company, push__push_downstream='yes', user=selluser) | Q(id__in=sellPushUsers)).exclude(push__buyer_segmentation__isnull = True).select_related('push__buyer_segmentation', 'catalog', 'selection', 'selling_company', 'buying_company', 'push__company').order_by('-push__time')[:7] ##[::-1]
	else:
		logger.info("In pushOnApproves Downstream = no")
		pushUserObj = Push_User.objects.filter(id__in=sellPushUsers).exclude(push__buyer_segmentation__isnull = True).select_related('push__buyer_segmentation', 'catalog', 'selection', 'selling_company', 'buying_company', 'push__company').order_by('-push__time')[:7] ##[::-1]

	if pushUserObj:
		logger.info("In pushOnApproves has pushUserObj = ")



		completedCatalog = []
		completedSelection = []

		#logger.info(str(pushUserObj))

		for puObj in pushUserObj:
			logger.info("In pushOnApproves in  for loop of pushUserObj")

			group_type = puObj.push.buyer_segmentation.group_type.values_list('id', flat=True)
			if puObj.push.buyer_segmentation.city.count() == 0:
				city = City.objects.all().values_list('id', flat=True)
			else:
				city = puObj.push.buyer_segmentation.city.values_list('id', flat=True)
			if puObj.push.buyer_segmentation.category.count() == 0:
				category = Category.objects.all().values_list('id', flat=True)
			else:
				category = puObj.push.buyer_segmentation.category.values_list('id', flat=True)

			#buyerIds =  Buyer.objects.filter(selling_company = selling_company, buying_company=buying_company, buying_company__city__in=city, buying_company__category__in=category, group_type__in=group_type).distinct().select_related('selling_company', 'buying_company')
			buyerIds =  Buyer.objects.filter(Q(selling_company = selling_company, buying_company=buying_company, buying_company__category__in=category, group_type__in=group_type) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).distinct().select_related('selling_company', 'buying_company')

			if Push_User.objects.filter(push=puObj.push, buying_company=buying_company).exists():
				logger.info("In pushOnApproves alredy pushed to buyer company : pushId / continue")
				continue

			if buyerIds:
				global push_users
				push_users = []

				global peding_push_users
				peding_push_users = []

				global push_user_product
				push_user_product = []

				global push_user
				push_user = []

				global dfsCount
				dfsCount = 0

				logger.info("In pushOnApproves in  for loop of pushUserObj has buyerIds")

				catalog = puObj.catalog
				selection = puObj.selection

				if catalog:
					if catalog.id in completedCatalog:
						logger.info("In pushOnApproves alredy pushed to buyer company : catalog / continue")
						continue
					else:
						completedCatalog.append(catalog.id)

					catalogs = Catalog.objects.filter(id=catalog.id)
				else:
					catalogs = Catalog.objects.none()

				if selection:
					if selection.id in completedSelection:
						logger.info("In pushOnApproves alredy pushed to buyer company : selection / continue")
						continue
					else:
						completedSelection.append(selection.id)

					selections = Selection.objects.filter(id=selection.id)
				else:
					selections = Selection.objects.none()

				catalogProducts = []
				selectionProducts = []
				catalogRate = []
				selectionRate = []

				pushImage = ''
				pushType = ''
				catalogId = None
				pushName = ''
				table_id = None

				if catalogs:
					logger.info("In pushOnApproves catalogs")
					for catalog in catalogs:
						pushName = catalog.title
						pushImage = catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
						pushType="catalog"
						table_id = catalog.id

						logger.info(pushName)

						fixRate = 0
						percentageRate = 0

						productDObj = []

						##check push is seller_company
						if puObj.selling_company == selling_company:
							pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=puObj.user, catalog=catalog).select_related('product')
							for productDetail in pushUserProduct:
								productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price])

							catalogProducts.append(productDObj)

							#buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()
							catalogRate.append([0,0])
						else:
							pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=selluser, catalog=catalog).select_related('product')
							for productDetail in pushUserProduct:
								productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price])

							catalogProducts.append(productDObj)

							buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()

							if buyerobj is None:
								logger.info("In pushOnApproves has not approve buyer for perticuler push : selection / continue")
								continue
							catalogRate.append([buyerobj.fix_amount,buyerobj.percentage_amount])

				if selections:
					logger.info("In pushOnApproves selections")
					for selection in selections:
						pushName = selection.name
						pushImage = ""
						if selection.products.exists():
							pushImage = selection.products.all().first().image.thumbnail[settings.MEDIUM_IMAGE].url #[0]
						pushType="selection"
						table_id = selection.id

						logger.info(pushName)

						fixRate = 0
						percentageRate = 0

						productDObj = []

						##check push is seller_company
						if puObj.selling_company == selling_company:
							pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=puObj.user, selection=selection).select_related('product')
							for productDetail in pushUserProduct:
								productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price])

							selectionProducts.append(productDObj)

							#buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()
							selectionRate.append([0,0])

						else:
							pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=selluser, selection=selection).select_related('product')
							for productDetail in pushUserProduct:
								productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price])

							selectionProducts.append(productDObj)

							buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()

							if buyerobj is None:
								logger.info("In pushOnApproves has not approve buyer for perticuler push : selection / continue")
								continue
							selectionRate.append([buyerobj.fix_amount,buyerobj.percentage_amount])



				title = puObj.push.message

				pushobj = puObj.push

				#city = puObj.push.buyer_segmentation.city.all().values_list('id', flat=True)
				#category = puObj.push.buyer_segmentation.category.all().values_list('id', flat=True)
				#group_type = puObj.push.buyer_segmentation.group_type.all().values_list('id', flat=True)

				push_downstream = "no" #puObj.push.push_downstream

				company_image = None
				if puObj.push.company.thumbnail:
					company_image = puObj.push.company.thumbnail.url
				elif Brand.objects.filter(company=puObj.push.company).exists():
					brandObj = Brand.objects.filter(company=puObj.push.company).only('image').first()
					company_image=brandObj.image.thumbnail[settings.MEDIUM_IMAGE].url

				fullCatalogOrders = puObj.full_catalog_orders_only


				logger.info("In pushOnApproves ready for dfsPush")
				buyerIds = buyerIds.values_list('id', flat=True)
				buyerIds = list(buyerIds)
				if catalogs:
					catalogs = catalogs.values_list('id', flat=True)
					#catalogs = list(catalogs)
				else:
					selections = selections.values_list('id', flat=True)
					#selections = list(selections)
				catalogs = list(catalogs)
				selections = list(selections)
				city = list(city)
				category = list(category)
				group_type = list(group_type)
				print catalogProducts

				logger.info("In pushOnApproves before apply_async")
				if settings.TASK_QUEUE_METHOD == 'celery':
					dfsPushTask.apply_async((buyerIds, [], push_downstream, pushobj.id, pushType, pushImage, title, city, category, catalogs, selections, catalogProducts, selectionProducts, catalogRate, selectionRate, pushName, group_type, selling_company.id, fullCatalogOrders, company_image, table_id, False, True), expires=datetime.now() + timedelta(days=2))
				elif settings.TASK_QUEUE_METHOD == 'djangoQ':
					task_id = async(
						'api.tasks.dfsPushTask',
						buyerIds, [], push_downstream, pushobj.id, pushType, pushImage, title, city, category, catalogs, selections, catalogProducts, selectionProducts, catalogRate, selectionRate, pushName, group_type, selling_company.id, fullCatalogOrders, company_image, table_id, False, True
					)
				#dfsPush(buyerIds, [], push_downstream, pushobj, pushType, pushImage, title, city, category, catalogs, selections, catalogProducts, selectionProducts, catalogRate, selectionRate, pushName, group_type, selling_company, fullCatalogOrders, company_image, table_id, False) #supplier,
				logger.info("In pushOnApproves after apply_async")

				pup = Push_User_Product.objects.bulk_create(push_user_product)
				pu = Push_User.objects.bulk_create(push_user)

				push_user_product = []
				push_user = []

	logger.info("== pushOnApproves /V1/ DONE ============================")

def requestNotification(senderCompanyId, mobileNumber, requestType, tableId, receiverCompanyId, status, sendLastShares=True):
	logger.info("In requestNotification /V1/ for supplier/buyer sms n notification start at "+str(datetime.now()))
	title = ""
	if requestType.lower()=="buyer":
		title = "Supplier Request"
	else:
		title = "Buyer Request"

	company_image = None
	if senderCompanyId.thumbnail:
		company_image = senderCompanyId.thumbnail.url
	elif Brand.objects.filter(company=senderCompanyId).exists():
		brandObj = Brand.objects.filter(company=senderCompanyId).only('image').first()
		if brandObj:
			company_image = brandObj.image.thumbnail[settings.MEDIUM_IMAGE].url

	username = CompanyUser.objects.filter(company=senderCompanyId).values_list('user__username', flat=True).first()

	if requestType.lower()=="supplier":
		jsonarr = {}
		jsonarr['company_name'] = senderCompanyId.name
		jsonarr['table_id'] = tableId.id
		jsonarr['notId'] = tableId.id
		jsonarr['push_type'] = requestType
		jsonarr['company_id'] = senderCompanyId.id
		jsonarr['title'] = title
		jsonarr['company_image'] = company_image
		jsonarr['username'] = username

		user1 = CompanyUser.objects.filter(company=receiverCompanyId).values_list('user', flat=True)
		user1 = User.objects.filter(id__in=user1, groups__name="administrator")
		if status != "approved":
			# send_notification('supplier-request', user1, jsonarr)
			sendAllTypesMessage("default_supplier_not_approved", user1, jsonarr)
		else:
			#if sendLastShares == True:
			#	shareOnApproves(receiverCompanyId, senderCompanyId)
			sendAllTypesMessage("default_supplier_approved", user1, jsonarr)
	else:
		jsonarr = {}
		jsonarr['company_name'] = senderCompanyId.name
		jsonarr['table_id'] = tableId.id
		jsonarr['notId'] = tableId.id
		jsonarr['push_type'] = requestType
		jsonarr['company_id'] = senderCompanyId.id
		jsonarr['title'] = title
		jsonarr['company_image'] = company_image
		jsonarr['username'] = username

		user1 = CompanyUser.objects.filter(company=receiverCompanyId).values_list('user', flat=True)
		user1 = User.objects.filter(id__in=user1, groups__name="administrator")
		if status != "approved":
			# send_notification('buyer-request', user1, jsonarr)
			sendAllTypesMessage("default_buyer_not_approved", user1, jsonarr)
		else:
			#if sendLastShares == True:
			#	shareOnApproves(senderCompanyId, receiverCompanyId)
			sendAllTypesMessage("default_buyer_approved", user1, jsonarr)

def makeBuyerSupplierFromInvitee(mobile_number, country, company):
	logger.info("in makeBuyerSupplierFromInvitee start == /V1/ folder")
	##start make default buyer/supplier
	inviteeIds = Invitee.objects.filter(invitee_number=mobile_number, invite__isnull=False, country=country)
	if inviteeIds:
		for invitee in inviteeIds:
			try:
				if invitee.invite.relationship_type.lower() == "buyer":
					logger.info("in makeBuyerSupplierFromInvitee if buyer")
					if Buyer.objects.filter(invitee=invitee).exists():
						buyerObj = Buyer.objects.filter(invitee=invitee).last()
						buyerObj.buying_company = company
						buyerObj.status="approved"
						buyerObj.save()
						#shareOnApproves(buyerObj.selling_company, buyerObj.buying_company)
					else:
						buyerObj = Buyer.objects.get_or_create(selling_company = invitee.invite.company, buying_company = company, status="approved", group_type=GroupType.objects.get(pk=2))
						#shareOnApproves(buyerObj.selling_company, buyerObj.buying_company)
				elif invitee.invite.relationship_type.lower() == "supplier":
					logger.info("in makeBuyerSupplierFromInvitee elif supplier")
					if Buyer.objects.filter(invitee=invitee).exists():
						buyerObj = Buyer.objects.filter(invitee=invitee).last()
						buyerObj.selling_company = company
						buyerObj.status="approved"
						buyerObj.save()
						#shareOnApproves(buyerObj.selling_company, buyerObj.buying_company)
					else:
						buyerObj = Buyer.objects.get_or_create(selling_company = company, buying_company = invitee.invite.company, status="approved", group_type=GroupType.objects.get(pk=2))
						#shareOnApproves(buyerObj.selling_company, buyerObj.buying_company)
			except Exception as e:
				logger.info("in makeBuyerSupplierFromInvitee error")
				logger.info(str(e))
				'''try:
					if "Duplicate entry" in str(e):
						logger.info("in makeBuyerSupplierFromInvitee deleting id = ")
						logger.info(str(buyerObj.id))
						buyerObj.delete()
				except Exception as e:
					logger.info("in makeBuyerSupplierFromInvitee deleting id error")
					logger.info(str(e))
					pass'''
				pass
	logger.info("in makeBuyerSupplierFromInvitee end == /V1/ folder")

def push(userId, message, pid, pushType, pushImage, pushName, companyImage, tableId, sendSMS, senderCompany):
	push_users = []
	logger.info("In last push() function for sms n notification start at "+str(datetime.now()))
	logger.info(pushName)

	title = ""
	if pushType.lower()=="catalog":
		title = "Received new catalog"
	else:
		title = "Received new selection"

	jsonarr = {}
	jsonarr['message'] = message
	jsonarr['push_id'] = pid
	jsonarr['notId'] = pid
	jsonarr['push_type'] = pushType
	jsonarr['image'] = pushImage
	jsonarr['company_image'] = companyImage
	jsonarr['title'] = title
	jsonarr['name'] = pushName
	jsonarr['table_id'] = tableId

	'''usn_user_exclude = UserSendNotification.objects.filter(user__in=userId, created_at=date.today(), send_gcm__gte = 1).values_list('user', flat=True)
	shareUserId = list(set(userId) - set(usn_user_exclude))
	print "shareUserId"
	print shareUserId'''


	'''for user_id in userId:
		usnObj, created = UserSendNotification.objects.get_or_create(user=user_id, created_at=date.today())
		usnObj.send_gcm = usnObj.send_gcm + 1
		usnObj.save()'''

	brandName = ""
	pushObj = Push.objects.get(pk=pid)
	if pushType.lower() == "catalog":
		catalogObj = Catalog.objects.get(pk=tableId)
		#smstitle = catalogObj.title
		smsurl = 'https://app.wishbooks.io/m?type=catalog&id='+str(tableId)
		whatsappurl = 'https://app.wishbooks.io/m?type=catalog&id='+str(tableId)
		brandName = catalogObj.brand.name

	jsonarr['brand_name'] = brandName
	# send_notification('share', userId, jsonarr)
	sendAllTypesMessage("share", userId, jsonarr)

	if pushObj.sms.lower() == "yes" and pushType.lower() == "catalog" and sendSMS==True:
		usn_user_exclude = UserSendNotification.objects.filter(user__in=userId, created_at=date.today(), send_sms__gte = settings.SHARE_SMS_LIMIT).values_list('user', flat=True)
		'''smsUserId = list(set(userId) - set(usn_user_exclude))
		logger.info(userId)
		logger.info(usn_user_exclude)
		logger.info(smsUserId)'''

		#phone_number = UserProfile.objects.filter(user__in=userId, is_profile_set=True).exclude(user__in=usn_user_exclude).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
		phone_number = UserProfile.objects.filter(user__in=userId).exclude(user__in=usn_user_exclude).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()

		unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
		phone_number = list(set(phone_number) - set(unsubscribed_number))

		#template = smsTemplates("push")% (brandName, smstitle, smsurl)
		template = smsTemplates("push")% (brandName, message, smsurl)
		smsSend(phone_number, template)

		#smsUser = UserProfile.objects.filter(user__in=userId, is_profile_set=True).exclude(user__in=usn_user_exclude)
		smsUser = UserProfile.objects.filter(user__in=userId).exclude(user__in=usn_user_exclude)
		for userPObj in smsUser:
			usnObj, created = UserSendNotification.objects.get_or_create(user=userPObj.user, created_at=date.today())
			usnObj.send_sms = usnObj.send_sms + 1
			usnObj.save()
		#smsSendICubes.apply_async((phone_number, template), expires=datetime.now() + timedelta(days=2))

	'''ofUserId = CompanyUser.objects.filter(company=senderCompany).values_list('user__username', flat=True).first()
	#userNames = CompanyUser.objects.filter(user__in=userId).values_list('user__username', flat=True).distinct()
	#userNames = list(userNames)
	ofUserId = str(ofUserId)

	message = str(title)+" "+str(message)
	print "applozic v1 serializer"
	print pushObj.buyer_segmentation.applozic_id
	r = chat_send_message({"ofUserId":ofUserId, "groupId":str(pushObj.buyer_segmentation.applozic_id), "message":message})
	#r = chat_send_broadcast_message({"ofUserId":ofUserId, "userNames":userNames, "messageObject":{"message":message}})
	#print r
	#print r.text
	print "applozic"'''

	push_users = []


def pushPendingBuyer(phone_number, pid, pushType, pushName, tableId):
	logger.info("pushPending sms to")
	pushObj = Push.objects.get(pk=pid)

	if pushType.lower() == "catalog":
		catalogObj = Catalog.objects.get(pk=tableId)
		brandName = catalogObj.brand.name
	else:
		selectionObj = Selection.objects.get(pk=tableId)
		brandName=selectionObj.user.companyuser.company.name

	template = smsTemplates("pushPendingBuyer")% (brandName, pushType+' '+pushName)
	smsSend(phone_number, template)
	#smsSendICubes.apply_async((phone_number, template), expires=datetime.now() + timedelta(days=2))


class PushSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	catalog = serializers.ListField(required=False)
	selection = serializers.ListField(required=False)
	company = serializers.ReadOnlyField(source='company.name', read_only=True)

	full_catalog_orders_only = serializers.BooleanField(required=False)

	def create(self, validated_data):
		logger.info("create pushed start at "+str(datetime.now()))

		currentUser = self.context['request'].user
		currentuserCompany = currentUser.companyuser.company

		global pending_push_users
		pending_push_users = []

		catalog = validated_data.pop('catalog', [])
		selection = validated_data.pop('selection', [])
		catalogs = Catalog.objects.filter(id__in=catalog).select_related('company')
		catalogSharedProducts = []
		#catalogSharedRate = []

		logger.info("catalog = %s"% (str(catalog)))

		change_price_add_percentage = validated_data.get('change_price_add', None)
		change_price_fix = validated_data.get('change_price_fix', None)
		change_price_add_amount = validated_data.get('change_price_add_amount', None)
		logger.info("change_price_add = %s"% (str(change_price_add_percentage)))
		logger.info("change_price_fix = %s"% (str(change_price_fix)))
		logger.info("change_price_add_amount = %s"% (str(change_price_add_amount)))

		full_catalog_orders_only = False
		if validated_data.get('full_catalog_orders_only', None) is not None:
			full_catalog_orders_only = validated_data.pop('full_catalog_orders_only')
		logger.info("validated_data=")
		logger.info(validated_data)
		pushobj = Push.objects.create(**validated_data)

		logger.info("PushSerializer push id = %s"% (str(pushobj.id)))

		if change_price_add_percentage is None and change_price_fix is None and change_price_add_amount is None and catalogs:
			for catalog in catalogs:
				if catalog.view_permission == "public":
					logger.info("PushSerializer push id = %s, creating catalog seller  "% (str(pushobj.id)))

					jsondata={'catalog':catalog.id, 'selling_company':pushobj.company.id, 'selling_type':"Public", 'sell_full_catalog':full_catalog_orders_only}

					csser = CatalogSellerAdminSerializer(data=jsondata)
					if csser.is_valid():
						print "csser is valid"
						csser.save()
					else:
						print "csser errors"
						print csser.errors

					pushobj.status = "Delivered"
					pushobj.shared_catalog = catalog
					pushobj.save()
					return pushobj

		city= []
		category= []
		group_type= []
		if pushobj.buyer_segmentation is not None:
			if pushobj.buyer_segmentation.buyer_grouping_type == "Location Wise":
				group_type = pushobj.buyer_segmentation.group_type.values_list('id', flat=True)
				if pushobj.buyer_segmentation.city.count() == 0:
					city = City.objects.all().values_list('id', flat=True)
				else:
					city = pushobj.buyer_segmentation.city.values_list('id', flat=True)
				if pushobj.buyer_segmentation.category.count() == 0:
					category = Category.objects.all().values_list('id', flat=True)
				else:
					category = pushobj.buyer_segmentation.category.values_list('id', flat=True)
				buyers = Buyer.objects.filter(Q(selling_company = currentuserCompany, status='approved', buying_company__category__in=category, group_type__in=group_type) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).distinct().select_related('selling_company', 'buying_company')
			else:
				buyers = Buyer.objects.filter(selling_company = currentuserCompany, status='approved', buying_company__in=pushobj.buyer_segmentation.buyers.all()).distinct().select_related('selling_company', 'buying_company')

		else:
			buyers = Buyer.objects.filter(selling_company = currentuserCompany, status='approved', buying_company=pushobj.single_company_push)
		logger.info("buyers=")
		logger.info(buyers)

		#return True
		if catalogs:
			logger.info("if catalogs:")
			for catalog in catalogs:
				#completedBuyer.append(catalog.company.id)
				pushobj.shared_catalog = catalog
				pushobj.save()

				catalogowner = catalog.company

				fixRate = 0
				percentageRate = 0

				disableProducts = ProductStatus.objects.filter(Q(Q(company=currentuserCompany) | Q(company=catalog.company, product__catalog__view_permission="public")) & Q(status="Disable")).values_list('product', flat=True)

				if catalogowner == currentuserCompany:
					logger.info("if SAME company")
					productDObj = []

					productObj = Product.objects.filter(catalog=catalog.id).exclude(id__in=disableProducts)
					for productDetail in productObj:
						if change_price_add_percentage is not None and change_price_add_percentage != 0:
							productDObj.append([productDetail.id,productDetail.sku, productDetail.price+(productDetail.price*change_price_add_percentage/100)])
						elif change_price_fix is not None and change_price_fix > 0:
							productDObj.append([productDetail.id,productDetail.sku, change_price_fix])
						elif change_price_add_amount is not None and change_price_add_amount != 0:
							productDObj.append([productDetail.id,productDetail.sku, productDetail.price+change_price_add_amount])
						else:
							productDObj.append([productDetail.id,productDetail.sku, productDetail.price])

					catalogSharedProducts.append(productDObj)

					#catalogSharedRate.append([fixRate,percentageRate])
				else:
					logger.info("if Different company")
					##supplierIds = Buyer.objects.filter(buying_company=currentuserCompany, status="approved").values_list('selling_company', flat=True)
					#pushUserObjId = Push_User.objects.filter(user=currentUser, catalog=catalog, selling_company__in=supplierIds).values('user','catalog','selling_company').annotate(Max('id')).values('id__max')

					#pushUserObj = Push_User.objects.filter(id__in=pushUserObjId).select_related('push', 'selling_company').order_by('total_price').first()

					productDObj = []

					#pushUserProduct = Push_User_Product.objects.filter(push=pushUserObj.push,user=currentUser, catalog=catalog).exclude(product__in=disableProducts).select_related('product') #.exclude(product__in=disableProducts)
					pushUserProduct = CompanyProductFlat.objects.filter(buying_company=currentuserCompany, catalog=catalog).exclude(product__in=disableProducts).select_related('product') #.exclude(product__in=disableProducts)
					if pushUserProduct:
						for productDetail in pushUserProduct:
							if change_price_add_percentage is not None and change_price_add_percentage != 0:
								productDObj.append([productDetail.product.id,productDetail.product.sku, productDetail.final_price+(productDetail.final_price*change_price_add_percentage/100)])
							elif change_price_fix is not None and change_price_fix > 0:
								productDObj.append([productDetail.product.id,productDetail.product.sku, change_price_fix])
							elif change_price_add_amount is not None and change_price_add_amount != 0:
								productDObj.append([productDetail.product.id,productDetail.product.sku, productDetail.final_price+change_price_add_amount])
							else:
								productDObj.append([productDetail.product.id,productDetail.product.sku, productDetail.final_price])

						catalogSharedProducts.append(productDObj)

					elif catalog.view_permission == "public": #on share public catalog calculation
						productObj = Product.objects.filter(catalog=catalog.id).exclude(id__in=disableProducts)
						for productDetail in productObj:
							if change_price_add_percentage is not None and change_price_add_percentage != 0:
								productDObj.append([productDetail.id,productDetail.sku, productDetail.public_price+(productDetail.public_price*change_price_add_percentage/100)])
							elif change_price_fix is not None and change_price_fix > 0:
								productDObj.append([productDetail.id,productDetail.sku, change_price_fix])
							elif change_price_add_amount is not None and change_price_add_amount != 0:
								productDObj.append([productDetail.id,productDetail.sku, productDetail.public_price+change_price_add_amount])
							else:
								productDObj.append([productDetail.id,productDetail.sku, productDetail.public_price])

						catalogSharedProducts.append(productDObj)

					'''if (change_price_add_percentage is not None and change_price_add_percentage > 0) or (change_price_fix is not None and change_price_fix > 0):
						catalogSharedRate.append([fixRate,percentageRate])
					else:
						pushUserObj = pushUserProduct.first()
						#buyerobj = Buyer.objects.filter(selling_company=pushUserObj.selling_company, buying_company=currentuserCompany, status="approved").last()#selling_company=pushUserObj.push.company
						buyerobj = Buyer.objects.filter(selling_company=pushUserObj.selling_company, buying_company=currentuserCompany).last()#, status="approved" selling_company=pushUserObj.push.company
						catalogSharedRate.append([buyerobj.fix_amount,buyerobj.percentage_amount])'''


		if catalogs:
			catalogs = catalogs.values_list('id', flat=True)
		catalogs = list(catalogs)
		city = list(city)
		category = list(category)
		group_type = list(group_type)
		buyers = buyers.values_list('id', flat=True)
		buyers = list(buyers)

		if settings.TASK_QUEUE_METHOD == 'celery':
			logger.info("push celery ser")
			dfsShare.apply_async((pushobj.id, pushobj.company.id, buyers, city, category, group_type, catalogs, catalogSharedProducts, full_catalog_orders_only, True), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			logger.info("push djangoQ ser")
			task_id = async(
				'api.tasks.dfsShare',  # func full name
				pushobj.id, pushobj.company.id, buyers, city, category, group_type, catalogs, catalogSharedProducts, full_catalog_orders_only, True,
				broker = priority_broker_trivenilabs
			)
			logger.info("task_id")
			logger.info(task_id)

		pushobj.status = "Delivered"
		pushobj.save()

		return pushobj

	def validate(self, data):
		user=self.context['request'].user
		company = user.companyuser.company

		catalog = data.get('catalog', [])
		selection = data.get('selection', [])

		buyerSegmentation = data.get('buyer_segmentation', None)
		singleCompanyPush = data.get('single_company_push', None)

		changePriceFix = data.get('change_price_fix', None)

		if buyerSegmentation is None and singleCompanyPush is None:
			raise serializers.ValidationError({"message":"Must include either 'group' or 'buyer'"})

		if buyerSegmentation:
			if buyerSegmentation.company != company:
				raise serializers.ValidationError({"buyer_segmentation":"Selected valid group."})
			if buyerSegmentation.active_buyers() == 0:
				raise serializers.ValidationError({"buyer_segmentation":"There are no users in the selected group."})

		catalogs = Catalog.objects.filter(id__in=catalog)
		selections = Selection.objects.filter(id__in=selection)

		if catalogs:
			disableCatalogIds = getMyDisableCatalogIds(company)

			for catalog in catalogs:
				supplier = catalog.company

				if Product.objects.filter(catalog=catalog).exists() == False:
					raise serializers.ValidationError({"catalog":"There are no products in the selected catalog."})

				if (changePriceFix is None or changePriceFix == 0) and Product.objects.filter(Q(catalog=catalog) & (Q(price__isnull=True) | Q(price__lt=Decimal('0.01')))).exists():
					raise serializers.ValidationError({"product":"Product prices are empty for this catalog . Please enter the fixed price."})

				if supplier != company:
					if Push_User.objects.filter(buying_company=company, catalog=catalog).exists() == False and catalog.view_permission=="push":
						raise serializers.ValidationError({"catalog":"Select valid catalog"})

				if catalog.id in disableCatalogIds:
					raise serializers.ValidationError({"catalog":"This Catalog is disabled."})
		if selections:
			for selection in selections:
				supplier = selection.user.companyuser.company

				if selection.products.all().exists() == False:
					raise serializers.ValidationError({"selection":"There are no products in the selected selection."})

				if supplier != company:
					if Push_User.objects.filter(buying_company=company, selection=selection).exists() == False:
						raise serializers.ValidationError({"selection":"Select valid selection"})

		return data

	class Meta:
		model = Push
		#depth = 1
		fields = ('id', 'date', 'time', 'push_type', 'push_downstream', 'status', 'message', 'buyer_segmentation', 'single_company_push', 'company', 'catalog', 'selection', 'user', 'sms', 'whatsapp', 'email', 'full_catalog_orders_only', 'change_price_add', 'change_price_fix', 'exp_desp_date', 'change_price_add_amount')

class GetPushSerializer(serializers.ModelSerializer):
	buyer_segmentation_name = serializers.CharField(source='buyer_segmentation.segmentation_name', read_only=True)
	single_company_push_name = serializers.CharField(source='single_company_push.name', read_only=True)
	shared_catalog_title = serializers.CharField(source='shared_catalog.title', read_only=True)
	brand_name = serializers.CharField(source='shared_catalog.brand.name', read_only=True)

	class Meta:
		model = Push
		#depth = 1
		fields = ('id', 'date', 'time', 'push_type', 'push_downstream', 'status', 'message', 'buyer_segmentation', 'buyer_segmentation_name', 'single_company_push', 'single_company_push_name', 'company', 'direct_users', 'total_users', 'total_viewed', 'total_products', 'push_amount', 'user', 'title', 'image', 'sms', 'whatsapp', 'email', 'total_products_viewed', 'exp_desp_date', 'shared_catalog', 'shared_catalog_title', 'brand_name') # 'push_catalog', 'push_selection',



class Child3CategorySerializer(serializers.ModelSerializer):
	image = VersatileImageFieldSerializer(
		sizes='category_image'
	)

	class Meta:
		model = Category

class Child2CategorySerializer(serializers.ModelSerializer):
	child_category = Child3CategorySerializer(many=True, required=False, read_only=True)
	image = VersatileImageFieldSerializer(
		sizes='category_image'
	)

	class Meta:
		model = Category

class Child1CategorySerializer(serializers.ModelSerializer):
	child_category = Child2CategorySerializer(many=True, required=False, read_only=True)
	image = VersatileImageFieldSerializer(
		sizes='category_image'
	)

	class Meta:
		model = Category

class CategorySerializer(serializers.ModelSerializer):
	child_category = Child1CategorySerializer(many=True, required=False, read_only=True)
	image = VersatileImageFieldSerializer(
		sizes='category_image'
	)

	class Meta:
		model = Category

class WishbookInvoiceItemSerializer(serializers.ModelSerializer):
	def create(self, validated_data):
		invoice = WishbookInvoiceItem.objects.create(**validated_data)

		total_push_amount = Push_User_Product.all_objects.filter(push__company=invoice.company, is_viewed='yes', viewed_date__gte=invoice.start_date, viewed_date__lte=invoice.end_date).count()

		invoice.qty = total_push_amount
		invoice.rate = settings.PUSH_AMOUNT_PER_VIEWED
		invoice.amount = invoice.qty * invoice.rate

		invoice.save()

		return invoice

	class Meta:
		model = WishbookInvoiceItem

class WishbookInvoiceSerializer(serializers.ModelSerializer):
	invoiceitem_set = WishbookInvoiceItemSerializer(many=True, required=False, read_only=True)
	total_credit_used = serializers.SerializerMethodField()

	def get_total_credit_used(self, obj):
		total = WishbookInvoiceCredit.objects.filter(invoice=obj).aggregate(Sum('amount')).get('amount__sum', 0)
		if total is None:
			total = 0
		return total

	def create(self, validated_data):
		invoice = WishbookInvoice.objects.create(**validated_data)

		invoiceitems = WishbookInvoiceItem.objects.filter(company=invoice.company, start_date__gte=invoice.start_date, end_date__lte=invoice.end_date)

		billed_amount = 0
		for invoiceitem in invoiceitems:
			billed_amount += invoiceitem.amount

		invoice.billed_amount = billed_amount
		invoice.balance_amount = billed_amount
		invoice.save()

		credit_amount = WishbookCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).aggregate(Sum('balance_amount')).get('balance_amount__sum', 0)#datetime.date.today()
		credit_ids = WishbookCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).values_list('id', flat=True)#datetime.date.today()

		#print invoice_credit
		#print invoice_credit_ids

		if credit_amount is None:
			#print "Is None"
			credit_amount = 0

		total_charge = invoice.balance_amount

		if total_charge<credit_amount:
			print "if"
			#invoice.discount = total_charge
			invoice.balance_amount = 0
			invoice.status = 'paid'
			#invoice.payment_datetime = datetime.now()
			if total_charge > 0:
				for cid in credit_ids:
					current_credit_invoice = WishbookCredit.objects.get(pk=cid)
					if current_credit_invoice.balance_amount > total_charge:
						current_credit_invoice.balance_amount -= total_charge
						current_credit_invoice.save()

						WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=total_charge)
						break
					else:
						total_charge -= current_credit_invoice.balance_amount
						WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=current_credit_invoice.balance_amount)
						current_credit_invoice.balance_amount = 0
						current_credit_invoice.save()


		elif total_charge>credit_amount:
			print "elif"
			#invoice.discount = credit_amount
			invoice.balance_amount = total_charge-credit_amount
			for cid in credit_ids:
				current_credit_invoice = WishbookCredit.objects.get(pk=cid)
				WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=current_credit_invoice.balance_amount)
				current_credit_invoice.balance_amount = 0
				current_credit_invoice.save()

		else:
			print "else"
			#invoice.discount = total_charge
			invoice.balance_amount = 0
			invoice.status = 'paid'
			#invoice.payment_datetime = datetime.now()
			if total_charge > 0:
				for cid in credit_ids:
					current_credit_invoice = WishbookCredit.objects.get(pk=cid)
					WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=current_credit_invoice.balance_amount)
					current_credit_invoice.balance_amount = 0
					current_credit_invoice.save()
		invoice.save()

		invoiceitems.update(invoice=invoice)

		return invoice

	def update(self, instance, validated_data):
		invoice = instance

		invoiceitems = WishbookInvoiceItem.objects.filter(company=invoice.company, start_date__gte=invoice.start_date, end_date__lte=invoice.end_date)

		billed_amount = 0
		for invoiceitem in invoiceitems:
			billed_amount += invoiceitem.amount



		if invoice.billed_amount != billed_amount:
			print 'amout has changed'

			total_charge = billed_amount - invoice.billed_amount + invoice.balance_amount

			invoice.billed_amount = billed_amount
			invoice.status = 'pending'
			#print invoice_credit
			#print invoice_credit_ids

			if total_charge < 0:
				credit_amount = WishbookCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).aggregate(Sum('balance_amount')).get('balance_amount__sum', 0)
				credit_ids = WishbookCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).values_list('id', flat=True)#.exclude(balance_amount=0)
			else:
				credit_amount = WishbookCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).exclude(balance_amount=0).aggregate(Sum('balance_amount')).get('balance_amount__sum', 0)
				credit_ids = WishbookCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).exclude(balance_amount=0).values_list('id', flat=True)#

			if credit_amount is None:
				#print "Is None"
				credit_amount = 0



			if total_charge<credit_amount:
				print "if"
				#invoice.discount = total_charge
				invoice.balance_amount = 0
				invoice.status = 'paid'
				#invoice.payment_datetime = datetime.now()
				#print datetime.datetime.now()
				if total_charge > 0:
					for cid in credit_ids:
						current_credit_invoice = WishbookCredit.objects.get(pk=cid)
						if current_credit_invoice.balance_amount > total_charge:
							current_credit_invoice.balance_amount -= total_charge
							current_credit_invoice.save()

							WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=total_charge)
							break
						else:
							total_charge -= current_credit_invoice.balance_amount
							WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=current_credit_invoice.balance_amount)
							current_credit_invoice.balance_amount = 0
							current_credit_invoice.save()


			elif total_charge>credit_amount:
				print "elif"
				#invoice.discount = credit_amount
				invoice.balance_amount = total_charge-credit_amount
				for cid in credit_ids:
					current_credit_invoice = WishbookCredit.objects.get(pk=cid)
					WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=current_credit_invoice.balance_amount)
					current_credit_invoice.balance_amount = 0
					current_credit_invoice.save()

			else:
				print "else"
				#invoice.discount = total_charge
				invoice.balance_amount = 0
				invoice.status = 'paid'
				#invoice.payment_datetime = datetime.now()
				if total_charge > 0:
					for cid in credit_ids:
						current_credit_invoice = WishbookCredit.objects.get(pk=cid)
						WishbookInvoiceCredit.objects.create(invoice=invoice, credit=current_credit_invoice, amount=current_credit_invoice.balance_amount)
						current_credit_invoice.balance_amount = 0
						current_credit_invoice.save()
			invoice.save()

			invoiceitems.update(invoice=invoice)

		return instance

	class Meta:
		model = WishbookInvoice
		fields = ('id', 'company', 'billed_amount', 'balance_amount', 'discount', 'status', 'start_date', 'end_date', 'invoiceitem_set', 'total_credit_used')

class WishbookCreditSerializer(serializers.ModelSerializer):
	class Meta:
		model = WishbookCredit

class WishbookInvoiceCreditSerializer(serializers.ModelSerializer):
	class Meta:
		model = WishbookInvoiceCredit

class WishbookPaymentSerializer(serializers.ModelSerializer):
	class Meta:
		model = WishbookPayment

class WishbookInvoicePaymentSerializer(serializers.ModelSerializer):
	class Meta:
		model = WishbookInvoicePayment

class CompanyPhoneAliasSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)

	def create(self, validated_data):
		phoneNumber = validated_data.get('alias_number', None)

		country = validated_data.get('country', Country.objects.get(pk=1))

		user = self.context['request'].user
		company = user.companyuser.company

		phoneAlias = CompanyPhoneAlias.objects.create(country=country, alias_number=phoneNumber, company=company)

		'''otp = random.randrange(100000, 999999, 1)

		sendOTP(str(country.phone_code)+str(phoneNumber), str(otp))

		registrationOtp = RegistrationOTP.objects.create(phone_number=phoneNumber, otp=otp, country=country)'''
		checkAndSendOTP(phoneNumber, country)

		return phoneAlias

	def validate(self, data):
		user=self.context['request'].user

		country = Country.objects.get(pk=1)
		if data.get('country', None) != None:
			country = data['country']

		phone_number = data['alias_number']

		if not is_phone_number_available(country, phone_number, True):
			raise serializers.ValidationError({"phone_number":"User is registered with this number"})

		'''if self.instance is None:
			if UserProfile.objects.filter(phone_number=phone_number, country=country).exists() or Company.objects.filter(phone_number=phone_number, country=country).exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exists():
				raise serializers.ValidationError({"phone_number":"User is registered with this number"})
		else:
			if UserProfile.objects.filter(phone_number=phone_number, country=country).exists() or Company.objects.filter(phone_number=phone_number, country=country).exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exclude(id=self.instance.id).exists():
				raise serializers.ValidationError({"phone_number":"User is registered with this number"})'''

		return data

	class Meta:
		model = CompanyPhoneAlias

class CompanyPriceListSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	class Meta:
		model = CompanyPriceList

class CompanyBuyerGroupSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	class Meta:
		model = CompanyBuyerGroup

class BuyerSegmentationSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)

	def create(self, validated_data):
		state = validated_data.pop('state', [])
		city = validated_data.pop('city', [])
		category = validated_data.pop('category', [])
		group_type = validated_data.pop('group_type', [])
		buyers = validated_data.pop('buyers', [])

		if len(group_type) == 0:
			group_type = GroupType.objects.all().values_list('id', flat=True).distinct()
			group_type = list(group_type)

		buyersegment = BuyerSegmentation.objects.create(**validated_data)
		buyersegment.state = state
		buyersegment.city = city
		buyersegment.category = category
		buyersegment.group_type = group_type
		buyersegment.buyers = buyers
		buyersegment.save()

		user = CompanyUser.objects.filter(company=buyersegment.company).first().user

		group_type = buyersegment.group_type.values_list('id', flat=True)
		if buyersegment.city.count() == 0:
			city = City.objects.all().values_list('id', flat=True)
		else:
			city = buyersegment.city.values_list('id', flat=True)
		if buyersegment.category.count() == 0:
			category = Category.objects.all().values_list('id', flat=True)
		else:
			category = buyersegment.category.values_list('id', flat=True)

		#usrnames = Buyer.objects.filter(selling_company=buyersegment.company, status="approved", group_type__in=group_type, buying_company__city__in=city, buying_company__category__in=category).values_list('buying_company__chat_admin_user__username', flat=True)
		usrnames = Buyer.objects.filter(Q(selling_company=buyersegment.company, status="approved", group_type__in=group_type, buying_company__category__in=category) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).values_list('buying_company__chat_admin_user__username', flat=True)
		usrnames = list(usrnames)

		r = chat_create_group({"ofUserId":user.username, "groupName":user.username+" "+buyersegment.segmentation_name, "groupMemberList":usrnames, "type":"5"}, {'task':'set_segmentation_applozic_id', 'company':buyersegment.company.id, 'segmentation':buyersegment.id})
		#r = r.json()
		print r
		#buyersegment.applozic_id = r["response"]["id"]
		#buyersegment.save()

		return buyersegment

	def validate(self, data):
		user=self.context['request'].user
		company = user.companyuser.company

		if self.instance is None:
			if BuyerSegmentation.objects.filter(segmentation_name=data['segmentation_name'], company=company).exists():
				raise serializers.ValidationError({'segmentation_name': 'This group already exists. Please enter a different name'})
		else:
			if BuyerSegmentation.objects.filter(segmentation_name=data['segmentation_name'], company=company).exclude(id=self.instance.id).exists():
				raise serializers.ValidationError({'segmentation_name': 'This group already exists. Please enter a different name'})

		return data

	class Meta:
		model = BuyerSegmentation
		'''validators = [
			UniqueTogetherValidator(
				queryset=BuyerSegmentation.objects.all(),
				fields=('segmentation_name', 'company', ),
				message='should be unique'
			)
		]'''
		fields = ('id', 'segmentation_name', 'state', 'city', 'category', 'active_buyers', 'last_generated', 'company', 'group_type', 'applozic_id', 'buyer_grouping_type', 'buyers')

class GetBuyerSegmentationSerializer(serializers.ModelSerializer):
	class Meta:
		model = BuyerSegmentation
		fields = ('id', 'segmentation_name', 'state', 'city', 'category', 'active_buyers', 'last_generated', 'group_type', 'applozic_id', 'buyer_grouping_type', 'buyers')




class AppInstanceV1Serializer(serializers.ModelSerializer):
	app_name = serializers.CharField(source='app.name', read_only=True)
	class Meta:
		model = AppInstance

class AppV1Serializer(serializers.ModelSerializer):
	class Meta:
		model = App

class AppExpandV1Serializer(serializers.ModelSerializer):
	instance_app = AppInstanceV1Serializer(many=True, read_only=True)
	class Meta:
		model = App

class SKUMapV1Serializer(serializers.ModelSerializer):
	class Meta:
		model = SKUMap
		validators = [
			serializers.UniqueTogetherValidator(
				queryset=SKUMap.objects.all(),
				fields=('app_instance', 'external_sku'),
				message="The fields App Instance, External SKU must make a unique set."
			)
			# ~ serializers.UniqueTogetherValidator(
				# ~ queryset=SKUMap.objects.all(),
				# ~ fields=('app_instance', 'product'),
				# ~ message="The fields App Instance, Product must make a unique set."
			# ~ )
		]

class WarehouseV1Serializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	class Meta:
		model = Warehouse

class StockV1Serializer(serializers.ModelSerializer):
	class Meta:
		model = Stock

	def update(self, instance, validated_data):
		in_stock = validated_data.get('in_stock', instance.in_stock)

		instance.warehouse = validated_data.get('warehouse', instance.warehouse)
		instance.company = validated_data.get('company', instance.company)
		instance.product = validated_data.get('product', instance.product)

		available = instance.available
		blocked = instance.blocked
		open_sale = instance.open_sale

		instance.in_stock = in_stock
		instance.available = max(in_stock - (open_sale + blocked), 0)
		instance.blocked = min(open_sale + blocked, in_stock)
		instance.open_sale = max(open_sale + blocked - in_stock, 0)

		instance.save()

		return instance

class GetStockV1Serializer(serializers.ModelSerializer):
	product = GetProductSerializer()
	class Meta:
		model = Stock

class StockV1ListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Stock
		depth = 1

class BarcodeV1Serializer(serializers.ModelSerializer):
	class Meta:
		model = Barcode

'''class OpeningStockQtyListSerializer(serializers.ListSerializer):
	def create(self, validated_data):
		osqs = [OpeningStockQty(**item) for item in validated_data]
		return OpeningStockQty.objects.bulk_create(osqs)

	def __iter__(self):
		return self

	def next(self):
		raise StopIteration'''

class OpeningStockQtySerializer(serializers.ModelSerializer):
	product_title = serializers.CharField(source='product.title', read_only=True)

	def create(self, validated_data):
		print validated_data
		opening_stock = validated_data.pop('opening_stock')
		product = validated_data.pop('product')
		in_stock = validated_data.pop('in_stock')

		invAdjObj = OpeningStockQty.objects.create(opening_stock=opening_stock, product=product, in_stock=in_stock)

		if not Stock.objects.filter(company=opening_stock.company, product=product).exists():
			Stock.objects.create(company=opening_stock.company, product=product, in_stock=in_stock, available=in_stock)
		else:
			#Stock.objects.filter(warehouse=opening_stock.warehouse, product=product).update(warehouse=opening_stock.warehouse, product=product, in_stock=in_stock)
			stockObj = Stock.objects.get(company=opening_stock.company, product=product)

			available = stockObj.available
			blocked = stockObj.blocked
			open_sale = stockObj.open_sale

			stockObj.in_stock = in_stock
			stockObj.available = max(in_stock - (open_sale + blocked), 0)
			stockObj.blocked = min(open_sale + blocked, in_stock)
			stockObj.open_sale = max(open_sale + blocked - in_stock, 0)

			stockObj.save()

		return invAdjObj

	class Meta:
		model = OpeningStockQty
		#list_serializer_class = OpeningStockQtyListSerializer

class OpeningStockSerializer(serializers.ModelSerializer):
	openingstockqty_set = OpeningStockQtySerializer(many=True,  required=False)

	def create(self, validated_data):
		qtys = validated_data.pop('openingstockqty_set')

		invAdj = OpeningStock.objects.create(**validated_data)
		print invAdj
		res = []
		for item in qtys:
			print "for loop"
			print item
			product = item.pop('product')
			opening_stock = invAdj
			in_stock = item.pop('in_stock')

			jsondata={'opening_stock':invAdj.id, 'product':product.id, 'in_stock':in_stock}

			invaq = OpeningStockQtySerializer(data=jsondata)
			if invaq.is_valid():
				print "save for looppp"
				invaq.save()
			else:
				print invaq.errors

		return invAdj

	class Meta:
		model = OpeningStock



from django.utils import timezone

'''class InventoryAdjustmentQtyListSerializer(serializers.ListSerializer):
	def create(self, validated_data):
		#iaqs = [InventoryAdjustmentQty(**item) for item in validated_data]
		#return InventoryAdjustmentQty.objects.bulk_create(iaqs)
		res = []
		for item in validated_data:
			product = item.pop('product')
			inventory_adjustment = item.pop('inventory_adjustment')
			quantity = item.pop('quantity')
			adjustment_type = item.pop('adjustment_type')
			to_warehouse = item.get('to_warehouse', None)

			invAdjObj = InventoryAdjustmentQty.objects.create(inventory_adjustment=inventory_adjustment, product=product, quantity=quantity, adjustment_type=adjustment_type, to_warehouse=to_warehouse)
			res.append(invAdjObj)

			if not Stock.objects.filter(warehouse=inventory_adjustment.warehouse, product=product).exists():
				Stock.objects.create(warehouse=inventory_adjustment.warehouse, product=product, in_stock=quantity)
			elif invAdjObj.adjustment_type == "Add":
				stockObj = Stock.objects.get(warehouse=inventory_adjustment.warehouse, product=product)
				stockObj.in_stock = stockObj.in_stock + quantity
				stockObj.save()
				if stockObj.blocked < stockObj.open_sale:
					stockObj.blocked = stockObj.blocked + min((stockObj.open_sale - stockObj.blocked), stockObj.in_stock)
					stockObj.save()
			elif invAdjObj.adjustment_type == "Remove":
				stockObj = Stock.objects.get(warehouse=inventory_adjustment.warehouse, product=product)
				stockObj.in_stock = stockObj.in_stock - quantity
				stockObj.save()
				stockObj.blocked = stockObj.in_stock
				stockObj.save()
		return res

	def __iter__(self):
		return self

	def next(self):
		raise StopIteration'''

class InventoryAdjustmentQtySerializer(serializers.ModelSerializer):
	#warehouse = serializers.IntegerField(required=False, allow_null=True)
	#inventory_adjustment = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
	product_title = serializers.CharField(source='product.title', read_only=True)

	def create(self, validated_data):
		'''warehouse = validated_data.pop('warehouse')
		warehouse=Warehouse.objects.get(pk=warehouse)
		invAdj = InventoryAdjustment.objects.create(warehouse=warehouse, created_at=timezone.now())'''
		print validated_data
		inventory_adjustment = validated_data.pop('inventory_adjustment')
		product = validated_data.pop('product')
		quantity = validated_data.pop('quantity')
		adjustment_type = validated_data.pop('adjustment_type')
		to_warehouse = validated_data.get('to_warehouse', None)

		invAdjObj = InventoryAdjustmentQty.objects.create(inventory_adjustment=inventory_adjustment, product=product, quantity=quantity, adjustment_type=adjustment_type, to_warehouse=to_warehouse)

		if not Stock.objects.filter(company=inventory_adjustment.company, product=product).exists():
			Stock.objects.create(company=inventory_adjustment.company, product=product, in_stock=quantity, available=quantity)
		elif invAdjObj.adjustment_type == "Add":
			stockObj = Stock.objects.get(company=inventory_adjustment.company, product=product)

			available = stockObj.available
			blocked = stockObj.blocked
			in_stock = stockObj.in_stock
			open_sale = stockObj.open_sale

			stockObj.available = max(in_stock + quantity - (open_sale+blocked), 0)
			stockObj.blocked = min(open_sale + blocked, (in_stock + quantity))
			stockObj.in_stock = in_stock + quantity
			stockObj.open_sale = max(open_sale + blocked - (in_stock+quantity), 0)
			stockObj.save()
			#if stockObj.blocked < stockObj.open_sale:
			#	stockObj.blocked = stockObj.blocked + min((stockObj.open_sale - stockObj.blocked), stockObj.in_stock)
			#	stockObj.save()
		elif invAdjObj.adjustment_type == "Remove":
			stockObj = Stock.objects.get(company=inventory_adjustment.company, product=product)

			available = stockObj.available
			blocked = stockObj.blocked
			in_stock = stockObj.in_stock
			open_sale = stockObj.open_sale

			stockObj.in_stock = max(in_stock - quantity, 0)
			stockObj.available = max(in_stock - quantity - (open_sale + blocked), 0)
			stockObj.blocked = min(open_sale + blocked, (in_stock - quantity))
			stockObj.open_sale = max(open_sale + blocked -(in_stock - quantity), 0)

			stockObj.save()

		return invAdjObj

	class Meta:
		model = InventoryAdjustmentQty
		###list_serializer_class = InventoryAdjustmentQtyListSerializer
		'''extra_kwargs = {
			"inventory_adjustment": {
				"validators": [],
			},
		}'''
		#fields = ('id', 'inventory_adjustment', 'product', 'quantity', 'adjustment_type', 'to_warehouse', 'warehouse')

class InventoryAdjustmentSerializer(serializers.ModelSerializer):
	#qty = serializers.CharField()
	inventoryadjustmentqty_set = InventoryAdjustmentQtySerializer(many=True,  required=False)

	def create(self, validated_data):
		#iaqs = [InventoryAdjustmentQty(**item) for item in validated_data]
		#return InventoryAdjustmentQty.objects.bulk_create(iaqs)

		qtys = validated_data.pop('inventoryadjustmentqty_set')

		invAdj = InventoryAdjustment.objects.create(**validated_data)
		print invAdj
		res = []
		for item in qtys:
			print "for loop"
			print item
			product = item.pop('product')
			inventory_adjustment = invAdj#item.pop('inventory_adjustment')
			quantity = item.pop('quantity')
			adjustment_type = item.pop('adjustment_type')
			to_warehouse = item.get('to_warehouse', None)

			jsondata={'inventory_adjustment':invAdj.id, 'product':product.id, 'quantity':quantity, 'adjustment_type':adjustment_type, 'to_warehouse':to_warehouse}
			if to_warehouse is not None:
				jsondata['to_warehouse'] = to_warehouse.id
			invaq = InventoryAdjustmentQtySerializer(data=jsondata)
			if invaq.is_valid():
				print "save for looppp"
				invaq.save()
			else:
				print invaq.errors


			'''print "before create qty"
			invAdjObj = InventoryAdjustmentQty.objects.create(inventory_adjustment=inventory_adjustment, product=product, quantity=quantity, adjustment_type=adjustment_type, to_warehouse=to_warehouse)
			res.append(invAdjObj)
			print "after create qty"

			if not Stock.objects.filter(warehouse=inventory_adjustment.warehouse, product=product).exists():
				Stock.objects.create(warehouse=inventory_adjustment.warehouse, product=product, in_stock=quantity)
			elif invAdjObj.adjustment_type == "Add":
				stockObj = Stock.objects.get(warehouse=inventory_adjustment.warehouse, product=product)
				stockObj.in_stock = stockObj.in_stock + quantity
				stockObj.save()
				if stockObj.blocked < stockObj.open_sale:
					stockObj.blocked = stockObj.blocked + min((stockObj.open_sale - stockObj.blocked), stockObj.in_stock)
					stockObj.save()
			elif invAdjObj.adjustment_type == "Remove":
				stockObj = Stock.objects.get(warehouse=inventory_adjustment.warehouse, product=product)
				stockObj.in_stock = stockObj.in_stock - quantity
				stockObj.save()
				stockObj.blocked = stockObj.in_stock
				stockObj.save()'''
		return invAdj

	class Meta:
		model = InventoryAdjustment
		fields = ('id', 'warehouse', 'date', 'remark', 'inventoryadjustmentqty_set')

class AttendanceSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	class Meta:
		model = Attendance

class CompanyAccountSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	class Meta:
		model = CompanyAccount

class CompanyCatalogViewSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def create(self, validated_data):
		company = validated_data.get('company')
		user = validated_data.get('user')

		catalog = validated_data.get('catalog')
		catalog_type = validated_data.get('catalog_type')

		if company:
			if CompanyCatalogView.objects.filter(company=company, catalog=catalog, catalog_type=catalog_type).count() > 0:
				ccvObj = CompanyCatalogView.objects.filter(company=company, catalog=catalog, catalog_type=catalog_type).first()
				ccvObj.created_at=datetime.now()
				ccvObj.clicks += 1
				ccvObj.save()
			else:
				ccvObj, created = CompanyCatalogView.objects.get_or_create(company=company, catalog=catalog, catalog_type=catalog_type)
		elif user:
			if CompanyCatalogView.objects.filter(user=user, catalog=catalog, catalog_type=catalog_type).count() > 0:
				ccvObj = CompanyCatalogView.objects.filter(user=user, catalog=catalog, catalog_type=catalog_type).first()
				ccvObj.created_at=datetime.now()
				ccvObj.clicks += 1
				ccvObj.save()
			else:
				ccvObj, created = CompanyCatalogView.objects.get_or_create(user=user, catalog=catalog, catalog_type=catalog_type)

		return ccvObj

	'''def validate(self, data):
		user=self.context['request'].user
		company = user.companyuser.company

		if self.instance is None:
			if CompanyCatalogView.objects.filter(catalog=data['catalog'], catalog_type=data['catalog_type'], company=company).exists():
				raise serializers.ValidationError({'failed': 'The fields Company, Catalog and Catalog Type must make a unique set.'})
		else:
			if CompanyCatalogView.objects.filter(catalog=data['catalog'], catalog_type=data['catalog_type'], company=company).exclude(id=self.instance.id).exists():
				raise serializers.ValidationError({'failed': 'The fields Company, Catalog and Catalog Type must make a unique set.'})

		return data'''

	class Meta:
		model = CompanyCatalogView
		'''validators = [
			serializers.UniqueTogetherValidator(
				queryset=CompanyCatalogView.objects.all(),
				fields=('company', 'catalog', 'catalog_type'),
				message="The fields Company, Catalog and Catalog Type must make a unique set."
			)
		]'''

class LanguageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Language

class PromotionSerializer(serializers.ModelSerializer):
	image = VersatileImageFieldSerializer(
		sizes='promotion_image'
	)
	class Meta:
		model = Promotion

class SalesmanLocationSerializer(serializers.ModelSerializer):

	def create(self, validated_data):
		city = validated_data.pop('city', None)
		state = validated_data.pop('state')
		slObj = SalesmanLocation.objects.create(**validated_data)
		if city:
			slObj.city = city
		slObj.state = state
		slObj.save()

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

		return slObj

	def update(self, instance, validated_data):
		instance.salesman = validated_data.get('salesman', instance.salesman)
		instance.city = validated_data.get('city', instance.city)
		instance.state = validated_data.get('state', instance.state)
		instance.save()

		'''buyers = Buyer.objects.filter(selling_company=instance.salesman.companyuser.company, buying_company__city__in=instance.city.all(), buying_company__state__in=instance.state.all())

		buyers_ids = buyers.values_list('buying_company', flat=True)

		BuyerSalesmen.objects.filter(salesman=instance.salesman).exclude(buyer__in=buyers_ids).delete()

		buyers_ids = BuyerSalesmen.objects.filter(salesman=instance.salesman).values_list('buyer', flat=True)
		buyers = buyers.exclude(buying_company__in = buyers_ids)

		for buyer in buyers:
			BuyerSalesmen.objects.create(salesman=instance.salesman, buyer=buyer.buying_company)'''

		states = instance.state.all()
		if instance.city.count() == 0:
			cities = City.objects.filter(state__in=states)
		else:
			cities = instance.city.all()
		buying_company_ids = Buyer.objects.filter(selling_company=instance.salesman.companyuser.company, buying_company__city__in=cities, buying_company__state__in=states).values_list('buying_company', flat=True)
		companyObjs = Company.objects.filter(id__in=buying_company_ids)

		bsObj, created = BuyerSalesmen.objects.get_or_create(salesman=instance.salesman)
		bsObj.buyers=companyObjs
		bsObj.save()


		return instance

	class Meta:
		model = SalesmanLocation

class BuyerSalesmenSerializer(serializers.ModelSerializer):
	class Meta:
		model = BuyerSalesmen

class AssignGroupsSerializer(serializers.ModelSerializer):
	def create(self, validated_data):
		print "create"
		user = validated_data.get('user')
		groups = validated_data.get('groups')
		print user
		agObj, created = AssignGroups.objects.get_or_create(user=user)
		agObj.groups = groups
		agObj.save()

		return agObj

	class Meta:
		model = AssignGroups
		extra_kwargs = {
			"user": {
				"validators": [],
			},
		}

from api.models import SELLER_REMARK, BUYER_REMARK
class OrderRatingSerializer(serializers.ModelSerializer):
	seller_remark = fields.MultipleChoiceField(choices=SELLER_REMARK, required=False)
	buyer_remark = fields.MultipleChoiceField(choices=BUYER_REMARK, required=False)
	class Meta:
		model = OrderRating

class GetOrderRatingSerializer(serializers.ModelSerializer):
	#seller_remark = fields.MultipleChoiceField(choices=SELLER_REMARK)
	#buyer_remark = fields.MultipleChoiceField(choices=BUYER_REMARK)
	seller_remark = serializers.SerializerMethodField()
	buyer_remark = serializers.SerializerMethodField()

	def get_seller_remark(self, obj):
		return obj.seller_remark

	def get_buyer_remark(self, obj):
		return obj.buyer_remark

	class Meta:
		model = OrderRating

class CompanyBrandFollowSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	brand_name = serializers.CharField(source='brand.name', read_only=True)
	class Meta:
		model = CompanyBrandFollow
		'''validators = [
			serializers.UniqueTogetherValidator(
				queryset=CompanyBrandFollow.objects.all(),
				fields=('brand', 'company', 'user'),
				message="Already selected brand can not select"
			)
		]'''

class ApprovedCreditSerializer(serializers.ModelSerializer):
	class Meta:
		model = ApprovedCredit

class LoanSerializer(serializers.ModelSerializer):
	class Meta:
		model = Loan

class PaymentMethodSerializer(serializers.ModelSerializer):
	amount = serializers.SerializerMethodField()

	def get_amount(self, obj):
		total = 0

		order = self.context['request'].query_params.get('order', None)
		if order is not None:
			if obj.name.lower() == "cod":
				invObj = Invoice.objects.filter(order=order).last()
				total = max(Decimal('500.00'), invObj.total_amount*10/100)

		return total

	class Meta:
		model = PaymentMethod

class ConfigSerializer(serializers.ModelSerializer):
	class Meta:
		model = Config

class UserPlatformInfoSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def create(self, validated_data):
		print "UserPlatformInfo create"

		user = validated_data.get('user')
		print user

		upiObj, created = UserPlatformInfo.objects.get_or_create(user=user)
		upiObj.platform = validated_data.get('platform', None)
		upiObj.app_version = validated_data.get('app_version', None)
		upiObj.app_version_code = validated_data.get('app_version_code', None)
		upiObj.device_model = validated_data.get('device_model', None)
		upiObj.brand = validated_data.get('brand', None)
		upiObj.operating_system = validated_data.get('operating_system', None)
		upiObj.operating_system_version = validated_data.get('operating_system_version', None)
		upiObj.screen_width = validated_data.get('screen_width', None)
		upiObj.screen_height = validated_data.get('screen_height', None)
		upiObj.save()

		return upiObj

	class Meta:
		model = UserPlatformInfo
		extra_kwargs = {
			"user": {
				"validators": [],
			},
		}

class CategoryEavAttributeSerializer(serializers.ModelSerializer):
	attribute_name = serializers.ReadOnlyField(source='attribute.name', read_only=True)
	attribute_slug = serializers.ReadOnlyField(source='attribute.slug', read_only=True)
	attribute_datatype = serializers.ReadOnlyField(source='attribute.datatype', read_only=True)
	attribute_values = serializers.SerializerMethodField()

	def get_attribute_values(self, obj):
		#return EnumGroup.objects.filter(name=obj.attribute.name).values_list('enums__value', flat=True)
		queryset = EnumGroup.objects.filter(name=obj.attribute.name).values('enums__id', 'enums__value')
		jsonarr = []
		for data in list(queryset):
			tempjson = {}
			tempjson['id'] = data['enums__id']
			tempjson['value'] = data['enums__value']
			jsonarr.append(tempjson)
		return jsonarr

	class Meta:
		model = CategoryEavAttribute

class CompanySellsToStateSerializer(serializers.ModelSerializer):
	buyer_name = serializers.ReadOnlyField(source='intermediate_buyer.name', read_only=True)
	class Meta:
		model = CompanySellsToState

class CatalogSellerSerializer(serializers.ModelSerializer):
	selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)
	add_brand = serializers.CharField(required=False)
	single_piece_price = serializers.DecimalField(max_digits=10 , decimal_places=2, required=False)
	single_piece_price_percentage = serializers.DecimalField(max_digits=10 , decimal_places=2, required=False)

	def create(self, validated_data):
		add_brand = validated_data.pop('add_brand', None)

		#csObj = CatalogSeller.objects.create(**validated_data)
		catalog = validated_data.get('catalog')
		selling_company = validated_data.get('selling_company')
		selling_type = validated_data.get('selling_type')

		single_piece_price = validated_data.pop('single_piece_price', None)
		single_piece_price_percentage = validated_data.pop('single_piece_price_percentage', None)

		#csObj, created = CatalogSeller.objects.get_or_create(catalog=catalog, selling_company=selling_company, selling_type=selling_type)

		if CatalogSeller.objects.filter(catalog=catalog, selling_company=selling_company, selling_type=selling_type).count() > 0:
			csObj = CatalogSeller.objects.filter(catalog=catalog, selling_company=selling_company, selling_type=selling_type).first()
		else:
			try:
				csObj = CatalogSeller.objects.create(catalog=catalog, selling_company=selling_company, selling_type=selling_type)
			except Exception as e:
				csObj, created = CatalogSeller.objects.get_or_create(catalog=catalog, selling_company=selling_company, selling_type=selling_type)

		user = self.context['request'].user

		prostaObjs = ProductStatus.objects.filter(product__catalog=catalog, status="Disable", company=catalog.company)
		for prostaObj in prostaObjs:
			psObj = ProductStatus.objects.get_or_create(company=selling_company, product=prostaObj.product)
			psObj = ProductStatus.objects.filter(company=selling_company, product=prostaObj.product).first()
			psObj.user = user
			psObj.status="Disable"
			psObj.save()

		csObj.buyer_segmentation = validated_data.get('buyer_segmentation', None)
		csObj.sell_full_catalog = validated_data.get('sell_full_catalog', False)
		csObj.full_catalog_price = validated_data.get('full_catalog_price', None)
		csObj.status = "Enable"

		expiry_date = validated_data.get('expiry_date', None)
		if expiry_date is None:
			todayDate = date.today()
			expiry_date = todayDate + timedelta(days=csObj.selling_company.default_catalog_lifetime)
		csObj.expiry_date = expiry_date

		csObj.save()

		if (single_piece_price is not None and csObj.catalog.single_piece_price is None) or (single_piece_price_percentage is not None and csObj.catalog.single_piece_price_percentage is None):
			logger.info("CatalogSellerSerializer create single_piece_price = %s, single_piece_price_percentage = %s" % (single_piece_price, single_piece_price_percentage))
			csObj.catalog.single_piece_price = single_piece_price
			csObj.catalog.single_piece_price_percentage = single_piece_price_percentage
			csObj.catalog.save()
			# products = csObj.catalog.products.all()
			# for product in products:
			# 	add_price = 0
			# 	if single_piece_price:
			# 		add_price += single_piece_price
			# 	if single_piece_price_percentage:
			# 		add_price += product.public_price * single_piece_price_percentage / 100
			# 	logger.info("CatalogSellerSerializer create product.id = %s, add_price = %s" % (product.id, add_price))
			# 	product.single_piece_price = product.public_price + add_price
			# 	product.save()

		if add_brand is not None:
			print "add_brand=",add_brand
			company = user.companyuser.company

			bdObj, created = BrandDistributor.objects.get_or_create(company=company)
			bdObj.brand.add(csObj.catalog.brand)
			bdObj.save()

		return csObj

	class Meta:
		model = CatalogSeller

class CatalogSellerAdminSerializer(serializers.ModelSerializer):

	def create(self, validated_data):
		add_brand = validated_data.pop('add_brand', None)

		#csObj = CatalogSeller.objects.create(**validated_data)
		catalog = validated_data.get('catalog')
		selling_company = validated_data.get('selling_company')
		selling_type = validated_data.get('selling_type')

		#csObj, created = CatalogSeller.objects.get_or_create(catalog=catalog, selling_company=selling_company, selling_type=selling_type)

		if CatalogSeller.objects.filter(catalog=catalog, selling_company=selling_company, selling_type=selling_type).count() > 0:
			csObj = CatalogSeller.objects.filter(catalog=catalog, selling_company=selling_company, selling_type=selling_type).first()
		else:
			try:
				csObj = CatalogSeller.objects.create(catalog=catalog, selling_company=selling_company, selling_type=selling_type)
			except Exception as e:
				csObj, created = CatalogSeller.objects.get_or_create(catalog=catalog, selling_company=selling_company, selling_type=selling_type)

		csObj.buyer_segmentation = validated_data.get('buyer_segmentation', None)
		csObj.sell_full_catalog = validated_data.get('sell_full_catalog', False)
		csObj.full_catalog_price = validated_data.get('full_catalog_price', None)
		csObj.status = "Enable"

		expiry_date = validated_data.get('expiry_date', None)
		if expiry_date is None:
			todayDate = date.today()
			expiry_date = todayDate + timedelta(days=csObj.selling_company.default_catalog_lifetime)
		csObj.expiry_date = expiry_date

		csObj.save()

		bids = Brand.objects.filter(Q(manufacturer_company=csObj.selling_company) | Q(company=csObj.selling_company)).values_list('id', flat=True)
		bids = list(bids)
		tempbids = BrandDistributor.objects.filter(company=csObj.selling_company).values_list('brand', flat=True)
		bids.extend(list(tempbids))
		#print bids
		#print csObj.catalog.brand.id

		if csObj.catalog.brand.id not in bids:
			bdObj, created = BrandDistributor.objects.get_or_create(company=csObj.selling_company)
			bdObj.brand.add(csObj.catalog.brand)
			bdObj.save()

		return csObj

	class Meta:
		model = CatalogSeller

class UserReviewSerializer(serializers.ModelSerializer):
	image = VersatileImageFieldSerializer(
		sizes='promotion_image'
	)
	class Meta:
		model = UserReview

class PromotionalTagSerializer(serializers.ModelSerializer):
	image = VersatileImageFieldSerializer(
		sizes='promotion_image'
	)
	class Meta:
		model = PromotionalTag


class PreDefinedFilterSerializer(serializers.ModelSerializer):
	category = serializers.CharField(source='category.category_name', read_only=True)
	class Meta:
		model = PreDefinedFilter

class GetUserWishlistSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	catalog = GetCatalogSerializer(read_only=True)
	class Meta:
		model = UserWishlist

class UserWishlistSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	class Meta:
		model = UserWishlist

class ActionLogSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	class Meta:
		model = ActionLog

class UserSavedFilterSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	class Meta:
		model = UserSavedFilter

class AppVersionSerializer(serializers.ModelSerializer):

	class Meta:
		model = AppVersion

class DiscountRuleSerializer(serializers.ModelSerializer):
	selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)

	class Meta:
		model = DiscountRule

class GetDiscountRuleSerializer(serializers.ModelSerializer):
	selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)
	#brands = BrandSerializer(many=True)
	brands = serializers.SerializerMethodField()
	buyer_segmentations = serializers.SerializerMethodField()
	#buyer_segmentations = BuyerSegmentationSerializer(many=True)

	class Meta:
		model = DiscountRule

	def get_brands(self, obj):
		queryset = obj.brands.values('id','name').order_by('id')

		return list(queryset)

	def get_buyer_segmentations(self, obj):
		queryset = obj.buyer_segmentations.values('id','segmentation_name').order_by('id')

		return list(queryset)

class MarketingSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def create(self, validated_data):
		state = validated_data.pop('state', [])
		city = validated_data.pop('city', [])
		test_users = validated_data.pop('test_users', [])
		categories = validated_data.pop('categories', [])

		marketing = Marketing.objects.create(**validated_data)

		marketing.state = state
		marketing.city = city
		marketing.test_users = test_users
		marketing.categories = categories
		marketing.save()

		serializer = MarketingSerializer(instance=marketing, context={'request': self.context['request']})

		finaljson = serializer.data
		if "specific_no_file" in finaljson.keys():
			del finaljson["specific_no_file"]

		count_json = startMarketing(finaljson, "send")

		return marketing

	def update(self, instance, validated_data):
		state = validated_data.pop('state', [])
		city = validated_data.pop('city', [])
		test_users = validated_data.pop('test_users', [])
		categories = validated_data.pop('categories', [])

		for attr, value in validated_data.items():
			print attr, value
			setattr(instance, attr, value)

		instance.state = state
		instance.city = city
		instance.test_users = test_users
		instance.categories = categories

		instance.save()

		serializer = MarketingSerializer(instance=instance, context={'request': self.context['request']})

		finaljson = serializer.data
		if "specific_no_file" in finaljson.keys():
			del finaljson["specific_no_file"]

		count_json = startMarketing(finaljson, "send")

		return instance

	class Meta:
		model = Marketing

class CompanyCreditRatingSerializer(serializers.ModelSerializer):
	company_name = serializers.ReadOnlyField(source='company.name', read_only=True)
	total_feedback = serializers.SerializerMethodField()
	feedback_by = serializers.SerializerMethodField()

	bureau_report_rating = serializers.SerializerMethodField()
	financial_statement_rating = serializers.SerializerMethodField()

	def get_total_feedback(self, obj):
		return CreditReference.objects.filter(buying_company=obj.company).count()

	def get_feedback_by(self, obj):
		crObjs = CreditReference.objects.filter(buying_company=obj.company)[:2]
		jsonarr = []

		user = self.context['request'].user
		company = get_user_company(user)

		for crObj in crObjs:
			jsondata = {}
			jsondata['name'] =  crObj.selling_company.name
			jsondata['company_id'] = crObj.selling_company.id

			jsondata['relation_id'] = None
			buyer_table_id = Buyer.objects.filter(selling_company=crObj.selling_company, buying_company=company, status="approved").values_list('id', flat=True).first()
			if buyer_table_id:
				jsondata['relation_id'] = buyer_table_id

			jsonarr.append(jsondata)

		return jsonarr

	def get_bureau_report_rating(self, obj):
		if obj.bureau_report_rating == "Positive" and obj.rating == "Good":
			return obj.bureau_report_rating
		return None

	def get_financial_statement_rating(self, obj):
		if obj.financial_statement_rating == "Positive" and obj.rating == "Good":
			return obj.financial_statement_rating
		return None

	class Meta:
		model = CompanyCreditRating

class CreditReferenceSerializer(serializers.ModelSerializer):
	selling_company_name = serializers.ReadOnlyField(source='selling_company.name', read_only=True)
	buying_company_name = serializers.ReadOnlyField(source='buying_company.name', read_only=True)
	relation_id = serializers.SerializerMethodField()#wish selling company

	def get_relation_id(self, obj):
		user = self.context['request'].user
		company = get_user_company(user)

		buyer_table_id = Buyer.objects.filter(selling_company=obj.selling_company, buying_company=company, status="approved").values_list('id', flat=True).first()
		return buyer_table_id

	class Meta:
		model = CreditReference

class SolePropreitorshipKYCSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)

	def create(self, validated_data):
		company = validated_data.pop('company')

		spkycObj, created = SolePropreitorshipKYC.objects.get_or_create(company=company)

		for key, value in validated_data.items():
			#if value:
			#print key, value
			setattr(spkycObj, key, value)
		spkycObj.save()

		return spkycObj

	class Meta:
		model = SolePropreitorshipKYC



'''class DiscountRuleBrandSerializer(serializers.ModelSerializer):
	class Meta:
		model = DiscountRuleBrand

class DiscountRuleBuyerGroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = DiscountRuleBuyerGroup'''

class ImageTestSerializer(serializers.ModelSerializer):
	class Meta:
		model = ImageTest

class StorySerializer(serializers.ModelSerializer):
	catalogs = serializers.SerializerMethodField()

	def get_catalogs(self, obj):
		user = self.context['request'].user
		company=get_user_company(user)

		catalog_res = []

		catalogObjs = []

		urlPath = "story_"+str(obj.id)
		result = cache.get(urlPath)
		if result:
			print "if result"
			catalogObjs = result
		else:
			print "else result"
			if obj.deep_link:
				catalogObjs = get_story_deeplink(obj, user, company)
			else:
				disableCatalogIds = getDisableCatalogIds(company)
				disable_cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Disable").values_list('catalog', flat=True).distinct()
				catalogObjs = obj.catalogs.exclude(Q(id__in=disableCatalogIds) | Q(id__in=disable_cscatalogids)).order_by('-sort_order')

			cache.set(urlPath, catalogObjs, settings.CACHE_EXPIRE_TIME)

		catalog_res = catalogObjs.values_list('id', flat=True)

		return catalog_res

	class Meta:
		model = Story

class GetStorySerializer(serializers.ModelSerializer):
	catalogs_details = serializers.SerializerMethodField()
	catalogs = serializers.SerializerMethodField()

	def get_catalogs_details(self, obj):
		global catalogObjs
		user = self.context['request'].user
		company=get_user_company(user)

		catalog_res = []

		catalogObjs = []

		urlPath = "story_"+str(obj.id)
		result = cache.get(urlPath)
		if result:
			print "if result"
			catalogObjs = result
		else:
			print "else result"
			if obj.deep_link:
				catalogObjs = get_story_deeplink(obj, user, company)
			else:
				disableCatalogIds = getDisableCatalogIds(company)
				disable_cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Disable").values_list('catalog', flat=True).distinct()
				catalogObjs = obj.catalogs.exclude(Q(id__in=disableCatalogIds) | Q(id__in=disable_cscatalogids)).order_by('-sort_order')

			cache.set(urlPath, catalogObjs, settings.CACHE_EXPIRE_TIME)

		for catalogObj in catalogObjs:
			catalogdata = {}
			catalogdata['id'] = catalogObj.id
			catalogdata['title'] = catalogObj.title
			#catalogdata['is_added_to_wishlist'] =

			catalogdata['thumbnail'] = {}
			catalogdata['thumbnail']['thumbnail_small'] = catalogObj.thumbnail.thumbnail[settings.SMALL_IMAGE].url
			catalogdata['thumbnail']['thumbnail_medium'] = catalogObj.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url

			brandserializer = BrandSerializer(instance=catalogObj.brand, context={'request': self.context['request']})
			catalogdata['brand'] = brandserializer.data

			catalogdata['products']  = []

			productObjs = catalogObj.products.all()

			for productObj in productObjs:
				productdata = {}
				productdata['id'] = productObj.id
				productdata['image'] = {}
				productdata['image']['thumbnail_small'] = productObj.image.thumbnail[settings.SMALL_IMAGE].url
				productdata['image']['thumbnail_medium'] = productObj.image.thumbnail[settings.LARGE_IMAGE].url


				catalogdata['products'].append(productdata)

			catalog_res.append(catalogdata)

		return catalog_res

	def get_catalogs(self, obj):
		global catalogObjs

		return catalogObjs.values_list('id', flat=True)

	class Meta:
		model = Story

class CatalogEnquirySerializer(serializers.ModelSerializer):
	catalog_title = serializers.CharField(source='catalog.title', read_only=True)
	selling_company_name = serializers.CharField(source='selling_company.name', read_only=True)
	selling_company_chat_user = serializers.CharField(source='selling_company.chat_admin_user.username', read_only=True)
	buying_company_name = serializers.CharField(source='buying_company.name', read_only=True)
	buying_company_chat_user = serializers.CharField(source='buying_company.chat_admin_user.username', read_only=True)
	thumbnail = serializers.SerializerMethodField()
	price_range = serializers.SerializerMethodField()
	total_products = serializers.SerializerMethodField()

	def get_thumbnail(self, obj):
		return obj.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url

	def get_price_range(self, obj):
		# min_price = Product.objects.filter(catalog=obj.catalog).aggregate(Min('public_price')).get('public_price__min', 0)
		# max_price = Product.objects.filter(catalog=obj.catalog).aggregate(Max('public_price')).get('public_price__max', 0)
		product_minmax = Product.objects.filter(catalog=obj.catalog).aggregate(min_public_price=Min('public_price'), max_public_price=Max('public_price'))
		min_price = product_minmax['min_public_price']
		max_price = product_minmax['max_public_price']

		if min_price is None:
			min_price = 0
		if max_price is None:
			max_price = 0

		if min_price == max_price:
			return str(int(min_price))
		else:
			return str(int(min_price))+"-"+str(int(max_price))

	def get_total_products(self, obj):
		global currentUserCompany
		user = self.context['request'].user
		currentUserCompany = get_user_company(user)

		disableProductsIds = ProductStatus.objects.filter(product__catalog=obj.catalog, status='Disable', company=currentUserCompany).values_list('product', flat=True)
		total = obj.catalog.products.all().exclude(id__in=disableProductsIds).count()

		return total

	def create(self, validated_data):
		print "CatalogEnquiry create"
		ceObj = CatalogEnquiry.objects.create(**validated_data)

		if not Buyer.objects.filter(selling_company=ceObj.selling_company, buying_company=ceObj.buying_company).exists():
			loginUser = self.context['request'].user
			loginCompany = ceObj.buying_company

			selling_company = ceObj.selling_company
			buying_company = ceObj.buying_company

			inviteobj = Invite.objects.create(relationship_type="supplier", company=loginCompany ,user=loginUser)
			inviteeObj = Invitee.objects.create(invitee_company=selling_company.name,invitee_name=selling_company.name,country=selling_company.country,invitee_number=selling_company.phone_number, invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Supplier")

			status='supplier_pending'
			if selling_company.connections_preapproved == True:
				status='approved'

			enquiry_item_type = ceObj.item_type
			enquiry_quantity = ceObj.item_quantity
			catalog = ceObj.catalog

			group_type = GroupType.objects.get(name="Retailer")

			buyer = Buyer.objects.create(selling_company = selling_company, buying_company = loginCompany, status=status, invitee=inviteeObj, buyer_type="Enquiry", created_type="Enquiry", user=loginUser, enquiry_catalog=catalog, enquiry_item_type=enquiry_item_type, enquiry_quantity=enquiry_quantity, buying_company_name=loginCompany.name, buying_person_name=loginCompany.name, supplier_person_name=selling_company.name, group_type=group_type)

		return ceObj

	class Meta:
		model = CatalogEnquiry

class ViewFollowerSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	class Meta:
		model = ViewFollower

class UserCreditSubmissionSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def create(self, validated_data):
		logger.info("UserCreditSubmission create")
		ucsObj = UserCreditSubmission.objects.create(**validated_data)

		ccrObj, created = CompanyCreditRating.objects.get_or_create(company=ucsObj.company)

		validated_data['company'] = ccrObj.company.id

		serializer = CompanyCreditRatingSerializer(ccrObj, data=validated_data, partial=True)
		if serializer.is_valid():
			logger.info("UserCreditSubmission create is_valid")
			serializer.save()
		else:
			logger.info("UserCreditSubmission create serializer.errors = %s" % (serializer.errors))

		return ucsObj
	class Meta:
		model = UserCreditSubmission

# class CompanyCreditAprovedLine(serializers.ModelSerializer):
# 	#user = serializers.ReadOnlyField(source='user.username', read_only=True)
# 	class Meta:
# 		model = CompanyCreditAprovedLine
# 		fields = ('id', 'company', 'approved_line')

class CompanyBankDetailsSerializer(serializers.ModelSerializer):
	company = serializers.ReadOnlyField(source='company.name', read_only=True)

	class Meta:
		model = CompanyBankDetails
