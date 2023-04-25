from django.contrib.auth.models import User, Group
from api.models import *
from api.v1.serializers import *
from api.common_functions import *

import random


companies = Company.objects.filter(refer_id__isnull=False)
print companies.count()


for company in companies:
	print company.id
	
	message = "Refer App ab jud gaya hai Wishbook B2B App se! 200+ jabardast brands ke catalogs dekhne aur khareedne ke liye download Wishbook - Android www.wishbooks.io/android , iOS www.wishbooks.io/ios ,Also mobile browser %s Call/WhatsApp - 8469218980"
	otp = random.randrange(100000, 999999, 1)
	registrationOtp = RegistrationOTP.objects.create(phone_number=company.phone_number, otp=otp, country=company.country)
	smsurl = 'https://app.wishbooks.io/?m='+str(company.phone_number)+'&o='+str(otp)+'&c='+str(company.country.id)
	smsurl = urlShortener(smsurl)
	
	template = message % (smsurl)
	usernumber = str(company.country.phone_code)+str(company.phone_number)
	print template
	smsSend([usernumber], template, True, True)
	
	

