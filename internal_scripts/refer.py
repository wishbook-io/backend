from django.contrib.auth.models import User, Group
from api.models import *
from api.v1.serializers import *
from api.v0.serializers import RegisterSerializer

from api.common_functions import getCompanyNumberFromNumber

import string
import random
import os
from decimal import Decimal
import csv

from api.v1.views import randomString

import dateutil
from django.conf import settings

#~ import json
#~ import os
#~ import glob

#~ f = open(os.path.join("/home/tech3/b2b/django-user/projectname/internal_scripts/", "refer.csv"), "r")

projectpath = os.getcwd()
print "projectpath =", projectpath

#reader = csv.DictReader(open(os.path.join("/home/tech3/b2b/django-user/projectname/internal_scripts/", "refer.csv"), 'rb'))
reader = csv.DictReader(open(os.path.join(projectpath+"/internal_scripts/", "refer_final_jay.csv"), 'rb'))
print "reader =",reader


errorfilename = 'refer_error_'+str(randomString())+'.csv'
#errorfilepath = os.path.join("/home/tech3/b2b/django-user/projectname/internal_scripts/", errorfilename)
errorfilepath = os.path.join(projectpath+"/internal_scripts/", errorfilename)
fieldnames = ['refer_id', 'name', 'photo', 'shop_number', 'market_name', 'street_address', 'city', 'state', 'language', 'contact_name', 'phone_number', 'product_min_price', 'product_max_price', 'est_year', 'auto_approve_buyer_request', 'gst_number', 'shop_ownership', 'created_date', 'error']
#fieldnames = ['refer_id']
#print "errorfilename =", errorfilename
with open(errorfilepath, "wb") as out_file:
	writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
	writer.writeheader()
	
	
	for line in reader:
		print "CSV LINE JSON =",line
		
		phone_number = re.sub('[^0-9+]', '',line['phone_number'])
		phone_number = str(phone_number)[-10:]
		
		print "refer_id ==",line['refer_id']
		print "phone_number ==",phone_number
		
		if len(str(phone_number)) < 5:
			line["error"] = "phone number is not valid. integer length should be more than 5"
			writer.writerow(line)
			continue
			
		if int(phone_number[0]) in [0,1,2,3,4,5]:
			line["error"] = "phone number is not valid. should start from 6-9"
			writer.writerow(line)
			continue
		
		name=line['name']
		name=name.encode('utf-8').strip()
		name=str(name).rstrip('\n')
		
		#country = Country.objects.get(phone_code="+"+str(line['country_code']))
		country = Country.objects.get(pk=1)
		
		state = line['state']
		city = line['city']
		street_address = line['street_address']
		
		
		refer_id = line['refer_id']
		#landline_numbers = line['landline_numbers']
		shop_number = line['shop_number']
		market_name = line['market_name']
		est_year = line['est_year']
		shop_ownership = line['shop_ownership']
		product_min_price = line['product_min_price']
		product_max_price = line['product_max_price']
		language = line['language']
		auto_approve_buyer_request = line['auto_approve_buyer_request']
		#refer_userinvitation_id = line['refer_userinvitation_id'] #not use
		photo = line['photo']
		contact_name = line['contact_name']
		gst_number = line['gst_number']
		
		created_date = line['created_date']

		try:
			created_date = dateutil.parser.parse(created_date)
		except Exception:
			created_date = datetime.now()
			pass
		print "created_date ======",created_date
		
		if est_year == 0 or est_year == "":
			est_year = None
		else:
			est_year = int(est_year)
		
		if product_min_price == 0 or product_min_price == "":
			product_min_price = None
		else:
			product_min_price = Decimal(product_min_price)
		
		if product_max_price == 0 or product_max_price == "":
			product_max_price = None
		else:
			product_max_price = Decimal(product_max_price)
		
		if language:
			if int(language)==1:
				language = Language.objects.get(pk=1)
			else:
				language = Language.objects.get(pk=2)
		else:
			language = Language.objects.get(pk=2)
		
		connections_preapproved = True
		#if int(auto_approve_buyer_request) == 0:
		#	connections_preapproved = False
		
		shop_ownership = "Owned"
		if shop_ownership.lower() == "n":
			shop_ownership = "Rented"
		
		if state:
			state = State.objects.filter(state_name=state).first()
		if state is None or state == "":
			state = State.objects.filter(state_name="-").first()
		
		if city:
			city = City.objects.filter(city_name=city, state=state).first()
		if city is None or city == "":
			city = City.objects.filter(city_name="-").first()
		
		
		compnumber = getCompanyNumberFromNumber(country, phone_number)
		#print compnumber
		country = compnumber[0]
		phone_number = compnumber[1]
		
			
		if not Company.objects.filter(country=country, phone_number=phone_number).exists():
			print "if cond."
			email = str(country.phone_code).replace("+", "")+str(phone_number)+"@wishbooks.io"
			
			username = str(country.phone_code)+str(phone_number)
			username = username.replace("+", "")
			user = None
			try:
				user = User.objects.create(username=username, email=email, date_joined=created_date)
			except Exception as e:
				logger.info(str(e))
				line["error"] = str(e)
				writer.writerow(line)
				continue
				pass
			UserProfile.objects.filter(user=user).update(phone_number=phone_number, country=country, is_profile_set=True, language=language, phone_number_verified='yes')
			
			groupObj = Group.objects.get(name="administrator")
			user.groups.add(groupObj)
			if contact_name is not None and contact_name != "":
				print "if user.first_name = contact_name"
				user.first_name = contact_name
			else:
				print "else user.first_name = name"
				user.first_name = name
			user.save()
			
			user = User.objects.get(pk=user.id)
			
			usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)			
			r = chat_user_registration({"userId":user.username, "deviceType":"1", "applicationId":settings.APPLOZIC_APPID, "contactNumber":usernumber})
			
			addressObj = Address.objects.create(name=name, city=city, state=state, country=country, user=user, street_address=street_address, shop_number=shop_number, market_name=market_name)
			company = Company.objects.create(name=name, phone_number=phone_number, city=city, state=state, country=country, chat_admin_user=user, address=addressObj, is_profile_set=False, street_address=street_address, refer_id=refer_id, connections_preapproved=connections_preapproved, email=email, company_type_filled=True, phone_number_verified='yes') #landline_numbers=landline_numbers, 
			#in company details is_profile_set = True because of state and city from model save() overight :::set False if refer_id exists.
			category = Category.objects.all().values_list('id', flat=True)
			company.category.add(*category)
			company.save()
			
			companyUser = CompanyUser.objects.create(user=user, company=company)
			companyType = CompanyType.objects.create(company=company, retailer=True)
			
			branch = Branch.objects.get_or_create(company = company, name="Main Branch - "+company.name, street_address=company.street_address, city=company.city, state=company.state, phone_number=company.phone_number, country=country, address=addressObj)
			warehouse = Warehouse.objects.create(company=company, name=company.name+" warehouse")
			
			AdvancedProfile.objects.create(company=company, est_year=est_year, shop_ownership=shop_ownership, product_min_price=product_min_price, product_max_price=product_max_price)
			
			if gst_number is not None and gst_number != "":
				CompanyKycTaxation.objects.create(company=company, gstin=gst_number)

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="Send All",company=company)
			buyerSegmentation.group_type = GroupType.objects.all().values_list('id', flat=True).distinct()

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Distributor",company=company)
			buyerSegmentation.group_type = GroupType.objects.filter(id=1).values_list('id', flat=True).distinct()

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Wholesaler",company=company)
			buyerSegmentation.group_type = GroupType.objects.filter(id=2).values_list('id', flat=True).distinct()

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Semi-Wholesaler",company=company)
			buyerSegmentation.group_type = GroupType.objects.filter(id=3).values_list('id', flat=True).distinct()

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Retailer",company=company)
			buyerSegmentation.group_type = GroupType.objects.filter(id=4).values_list('id', flat=True).distinct()

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Online-Retailer",company=company)
			buyerSegmentation.group_type = GroupType.objects.filter(id=5).values_list('id', flat=True).distinct()

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Resellers",company=company)
			buyerSegmentation.group_type = GroupType.objects.filter(id=8).values_list('id', flat=True).distinct()

			buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Broker",company=company)
			buyerSegmentation.group_type = GroupType.objects.filter(id=9).values_list('id', flat=True).distinct()
			
			
			#otp = random.randrange(100000, 999999, 1)
			#registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otp, country=country)
			#add dif msg for new registration
			#sendOTP(usernumber, otp, True)
		
		else:
			print "else cond."
			
			company = getCompanyFromNumber(country, phone_number)
			
			print "company.id=",company.id
			print "company is_profile_set=",company.is_profile_set
			
			if company.is_profile_set:
				#is_profile_set-true
				company.refer_id = refer_id
				#company.landline_numbers = landline_numbers
				company.connections_preapproved = connections_preapproved
				company.save()
				
				company.address.shop_number = shop_number
				company.address.market_name = market_name
				company.address.save()
				
				apObj, created = AdvancedProfile.objects.get_or_create(company=company)
				apObj.est_year=est_year
				apObj.shop_ownership=shop_ownership
				apObj.product_min_price=product_min_price
				apObj.product_max_price=product_max_price
				apObj.save()
				
				if gst_number is not None and gst_number != "":
					kycObj, created = CompanyKycTaxation.objects.get_or_create(company=company)
					if kycObj.gstin is None:
						kycObj.gstin=gst_number
						kycObj.save()
				
				users = CompanyUser.objects.filter(company=company).values_list('user', flat=True)
				UserProfile.objects.filter(user__in=users).update(language=language)
				
			else:
				#is_profile_set-false
				company.refer_id = refer_id
				#company.landline_numbers = landline_numbers
				company.connections_preapproved = connections_preapproved
				company.state = state
				company.city = city
				company.street_address = street_address
				company.name = name
				company.save()
				
				company.address.shop_number = shop_number
				company.address.market_name = market_name
				company.address.state = state
				company.address.city = city
				company.address.street_address = street_address
				company.address.name = name
				company.address.save()
				
				Branch.objects.filter(company=company).update(state=state, city=city, street_address=street_address)
				
				apObj, created = AdvancedProfile.objects.get_or_create(company=company)
				apObj.est_year=est_year
				apObj.shop_ownership=shop_ownership
				apObj.product_min_price=product_min_price
				apObj.product_max_price=product_max_price
				apObj.save()
				
				if gst_number is not None and gst_number != "":
					kycObj, created = CompanyKycTaxation.objects.get_or_create(company=company)
					kycObj.gstin=gst_number
					kycObj.save()
				
				users = CompanyUser.objects.filter(company=company).values_list('user', flat=True)
				UserProfile.objects.filter(user__in=users).update(language=language)
				#User.objects.filter(id__in=users).update(first_name=name)
				if contact_name is not None and contact_name != "":
					print "if user.first_name = contact_name"
					User.objects.filter(id__in=users).update(first_name=contact_name)
				else:
					print "else user.first_name = name"
					User.objects.filter(id__in=users).update(first_name=name)

print "errorfilename ===========", errorfilename
