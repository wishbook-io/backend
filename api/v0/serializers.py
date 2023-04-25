from django.forms import widgets
from rest_framework import serializers
from api.models import *
from api.common_functions import *

from django.contrib.auth.models import User, Group
from rest_framework import permissions
from django.conf import settings

from push_notifications.models import GCMDevice ,APNSDevice

import requests
import grequests
from django.db.models import Sum, Min, Max, Count
import datetime
#from datetime import datetime


from django.core.exceptions import ObjectDoesNotExist

import random

from versatileimagefield.serializers import VersatileImageFieldSerializer
#from rest_framework.validators import UniqueTogetherValidator

from django.db.models import Value
from django.db.models.functions import Concat

#~ from whatsapp import Client
#~ whatsappNo = '918469298998'
#~ whatsappPass = 'apvLoh1w33917g07dbaftJ/PP20='


'''client = Client(login=whatsappNo, password=whatsappPass)
whatsappStatus = client.send_message('919586773322', "ok this is new")'''

'''client = Client(login=whatsappNo, password=whatsappPass)
whatsappStatus = client.send_message('919586773322', 'Hello World')
print whatsappStatus
#whatsappStatus = client.send_media('919586773322', path='/home/tech3/Pictures/BMW-i8-2015-3.jpg')
whatsappStatus = client.send_media('919586773322', path='media/product_image/MANDIRA_PINK_SAREE.jpg')
print whatsappStatus'''

from django.core.mail import send_mail
from django.template import loader

from rest_framework.validators import UniqueTogetherValidator
import logging
logger = logging.getLogger(__name__)
#push_users = []
#peding_push_users = []

'''
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
template = get_template('received_order.txt')
context = Context({"user": "aaakaash"})
content = template.render(context)
#if not user.email:
#    raise BadHeaderError('No email address given for {0}'.format(user))
msg = EmailMessage("test django rest", content, "tech@wishbooks.io", ["tech@wishbooks.io"])
msg.send()'''


import json
import ast

import urllib

from api.v0.notifications import *
from notifier.shortcuts import send_notification
#from notifier.shortcuts import create_notification
from api.v0.notifier_backend import *

from django_q.tasks import async, result



from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from django.contrib.auth import login
from django.utils import timezone

class LoginSerializer(serializers.Serializer):
	username = serializers.CharField(required=False, allow_blank=True)
	email = serializers.EmailField(required=False, allow_blank=True)
	password = serializers.CharField(style={'input_type': 'password'}, required=False, allow_blank=True)
	
	login_for = serializers.CharField(required=False, allow_blank=True)
	otp = serializers.CharField(required=False, allow_blank=True)
	
	country = serializers.CharField(required=False)
	name_or_number = serializers.CharField(required=False)

	def validate(self, attrs):
		username = attrs.get('username')
		email = attrs.get('email')
		password = attrs.get('password')
		
		country = attrs.get('country')
		name_or_number = attrs.get('name_or_number')
		
		login_for = attrs.get('login_for')
		otp = attrs.get('otp', None)
		
		user = None
		
		print "validate login"
		
		if country is not None and name_or_number is not None:
			if name_or_number.isdigit():
				print "isdigit if"
				if UserProfile.objects.filter(country=country, phone_number=name_or_number[-10:]).exists():
					username = UserProfile.objects.filter(country=country, phone_number=name_or_number[-10:]).first().user.username
				elif User.objects.filter(username=name_or_number).exists():
					username = name_or_number
				else:
					msg = _('Enter valid phone number.')
					raise exceptions.ValidationError(msg)
			else:
				print "isdigit else"
				username = name_or_number
		'''
		if 'allauth' in settings.INSTALLED_APPS:
			from allauth.account import app_settings
			# Authentication through email
			if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
				if email and password:
					user = authenticate(email=email, password=password)
				else:
					msg = _('Must include "email" and "password".')
					raise exceptions.ValidationError(msg)
			# Authentication through username
			elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
				if username and password:
					user = authenticate(username=username, password=password)
				else:
					msg = _('Must include "username" and "password".')
					raise exceptions.ValidationError(msg)
			# Authentication through either username or email
			else:
				if email and password:
					user = authenticate(email=email, password=password)
				elif username and password:
					user = authenticate(username=username, password=password)
				else:
					msg = _('Must include either "username" or "email" and "password".')
					raise exceptions.ValidationError(msg)
		'''
		if not username and not name_or_number:
			msg = _('Must include "name" or "number" and "password".')
			raise exceptions.ValidationError(msg)
			
		if not password and not otp:
			msg = _('Must include "password" or "otp".')
			raise exceptions.ValidationError(msg)
		
		#elif
		if username and password:
			user = authenticate(username=username, password=password)
		
		elif username and otp:
			user = User.objects.filter(username=username).first()
			user.backend = 'django.contrib.auth.backends.ModelBackend'
			registrationOtp = RegistrationOTP.objects.filter(phone_number=user.userprofile.phone_number, country=user.userprofile.country).order_by('-id').first()
			if registrationOtp is not None and str(registrationOtp.otp) == otp:
				login(self.context.get('request'), user)
			
		else:
			#attrs['user'] = user
			return attrs
			msg = _('Must include "username" and "password".')
			raise exceptions.ValidationError(msg)

		# Did we get back an active user?
		if user:
			if user.userprofile.user_approval_status == "Pending":
				raise serializers.ValidationError({'Disabled':'Your request is pending by Company. To browse, please update Wishbook App'})
				
			if not user.is_active:
				#msg = _('User account is disabled.')
				#raise exceptions.ValidationError(msg)
				raise serializers.ValidationError({'username':'User account is disabled.'})
			
			if login_for == "webapp":
				if not user.is_staff and not CompanyUser.objects.filter(user=user).exists():
					raise serializers.ValidationError({'guest_user':'Guest user is not allow to login here.'})
				if not user.is_staff and not User.objects.filter(id=user.id, groups__name="administrator").exists():
					raise serializers.ValidationError({'username':'You are not allow to login here.'})
		else:
			if User.objects.filter(username=username).exists():
				raise serializers.ValidationError({"password":"Password is invalid. Try forget password."})
			else:
				raise serializers.ValidationError({"username":"This username doesn't exist. Please enter username or mobile number registered with Wishbook."})
			#msg = _('Unable to log in with provided credentials.')
			#raise exceptions.ValidationError(msg)
			#raise serializers.ValidationError({'username':'Username or Password is invalid'})

		# If required, is the email verified?
		if 'rest_auth.registration' in settings.INSTALLED_APPS:
			from allauth.account import app_settings
			if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
				email_address = user.emailaddress_set.get(email=user.email)
				if not email_address.verified:
					raise serializers.ValidationError('E-mail is not verified.')
		
		if otp is not None and otp != "":
			registrationOtp = RegistrationOTP.objects.filter(phone_number=user.userprofile.phone_number, country=user.userprofile.country).order_by('-id').first()
			print str(registrationOtp.otp)
			if str(registrationOtp.otp) == str(otp):
				registrationOtp.is_verified = "yes"
				registrationOtp.save()
				
				#UserProfile.objects.filter(user=user.id).update(phone_number_verified = "yes")
				
				user.userprofile.phone_number_verified = "yes"
				user.userprofile.save()
				print user.userprofile.phone_number_verified
				#user = User.objects.get(pk=user.id)
				print "b4 if ========"
				if CompanyUser.objects.filter(user=user).exists():
					cu = CompanyUser.objects.filter(user=user).first()
					print cu
					
					Company.objects.filter(id=cu.company.id).update(phone_number_verified = "yes")
			else:
				raise serializers.ValidationError({'otp':'Enter valid OTP.'})
		
		if UserProfile.objects.filter(user=user, phone_number_verified="no").exists():# user.userprofile.phone_number_verified == "no":
			'''rotp = RegistrationOTP.objects.filter(country = user.userprofile.country, phone_number = user.userprofile.phone_number).last()
			if rotp:
				dtime = datetime.utcnow().replace(tzinfo=None) - rotp.created_date.replace(tzinfo=None)
				if dtime > timedelta(hours=4):
					otp = random.randrange(100000, 999999, 1)
					jsonarr = {}
					jsonarr['otp'] = otp
					send_notification('otp', [user], jsonarr)
					registrationOtp = RegistrationOTP.objects.create(phone_number=user.userprofile.phone_number, otp=otp, country=user.userprofile.country)
			else:'''
			
			'''otp = random.randrange(100000, 999999, 1)
			jsonarr = {}
			jsonarr['otp'] = otp
			send_notification('otp', [user], jsonarr)
			registrationOtp = RegistrationOTP.objects.create(phone_number=user.userprofile.phone_number, otp=otp, country=user.userprofile.country)'''
			
			checkAndSendOTP(user.userprofile.phone_number, user.userprofile.country, True)
			
			raise serializers.ValidationError({'phone_number':'Phone number is not verified.'})
		
		if user.userprofile.first_login is None:
			user.userprofile.first_login = timezone.now()
			user.userprofile.save()
			
			cu = CompanyUser.objects.filter(user=user).first()
			if cu:
				company = cu.company
				
				buyerarr = []
				suppliers = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True)
				'''buyerarr.extend(suppliers)
				buyers = Buyer.objects.filter(selling_company=company, status="approved").values_list('buying_company', flat=True)
				buyerarr.extend(buyers)
				print buyerarr
				users = CompanyUser.objects.filter(company__in=buyerarr, user__groups__name="administrator").values_list('user', flat=True)
				users = list(users)
				print users
				message = "Your contact "+company.name+" has joined Wishbook."
				rno = random.randrange(100000, 999999, 1)
				image = settings.MEDIA_URL+"logo-single.png"
				
				if settings.TASK_QUEUE_METHOD == 'celery':
					notificationSend.apply_async((users, message, {"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image}), expires=datetime.now() + timedelta(days=2))
				elif settings.TASK_QUEUE_METHOD == 'djangoQ':
					task_id = async(
						'api.tasks.notificationSend',
						users, message, {"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image}
					)'''
				
				sellingCompanys = Company.objects.filter(id__in=suppliers)
				for sellingCompany in sellingCompanys:
					shareOnApproves(sellingCompany, company)
		
		user_agent = self.context.get('request').META.get('HTTP_USER_AGENT', None)
		user_agent = user_agent.lower()
		logger.info("useragent = %s"% (str(user_agent)))
		
		if 'chrome' in user_agent or 'firefox' in user_agent or 'safari' in user_agent:
			if login_for == "webapp":
				logger.info("Webapp")
				user.userprofile.last_login_platform = "Webapp"
				user.userprofile.save()
			else:
				logger.info("Lite")
				user.userprofile.last_login_platform = "Lite"
				user.userprofile.save()
		elif 'iphone' in user_agent:
			logger.info("iphone iOS")
			user.userprofile.last_login_platform = "iOS"
			user.userprofile.save()
		elif 'android' in user_agent:
			logger.info("Android")
			user.userprofile.last_login_platform = "Android"
			user.userprofile.save()
		
		attrs['user'] = user
		return attrs

try:
	from allauth.account import app_settings as allauth_settings
	from allauth.utils import (email_address_exists,
							   get_username_max_length)
	from allauth.account.adapter import get_adapter
	from allauth.account.utils import setup_user_email
except ImportError:
	raise ImportError('allauth needs to be added to INSTALLED_APPS.')
	
class RegisterSerializer(serializers.Serializer):
	username = serializers.CharField(
		max_length=get_username_max_length(),
		min_length=allauth_settings.USERNAME_MIN_LENGTH,
		required=allauth_settings.USERNAME_REQUIRED
	)
	email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
	password1 = serializers.CharField(required=True, write_only=True)
	password2 = serializers.CharField(required=True, write_only=True)
	
	
	country = serializers.CharField(required=False)
	state = serializers.CharField(required=False)
	city = serializers.CharField(required=False)
	phone_number = serializers.CharField(required=True)
	company_name = serializers.CharField(required=False, allow_blank=True)
	registration_id = serializers.CharField(required=False, allow_blank=True)
	discovery_ok = serializers.CharField(required=False)
	connections_preapproved = serializers.CharField(required=False)
	usertype = serializers.CharField(required=False, allow_blank=True)
	company = serializers.CharField(required=False, allow_blank=True)
	number_verified = serializers.CharField(required=False, allow_blank=True)
	invite_as = serializers.CharField(required=False, allow_blank=True)
	group_type = serializers.CharField(required=False, allow_blank=True)
	
	agent = serializers.CharField(required=False, allow_blank=True)
	send_user_detail = serializers.CharField(required=False, allow_blank=True)
	deputed_from = serializers.CharField(required=False, allow_blank=True)
	address = serializers.CharField(required=False, allow_blank=True)
	logistics = serializers.CharField(required=False, allow_blank=True)
	is_profile_set = serializers.BooleanField(required=False, default=True)
	invited_from = serializers.CharField(required=False, default=True)
	
	first_name = serializers.CharField(required=False, allow_blank=True)
	last_name = serializers.CharField(required=False, allow_blank=True)
	
	connect_supplier = serializers.CharField(required=False, allow_blank=True) #set broker from login company
	
	refered_by = serializers.CharField(required=False, allow_blank=True)
	meeting = serializers.CharField(required=False, allow_blank=True)
	
	

	def validate_username(self, username):
		username = get_adapter().clean_username(username)
		return username
	
	'''def validate_email(self, email):
		global validate_mail_err
		validate_mail_err = False
		print "validate_email"
		email = get_adapter().clean_email(email)
		if email == "":
			print "email NONE"
			data = self.request.data
			phone_number = data.get('phone_number')[-10:]
			if data.get('country', None):
				country = Country.objects.get(pk=data.get('country'))
			else:
				country = Country.objects.get(pk=1)
			email = str(country.phone_code).replace("+", "")+str(phone_number)+"@wishbooks.io"
			print email
		
		if allauth_settings.UNIQUE_EMAIL:
			if email and email_address_exists(email):
				validate_mail_err = True
				raise serializers.ValidationError(
					_("A user is already registered with this e-mail address."))
		return email'''

	def validate_password1(self, password):
		return get_adapter().clean_password(password)

	def validate(self, data):
		print "in validate fun"
		global userpassword
		if data['password1'] != data['password2']:
			raise serializers.ValidationError({"password":"The two password fields did't match."})
		
		userpassword = data['password2']
		
		logger.info("country id = %s, phone number = %s"% (str(data.get('country', None)), str(data['phone_number'])))
		
		country = data.get('country', Country.objects.get(pk=1))
		
		phone_number = data['phone_number']
		phone_number = phone_number.replace("+", "")
		phone_number = phone_number[-10:]
		data['phone_number'] = phone_number
		
		if int(phone_number[0]) in [0,1,2,3,4,5]:
			raise serializers.ValidationError({"phone_number":"Mobile number is not valid : "+str(phone_number)})
			
		if UserProfile.objects.filter(phone_number=phone_number, country=country).exists() or Company.objects.filter(phone_number=phone_number, country=country).exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exists():
			raise serializers.ValidationError({'phone_number':'Phone number already exists. Please choose another phone number'})
		
		email = data.get('email', "")
		email = get_adapter().clean_email(email)
		if email == "":
			print "email NONE"
			'''data = self.request.data
			phone_number = data.get('phone_number')[-10:]
			if data.get('country', None):
				country = Country.objects.get(pk=data.get('country'))
			else:
				country = Country.objects.get(pk=1)'''
			email = str(country.phone_code).replace("+", "")+str(phone_number)+"@wishbooks.io"
			print email
			data['email'] = email
		
		if allauth_settings.UNIQUE_EMAIL:
			if email and email_address_exists(email):
				validate_mail_err = True
				raise serializers.ValidationError(
					_("A user is already registered with this e-mail address."))
		
		return data

	def custom_signup(self, request, user):
		from api.v1.serializers import makeBuyerSupplierFromInvitee#, pushOnApproves
		#from api.common_functions import shareOnApproves
		global userpassword
		logger.info("in register serializer custom_signup start")
				
		data = request.data
		
		phone_number = data.get('phone_number')
		phone_number = phone_number.replace("+", "")
		phone_number = phone_number[-10:]
		
		company_name = data.get('company_name', None)
		if company_name is not None and company_name != "":
			company_name = data.get('company_name')
		
		logger.info(company_name)
		
		discovery_ok = True
		if data.get('discovery_ok', None):
			discovery_ok = data.get('discovery_ok')
		
		connections_preapproved = True
		if data.get('connections_preapproved', None):
			connections_preapproved = data.get('connections_preapproved')
		
		country = Country.objects.get(pk=1)
		if data.get('country', None):
			country = Country.objects.get(pk=data.get('country'))
		
		state = State.objects.filter(state_name="-").first()
		if data.get('state', None):
			state = State.objects.get(pk=data.get('state'))
		
		city = City.objects.filter(city_name="-").first()
		if data.get('city', None):
			city = City.objects.get(pk=data.get('city'))
		
		phone_number_verified = "yes"
		if data.get('number_verified', None):
			phone_number_verified = "no"
		
		invite_as = data.get('invite_as', None)
		group_type_invite = data.get('group_type', None)
		agent = data.get('agent', None)
		send_user_detail = data.get('send_user_detail', None)
		deputed_from = data.get('deputed_from', None)
		address = data.get('address', None)
		logistics = data.get('logistics', None)
		
		is_profile_set = data.get('is_profile_set', True)
		
		first_name = data.get('first_name', None)
		last_name = data.get('last_name', None)
		
		connect_supplier = data.get('connect_supplier', None)
		
		refered_by = data.get('refered_by', None)
		meeting = data.get('meeting', None)
		
		UserProfile.objects.filter(user=user).update(phone_number=phone_number, country=country, phone_number_verified=phone_number_verified, is_profile_set=is_profile_set) #company_name=self.cleaned_data['company_name'], 
		#user_number = UserNumber(user=user, phone_number=self.cleaned_data['phone_number'])
		#user_number.save()
		inviteeObj = Invitee.objects.filter(invitee_number=phone_number, country=country).update(status="registered", registered_user=user)
		'''if inviteeObj is not None:
			for obj in inviteeObj:
				obj.status = "registered"
				obj.registered_user = user
				obj.save()'''
		
		'''if "@wishbooks.io" in user.email:
			newemail = str(country.phone_code).replace("+", "")+user.email
			if not User.objects.filter(email=newemail).exists():
				user.email = newemail
		'''
		
		registration_id = data.get('registration_id', None)
		if registration_id is not None and registration_id != "":
			logger.info(str(registration_id))
			user_agent = request.META.get('HTTP_USER_AGENT', None)
			logger.info(str(user_agent))
			
			if 'android' in user_agent.lower():
				logger.info("android")
				gcmDeviceDelete = GCMDevice.objects.filter(registration_id=registration_id).delete()
				gcmDevice = GCMDevice.objects.create(registration_id=registration_id, active=True, user=user)
			elif 'iphone' in user_agent.lower():
				logger.info("iphone")
				apnsDeviceDelete = APNSDevice.objects.filter(registration_id=registration_id).delete()
				apnsDevice = APNSDevice.objects.create(registration_id=registration_id, active=True, user=user)
		
		usertype_group = data.get('usertype', None)
		company_id = data.get('company', None)
		
		if first_name is None:
			first_name = company_name
		
		if usertype_group is not None and company_id is not None and usertype_group != "" and company_id != "":
			logger.info(str("in register serializer company_id exists"))
			logger.info(usertype_group)
			groupObj = Group.objects.get(name=str(usertype_group))
			user.groups.add(groupObj)
			user.first_name=first_name
			user.last_name=last_name
			
			company = Company.objects.get(pk=int(company_id))
			companyUser = CompanyUser.objects.create(user=user, company=company)
			
			loginUser = self.context['request'].user
			loginCompany = None
			if loginUser.is_authenticated():
				loginCompany=loginUser.companyuser.company
			
			user.is_active = False
			if loginCompany is not None and loginCompany.id == int(company_id):
				user.is_active = True
			user.save()
			
			if loginCompany is not None and deputed_from is not None and deputed_from.lower() == 'yes':
				companyUser.deputed_from = loginCompany
				companyUser.save()
				
				user.is_active = True
				user.save()
			
			user = User.objects.get(pk=user.id)
		
		else:
			logger.info(str("in register serializer New company created"))
			groupObj = Group.objects.get(name="administrator")
			user.groups.add(groupObj)
			user.first_name=first_name
			user.last_name=last_name
			user.save()
			
			user = User.objects.get(pk=user.id)
			usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)			
			r = chat_user_registration({"userId":user.username, "deviceType":"1", "applicationId":settings.APPLOZIC_APPID, "contactNumber":usernumber})
			
			##start making company, branch and companyuser
			if company_name == None:
				company_name = user.username #phone_number
			
			addressObj = Address.objects.create(name=company_name, city=city, state=state, country=country, street_address=address, user=user)
			company = Company.objects.create(name=company_name, phone_number=phone_number, city=city, state=state, country=country, discovery_ok=discovery_ok, connections_preapproved=connections_preapproved, email=user.email, chat_admin_user=user, street_address=address, is_profile_set=is_profile_set, name_updated=is_profile_set, address=addressObj)
			category = Category.objects.all().values_list('id', flat=True)
			company.category.add(*category)
			
			if refered_by is not None:
				referedCompanyObj = getCompanyFromNumber(country, refered_by)
				if referedCompanyObj:
					company.refered_by=referedCompanyObj
					group_type = GroupType.objects.get(name="Retailer")
					#Buyer.objects.create(selling_company=referedCompanyObj, buying_company=company, )
					buyingcompany = add_buyer(referedCompanyObj.chat_admin_user, referedCompanyObj, phone_number, country, phone_number, group_type, True);
			
			company.save()
			
			if meeting is not None and meeting != "":
				meetingObj = Meeting.objects.filter(id=meeting).first()
				if meetingObj:
					meetingObj.buying_company_ref = company
					meetingObj.save()
			
			companyType = CompanyType.objects.create(company=company)
			
			branch = Branch.objects.get_or_create(company = company, name="Main Branch - "+company.name, street_address=company.street_address, city=company.city, state=company.state, phone_number=company.phone_number, country=country, address=addressObj)# ,
			
			companyUser = CompanyUser.objects.create(user=user, company=company)
			
			
			##end making company, branch and companyuser
			
			logger.info("in register serializer start default segmentation")
			##start default segmentation
			#city = City.objects.all().values_list('id', flat=True).distinct()
			#category = Category.objects.all().values_list('id', flat=True).distinct()
			#group_type = GroupType.objects.all().values_list('id', flat=True).distinct()
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="Send All",company=company)#city=city,category=category,
			#buyerSegmentation.city = city #.add(city)
			#buyerSegmentation.category = category #.add(category)
			buyerSegmentation.group_type = GroupType.objects.all().values_list('id', flat=True).distinct() #group_type
			
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Distributor",company=company)
			#buyerSegmentation.city = city
			#buyerSegmentation.category = category
			buyerSegmentation.group_type = GroupType.objects.filter(id=1).values_list('id', flat=True).distinct()
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Wholesaler",company=company)
			#buyerSegmentation.city = city
			#buyerSegmentation.category = category
			buyerSegmentation.group_type = GroupType.objects.filter(id=2).values_list('id', flat=True).distinct()
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Semi-Wholesaler",company=company)
			#buyerSegmentation.city = city
			#buyerSegmentation.category = category
			buyerSegmentation.group_type = GroupType.objects.filter(id=3).values_list('id', flat=True).distinct()
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Retailer",company=company)
			#buyerSegmentation.city = city
			#buyerSegmentation.category = category
			buyerSegmentation.group_type = GroupType.objects.filter(id=4).values_list('id', flat=True).distinct()
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Online-Retailer",company=company)
			#buyerSegmentation.city = city
			#buyerSegmentation.category = category
			buyerSegmentation.group_type = GroupType.objects.filter(id=5).values_list('id', flat=True).distinct()
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Resellers",company=company)
			#buyerSegmentation.city = city
			#buyerSegmentation.category = category
			buyerSegmentation.group_type = GroupType.objects.filter(id=8).values_list('id', flat=True).distinct()
			
			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Broker",company=company)
			#buyerSegmentation.city = city
			#buyerSegmentation.category = category
			buyerSegmentation.group_type = GroupType.objects.filter(id=9).values_list('id', flat=True).distinct()
			##end default segmentation
			
			logger.info(str("in register serializer on create applozic user"))
			'''user = User.objects.get(pk=user.id)
			usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)			
			r = chat_user_registration({"userId":user.username, "deviceType":"1", "applicationId":settings.APPLOZIC_APPID, "contactNumber":usernumber}, {'task':'create_segmentation', 'company':company.id})
			print r'''
			
			logger.info("in register serializer start make default buyer/supplier to call makeBuyerSupplierFromInvitee")
			##start make default buyer/supplier
			makeBuyerSupplierFromInvitee(company.phone_number, country, company)
			##end make default buyer/supplier
			
			##start make default warehouse
			warehouse = Warehouse.objects.create(company=company, name=company.name+" warehouse")
			##end make default warehouse
		
		if phone_number_verified.lower() == "no" and invite_as is None and group_type_invite is None and is_profile_set == True and (str(userpassword).lower() != "123456"):
			'''otp = random.randrange(100000, 999999, 1)
			user1 = User.objects.get(pk=user.id)
			jsonarr = {}
			jsonarr['otp'] = otp
			
			registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otp, country=country)
			
			#if is_profile_set:
			send_notification('otp', [user1], jsonarr)'''
			
			checkAndSendOTP(phone_number, country, is_profile_set) #is_profile_set using = False from add_buyer and add_supplier function
			
			'''else:
				print "is_profile_set false"
				smsurl = 'http://m.wishbooks.io/?m='+str(user.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(user.userprofile.country.id)
				invited_from = data.get('invited_from', 'Wishbook')
				template = smsTemplates("profile_not_set_msg")% (invited_from, smsurl)
				print template
				smsSend([usernumber], template, True)
			'''
			#logger.info(str(otpstatus))
		
		logisticsObj = None
		if logistics is not None and logistics != "":
			logisticsObj = Logistics.objects.create(name=logistics)
		
		logger.info("in register serializer invite_as = ")
		logger.info(str(invite_as))
		if invite_as is not None and group_type_invite is not None and invite_as.lower() != "none":
			loginUser = self.context['request'].user
			if loginUser.groups.filter(name="salesperson").exists() and loginUser.companyuser.deputed_to is not None:
				loginCompany = loginUser.companyuser.deputed_to
			else:
				loginCompany = loginUser.companyuser.company
			#loginCompany=loginUser.companyuser.company
			group_type = GroupType.objects.get(pk=group_type_invite)
			company = Company.objects.get(pk=company.id)
			if agent is not None:
				agent = Company.objects.get(pk=agent)
			if invite_as.lower() == "buyer":
				buying_company = company
				logger.info(str("in register serializer invite_as if buyer"))
				if not Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).exists():				
					inviteobj = Invite.objects.create(relationship_type="buyer", company=loginCompany ,user=loginUser) #, time=datetime.now()-timedelta(hours=1)
					inviteeObj = Invitee.objects.create(invitee_company=buying_company.name,invitee_name=buying_company.name,country=buying_company.country,invitee_number=buying_company.phone_number,invite=inviteobj, status="registered", invite_type="directinvitation", invitation_type="Buyer")
					
					status='buyer_pending'
					if buying_company.connections_preapproved is True:
						status='approved'
					
					logger.info(str(buying_company))
					logger.info(str(buying_company.connections_preapproved))
					logger.info(str(status))
					
					buyer = Buyer.objects.create(selling_company = loginCompany, buying_company = buying_company, status=status, group_type=group_type, invitee=inviteeObj, buying_company_name=buying_company.name, buying_person_name=buying_company.name)
					
					if agent is not None:
						buyer.broker_company=agent
						buyer.save()
					
					if logisticsObj is not None:
						buyer.preferred_logistics = logisticsObj
						buyer.save()
					
					#if status=='approved':
					#	shareOnApproves(loginCompany, buying_company)
					
			elif invite_as.lower() == "supplier":
				selling_company = company
				logger.info(str("in register serializer invite_as if supplier"))
				if not Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exists():
					inviteobj = Invite.objects.create(relationship_type="supplier", company=loginCompany ,user=loginUser) #, time=datetime.now()-timedelta(hours=1)
					inviteeObj = Invitee.objects.create(invitee_company=selling_company.name,invitee_name=selling_company.name,country=selling_company.country,invitee_number=selling_company.phone_number,invite=inviteobj, status="registered", invite_type="directinvitation", invitation_type="Supplier")
					
					status='supplier_pending'
					if selling_company.connections_preapproved is True:
						status='approved'
					
					logger.info(str(selling_company))
					logger.info(str(selling_company.connections_preapproved))
					logger.info(str(status))
						
					buyer = Buyer.objects.create(selling_company = selling_company, buying_company = loginCompany, status=status, group_type=group_type, invitee=inviteeObj, broker_company=agent, buying_company_name=loginCompany.name, buying_person_name=loginCompany.name)
					
					if agent is not None:
						buyer.broker_company=agent
						buyer.save()
					
					if logisticsObj is not None:
						buyer.preferred_logistics = logisticsObj
						buyer.save()
					
					#if status=='approved':
					#	shareOnApproves(selling_company, loginCompany)
		
		if connect_supplier is not None:
			loginUser = self.context['request'].user
			if loginUser.groups.filter(name="salesperson").exists() and loginUser.companyuser.deputed_to is not None:
				loginCompany = loginUser.companyuser.deputed_to
			else:
				loginCompany = loginUser.companyuser.company
			connect_supplier = Company.objects.get(pk=int(connect_supplier))
			company = Company.objects.get(pk=company.id)
			
			inviteobj = Invite.objects.create(relationship_type="supplier", company=company ,user=user) #, time=datetime.now()-timedelta(hours=1)
			inviteeObj = Invitee.objects.create(invitee_company=connect_supplier.name,invitee_name=connect_supplier.name,country=connect_supplier.country,invitee_number=connect_supplier.phone_number,invite=inviteobj, status="registered", invite_type="directinvitation", invitation_type="Supplier")
			
			status='supplier_pending'
			if connect_supplier.connections_preapproved is True:
				status='approved'
			
			logger.info(str(connect_supplier))
			logger.info(str(connect_supplier.connections_preapproved))
			logger.info(str(status))
			
			#group_type = GroupType.objects.filter(name="Resellers").first()
			group_type = GroupType.objects.get(name="Retailer")
				
			buyer = Buyer.objects.create(selling_company = connect_supplier, buying_company = company, status=status, group_type=group_type, invitee=inviteeObj, broker_company=loginCompany, buying_company_name=company.name, buying_person_name=company.name)
			
			if logisticsObj is not None:
				buyer.preferred_logistics = logisticsObj
				buyer.save()
			
		
		'''if send_user_detail is not None and send_user_detail == "yes":
			print " in send_user_detail"
			user = User.objects.get(pk=user.id)
			usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
			template = smsTemplates("send_user_detail")% (user.userprofile.phone_number, data.get('password1'))
			smsSend([usernumber], template, True)
			#smsSendICubes.apply_async(([usernumber], template, True), expires=datetime.now() + timedelta(days=2))
		'''
		
		if (phone_number_verified.lower() == "no" and invite_as is None and group_type_invite is None and is_profile_set == False) or (send_user_detail is not None and send_user_detail.lower() == "yes") or (str(userpassword).lower() == "123456"):
			logger.info(str("in register serializer send user_detail sms start"))
			otp = random.randrange(100000, 999999, 1)
			registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otp, country=country)
			smsurl = 'https://app.wishbooks.io/?m='+str(user.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(user.userprofile.country.id)
			smsurl = urlShortener(smsurl)
			invited_from = data.get('invited_from', 'Wishbook')
			#template = smsTemplates("user_detail")% (invited_from, smsurl, user.userprofile.phone_number, userpassword)
			template = smsTemplates("user_detail_3")% (invited_from, smsurl)
			#template = smsTemplates("user_detail_2")% (invited_from)
			logger.info(str(template))
			usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
			
			smsSend([usernumber], template, True, True)
			
			#checkAndSendOTP(user.userprofile.phone_number, country)
			sendOTP(usernumber, otp, is_profile_set) #is_profile_set using = False from add_buyer and add_supplier function
			logger.info(str("in register serializer send user_detail sms end"))
		
		pass

	def get_cleaned_data(self):
		return {
			'username': self.validated_data.get('username', ''),
			'password1': self.validated_data.get('password1', ''),
			'email': self.validated_data.get('email', '')
		}

	def save(self, request):
		adapter = get_adapter()
		user = adapter.new_user(request)
		self.cleaned_data = self.get_cleaned_data()
		adapter.save_user(request, user, self)
		self.custom_signup(request, user)
		#setup_user_email(request, user, [])
		return user


class BuyerSerializer(serializers.ModelSerializer):
	selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)#add user on create
		
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
		
		instance.status = validated_data.get('status', instance.status)
		instance.fix_amount = validated_data.get('fix_amount', instance.fix_amount)
		instance.percentage_amount = validated_data.get('percentage_amount', instance.percentage_amount)
		
		instance.group_type = validated_data.get('group_type', instance.group_type)
		
		instance.payment_duration = validated_data.get('payment_duration', instance.payment_duration)
		instance.discount = validated_data.get('discount', instance.discount)
		instance.cash_discount = validated_data.get('cash_discount', instance.cash_discount)
		instance.credit_limit = validated_data.get('credit_limit', instance.credit_limit)
		
		instance.broker_company = validated_data.get('broker_company', instance.broker_company)
		
		if instance.status == "rejected":
			user=self.context['request'].user
			company = user.companyuser.company
			if instance.selling_company == company:
				instance.supplier_approval = False
			elif instance.buying_company == company:
				instance.buyer_approval = False
				
		instance.save()
		
		if newStatus is not None and oldStatus != newStatus and newStatus == "approved":
			#print "pushOnApproves"
			#pushOnApproves(instance.selling_company, instance.buying_company)
			print "shareOnApproves"
			shareOnApproves(instance.selling_company, instance.buying_company)
		
		return instance
	
	def validate(self, data):
		status = data.get('status', None)
		if status is not None and status == "approved" and self.instance is not None:
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
