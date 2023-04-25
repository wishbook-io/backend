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


projectpath = os.getcwd()
print "projectpath =", projectpath

#reader = csv.DictReader(open(os.path.join("/home/tech3/b2b/django-user/projectname/internal_scripts/", "refer.csv"), 'rb'))
reader = csv.DictReader(open(os.path.join(projectpath+"/internal_scripts/", "refer_final_jay.csv"), 'rb'))
print "reader =",reader


errorfilename = 'usercontact_onwishbook_'+str(randomString())+'.csv'
errorfilepath = os.path.join(projectpath+"/internal_scripts/", errorfilename)
fieldnames = ['number', 'message', 'error']




ucrawqueryset = UserContact.objects.raw("select id, name, number from api_usercontact where name REGEXP 'retail|shop|Vastra|Saree|saari|saaree|kurti|lehenga|Lahenga|lehnga|lahnga|blouse|suit|agent|adhat|dalal|fashion|fasion|fashon|feshon|feshion|ethnic|ethanic|ethnik|textile|txtl|textl|market|markt|Online|resaler|Reseller|reseler|agenc' and number > 7486874689 group by number order by number");
#print ucrawqueryset
#print ucrawqueryset.query



countryObj = Country.objects.get(pk=1)
country = Country.objects.get(pk=1)


contactNoList = []
with open(errorfilepath, "wb") as out_file:
	writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
	writer.writeheader()
	
	for ucrawquery in ucrawqueryset:
		original_number = ""
		message = ""
		try:
			error = message = ""
			number = ucrawquery.number
			original_number = ucrawquery.number
			number = re.sub('[^0-9+]', '',number)
			number = str(number)[-10:]
			name = ucrawquery.name
			
			logger.info("number = %s, id = %s"% (str(number), str(ucrawquery.id)))
			
			if len(str(number)) < 5:
				error = "phone number is not valid. integer length should be more than 5"
				writer.writerow({"number":number, "message":message, "error":error})
				continue
				
			if int(number[0]) in [0,1,2,3,4,5]:
				error = "phone number is not valid. should start from 6-9"
				writer.writerow({"number":number, "message":message, "error":error})
				continue
			
			contactNoList.append(number)
			
			compnumber = getCompanyNumberFromNumber(countryObj, number)
			country = compnumber[0]
			phone_number = compnumber[1]
			
			if not Company.objects.filter(country=country, phone_number=phone_number).exists():
				
				
				email = str(country.phone_code).replace("+", "")+str(phone_number)+"@wishbooks.io"
				
				username = str(country.phone_code)+str(phone_number)
				username = username.replace("+", "")

				user = User.objects.create(username=username, email=email)
				user.save()
				UserProfile.objects.filter(user=user).update(phone_number=phone_number, country=country, is_profile_set=False)
				
				user = User.objects.get(pk=user.id)

				usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
				r = chat_user_registration({"userId":user.username, "deviceType":"1", "applicationId":settings.APPLOZIC_APPID, "contactNumber":usernumber})
				
				groupObj = Group.objects.get(name="administrator")
				user.groups.add(groupObj)
				user.save()
				
				state = State.objects.filter(state_name="-").first()
				city = City.objects.filter(city_name="-").first()
				company_name = name
				
				addressObj = Address.objects.create(name=company_name, city=city, state=state, country=country, user=user)
				company = Company.objects.create(name=company_name, phone_number=phone_number, city=city, state=state, country=country, chat_admin_user=user, address=addressObj, is_profile_set=False, email=email)
				category = Category.objects.all().values_list('id', flat=True)
				company.category.add(*category)
				company.save()

				companyUser = CompanyUser.objects.create(user=user, company=company)
				companyType = CompanyType.objects.create(company=company)

				branch = Branch.objects.get_or_create(company = company, name="Main Branch - "+company.name, street_address=company.street_address, city=company.city, state=company.state, phone_number=company.phone_number, country=country, address=addressObj)
				warehouse = Warehouse.objects.create(company=company, name=company.name+" warehouse")


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
				
				
				otp = random.randrange(100000, 999999, 1)
				registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otp, country=country)
				smsurl = 'https://app.wishbooks.io/?m='+str(company.phone_number)+'&o='+str(otp)+'&c='+str(company.country.id)
				smsurl = urlShortener(smsurl)
				
				
				
				
				userids = UserContact.objects.filter(number=original_number).values_list('user', flat=True)
				#print userids
				company_names = CompanyUser.objects.filter(user__in=userids, company__is_profile_set=True).values_list('company__name', flat=True)
				#print company_names
				
				final_number = str(country.phone_code)+str(phone_number)
				
				if len(company_names) > 0:
					userObj = CompanyUser.objects.filter(user__in=userids, company__is_profile_set=True).last()
					#print userObj.user
					print userObj.user.userprofile.language.name
					
					company_names_str = ", ".join(company_names[:2])
					namelen = len(company_names) - 2
					
					if userObj.user.userprofile.language.name == "Hindi":
						if namelen > 0:
							company_names_str = company_names_str+" aur "+str(namelen)+" vyapari"
						company_names_str = company_names_str.encode('utf-8')
						message = company_names_str+" apna textile business badha rahe hai Wishbook B2B App se. Aap bhi judiye! Download kijiye - Android - www.wishbooks.io/android, iOS - www.wishbooks.io/ios, Mobile browser - "+smsurl
						print message
						writer.writerow({"number":number, "message":message, "error":error})
						smsSend([final_number], message, True)
						
					else:
						if namelen > 0:
							company_names_str = company_names_str+" & "+str(namelen)+" others"
						company_names_str = company_names_str.encode('utf-8')
						message = company_names_str+" are on Wishbook B2B app to grow their textile business. Why don't you join? Download Wishbook - Android - www.wishbooks.io/android, iOS - www.wishbooks.io/ios, Also mobile browser - "+smsurl
						writer.writerow({"number":number, "message":message, "error":error})
						print message
						smsSend([final_number], message, True)
					
				else:
					userObj = UserContact.objects.filter(number=original_number).last()
					#print userObj.user
					print userObj.user.userprofile.language.name
					
					if userObj.user.userprofile.language.name == "Hindi":
						print "is_profile_set = false, number =",number
						message = "apna textile business badhane ke liye Wishbook B2B App se judiye!. Download kijiye - Android - www.wishbooks.io/android, iOS - www.wishbooks.io/ios, Mobile browser - "+smsurl
						writer.writerow({"number":number, "message":message, "error":error})
						print message
						smsSend([final_number], message, True)
					else:
						print "is_profile_set = false, number =",number
						message = "Use Wishbook B2B app to grow your textile business. Download Wishbook - Android - www.wishbooks.io/android, iOS - www.wishbooks.io/ios, Also Mobile browser - "+smsurl
						writer.writerow({"number":number, "message":message, "error":error})
						print message
						smsSend([final_number], message, True)
		except Exception as e:
			error = str(e)
			writer.writerow({"number":original_number, "message":message, "error":error})

print "csv file name ===========", errorfilename

