from django.conf import settings
import json
import requests

from api.models import *
from django.contrib.auth.models import User, Group

from api.v1.serializers import *
from api.v0.serializers import RegisterSerializer

inviteeObjs = Invitee.objects.filter(status='invited').order_by('id')

for invitee in inviteeObjs:
	print invitee.id
	country = invitee.country
	supplier_number = invitee.invitee_number
	companyName = invitee.invite.company.name
	
	
	print supplier_number
	
	if UserProfile.objects.filter(country=country, phone_number=supplier_number).exists():
		userprofile = UserProfile.objects.filter(country=country, phone_number=supplier_number).first()
		if CompanyUser.objects.filter(user=userprofile.user).exists():
			supplier_number=userprofile.user.companyuser.company.phone_number
	elif Company.objects.filter(country=country, phone_number=supplier_number).exists():
		print supplier_number
	elif CompanyPhoneAlias.objects.filter(country=country, alias_number=supplier_number, status="Approved").exists():
		companyalias = CompanyPhoneAlias.objects.filter(country=country, alias_number=supplier_number, status="Approved").first()
		supplier_number = companyalias.company.phone_number
	elif UnregisteredPhoneAlias.objects.filter(alias_country=country,alias_number=supplier_number).exists():
		unregister = UnregisteredPhoneAlias.objects.filter(alias_country=country,alias_number=supplier_number).first()
		supplier_number = unregister.master_number
		country = unregister.master_country
	
	if not Company.objects.filter(country=country, phone_number=supplier_number).exists():
		otpno = random.randrange(100000, 999999, 1)
		username = str(country.phone_code)+str(supplier_number)
		username = username.replace("+", "")
		supplier_name = username
		if invitee.invitee_company is not None and len(invitee.invitee_company) > 1:
			supplier_name = invitee.invitee_company
		elif invitee.invitee_name is not None and len(invitee.invitee_name) > 1:
			supplier_name = invitee.invitee_name
		#print username
		data = {"username":username, "password1": otpno, "password2": otpno, "phone_number":supplier_number, "country":country.id, "email":str(supplier_number)+"@wishbooks.io", "number_verified":"no", "is_profile_set":False, "company_name":supplier_name, "invited_from":companyName}
		register = RegisterSerializer(data=data)
		if register.is_valid():
			print "save register is_valid"
			try:
				registerObj = register.save(register)
				print registerObj
			except Exception as e:
				logger.info("registration error")
				logger.info(str(e))
				pass
	
