'''from api.models import *
from django.contrib.auth.models import User, Group

Company.objects.filter(id=9012)

buyers = Buyer.objects.filter(selling_company=9012).values_list('buying_company', flat=True)
CompanyUser.objects.filter(company__in=buyers)'''

from datetime import date, datetime, timedelta
from api.models import *
from django.db.models.functions import Concat
import random
from api.common_functions import smsSend, smsTemplates

logger.info("in ")
users = Push_User.objects.filter(push=5457).values_list('user', flat=True).distinct().order_by('user')#5457
users = list(users)

logger.info("users")
logger.info(str(users))

unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()

for user in users:
	logger.info(str(user))
	catalogtitles = Push_User.objects.filter(user=user, catalog__isnull=False).values_list('selling_company__name', flat=True).distinct()#catalog__title
	catalogtitles = ', '.join(catalogtitles)
	
	phone_number = UserProfile.objects.filter(user=user).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
	phone_number = list(set(phone_number) - set(unsubscribed_number))
	
	userObj = User.objects.get(pk=user)
	
	otp = None
	if userObj.userprofile.is_profile_set == False:
		print "if userObj.userprofile.is_profile_set == False"
		otpObj = RegistrationOTP.objects.filter(phone_number=userObj.userprofile.phone_number, country=userObj.userprofile.country).order_by('-created_date').first()
		if otpObj:
			print "if RegistrationOTP obj available"
			otp = otpObj.otp
	if otp is None:
		print "if otp is None"
		otp = random.randrange(100000, 999999, 1)
		registrationOtp = RegistrationOTP.objects.create(phone_number=userObj.userprofile.phone_number, otp=otp, country=userObj.userprofile.country)
	
	smsurl = 'http://m.wishbooks.io/?m='+str(userObj.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(userObj.userprofile.country.id)+'&t=page&id=received'
	logger.info(str(smsurl))
	template = smsTemplates("daily_1_share_sms")% (catalogtitles, smsurl)
	print phone_number
	print template
	smsSend(phone_number, template)
	#sending sms here
