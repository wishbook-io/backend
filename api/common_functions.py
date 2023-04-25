import requests
import grequests

import urllib

import logging
logger = logging.getLogger(__name__)

from django.core.mail import send_mail



from django.db.models import Sum

from datetime import datetime, date, time, timedelta



#from django.db import models
from django.contrib.auth.models import User, Group
from api.models import *

import pycurl, json
from cStringIO import StringIO

from django_q.tasks import async, result
from django_q.tasks import schedule
from django_q.models import Schedule


from django.conf import settings
import json

from urlshortner.models import Link

from django_q.brokers import get_broker
# set up a broker instance for better performance
priority_broker = get_broker('priority')

from django.db.models import Sum, Min, Max, Count

def isScheduledTime():
	x = datetime.now()
	#return True
	start = time(21, 0, 0) #9 PM
	end = time(9, 0, 0) #9 AM

	today = date.today()
	start = datetime.combine(today, start)
	end = datetime.combine(today, end)

	#~ print "now", x
	#~ print "start", start
	#~ print "end", end

	#~ print "====="

	if end <= start:
		end += timedelta(days=1) # tomorrow!
	if x <= start:
		x += timedelta(days=1) # tomorrow!

	#~ print "new now", x
	#~ print "new start", start
	#~ print "new end", end

	status = start <= x <= end
	print "isScheduledTime status =",status

	return status

def getScheduledTime():
	x = datetime.now()
	#return x + timedelta(minutes=1)
	print "getScheduledTime now=",x

	if x.time() > time(12, 0, 0): #At 12noon
		newdatetime = x.replace(hour=11, minute=0)+timedelta(days=1) #11 AM
	else:
		newdatetime = x.replace(hour=11, minute=0) #11 AM
	return newdatetime


def smsTrasaction(provider, sent):
	logger.info("smsTrasaction provider = %s, sent = %s" % (provider, sent))
	from api.models import SmsTransaction
	trasaction, created = SmsTransaction.objects.get_or_create(created_at = date.today(), provider=provider)
	trasaction.total_sent += sent
	trasaction.save()

def smsUrl():
	url = 'http://www.myvaluefirst.com/smpp/sendsms?username=trivenihttp&password=triv@123&from=WISHBK&dlr-mask=WISHBK&to=%s&text='
	return url

#def urlShortener(url, wait_sec=2):
def urlShortener(url):
	logger.info("in urlShortener")
	link_id = Link(url=url)
	short_link = Link.shorten(link_id)

	logger.info("short_link = %s" % (short_link))
	url = "https://app.wishbooks.io/s/" + short_link
	logger.info("url = %s " % (url))

	return url

	'''r = None
	try:
		google_url = "https://www.googleapis.com/urlshortener/v1/url?key="+str(settings.GOOGLE_API_KEY)
		jsonarr = {"longUrl": url}

		r = requests.post(google_url, data=json.dumps(jsonarr), headers={"content-type": "application/json"})
		logger.info(str(r))
		logger.info(str(r.text))

		r = r.json()
		logger.info(str(r))

		shortener = r["id"]
		return shortener
	except Exception as e:
		logger.info("urlShortener Exception e = %s"% (str(e)))
		mail_status = send_mail("urlShortener Google", "Error = "+str(e)+" & url = "+str(url)+" & r = "+str(r), "tech@wishbook.io", ["tech@wishbook.io"])
		return url
	'''

def smsTemplates(smsTemplateName):
	if smsTemplateName == "sendInvite":
		text = '%s has invited you to register & install the Wishbook Catalog application & jump onto a new better way to do business! Download on Android on www.wishbooks.io/android & iOS on www.wishbooks.io/ios. Know more on http://www.wishbooks.io/'
		return text

	elif smsTemplateName == "sendOTP":
		text = 'Dear Customer, One Time Password (OTP) for Wishbook is %s. Do NOT share it with anyone'
		return text

	elif smsTemplateName == "requestNotification_supplier":
		text = '%s ne aapko Wishbook pe add kiya hai. Apko apna catalog share/sell ke liye link se Approve kare %s'
		return text

	elif smsTemplateName == "requestNotification_default_supplier_approved":
		text = '%s ne aapko Wishbook pe add kiya hai. View Buyer details by clicking on %s'
		return text

	elif smsTemplateName == "requestNotification_supplierenquiry":
		text = 'Congratulations! %s ne aapke catalog %s ke baare me Enquiry bheji hai. Ye ek nayi relationship aur order ki taraf pahal hai. Wishbook se is Enquiry ko approve kare.'
		return text

	elif smsTemplateName == "requestNotification_buyer":
		text = '%s ne aapko Wishbook pe add kiya hai. Uske latest catalogs view/share/purchase karne ke liye link se Approve kare %s'
		return text

	elif smsTemplateName == "requestNotification_default_buyer_approved":
		text = '%s ne aapko Wishbook pe add kiya hai. View Supplier details by clicking on %s'
		return text

	elif smsTemplateName == "requestNotification_Relationship_buyersupplier_status":
		text = '%s has changed relationship status to %s'
		return text

	elif smsTemplateName == "requestNotification_approve_reject_buyersupplier_status":
		text = 'Aapki enquiry %s ne Approve kar di hai. Abhi Wishbook pe apna order place kare!'
		return text

	elif smsTemplateName == "requestNotification_enquiry_buyersupplier_status":
		text = 'Your enquiry from %s has been updated to %s'
		return text

	elif smsTemplateName == "push":
		text = '%s has shared you a new %s on Wishbook. Click to view %s in Wishbook.'
		return text

	elif smsTemplateName == "share":
		text = '%s ne aapse %s catalog share kiya hai. Dekhne ke liye %s pe click kare'
		return text

	elif smsTemplateName == "pushPendingBuyer":
		text = '%s has shared new %s. To view download Wishbook App. For Android on www.wishbooks.io/android & iOS on www.wishbooks.io/ios'
		return text

	elif smsTemplateName == "salesOrder_purchase":
		# text = 'Your order %s has been successfully placed. Track the status by logging into Wishbook. Thank you for ordering on Wishbook.'
		text = 'Order Placed! Your order%s %s %s successfully placed. Track orders status by logging into Wishbook App | Wishbook Support 02616718989' #("s", 201, "are") or ("", 201, "is")
		return text

	elif smsTemplateName == "salesOrder_purchase_2":
		text = 'Your payment for order%s %s %s pending. Without payment, the order will not be processed | Wishbook Support 02616718989' #("s", 201, "are") or ("", 201, "is")
		return text

	elif smsTemplateName == "salesOrder_sales":
		# text = 'You have received an order %s from %s. Process the order on Wishbook %s'
		text = 'Order Received! You have received an Sales Order on Wishbook. Touch %s or go to Orders tab in the App or WebApp for details | Wishbook Support 02616718989'
		return text

	elif smsTemplateName == "salesOrder_status":
		# text = 'Your order %s is %s. Track details by logging into Wishbook. Thank you for choosing us.'
		text = 'Wishbook Order %s is %s. Touch %s or go to Orders tab in the App or WebApp for details | Wishbook Support 02616718989'
		return text

	elif smsTemplateName == "overdue_reminder":
		text = 'Payment due for Order %s from %s for %s. Please pay & enter your payment details here %s'
		return text

	elif smsTemplateName == "send_user_detail":
		text = 'Welcome to Wishbook Catalog application! You can login by your mobile number %s and password %s Download on Android on www.wishbooks.io/android & iOS on www.wishbooks.io/ios.'
		return text

	elif smsTemplateName == "daily_1_share_sms":
		text = 'Aaj aapko %s naye catalog share kiye gaye. Click here to view/purchase/share the catalogs: %s'
		return text

	elif smsTemplateName == "profile_not_set_msg":
		text = '%s has added you on Wishbook Catalog application & jump onto a better way to do business! Experience Wishbook on %s. To login, click on "Forgot Password?" on the login password to get OTP to help set your password'
		return text

	elif smsTemplateName == "user_detail":
		text = '%s has added you on Wishbook Catalog application and jump onto a better way to do business! Experience Wishbook on %s You can login by your mobile number %s and password %s Download on Android on www.wishbooks.io/android and iOS on www.wishbooks.io/ios'
		return text

	elif smsTemplateName == "user_detail_2":
		text = '%s ne aapko nayi Wishbook B2B application pe invite kiya hai. Wholesale rate me latest catalogs dekhne, khareedne aur bechne ke liye, download kijiye Wishbook App. Android - www.wishbooks.io/android and iOS - www.wishbooks.io/ios'
		return text

	elif smsTemplateName == "user_detail_3":
		text = '%s invited you on Wishbook B2B App. Find latest catalogs at True Wholesale Rates - %s. For better experience, download on Android - www.wishbooks.io/android and iOS - www.wishbooks.io/ios'
		return text

	elif smsTemplateName == "catalogviewed":
		text = 'Congratulations! aapke catalog ne %s lagayi hai! aapka catalog %s ab tak %s baar dekha ja chuka hai'
		return text

	elif smsTemplateName == "catalogviewed_2":
		text = 'Congratulations! aapka catalog %s ab tak %s baar dekha ja chuka hai'
		return text

	elif smsTemplateName == "public_catalog":
		text = "%s ne %s catalog add kiya hai. Dekhne ke liye %s pe click kijiye"
		return text

	elif smsTemplateName == "disable_catalog":
		text = "Your catalog %s has been disabled. To enable again, go to your catalog %s and touch 'Start Selling Again' button. If you are using Web, just select the catalog and click enable"
		return text

	elif smsTemplateName == "inactive_user_english":
		text = "%s+ catalogs were uploaded last week. Did you see them? Check them out! %s Ph / WhatsApp: 8469218980"
		return text

	elif smsTemplateName == "inactive_user_hindi":
		text = "%s+ catalogs upload hue the last week. Aapne dekhe kya? Abhi dekhiye! %s  Ph / WhatsApp: 8469218980"
		return text

	elif smsTemplateName == "user_registration_1":
		text = "%s apna textile business badha rahe hai Wishbook B2B App se. Aap bhi judiye! Download kijiye - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Mobile browser - %s"
		return text

	elif smsTemplateName == "user_registration_2":
		text = "%s are on Wishbook B2B app to grow their textile business. Why don't you join? Download Wishbook - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Also mobile browser - %s"
		return text

	elif smsTemplateName == "user_registration_3":
		text = "apna textile business badhane ke liye Wishbook B2B App se judiye!. Download kijiye - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Mobile browser - %s"
		return text

	elif smsTemplateName == "user_registration_4":
		text = "Use Wishbook B2B app to grow your textile business. Download Wishbook - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Also Mobile browser - %s"
		return text

def notificationTemplates(notificationTemplateName):
	if notificationTemplateName == "salesOrder_purchase":
		text = 'Order Placed! Your order%s %s %s successfully placed. Track orders Now!' #("s", 201, "are") or ("", 201, "is")
		return text

	elif notificationTemplateName == "salesOrder_purchase_2":
		text = 'Your payment for order%s %s %s pending. Without payment, the order will not be processed. Pay Now!' #("s", 201, "are") or ("", 201, "is")
		return text

	elif notificationTemplateName == "send_order_on_credit":
		text = 'Credit Order Received! You have received a Credit Order on Wishbook. View Details!'
		return text

	elif notificationTemplateName == "salesOrder_sales":
		text = 'Order Received! You have received an Order on Wishbook. View Details!'
		return text

	elif notificationTemplateName == "salesOrder_status":
		text = 'Your Wishbook Order %s is %s. View Details!'
		return text

	elif notificationTemplateName == "buyersupplier_status_1":
		text = '%s has changed relationship status to %s'
		return text

	elif notificationTemplateName == "buyersupplier_status_2":
		text = 'Your enquiry has been %s by %s'
		return text

	elif notificationTemplateName == "buyersupplier_status_3":
		text = 'Your enquiry from %s has been updated to %s'
		return text

	elif notificationTemplateName == "add_buyers_broker":
		text = 'Broker %s connected you with %s buyers'
		return text

	elif notificationTemplateName == "add_suppliers_broker":
		text = '%s connected you with %s, You can now buy his catalogs on supplier credit from Wishbook'
		return text

	elif notificationTemplateName == "salesorder_broker":
		text = 'Broker %s just created an order for one of your catalogs. Check it out!'
		return text

	elif notificationTemplateName == "requestNotification_supplierenquiry":
		text = '%s has added enquiry for catalog %s on Wishbook'
		return text

	elif notificationTemplateName == "requestNotification_default_supplier_approved":
		text = '%s has added you as a Supplier on Wishbook.'
		return text

	elif notificationTemplateName == "requestNotification_supplier":
		text = '%s has added you as a Supplier on Wishbook.'
		return text

	elif notificationTemplateName == "requestNotification_buyer":
		text = '%s has added you as a Buyer on Wishbook'
		return text

	elif notificationTemplateName == "requestNotification_default_buyer_approved":
		text = '%s has added you as a Buyer on Wishbook.'
		return text

	elif notificationTemplateName == "purchaseorder_broker":
		text = '%s just created an order on your behalf. Check it out!'
		return text

	elif notificationTemplateName == "shipment_1":
		text = 'Your order %s is %s. Track details by logging into Wishbook. Thank you for choosing us.'
		return text

	elif notificationTemplateName == "shipment_2":
		text = 'Your shipment of order %s is updated. Track details by logging into Wishbook. Thank you for choosing us.'
		return text

	elif notificationTemplateName == "cart_payment":
		text = 'Your Cart %s is %s. Track details by logging into Wishbook. Thank you for choosing us.'
		return text

	elif notificationTemplateName == "share":
		text = '%s has shared with you a catalog - %s'
		return text

	elif notificationTemplateName == "brand_follower":
		text = 'You have a new follower! %s followed your brand %s'
		return text

	elif notificationTemplateName == "company_catalog_view_times":
		text = 'Your %s catalog was viewed %s times'
		return text

	elif notificationTemplateName == "company_catalog_view_times_2":
		text = 'Your %s catalog has been viewed %s times'
		return text

	elif notificationTemplateName == "catalog_added":
		text = '%s just added %s catalog of %s Brand'
		return text

	elif notificationTemplateName == "catalog_added_2":
		text = '%s just uploaded a catalog %s'
		return text

	elif notificationTemplateName == "wishlist_catalog_disable":
		text = '%s catalog from your Wishlist is now out-of-stock.'
		return text

	elif notificationTemplateName == "credit_reference_rate_request":
		text = '%s has requested you to rate them on the basis of their transaction history with your company. It will help them with getting the credit.'
		return text

	elif notificationTemplateName == "catalog_become_seller":
		text = '%s is also selling %s catalog of %s brand'
		return text

	elif notificationTemplateName == "seller_order_extra_discount":
		text = 'Woohoo! Seller has added %s percent discount on your order %s. Now total Discount is %s percent. Place the order now!'
		return text

	elif notificationTemplateName == "update_catalog_price_order":
		text = 'A buyer could not create a purchase order for your catalog %s because you have not updated the price. Please update the price of your catalog.'
		return text

	elif notificationTemplateName == "user_profile_approved":
		text = 'Your wishbook account has been approved'
		return text

	elif notificationTemplateName == "daily_1_share_sms":
		text = 'Aaj aapko %s naye catalog share kiye gaye'
		return text

	elif notificationTemplateName == "background_task_status":
		text = '%s invited successfully out of %s requests. %s'
		return text

def generateNewOTP(userPObj):
	from api.models import RegistrationOTP
	import random

	logger.info("generateNewOTP")
	otp = random.randrange(100000, 999999, 1)
	registrationOtp = RegistrationOTP.objects.create(phone_number=userPObj.phone_number, otp=otp, country=userPObj.country)

	return otp

def getLastOTP(userPObj):
	from api.models import RegistrationOTP
	import random

	logger.info("getLastOTP")
	otp = None
	otpObj = RegistrationOTP.objects.filter(phone_number=userPObj.phone_number, country=userPObj.country).order_by('-id').first()
	if otpObj:
		otp = otpObj.otp
	else:
		# logger.info("if otp is None")
		# otp = random.randrange(100000, 999999, 1)
		# registrationOtp = RegistrationOTP.objects.create(phone_number=userPObj.phone_number, otp=otp, country=userPObj.country)
		otp = generateNewOTP(userPObj)

	return otp

def sendInvite(mobile_number, username):
	logger.info("sendInvite")

	#url = smsUrl()% (mobile_number)

	template = smsTemplates("sendInvite")% (username)
	smsSend([mobile_number], template, True)
	#smsSendICubes.apply_async(([mobile_number], template, True), expires=datetime.now() + timedelta(days=2))

	#sendsmart = SMS([mobile_number], template)
	#smsSend.apply_async(([mobile_number], template), expires=datetime.now() + timedelta(days=2))
	return True

def sendOTP(mobile_number, otp, checkverifystatus=False):
	from api.models import *
	from django.core.mail import send_mail
	logger.info("in sendOTP")

	template = smsTemplates("sendOTP")% (otp)
	#smsSend([mobile_number], template, True, True)

	OTP_SMS_METHOD = Config.objects.get(key="OTP_SMS_METHOD").value
	#if settings.OTP_SMS_METHOD == 'msg91':
	if OTP_SMS_METHOD == 'msg91':
		logger.info("in msg91= ")
		template = urllib.quote_plus(template)
		url = 'http://api.msg91.com/api/sendotp.php?authkey=151375ANNvYMSeY0590c66db&sender=WISHBK&mobile=%s&message=%s&otp=%s'% (mobile_number, template, otp) #sender=OTPSMS
		sentMessageObj = requests.get(url)
		logger.info(str(mobile_number))
		logger.info(str(otp))
		logger.info(str(url))
		try:
			logger.info(str(sentMessageObj))
			logger.info(str(sentMessageObj.text))

			msgvalue = json.loads(sentMessageObj.text)

			logger.info(str(msgvalue))

			if msgvalue['type'] == "success":
				smsTrasaction("msg91", 1)
			else:
				mail_status = send_mail("MSG91", "Error = "+str(msgvalue)+" & mobile no = "+str(mobile_number)+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
				logger.info(str(mail_status))
				SmsError.objects.create(sms_text=template, mobile_no=str(mobile_number), provider="msg91", error_text=str(msgvalue))
		except Exception as e:
			logger.info("sendOTP Exception e = %s"% (e))
	else:
		smsSend([mobile_number], template, True, True)

	if checkverifystatus:# and settings.DEBUG
		tnow = datetime.now()
		nextrun = tnow+timedelta(seconds=15)
		logger.info("checkOTPVerifyStatusNSendSMS datetime.now() = %s, next_run = %s"% (tnow, nextrun))
		schedule('api.tasks.checkOTPVerifyStatusNSendSMS',
			mobile_number, otp,
			#schedule_type=Schedule.ONCE,
			schedule_type='O',
			next_run=nextrun,
			q_options={'broker': priority_broker}
			#broker = priority_broker
		)
		print "priority_broker", priority_broker

	'''url = 'http://api.msg91.com/api/retryotp.php?authkey=151375ANNvYMSeY0590c66db&retrytype=voice&mobile=%s'% (mobile_number)
	callMessageObj = requests.get(url)
	logger.info(str(url))
	logger.info(str(callMessageObj))
	logger.info(str(callMessageObj.text))'''

	return True

def otpCall(full_mobile_number):
	full_mobile_number = full_mobile_number.replace("+", "")
	url = 'http://api.msg91.com/api/retryotp.php?authkey=151375ANNvYMSeY0590c66db&retrytype=voice&mobile=%s'% (full_mobile_number)
	callMessageObj = requests.get(url)
	logger.info(str(url))
	logger.info(str(callMessageObj))
	logger.info(str(callMessageObj.text))

	return True

def verifyMSG91OTP(full_mobile_number, otp):
	from api.models import Config
	OTP_SMS_METHOD = Config.objects.get(key="OTP_SMS_METHOD").value
	if OTP_SMS_METHOD == 'msg91':
		url = 'http://api.msg91.com/api/verifyRequestOTP.php?authkey=151375ANNvYMSeY0590c66db&sender=WISHBK&mobile=%s&otp=%s'% (full_mobile_number, otp)
		logger.info(str(url))
		sentMessageObj = requests.get(url)
		logger.info(str(sentMessageObj))
		logger.info(str(sentMessageObj.text))

	return True

def checkAndSendOTP(phone_number, country, checkverifystatus=False):
	from api.models import *
	from django.utils import timezone
	import random

	logger.info("in checkAndSendOTP")

	full_mobile_number = str(country.phone_code)+str(phone_number)

	#otp = random.randrange(100000, 999999, 1)

	#otpObj = RegistrationOTP.objects.filter(phone_number=phone_number, country=country, is_verified='no').order_by('-created_date').first()
	otpObj = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-id').first()
	current_time = timezone.now()

	if otpObj is not None and otpObj.is_verified=='no':
		duration = current_time - otpObj.created_date
		minutes = int(duration.seconds / 60)
		if minutes < 30:
			logger.info("in if minutes < 30: - for resend otp")
			OTP_SMS_METHOD = Config.objects.get(key="OTP_SMS_METHOD").value
			#if settings.OTP_SMS_METHOD == 'msg91':
			if OTP_SMS_METHOD == 'msg91':
				logger.info("in msg91= ")
				otpCall(full_mobile_number)

				import time
				time.sleep(5) #in second

				logger.info("to msg")

				#~ url = 'http://api.msg91.com/api/retryotp.php?authkey=151375ANNvYMSeY0590c66db&retrytype=text&mobile=%s'% (full_mobile_number)
				#~ sentMessageObj = requests.get(url)
				#~ logger.info(str(full_mobile_number))
				#~ logger.info(str(url))
				#~ logger.info(str(sentMessageObj))
				#~ logger.info(str(sentMessageObj.text))

				if checkverifystatus:# and settings.DEBUG
					tnow = datetime.now()
					nextrun = tnow+timedelta(seconds=15)
					logger.info("checkOTPVerifyStatusNSendSMS datetime.now() = %s, next_run = %s"% (tnow, nextrun))
					schedule('api.tasks.checkOTPVerifyStatusNSendSMS',
						full_mobile_number, otpObj.otp,
						#schedule_type=Schedule.ONCE,
						schedule_type='O',
						next_run=nextrun,
						q_options={'broker': priority_broker}
						#broker = priority_broker
					)
					print "priority_broker", priority_broker

			else:
				sendOTP(full_mobile_number, str(otpObj.otp), checkverifystatus)
			return True

	logger.info("re-generate OTP")
	otp = random.randrange(100000, 999999, 1)

	sendOTP(full_mobile_number, str(otp), checkverifystatus)

	registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otp, country=country)

	return True

'''def catalogFabricFilter(fabric, queryset):
	from eav.models import Attribute, Value as EavValue
	from django.contrib.contenttypes.models import ContentType

	fabrics = list(fabric.strip().replace(', ',',').rstrip(",").split(','))

	if len(fabrics) > 0:
		if fabrics[0].isdigit():
			newfabrics = []
			for fabricid in fabrics:
				ev = EnumValue.objects.filter(id=fabricid).first()
				if ev:
					newfabrics.append(ev.value)
			if len(newfabrics) > 0:
				fabrics = newfabrics
	print "final fabrics", fabrics

	ct = ContentType.objects.get(id=25)
	#fabrics = fabric.split(',')
	#print fabrics
	attribute = Attribute.objects.get(name="fabric")
	#enumValue = EnumValue.objects.filter(id__in=fabrics)
	enumValue = EnumValue.objects.filter(reduce(lambda x, y: x | y, [Q(value__icontains=fabric) for fabric in fabrics]))
	print enumValue
	catalogids = queryset.values_list('id', flat=True)
	if enumValue.count() > 0:
		entityids = EavValue.objects.filter(entity_ct=ct, attribute=attribute, value_enum__in=enumValue, entity_id__in=catalogids).values_list('entity_id', flat=True).distinct()
		print "entityids =",entityids
		queryset = queryset.filter(id__in=entityids)
	return queryset'''

'''def catalogWorkFilter(work, queryset):
	from eav.models import Attribute, Value as EavValue
	from django.contrib.contenttypes.models import ContentType

	works = list(work.strip().replace(', ',',').rstrip(",").split(','))

	if len(works) > 0:
		if works[0].isdigit():
			newworks = []
			for workid in works:
				ev = EnumValue.objects.filter(id=workid).first()
				if ev:
					newworks.append(ev.value)
			if len(newworks) > 0:
				works = newworks
	print "final works = ", works

	#catalogsIds = ProductEAVFlat.objects.filter(Q(catalog__in=queryset) & (Q(reduce(lambda x, y: x | y, [Q(work_text__icontains=work) for work in works])) | Q(reduce(lambda x, y: x | y, [Q(work__icontains=work) for work in works])))).values_list('catalog', flat=True).distinct()
	#print catalogsIds
	#queryset = queryset.filter(id__in=catalogsIds)


	ct = ContentType.objects.get(id=25)
	#works = works.split(',')
	#print "works split = ",works
	attribute = Attribute.objects.get(name="work")
	#enumValue = EnumValue.objects.filter(id__in=works)
	enumValue = EnumValue.objects.filter(reduce(lambda x, y: x | y, [Q(value__icontains=work) for work in works]))
	print enumValue
	catalogids = queryset.values_list('id', flat=True)
	if enumValue.count() > 0:
		entityids = EavValue.objects.filter(entity_ct=ct, attribute=attribute, value_enum__in=enumValue, entity_id__in=catalogids).values_list('entity_id', flat=True).distinct()
		print "entityids =",entityids
		queryset = queryset.filter(id__in=entityids)
	return queryset'''

def addSearchQueryLog(user, params, request_for):
	from api.models import SearchQuery

	try:
		sqObj, created = SearchQuery.objects.get_or_create(user=user, params=params, request_for=request_for)
		sqObj.use_count += 1
		#sqObj.result_count = total_rows
		sqObj.save()
	except Exception as e:
		pass

	return True

def catalogFabricFilter(fabric, catalogids):
	from api.models import CatalogEAVFlat

	fabrics = list(fabric.strip().replace(', ',',').rstrip(",").split(','))

	cefids = []
	#catalogids = queryset.values_list('id', flat=True)

	if len(fabrics) > 0:
		if fabrics[0].isdigit():
			cefids = CatalogEAVFlat.objects.filter(Q(catalog__in=catalogids) & Q(reduce(lambda x, y: x | y, [Q(fabric__icontains=fabric) for fabric in fabrics]))).values_list('catalog', flat=True)
		else:
			cefids = CatalogEAVFlat.objects.filter(Q(catalog__in=catalogids) & Q(reduce(lambda x, y: x | y, [Q(fabric_value__icontains=fabric) for fabric in fabrics]))).values_list('catalog', flat=True)
	#print "cefids catalog ids=", cefids

	#~ queryset = queryset.filter(id__in=cefids)
	#~ return queryset
	return cefids

def catalogWorkFilter(work, catalogids):
	from api.models import CatalogEAVFlat

	works = list(work.strip().replace(', ',',').rstrip(",").split(','))

	cefids = []
	#catalogids = queryset.values_list('id', flat=True)

	if len(works) > 0:
		if works[0].isdigit():
			cefids = CatalogEAVFlat.objects.filter(Q(catalog__in=catalogids) & Q(reduce(lambda x, y: x | y, [Q(work__icontains=work) for work in works]))).values_list('catalog', flat=True)
		else:
			cefids = CatalogEAVFlat.objects.filter(Q(catalog__in=catalogids) & Q(reduce(lambda x, y: x | y, [Q(work_value__icontains=work) for work in works]))).values_list('catalog', flat=True)
	#print "cefids catalog ids=", cefids

	#~ queryset = queryset.filter(id__in=cefids)
	#~ return queryset
	return cefids

def filterCatalog(queryset, company, params, user=None):
	from api.models import *
	min_price = params.get('min_price', None)
	max_price = params.get('max_price', None)
	work = params.get('work', None)
	fabric = params.get('fabric', None)
	title = params.get('title', None)
	title_exact = params.get('title_exact', None)
	#~ company_id = params.get('company', None)
	stock = params.get('stock', None)

	size = params.get('size', None)
	stitching_type = params.get('stitching_type', None)
	size_mix = params.get('size_mix', None)
	style = params.get('style', None)

	viewType = params.get('view_type', None)
	brandIds = params.get('brand', None)
	category = params.get('category', None)
	sell_full_catalog = params.get('sell_full_catalog', None)

	q_search = params.get('q', None)#elastic search

	search = params.get('search', None)#common search. using for mycatalog filter

	#catalogids = queryset.values_list('id', flat=True)
	#cefids = CatalogEAVFlat.objects.filter(catalog__in=list(catalogids))
	cefids = CatalogEAVFlat.objects.all()
	is_cefids_filter=False

	if search is not None and search != "":
		cefids = cefids.filter(Q(catalog__id__icontains=search) | Q(view_permission__icontains=search) | Q(title__icontains=search) | Q(brand__name__icontains=search) | Q(category__category_name__icontains=search) | Q(sell_full_catalog__icontains=search) | Q(fabric_value__icontains=search) | Q(work_value__icontains=search) | Q(min_price__icontains=search) | Q(max_price__icontains=search) | Q(stitching_type__icontains=search) | Q(number_pcs_design_per_set__icontains=search) | Q(size_value__icontains=search) | Q(size_mix__icontains=search) | Q(style__icontains=search))
		is_cefids_filter=True

	if min_price is not None or max_price is not None:
		if min_price is not None and max_price is None:
			max_price = Decimal('1000000.00')
		if min_price is None and max_price is not None:
			min_price = Decimal('0.00')

		if viewType is not None and viewType.lower()=="public":
			print "public catalog price filter"
			cefids = cefids.filter(Q(min_price__gte=min_price, min_price__lte=max_price) | Q(max_price__gte=min_price, max_price__lte=max_price))
			is_cefids_filter=True
			#publicCatalog = Product.objects.filter(public_price__range=(min_price, max_price)).values_list('catalog', flat=True)
			#queryset = queryset.filter(id__in=publicCatalog)
		else:
			catalogs = queryset.filter(company=company).values_list('id', flat=True)
			catalogs2 =Product.objects.filter(catalog__in=catalogs, price__range=(min_price, max_price)).values_list('catalog', flat=True)
			#queryset = queryset.filter(Q(company=company) | Q(id__in=catalogs2)).order_by('-id')

			sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
			catalogsIds = CompanyProductFlat.objects.filter((Q(buying_company=company) & Q(selling_company__in=sellingCompanyObj) & Q(is_disable=False)) & (Q(final_price__range=(min_price, max_price)) | Q(selling_price__range=(min_price, max_price)))).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()

			publicCatalog = Product.objects.filter(catalog__view_permission='public', public_price__range=(min_price, max_price)).values_list('catalog', flat=True)

			#queryset = queryset.filter(Q(id__in=catalogsIds)).order_by('-id')
			queryset = queryset.filter(Q(id__in=catalogs2) | Q(id__in=catalogsIds) | Q(id__in=publicCatalog))#.order_by('-id')

	if work is not None:
		#print "in work"
		#works = work.split(' ')
		'''works = list(work.strip().replace(', ',',').split(','))

		if len(works) > 0:
			if works[0].isdigit():
				newworks = []
				for workid in works:
					ev = EnumValue.objects.filter(id=workid).first()
					if ev:
						newworks.append(ev.value)
				if len(newworks) > 0:
					works = newworks
		print "final works", works

		catalogsIds = ProductEAVFlat.objects.filter(Q(catalog__in=queryset) & (Q(reduce(lambda x, y: x | y, [Q(work_text__icontains=work) for work in works])) | Q(reduce(lambda x, y: x | y, [Q(work__icontains=work) for work in works])))).values_list('catalog', flat=True).distinct()
		#print catalogsIds
		queryset = queryset.filter(id__in=catalogsIds)#.order_by('-id')'''
		#~ cefids = catalogWorkFilter(work, catalogids)
		#~ queryset = queryset.filter(id__in=cefids)
		works = list(work.strip().replace(', ',',').rstrip(",").split(','))

		if len(works) > 0:
			if works[0].isdigit():
				cefids = cefids.filter(Q(reduce(lambda x, y: x | y, [Q(work__icontains=work) for work in works])))
			else:
				cefids = cefids.filter(Q(reduce(lambda x, y: x | y, [Q(work_value__icontains=work) for work in works])))
			is_cefids_filter=True

	if fabric is not None:
		#print "in fabric"
		#fabrics = fabric.split(' ')
		'''fabrics = list(fabric.strip().replace(', ',',').split(','))

		if len(fabrics) > 0:
			if fabrics[0].isdigit():
				newfabrics = []
				for fabricid in fabrics:
					ev = EnumValue.objects.filter(id=fabricid).first()
					if ev:
						newfabrics.append(ev.value)
				if len(newfabrics) > 0:
					fabrics = newfabrics
		print "final fabrics", fabrics

		catalogsIds = ProductEAVFlat.objects.filter(Q(catalog__in=queryset) & (Q(reduce(lambda x, y: x | y, [Q(fabric_text__icontains=fabric) for fabric in fabrics])) | Q(reduce(lambda x, y: x | y, [Q(fabric__icontains=fabric) for fabric in fabrics])))).values_list('catalog', flat=True).distinct()
		queryset = queryset.filter(id__in=catalogsIds)'''
		#~ cefids = catalogFabricFilter(fabric, catalogids)
		#~ queryset = queryset.filter(id__in=cefids)

		fabrics = list(fabric.strip().replace(', ',',').rstrip(",").split(','))

		if len(fabrics) > 0:
			if fabrics[0].isdigit():
				cefids = cefids.filter(Q(reduce(lambda x, y: x | y, [Q(fabric__icontains=fabric) for fabric in fabrics])))
			else:
				cefids = cefids.filter(Q(reduce(lambda x, y: x | y, [Q(fabric_value__icontains=fabric) for fabric in fabrics])))
			is_cefids_filter=True

	if title is not None:
		titles = title.split(' ')
		#queryset = queryset.filter(reduce(lambda x, y: x | y, [Q(title__icontains=title) for title in titles]))#.order_by('-id')
		queryset = queryset.filter(title__icontains=title)
		if title != "":
			addSearchQueryLog(user, "title="+title, "catalog")

	if title_exact is not None:
		queryset = queryset.filter(title__exact=title_exact)
		if title_exact != "":
			addSearchQueryLog(user, "title_exact="+title_exact, "catalog")

	#~ if company_id is not None:
		#~ sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved", selling_company=company_id).values_list('selling_company', flat=True).distinct()
		#~ catalogsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, is_disable=False).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
		#~ queryset = queryset.filter(Q(company=company_id) | Q(id__in=catalogsIds))

	if stock is not None:
		datomorrow = date.today() + timedelta(days=2)

		stock_arr = []
		for obj in queryset:
			pushUserObj=None
			cpfObj = CompanyProductFlat.objects.filter(catalog=obj, buying_company=company, is_disable=False).last()

			if cpfObj:
				pushUserObj = Push_User.objects.filter(buying_company=company, catalog=obj, push=cpfObj.push_reference).last()

			if pushUserObj:
				if stock == "prebook" and pushUserObj.push.exp_desp_date is not None and pushUserObj.push.exp_desp_date >= datomorrow:
					stock_arr.append(obj.id)
				elif stock == "instock" and (pushUserObj.push.exp_desp_date is None or pushUserObj.push.exp_desp_date < datomorrow):
					stock_arr.append(obj.id)
			else:
				print ""
		print stock_arr
		queryset = queryset.filter(id__in=stock_arr)

	if size is not None:#multi eav
		#~ from eav.models import Attribute, Value as EavValue
		#~ from django.contrib.contenttypes.models import ContentType
		#~ ct = ContentType.objects.get(id=25)
		sizes = size.split(',')
		'''attribute = Attribute.objects.get(name="size")
		enumValue = EnumValue.objects.filter(id__in=sizes)
		if enumValue.count() > 0:
			entityids = EavValue.objects.filter(entity_ct=ct, attribute=attribute, value_enum__in=enumValue).values_list('entity_id', flat=True).distinct()
			print "entityids =",entityids
			queryset = queryset.filter(id__in=entityids)'''
		#~ cefids = CatalogEAVFlat.objects.filter(Q(catalog__in=catalogids) & Q(reduce(lambda x, y: x | y, [Q(size__icontains=size) for size in sizes]))).values_list('catalog', flat=True)
		#~ queryset = queryset.filter(id__in=cefids)
		cefids = cefids.filter(Q(reduce(lambda x, y: x | y, [Q(size__icontains=size) for size in sizes])))
		is_cefids_filter=True

	if stitching_type is not None:#enum eav
		#~ from eav.models import Attribute, Value as EavValue
		#~ from django.contrib.contenttypes.models import ContentType
		#~ ct = ContentType.objects.get(id=25)

		#~ attribute = Attribute.objects.get(name="stitching_type")
		enumValue = EnumValue.objects.filter(id=stitching_type).first()
		#~ if enumValue:
			#~ entityids = EavValue.objects.filter(entity_ct=ct, attribute=attribute, value_enum=enumValue).values_list('entity_id', flat=True)
			#~ print "entityids =",entityids
			#~ queryset = queryset.filter(id__in=entityids)
		#~ cefids = CatalogEAVFlat.objects.filter(catalog__in=catalogids, stitching_type=enumValue).values_list('catalog', flat=True)
		#~ queryset = queryset.filter(id__in=cefids)
		cefids = cefids.filter(stitching_type=enumValue)
		is_cefids_filter=True

	if style is not None:#enum eav
		enumValue = EnumValue.objects.filter(id=style).first()
		cefids = cefids.filter(style=enumValue)
		is_cefids_filter=True

	if size_mix is not None:#text eav
		#~ from eav.models import Attribute, Value as EavValue
		#~ from django.contrib.contenttypes.models import ContentType
		#~ ct = ContentType.objects.get(id=25)

		#~ attribute = Attribute.objects.get(name="size_mix")
		#~ entityids = EavValue.objects.filter(entity_ct=ct, attribute=attribute, value_text__icontains=size_mix).values_list('entity_id', flat=True)
		#~ print "entityids =",entityids
		#~ queryset = queryset.filter(id__in=entityids)

		#~ cefids = CatalogEAVFlat.objects.filter(catalog__in=catalogids, size_mix__icontains=size_mix).values_list('catalog', flat=True)
		#~ queryset = queryset.filter(id__in=cefids)
		cefids = cefids.filter(size_mix__icontains=size_mix)
		is_cefids_filter=True

	if brandIds is not None and brandIds != "":
		brandIds = brandIds.split(',')
		cefids = cefids.filter(brand__in=brandIds)
		is_cefids_filter=True

	if category is not None and category != "":
		catalogArray = []
		catalogArray.append(int(category))

		catalogParent1 = Category.objects.filter(parent_category=category).order_by('id').values_list('id', flat=True).distinct()
		catalogArray += catalogParent1

		catalogParent2 = Category.objects.filter(parent_category__in=catalogParent1).order_by('id').values_list('id', flat=True).distinct()
		catalogArray += catalogParent2

		cefids = cefids.filter(category__in=list(catalogArray))
		is_cefids_filter=True
		#queryset = queryset.filter(category__in=list(catalogArray))


	if sell_full_catalog is not None and sell_full_catalog != "":
		if viewType is not None and viewType.lower()=="public":
			if sell_full_catalog.lower() == "true":
				cefids = cefids.filter(sell_full_catalog=True)
			elif sell_full_catalog.lower() == "false":
				cefids = cefids.filter(sell_full_catalog=False)
			is_cefids_filter=True

	if q_search:
		q_search = q_search.encode('utf-8')
		#q_search = " ".join(re.split("[^a-zA-Z0-9]*", q_search)).strip()
		logger.info("filterCatalog q_search = %s, len = %s"% (q_search, len(q_search)))

		if len(q_search) > 0:
			try:
				query_string = "*"+str(q_search)+"*"

				if "-" in q_search or "." in q_search or "=" in q_search or "~" in q_search or "!" in q_search or "&" in q_search:
					query_string = str(q_search)
				if ":" in q_search or "(" in q_search or ")" in q_search or "/" in q_search or "\\" in q_search or "*" in q_search or " - " in q_search:
					query_string = str(q_search)
					for qs in [":","(",")","/", "\\", "*", " - "]:
						query_string = query_string.replace(qs, " ")

				print query_string
				addSearchQueryLog(user, "q="+q_search, "catalog")
				from elasticsearch import Elasticsearch
				client = Elasticsearch(settings.ELASTICSEARCH_HOST)
				items = client.search(
					index="catalog-index",
					body={
					  "size" : 10000,
					  "query": {
						"query_string": {
							"query": query_string,
							"default_operator": "and",
							"fuzziness":"AUTO",
						}
					  }
					}
				)

				elasticarr = []
				for item in items["hits"]["hits"]:
					elasticarr.append(item["_id"])

				print "elasticarr=",elasticarr
				print "elasticarr len=",len(elasticarr)

				queryset = queryset.filter(id__in=elasticarr)
			except Exception as e:
				logger.info("filterCatalog Exception e = %s"% (e))
				queryset = queryset.none()
		else:
			queryset = queryset.none()

	if is_cefids_filter:
		cefids = cefids.values_list('catalog', flat=True)
		queryset = queryset.filter(id__in=list(cefids))

	return queryset#.order_by('-id')

def sortCatalog(queryset, company, params):
	from api.models import CompanyProductFlat
	from django.db.models import Case, When

	ordering = params.get('ordering', None)
	viewType = params.get('view_type', None)

	if ordering is not None and ordering.lower()=="views":
		queryset = queryset.annotate(catalog_views=Sum('companycatalogview__clicks')).order_by('catalog_views')
	elif ordering is not None and ordering.lower()=="-views":
		queryset = queryset.annotate(catalog_views=Sum('companycatalogview__clicks')).order_by('-catalog_views')

	elif ordering is not None and ordering.lower()=="title":
		queryset = queryset.order_by('title')
	elif ordering is not None and ordering.lower()=="-title":
		queryset = queryset.order_by('-title')

	elif ordering is not None and ordering.lower()=="price":
		if viewType is not None and viewType.lower()=="public":
			queryset = queryset.annotate(product_price=Min('products__public_price')).order_by('product_price')
		elif viewType is not None and viewType.lower()=="myreceived":
			catalogids = queryset.values_list('id', flat=True)
			cids = CompanyProductFlat.objects.filter(buying_company=company, catalog__in=catalogids).annotate(product_price=Min('final_price')).order_by('product_price').values_list('catalog',flat=True).distinct()
			print "cids=",list(cids)
			preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(cids)])
			queryset = queryset.order_by(preserved)
		else:
			queryset = queryset.annotate(product_price=Min('products__price')).order_by('product_price')
	elif ordering is not None and ordering.lower()=="-price":
		if viewType is not None and viewType.lower()=="public":
			queryset = queryset.annotate(product_price=Min('products__public_price')).order_by('-product_price')
		elif viewType is not None and viewType.lower()=="myreceived":
			catalogids = queryset.values_list('id', flat=True)
			cids = CompanyProductFlat.objects.filter(buying_company=company, catalog__in=catalogids).annotate(product_price=Min('final_price')).order_by('-product_price').values_list('catalog',flat=True).distinct()
			print "cids=",list(cids)
			preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(cids)])
			queryset = queryset.order_by(preserved)
		else:
			queryset = queryset.annotate(product_price=Min('products__price')).order_by('-product_price')

	return queryset



def catalogQuerysetFilter(queryset, company, params, user, action):
	from api.models import *

	from django.db.models import Case, When

	from django.utils import timezone
	from django.core.cache import cache
	from api.cache_functions import *

	catalog_type = params.get('catalog_type', 'catalog')
	queryset = queryset.filter(catalog_type = catalog_type)


	brandIds = params.get('brand', None)

	#fetching a single catalog detail using urlkey
	'''urlkey = params.get('urlkey', None)
	if urlkey:
		urlindex_obj  = URLIndex.objects.filter(urlkey = urlkey).first()
		if urlindex_obj:
			queryset = Catalog.objects.filter(id = urlindex_obj.urlobject_id)
			return queryset
		return Catalog.objects.none()'''

	follow_brand = params.get('follow_brand', None)
	if follow_brand is not None and follow_brand.lower() == "true":
		print "follow_brand"
		brandids = CompanyBrandFollow.objects.filter(company=company).values_list('brand', flat=True)
		brandids = list(brandids)
		print brandids
		mycatalogids = Catalog.objects.filter(company=company).values_list('id', flat=True).distinct()
		queryset = queryset.filter(brand__in=brandids, total_products_uploaded__gt=0).exclude(id__in=mycatalogids).order_by('-id') #view_permission="public",

		# ~ productcatalogs = Product.objects.filter(catalog__in=queryset).values_list('catalog', flat=True).distinct()
		# ~ queryset = queryset.filter(id__in=productcatalogs)

	is_disable = params.get('is_disable', 'false')
	supplier_disabled = params.get('supplier_disabled', 'false')
	buyer_disabled = params.get('buyer_disabled', 'false')

	disableCatalogIds = getDisableCatalogIds(company)
	myDisableCatalogIds = getMyDisableCatalogIds(company)

	#print selling_company
	if is_disable.lower() == 'true':
		queryset = queryset.filter(id__in=disableCatalogIds)
		#queryset = queryset.filter(id__in=myDisableCatalogIds)
	if supplier_disabled.lower() == 'true' and buyer_disabled.lower() == 'true':
		queryset = queryset.filter(id__in=disableCatalogIds)
		is_disable = 'true'
	elif supplier_disabled.lower() == 'true':
		supplierDisableCatalogIds = getSupplierDisableCatalogIds(company)
		queryset = queryset.filter(id__in=supplierDisableCatalogIds)
		is_disable = 'true'
	elif buyer_disabled.lower() == 'true':
		#myDisableCatalogIds = getMyDisableCatalogIds(company)
		queryset = queryset.filter(id__in=myDisableCatalogIds)
		is_disable = 'true'

	trusted_seller = params.get('trusted_seller', None)
	viewType = params.get('view_type', None)
	ordering = params.get('ordering', None)
	most_viewed = params.get('most_viewed', 'false')
	most_ordered = params.get('most_ordered', 'false')
	sell_full_catalog = params.get('sell_full_catalog', None)
	supplier_company = params.get('company', None)
	supplier_company_state = params.get('supplier_state', None)
	if supplier_company_state is not None:
		supplier_company_state = supplier_company_state.split(",")
		supplier_company_state = list(supplier_company_state)
	supplier_company_city = params.get('supplier_city', None)
	near_me = params.get('near_me', 'false')
	is_supplier_approved = params.get('is_supplier_approved', 'false')

	sellers = params.get('sellers', None)#multi supplier filter for public catalog

	dtnow = datetime.now()

	if viewType is not None and viewType.lower()=="public":
		# queryset = getCache("public")
		urlPath = "public"
		result = cache.get(urlPath)
		if result:
			print "if result"
			queryset = result
		else:
			print "else result"
			cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True).distinct()
			queryset = queryset.filter(id__in=cscatalogids, view_permission="public", total_products_uploaded__gt=0).order_by('-sort_order', '-id')

			cache.set(urlPath, queryset, settings.CACHE_EXPIRE_TIME)
		# print "queryset ======================", queryset
		if trusted_seller is not None and trusted_seller.lower() == "true":
			# queryset = getCache("trusted_seller")
			urlPath = "trusted_seller"
			result = cache.get(urlPath)
			if result:
				print "if result"
				queryset = result
			else:
				cscatalogids = CatalogSeller.objects.filter(catalog__in=queryset, selling_company__trusted_seller=True, selling_type="Public", status="Enable").values_list('catalog', flat=True)
				queryset = queryset.filter(id__in=list(cscatalogids)).order_by('-trusted_sort_order').distinct()

				cache.set(urlPath, queryset, settings.CACHE_EXPIRE_TIME)

		if supplier_company is not None:
			cscatalogids = CatalogSeller.objects.filter(catalog__in=queryset, selling_company=supplier_company, status="Enable").values_list('catalog', flat=True)
			queryset = queryset.filter(id__in=cscatalogids)
			#logger.info("catalog viewtype=public supplier_company catalog ids= %s"% (queryset.values_list('id',flat=True)))

		if sellers is not None and sellers != "":
			sellers = sellers.split(',')
			cscatalogids = CatalogSeller.objects.filter(catalog__in=queryset, selling_company__in=sellers, status="Enable").values_list('catalog', flat=True)
			queryset = queryset.filter(id__in=cscatalogids)

		if supplier_company_state is not None:
			cscatalogids = CatalogSeller.objects.filter(catalog__in=queryset, selling_company__address__state__in=supplier_company_state, status="Enable").values_list('catalog', flat=True)
			queryset = queryset.filter(id__in=cscatalogids)

		if supplier_company_city is not None:
			cscatalogids = CatalogSeller.objects.filter(catalog__in=queryset, company__address__city=supplier_company_city, status="Enable").values_list('catalog', flat=True)
			queryset = queryset.filter(id__in=cscatalogids)

		if near_me is not None and near_me.lower() == "true":
			state = company.address.state
			cstscompanyids = CompanySellsToState.objects.filter(state=state).values_list('company', flat=True).distinct()
			cstscompanyids = list(cstscompanyids)
			cstscompanyids1 = CompanySellsToState.objects.filter(state=state).exclude(intermediate_buyer__isnull=True).values_list('intermediate_buyer', flat=True).distinct()
			cstscompanyids.extend(list(cstscompanyids1))
			print cstscompanyids

			cscatalogids = CatalogSeller.objects.filter(selling_company__in=cstscompanyids, catalog__in=queryset, status="Enable").values_list('catalog', flat=True)

			queryset = queryset.filter(company__in=cstscompanyids).distinct()
			#logger.info("catalog viewtype=public near_me==true len= %s"% (queryset.count()))

		if most_viewed.lower() == "true":
			# queryset = getCache("most_viewed")
			urlPath = "most_viewed"

			result = cache.get(urlPath)
			if result:
				print "if result"
				queryset = result
			else:
				print "else result"
				todayDate = datetime.now()
				lastDate = todayDate - timedelta(days=7)
				ccvCatalogIds = CompanyCatalogView.objects.filter(catalog__in=queryset, created_at__gte=lastDate).values('catalog').annotate(catalog_count=Count('catalog')).order_by('-catalog_count').values_list('catalog', flat=True).distinct()
				ccvCatalogIds = list(ccvCatalogIds)[:10]
				#print "most_viewed ccvCatalogIds", ccvCatalogIds
				preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ccvCatalogIds)])
				queryset = queryset.filter(id__in=ccvCatalogIds).order_by(preserved)
				print "most_viewed=",queryset

				cache.set(urlPath, queryset, settings.CACHE_EXPIRE_TIME)

		if most_ordered.lower() == "true":
			# queryset = getCache("most_ordered")
			urlPath = "most_ordered"

			result = cache.get(urlPath)
			if result:
				print "if result"
				queryset = result
			else:
				print "else result"
				todayDate = datetime.now()
				lastDate = todayDate - timedelta(days=30)

				soiCatalogIds = SalesOrderItem.objects.filter(sales_order__created_at__gte=lastDate, product__catalog__in=queryset).values('product__catalog').annotate(catalog_count=Count('product__catalog')).order_by('-catalog_count').values_list('product__catalog', flat=True).distinct()
				soiCatalogIds = list(soiCatalogIds)[:10]
				#print "most_ordered soiCatalogIds", soiCatalogIds
				preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(soiCatalogIds)])
				queryset = queryset.filter(id__in=soiCatalogIds).order_by(preserved)

				cache.set(urlPath, queryset, settings.CACHE_EXPIRE_TIME)

		if is_supplier_approved.lower() == "true":
			suppliers = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
			cscatalogids = CatalogSeller.objects.filter(selling_company__in=suppliers, catalog__in=queryset, status="Enable").values_list('catalog', flat=True)
			queryset = queryset.filter(id__in=cscatalogids)

		# print "queryset ==================22====", queryset
		if most_ordered.lower() != "true" and most_viewed.lower() != "true":
			queryset = filterCatalog(queryset, company, params, user)
			queryset = sortCatalog(queryset, company, params)
		# print "queryset ==================33====", queryset
		print "return from public"
		return queryset

	if user.is_staff:
		return queryset

	if sell_full_catalog is not None and str(viewType).lower() != "myreceived":
		if sell_full_catalog.lower() == "true":
			cscatalogids = CatalogSeller.objects.filter(selling_type="Public", catalog__in=queryset, sell_full_catalog=True, status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True)
			queryset = queryset.filter(Q(id__in=cscatalogids) | Q(sell_full_catalog=True))
		elif sell_full_catalog.lower() == "false":
			cscatalogids = CatalogSeller.objects.filter(selling_type="Public", catalog__in=queryset, sell_full_catalog=False, status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True)
			queryset = queryset.filter(Q(id__in=cscatalogids) | Q(sell_full_catalog=False))

	if supplier_company is not None:
		cscatalogids = CatalogSeller.objects.filter(selling_type="Public", catalog__in=queryset, selling_company=supplier_company, status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True)

		catalogsIds = Push_User.objects.filter(buying_company=company, selling_company=supplier_company).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
		catalogsIds = list(catalogsIds)
		#queryset = queryset.filter(Q(company=supplier_company, view_permission='public') | Q(id__in=catalogsIds)).order_by('-id').distinct()
		queryset = queryset.filter(Q(id__in=cscatalogids) | Q(id__in=catalogsIds)).order_by('-id').distinct()
		# ~ catalogsIds = Product.objects.filter(catalog__in=queryset).values_list('catalog', flat=True).distinct()
		# ~ queryset = queryset.filter(id__in=catalogsIds)
		queryset = queryset.filter(total_products_uploaded__gt=0)

	if supplier_company_state is not None:
		catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__address__state__in=supplier_company_state).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
		catalogsIds = list(catalogsIds)
		queryset = queryset.filter(Q(company__address__state__in=supplier_company_state, view_permission='public') | Q(id__in=catalogsIds)).order_by('-id').distinct()

	if supplier_company_city is not None:
		catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__address__city=supplier_company_city).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
		catalogsIds = list(catalogsIds)
		queryset = queryset.filter(Q(company__address__city=supplier_company_city, view_permission='public') | Q(id__in=catalogsIds)).order_by('-id').distinct()


	if viewType is not None and viewType.lower()=="mycatalogs":
		#cscatalogids = CatalogSeller.objects.filter(selling_company=company, status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True)
		cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
		queryset = queryset.filter(Q(company=company) | Q(id__in=cscatalogids)).order_by('-id')

		if most_viewed.lower() == "true":
			queryset = queryset.filter(company=company)
			ccvCatalogIds = CompanyCatalogView.objects.filter(catalog__in=queryset).values('catalog').annotate(catalog_count=Count('catalog')).order_by('-catalog_count').values_list('catalog', flat=True).distinct()
			ccvCatalogIds = list(ccvCatalogIds)
			ccvCatalogIds.extend(list(queryset.values_list('id', flat=True)))
			print "most_viewed ccvCatalogIds", ccvCatalogIds
			preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ccvCatalogIds)])
			queryset = queryset.order_by(preserved)

	elif viewType is not None and viewType.lower()=="myreceived":
		if trusted_seller is not None and trusted_seller.lower() == "true":
			catalogsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__trusted_seller=True, is_disable=False).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
			catalogsIds = list(catalogsIds)
			queryset = queryset.filter(id__in=catalogsIds, total_products_uploaded__gt=0).order_by('-trusted_sort_order').distinct()
			# ~ productcatalogs = Product.objects.filter(catalog__in=queryset).values_list('catalog', flat=True).distinct()
			# ~ queryset = queryset.filter(id__in=productcatalogs)
			#logger.info("catalog view_type=myreceived trusted_seller==true len= %s"% (queryset.count()))

		mycatalogids = Catalog.objects.filter(company=company).values_list('id', flat=True).distinct()
		queryset = queryset.exclude(id__in=mycatalogids)

		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()

		catalogsIds = None
		if sell_full_catalog is not None:
			pushuserMaxIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).values('catalog','buying_company').annotate(Max('id')).values('id__max')
			if sell_full_catalog.lower() == "true":
				catalogsIds = Push_User.objects.filter(id__in=pushuserMaxIds, full_catalog_orders_only=True).order_by('-push').values_list('catalog', flat=True).distinct()
			elif sell_full_catalog.lower() == "false":
				catalogsIds = Push_User.objects.filter(id__in=pushuserMaxIds, full_catalog_orders_only=False).order_by('-push').values_list('catalog', flat=True).distinct()

		if catalogsIds is None:
			catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()

		catalogsIds = list(catalogsIds)
		#logger.info("catalogsIds sort by =")
		#logger.info(catalogsIds)
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(catalogsIds)])

		queryset = queryset.filter(id__in=catalogsIds).order_by(preserved)#.order_by('-id')
		if user.groups.filter(name="salesperson").exists(): #logic of viewType.lower()=="shared"
			catalogsIds = Push_User.objects.filter(selling_company=company).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()
			catalogsIds = list(catalogsIds)
			#logger.info("catalogsIds sort by =")
			#logger.info(catalogsIds)
			preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(catalogsIds)])

			queryset = queryset.filter(id__in=catalogsIds).order_by(preserved)#.distinct()

	elif viewType is not None and viewType.lower()=="shared":
		if user.groups.filter(name="salesperson").exists():
			catalogsIds = Push_User.objects.filter(selling_company=company).exclude(catalog__isnull=True).order_by('catalog').values_list('catalog', flat=True).distinct()

			queryset = queryset.filter(id__in=catalogsIds).order_by('-id').distinct()
		else:
			queryset = queryset.none()

	elif supplier_company is not None:
		print "if supplier_company is not None:"
	else:
		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
		catalogsIds = list(catalogsIds)
		if user.groups.filter(name="salesperson").exists():
			catalogsIds = Push_User.objects.filter(selling_company=company, catalog__in=catalogsIds).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
			catalogsIds = list(catalogsIds)

		#print action
		if action in ["retrieve", "suppliers", "all_suppliers", "enable", "disable"] or (follow_brand is not None and follow_brand.lower() == "true") or (trusted_seller is not None and trusted_seller.lower() == "true") or (brandIds is not None and brandIds != ""):
			cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True)
			# cscatalogids = CatalogSeller.objects.filter(selling_type="Public").values_list('catalog', flat=True).distinct()
			# ~ productcatalogs = Product.objects.filter(catalog__view_permission="public", catalog__in=cscatalogids).values_list('catalog', flat=True).distinct()
			# ~ queryset = queryset.filter(Q(company=company) | Q(id__in=catalogsIds) | Q(view_permission='public')).order_by('-id').distinct()

			userwishlists = []
			if user.is_authenticated():
				userwishlists = UserWishlist.objects.filter(user=user).exclude(catalog__deleted=True).values_list('catalog', flat=True).distinct()
				userwishlists = list(userwishlists)

			# ~ queryset = queryset.filter(Q(company=company) | Q(id__in=catalogsIds) | Q(id__in=productcatalogs) | Q(id__in=userwishlists)).order_by('-id').distinct()
			queryset = queryset.filter(Q(company=company) | Q(id__in=catalogsIds) | Q(id__in=cscatalogids, view_permission="public", total_products_uploaded__gt=0) | Q(id__in=userwishlists)).order_by('-id').distinct()
			# queryset = queryset.filter(Q(company=company) | Q(id__in=catalogsIds) | Q(id__in=cscatalogids, view_permission="public", total_products_uploaded__gt=0)).order_by('-id').distinct()
		else:
			cscatalogids = CatalogSeller.objects.filter(selling_type="Public", selling_company=company).values_list('catalog', flat=True)
			queryset = queryset.filter(Q(company=company) | Q(id__in=catalogsIds) | Q(id__in=cscatalogids)).order_by('-id').distinct()

	#if viewPermission is not None:
	if is_disable.lower() == 'false' and action in ["list"]:#, "dropdown"
		#logger.info("catalog before disable exclude len= %s"% (queryset.count()))
		queryset = queryset.exclude(id__in=disableCatalogIds)
		#queryset = queryset.exclude(id__in=myDisableCatalogIds)

	queryset = filterCatalog(queryset, company, params, user)
	queryset = sortCatalog(queryset, company, params)

	if trusted_seller is not None and trusted_seller.lower() == "true":
		queryset = queryset.order_by('-trusted_sort_order')

	return queryset

def filterSelection(queryset, company, params):
	from api.models import *
	min_price = params.get('min_price', None)
	max_price = params.get('max_price', None)
	work = params.get('work', None)
	fabric = params.get('fabric', None)
	title = params.get('title', None)
	#company_id = params.get('company', None)
	stock = params.get('stock', None)

	if min_price is not None and max_price is not None:
		selections = queryset.filter(user__companyuser__company=company).values_list('id', flat=True)
		selection2 =Selection.objects.filter(id__in=selections, products__price__range=(min_price, max_price)).values_list('id', flat=True)
		#queryset = queryset.filter(Q(company=company) | Q(id__in=catalogs2)).order_by('-id')

		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		selectionsIds = CompanyProductFlat.objects.filter((Q(buying_company=company) & Q(selling_company__in=sellingCompanyObj) & Q(is_disable=False)) & (Q(final_price__range=(min_price, max_price)) | Q(selling_price__range=(min_price, max_price)))).exclude(selection__isnull=True).values_list('selection', flat=True).distinct()

		#queryset = queryset.filter(Q(id__in=catalogsIds)).order_by('-id')
		queryset = queryset.filter(Q(id__in=selection2) | Q(id__in=selectionsIds)).order_by('-id')

	if work is not None:
		sProductIds = queryset.filter(user__companyuser__company=company).values_list('products', flat=True)
		sProductIds2 =ProductEAVFlat.objects.filter(Q(product__in=sProductIds) & (Q(work_text__icontains=work) | Q(work__icontains=work))).values_list('product', flat=True)
		#selection2 =Selection.objects.filter(id__in=selections, products__work__icontains=work).values_list('id', flat=True)

		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		productsIds = CompanyProductFlat.objects.filter((Q(buying_company=company) & Q(selling_company__in=sellingCompanyObj) & Q(is_disable=False))).exclude(selection__isnull=True).values_list('product', flat=True).distinct()# & Q(product__work__icontains=work)
		productsIds = ProductEAVFlat.objects.filter(Q(product__in=productsIds) & (Q(work_text__icontains=work) | Q(work__icontains=work))).values_list('product', flat=True)

		queryset = queryset.filter(Q(products__in=sProductIds2) | Q(products__in=productsIds)).order_by('-id')

	if fabric is not None:
		sProductIds = queryset.filter(user__companyuser__company=company).values_list('products', flat=True)
		sProductIds2 =ProductEAVFlat.objects.filter(Q(product__in=sProductIds) & (Q(fabric_text__icontains=fabric) | Q(fabric__icontains=fabric))).values_list('product', flat=True)
		#selection2 =Selection.objects.filter(id__in=selections, products__fabric__icontains=fabric).values_list('id', flat=True)

		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		productsIds = CompanyProductFlat.objects.filter((Q(buying_company=company) & Q(selling_company__in=sellingCompanyObj) & Q(is_disable=False))).exclude(selection__isnull=True).values_list('product', flat=True).distinct()
		productsIds = ProductEAVFlat.objects.filter(Q(product__in=productsIds) & (Q(fabric_text__icontains=fabric) | Q(fabric__icontains=fabric))).values_list('product', flat=True)

		queryset = queryset.filter(Q(products__in=sProductIds2) | Q(products__in=productsIds)).order_by('-id')

	if title is not None:
		titles = title.split(' ')
		queryset = queryset.filter(reduce(lambda x, y: x | y, [Q(name__icontains=title) for title in titles])).order_by('-id')

	if stock is not None:
		datomorrow = date.today() + timedelta(days=2)

		stock_arr = []
		for obj in queryset:
			pushUserObj=None
			cpfObj = CompanyProductFlat.objects.filter(selection=obj, buying_company=company, is_disable=False).last()

			if cpfObj:
				pushUserObj = Push_User.objects.filter(buying_company=company, selection=obj, push=cpfObj.push_reference).last()

			if pushUserObj:
				if stock == "prebook" and pushUserObj.push.exp_desp_date is not None and pushUserObj.push.exp_desp_date >= datomorrow:
					stock_arr.append(obj.id)
				elif stock == "instock" and (pushUserObj.push.exp_desp_date is None or pushUserObj.push.exp_desp_date < datomorrow):
					stock_arr.append(obj.id)
			else:
				print ""
		print stock_arr
		queryset = queryset.filter(id__in=stock_arr)

	return queryset.order_by('-id')

def allSegmentationUpdate():
	#from api.models import *
	from api.models import BuyerSegmentation, GroupType, Category, City
	logger.info("allSegmentationUpdate")
	cities = City.objects.all().values_list('id',flat=True)
	categories = Category.objects.all().values_list('id',flat=True)
	bs = BuyerSegmentation.objects.filter(segmentation_name__istartswith="All ")
	for bso in bs:
		tempcities = bso.city.all().values_list('id',flat=True)
		restcities = list(set(cities) - set(tempcities))

		tempcategories = bso.category.all().values_list('id',flat=True)
		restcategories = list(set(categories) - set(tempcategories))

		if len(restcities) > 0:
			bso.city.add(*restcities)

		if len(restcategories) > 0:
			bso.category.add(*restcategories)

	groups = GroupType.objects.all().values_list('id',flat=True)
	bs = BuyerSegmentation.objects.filter(segmentation_name="Send All")
	for bso in bs:
		tempgroups = bso.group_type.all().values_list('id',flat=True)
		restgroups = list(set(groups) - set(tempgroups))

		if len(restgroups) > 0:
			bso.group_type.add(*restgroups)


from api.tasks import *

def chat_user_profile(jsonarr):
	url = 'user/info?userIds='+jsonarr['userIds']

	r = requests.get(settings.APPLOZIC_URL+url, headers=settings.APPLOZIC_HEADERS)
	#r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get'), expires=datetime.now() + timedelta(days=2))
	print r
	print r.text

	return r

def chat_user_detail(jsonarr):
	url = 'user/detail?userIds='+jsonarr['userIds']
	r = requests.get(settings.APPLOZIC_URL+url, headers=settings.APPLOZIC_HEADERS)
	print r
	print r.text

	return r

def chat_user_registration(jsonarr, extra=None):
	#logger.info("in chat_user_registration")
	url = 'register/client'
	#r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr), extra, "chat_user_registration"), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr), extra, "chat_user_registration"
		)
	print r
	#print r.text

	return r

def chat_user_update(jsonarr):
	url = 'user/update?ofUserId='+jsonarr['ofUserId']
	#r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr)), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr)
		)
	print r
	#print r.text

	return r

def chat_user_exist(jsonarr):
	url = 'user/exist?userId='+jsonarr['userId']
	r = requests.get(settings.APPLOZIC_URL+url, headers=settings.APPLOZIC_HEADERS)
	print r
	print r.text

	return r

def chat_contact_list():
	url = 'user/filter'
	r = requests.get(settings.APPLOZIC_URL+url, headers=settings.APPLOZIC_HEADERS)
	print r
	print r.text

	return r

def chat_send_message(jsonarr):
	#logger.info("in chat_send_message")
	url = 'message/send?ofUserId='+jsonarr['ofUserId']
	#r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr), None, "chat_send_message"), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr), None, "chat_send_message"
		)
	print r
	#print r.text

	return r

def chat_send_broadcast_message(jsonarr):
	url = 'message/sendall?ofUserId='+jsonarr['ofUserId']
	#r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr)), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr)
		)
	print r
	#print r.text

	return r

def chat_message_list(jsonarr):
	url = 'message/list?ofUserId='+jsonarr['ofUserId']
	r = requests.get(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	print r
	print r.text

	return r

def chat_create_group(jsonarr, extra=None):
	#logger.info("in chat_create_group")
	url = 'group/v2/create?ofUserId='+jsonarr['ofUserId']
	#r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr), extra, "chat_create_group"), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'post', json.dumps(jsonarr), extra, "chat_create_group"
		)
	print r
	#print r.text

	return r

def chat_group_info(jsonarr):
	url = 'group/v2/info?groupId='+jsonarr['groupId']
	r = requests.get(settings.APPLOZIC_URL+url, headers=settings.APPLOZIC_HEADERS)
	print r
	print r.text

	return r

def chat_add_member_in_group(jsonarr):
	url = 'group/add/member?clientGroupId='+jsonarr['clientGroupId']+'&userId='+jsonarr['userId']+'&ofUserId='+jsonarr['ofUserId']
	#r = requests.get(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr)), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr)
		)
	print r
	#print r.text

	return r

def chat_add_members_in_groups(jsonarr):
	#logger.info("in chat_add_members_in_groups")
	url = 'group/add/users?ofUserId='+jsonarr['ofUserId']
	#r = requests.get(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr), None, "chat_add_members_in_groups"), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr), None, "chat_add_members_in_groups"
		)
	print r
	#print r.text

	return r

def chat_remove_member_from_group(jsonarr):
	url = 'group/remove/member?clientGroupId='+jsonarr['clientGroupId']+'&userId='+jsonarr['userId']+'&ofUserId='+jsonarr['ofUserId']
	#r = requests.get(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr)), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr)
		)
	print r
	#print r.text

	return r

def chat_remove_members_from_groups(jsonarr):
	#logger.info("in chat_remove_members_from_groups")
	url = 'group/remove/users?ofUserId='+jsonarr['ofUserId']
	#r = requests.get(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	r = None
	if settings.TASK_QUEUE_METHOD == 'celery':
		r = chatSend.apply_async((settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr), None, "chat_remove_members_from_groups"), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.chatSend',
			settings.APPLOZIC_URL+url, settings.APPLOZIC_HEADERS, 'get', json.dumps(jsonarr), None, "chat_remove_members_from_groups"
		)
	print r
	#print r.text

	return r

def chat_add_to_wishbook_group(userId):#master group
	r = chat_add_member_in_group({'clientGroupId':'767914', 'userId':userId, 'ofUserId':'admin'})
	print r
	print r.text

	return r

def is_phone_number_available(country, phone_number, check_verified):
	from django.contrib.auth.models import User, Group
	#from api.models import *
	from api.models import UserProfile, Company, CompanyPhoneAlias

	if check_verified: #verified='yes'
		if UserProfile.objects.filter(phone_number=phone_number, country=country, phone_number_verified='yes').exists() or Company.objects.filter(phone_number=phone_number, country=country, phone_number_verified='yes').exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exists():
			return False
	else:
		if UserProfile.objects.filter(phone_number=phone_number, country=country).exists() or Company.objects.filter(phone_number=phone_number, country=country).exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exists():
			return False

	return True

def companyBuyerGroupType(group_name):
	cbg_buyer_type = ""
	if group_name in ["Online-Retailer","Retailer"]:
		cbg_buyer_type = "Retailer"
	elif group_name in ["Broker"]:
		cbg_buyer_type = "Broker"
	else:
		cbg_buyer_type = "Wholesaler"
	return cbg_buyer_type

def companyBuyerGroupTypeToBuyerType(group_name):
	from api.models import GroupType
	if group_name == "Retailer":
		return GroupType.objects.filter(name__in=["Online-Retailer","Retailer"])
	elif group_name == "Broker":
		return GroupType.objects.filter(name__in=["Broker"])
	else:
		return GroupType.objects.all().exclude(name__in=["Online-Retailer","Retailer", "Broker"])

def getCompanyFromNumber(country, phone_number):
	from django.contrib.auth.models import User, Group
	#from api.models import *
	from api.models import UserProfile, CompanyUser, Company, CompanyPhoneAlias

	companyObj = None

	if UserProfile.objects.filter(country=country, phone_number=phone_number).exists():
		userprofile = UserProfile.objects.filter(country=country, phone_number=phone_number).first()
		if CompanyUser.objects.filter(user=userprofile.user).exists():
			companyObj = userprofile.user.companyuser.company
	elif Company.objects.filter(country=country, phone_number=phone_number).exists():
		companyObj = Company.objects.filter(country=country, phone_number=phone_number).first()
	elif CompanyPhoneAlias.objects.filter(country=country, alias_number=phone_number, status="Approved").exists():
		companyalias = CompanyPhoneAlias.objects.filter(country=country, alias_number=phone_number, status="Approved").first()
		companyObj = companyalias.company

	return companyObj

def getCompanyNumberFromNumber(country, phone_number):
	from django.contrib.auth.models import User, Group
	#from api.models import *
	from api.models import UserProfile, CompanyUser, Company, CompanyPhoneAlias, UnregisteredPhoneAlias

	if UserProfile.objects.filter(country=country, phone_number=phone_number).exists():
		userprofile = UserProfile.objects.filter(country=country, phone_number=phone_number).first()
		if CompanyUser.objects.filter(user=userprofile.user).exists():
			phone_number=userprofile.user.companyuser.company.phone_number
	elif Company.objects.filter(country=country, phone_number=phone_number).exists():
		print phone_number
	elif CompanyPhoneAlias.objects.filter(country=country, alias_number=phone_number, status="Approved").exists():
		companyalias = CompanyPhoneAlias.objects.filter(country=country, alias_number=phone_number, status="Approved").first()
		phone_number = companyalias.company.phone_number
	elif UnregisteredPhoneAlias.objects.filter(alias_country=country,alias_number=phone_number).exists():
		unregister = UnregisteredPhoneAlias.objects.filter(alias_country=country,alias_number=phone_number).first()
		phone_number = unregister.master_number
		country = unregister.master_country
	return [country, phone_number]

def add_buyer_v1(loginUser, loginCompany, buyer_name, country, buyer_number, group_type, is_raise_error, state=None, city=None, is_bulk=False, sendmessages=True, action_note=None, gst=None, pan=None):
	from django.contrib.auth.models import User, Group
	from api.models import *
	from api.v1.serializers import *
	#from api.v0.serializers import RegisterSerializer

	logger.info("in  add_buyer buyer_number = %s"% (str(buyer_number)))

	if loginUser.groups.filter(name="salesperson").exists() and loginUser.companyuser.deputed_to is not None:
		loginCompany = loginUser.companyuser.deputed_to
	else:
		loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	if state:
		state = State.objects.filter(state_name=state).first()
	if state is None or state == "":
		state = State.objects.filter(state_name="-").first()

	if city:
		city = City.objects.filter(city_name=city).first()
	if city is None or city == "":
		city = City.objects.filter(city_name="-").first()

	gst_pan_found = False
	if gst:
		kycObj = CompanyKycTaxation.objects.filter(gstin=gst).first()
		if kycObj:
			gst_pan_found = True
			if buyer_number != kycObj.company.phone_number:
				if not Company.objects.filter(phone_number=buyer_number).exists() and not UserProfile.objects.filter(phone_number=buyer_number).exists():
					#register buyer_number to kyc company
					jsondata = {"country":country.id, "phone_number":buyer_number, "invited_from":companyName, "state":state.id, "city":city.id, "company_id":kycObj.company.id, "user_group_type":"administrator"}
					jsondata_res = common_user_registration(jsondata, None, "send_invitee_sms")
				buyer_number = kycObj.company.phone_number
	if pan and gst_pan_found is False:
		kycObj = CompanyKycTaxation.objects.filter(pan=pan).first()
		if kycObj:
			gst_pan_found = True
			if buyer_number != kycObj.company.phone_number:
				if not Company.objects.filter(phone_number=buyer_number).exists() and not UserProfile.objects.filter(phone_number=buyer_number).exists():
					#register buyer_number to kyc company
					jsondata = {"country":country.id, "phone_number":buyer_number, "invited_from":companyName, "state":state.id, "city":city.id, "company_id":kycObj.company.id, "user_group_type":"administrator"}
					jsondata_res = common_user_registration(jsondata, None, "send_invitee_sms")
				buyer_number = kycObj.company.phone_number


	compnumber = getCompanyNumberFromNumber(country, buyer_number)
	country = compnumber[0]
	buyer_number = compnumber[1]

	if gst or pan:
		if gst_pan_found is False:
			if Company.objects.filter(country=country, phone_number=buyer_number).exists():
				buying_company = Company.objects.filter(country=country, phone_number=buyer_number).first()
				if CompanyKycTaxation.objects.filter(company=buying_company).exists():
					err = "Company exists but Gst or Pan not matching"
					if is_raise_error:
						raise serializers.ValidationError({"buyer_number":err})
					else:
						logger.info(err)
						return [buying_company, False, err, True]

	if not Company.objects.filter(country=country, phone_number=buyer_number).exists():
		if not UserProfile.objects.filter(country=country, phone_number=buyer_number).exists() or (action_note is not None and "company_registration" in action_note):

			jsondata = {"country":country.id, "phone_number":buyer_number, "invited_from":companyName, "state":state.id, "city":city.id}

			if action_note is not None and "company_registration" in action_note:
				jsondata["first_name"] = buyer_name
				jsondata["is_invitee_full_registration"] = True
				jsondata["company_name"] = buyer_name

			logger.info("jsondata = %s"% (jsondata))
			jsondata_res = common_user_registration(jsondata, None, "send_invitee_sms")

		#if action_note is None or "company_registration" not in action_note:
		if not Company.objects.filter(country=country, phone_number=buyer_number).exists():
			if Invitee.objects.filter(invite__company=loginCompany, invite__relationship_type="buyer", invitation_type="Buyer", country=country, invitee_number=buyer_number).exists():
				err = "You have already requested this buyer for approval"
				if is_raise_error:
					raise serializers.ValidationError({"buyer_number":err})
				else:
					logger.info(err)
					return [None, False, err, True]

			inviteobj = Invite.objects.create(relationship_type="buyer", company=loginCompany ,user=loginUser)
			inviteeObj = Invitee.objects.create(invitee_company=buyer_name,invitee_name=buyer_name,country=country,invitee_number=buyer_number,invite=inviteobj, status="invited", invite_type="userinvitation", invitation_type="Buyer")
			buyer = Buyer.objects.create(selling_company = loginCompany, status='buyer_registrationpending', invitee=inviteeObj, group_type=group_type, user=loginUser, buying_company_name=buyer_name, supplier_person_name=loginCompany.name, buying_person_name=buyer_name)
			#output = sendInvite(country.phone_code+buyer_number, str(companyName))
			return [None, True, None, True]

	buying_company = Company.objects.filter(country=country, phone_number=buyer_number).first()

	if Company.objects.filter(country=country, phone_number=buyer_number, id=loginCompany.id).exists():
		err = "You can not add your own user number"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, False]

	if CompanyType.objects.filter(company=buying_company, manufacturer=True, wholesaler_distributor=False, retailer=False, online_retailer_reseller=False, broker=False).exists() and loginCompany.id != 229:
		err = "Manufacturers cannot be invited as buyer"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, False]

	if gst_pan_found is False and gst is not None and pan is not None:
		if not CompanyKycTaxation.objects.filter(company=buying_company).exists():
			kycObj = CompanyKycTaxation.objects.create(company=buying_company, gstin=gst, pan=pan)

	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).exists():
		bObj = Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).first()
		bObj.group_type = group_type

		bObj.buying_company_name = buyer_name
		bObj.buying_person_name = buyer_name
		bObj.save()

		if bObj.invitee:
			bObj.invitee.invitee_company = buyer_name
			bObj.invitee.invitee_name = buyer_name
			bObj.invitee.save()

	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).exclude(Q(status="approved")|Q(status="rejected")).exists():
		err = "You have already requested this buyer for approval"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, True]
	#print buying_company.name
	#print buying_company.phone_number
	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company, status="approved").exists():
		err = "Buyer is already connected with you"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, True]
		'''logger.info("Buyer approved!")
		return buying_company'''

	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).exists():
		err = "Buyer has already responded"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, True]

	if is_bulk == False:
		inviteobj = Invite.objects.create(relationship_type="buyer", company=loginCompany ,user=loginUser)
		inviteeObj = Invitee.objects.create(invitee_company=buying_company.name,invitee_name=buyer_name,country=country,invitee_number=buyer_number,invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Buyer")

		status='buyer_pending'
		if buying_company.connections_preapproved == True:
			status='approved'

		payment_duration = 0
		discount = cash_discount = credit_limit = Decimal('0.00')
		cbg_buyer_type = companyBuyerGroupType(group_type.name)
		cbgObj = CompanyBuyerGroup.objects.filter(company=loginCompany, buyer_type=cbg_buyer_type).first()
		if cbgObj:
			print "cbgObj------", cbgObj
			discount = cbgObj.discount
			cash_discount = cbgObj.cash_discount
			credit_limit = cbgObj.credit_limit
			payment_duration = cbgObj.payment_duration

		buyer = Buyer.objects.create(selling_company = loginCompany, buying_company = buying_company, status=status, group_type=group_type, invitee=inviteeObj, user=loginUser, buying_company_name=buyer_name, supplier_person_name=loginCompany.name, buying_person_name=buyer_name, discount=discount, cash_discount=cash_discount, credit_limit=credit_limit, payment_duration=payment_duration)

		if sendmessages:
			requestNotification(buyer.selling_company, country.phone_code+buyer_number, "buyer", buyer, buyer.buying_company, status)

	#return buying_company
	return [buying_company, True, None, True]

def add_buyer(loginUser, loginCompany, buyer_name, country, buyer_number, group_type, is_raise_error, state=None, city=None, is_bulk=False, sendmessages=True):
	from django.contrib.auth.models import User, Group
	from api.models import *
	from api.v1.serializers import *
	from api.v0.serializers import RegisterSerializer

	logger.info("in  add_buyer buyer_number = %s"% (str(buyer_number)))

	if loginUser.groups.filter(name="salesperson").exists() and loginUser.companyuser.deputed_to is not None:
		loginCompany = loginUser.companyuser.deputed_to
	else:
		loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	compnumber = getCompanyNumberFromNumber(country, buyer_number)
	country = compnumber[0]
	buyer_number = compnumber[1]

	if not Company.objects.filter(country=country, phone_number=buyer_number).exists():
		otpno = random.randrange(100000, 999999, 1)
		username = str(country.phone_code)+str(buyer_number)
		username = username.replace("+", "")

		if state:
			state = State.objects.filter(state_name=state).first()
		if state is None or state == "":
			state = State.objects.filter(state_name="-").first()

		if city:
			city = City.objects.filter(city_name=city, state=state).first()
		if city is None or city == "":
			city = City.objects.filter(city_name="-").first()

		print "===state==="
		print state
		print city

		data = {"username":username, "password1": otpno, "password2": otpno, "phone_number":buyer_number, "country":country.id, "email":str(buyer_number)+"@wishbooks.io", "number_verified":"no", "is_profile_set":False, "company_name":buyer_name, "invited_from":companyName, "state":state.id, "city":city.id}
		register = RegisterSerializer(data=data)
		if register.is_valid():
			logger.info("save user register is_valid = %s"% (str(data)))
			try:
				registerObj = register.save(register)
				logger.info("registerObj = %s"% (str(registerObj)))
				sendmessages = False
			except Exception as e:
				logger.info("add_buyer registration error buyer_number = %s , error = %s"% (str(buyer_number), str(e)))
				pass
		else:
			logger.info("add_buyer is_valid() else registration error buyer_number = %s , error = %s"% (str(buyer_number), str(register.errors)))

	buying_company = Company.objects.filter(country=country, phone_number=buyer_number).first()

	if Company.objects.filter(country=country, phone_number=buyer_number, id=loginCompany.id).exists():
		err = "You can not add your own user number"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, False]

	if CompanyType.objects.filter(company=buying_company, manufacturer=True, wholesaler_distributor=False, retailer=False, online_retailer_reseller=False, broker=False).exists() and loginCompany.id != 229:
		err = "Manufacturers cannot be invited as buyer"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, False]

	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).exists():
		bObj = Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).first()
		bObj.group_type = group_type
		bObj.save()

	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).exclude(Q(status="approved")|Q(status="rejected")).exists():
		err = "You have already requested this buyer for approval"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, True]
	#print buying_company.name
	#print buying_company.phone_number
	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company, status="approved").exists():
		err = "Buyer is already connected with you"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, True]
		'''logger.info("Buyer approved!")
		return buying_company'''

	if Buyer.objects.filter(selling_company = loginCompany, buying_company = buying_company).exists():
		err = "Buyer has already responded"
		if is_raise_error:
			raise serializers.ValidationError({"buyer_number":err})
		else:
			logger.info(err)
			#return buying_company
			return [buying_company, False, err, True]

	if is_bulk == False:
		inviteobj = Invite.objects.create(relationship_type="buyer", company=loginCompany ,user=loginUser)
		inviteeObj = Invitee.objects.create(invitee_company=buying_company.name,invitee_name=buyer_name,country=country,invitee_number=buyer_number,invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Buyer")

		status='buyer_pending'
		if buying_company.connections_preapproved == True:
			status='approved'

		payment_duration = 0
		discount = cash_discount = credit_limit = Decimal('0.00')
		cbg_buyer_type = companyBuyerGroupType(group_type.name)
		cbgObj = CompanyBuyerGroup.objects.filter(company=loginCompany, buyer_type=cbg_buyer_type).first()
		if cbgObj:
			print "cbgObj------", cbgObj
			discount = cbgObj.discount
			cash_discount = cbgObj.cash_discount
			credit_limit = cbgObj.credit_limit
			payment_duration = cbgObj.payment_duration

		buyer = Buyer.objects.create(selling_company = loginCompany, buying_company = buying_company, status=status, group_type=group_type, invitee=inviteeObj, user=loginUser, buying_company_name=buyer_name, supplier_person_name=loginCompany.name, buying_person_name=buyer_name, discount=discount, cash_discount=cash_discount, credit_limit=credit_limit, payment_duration=payment_duration)

		if sendmessages:
			requestNotification(buyer.selling_company, country.phone_code+buyer_number, "buyer", buyer, buyer.buying_company, status)

	#return buying_company
	return [buying_company, True, None, True]

	'''else:

		if Invitee.objects.filter(country=country, invitee_number=buyer_number, invite__relationship_type="buyer").values_list('id', flat=True).exclude(invite__isnull=True).exists():
			inviteList = Invitee.objects.filter(country=country, invitee_number=buyer_number, invite__relationship_type="buyer").values_list('id', flat=True).exclude(invite__isnull=True).distinct()
			if Buyer.objects.filter(selling_company = loginCompany, invitee__in=inviteList).exists():
				if is_raise_error:
					raise serializers.ValidationError({"buyer_number":"You have already requested this buyer for approval"})
				else:
					logger.info("You have already requested this buyer for approval")
					return

		inviteobj = Invite.objects.create(relationship_type="buyer", company=loginCompany ,user=loginUser)
		inviteeObj = Invitee.objects.create(invitee_name=buyer_name,country=country,invitee_number=buyer_number,invite=inviteobj, status="invited", invite_type="userinvitation", invitation_type="Buyer")
		buyer = Buyer.objects.create(selling_company = loginCompany, status='buyer_registrationpending', invitee=inviteeObj, group_type=group_type)
		output = sendInvite(country.phone_code+buyer_number, str(companyName))
	'''

def add_supplier_v1(loginUser, loginCompany, supplier_name, country, supplier_number, group_type, is_raise_error, state=None, city=None, sendmessages=True):
	from django.contrib.auth.models import User, Group
	from api.models import *
	from api.v1.serializers import *
	#from api.v0.serializers import RegisterSerializer

	logger.info("in  add_supplier_v1 supplier_number = %s"% (str(supplier_number)))

	companyName = loginCompany.name

	compnumber = getCompanyNumberFromNumber(country, supplier_number)
	country = compnumber[0]
	supplier_number = compnumber[1]

	if not Company.objects.filter(country=country, phone_number=supplier_number).exists():
		if not UserProfile.objects.filter(country=country, phone_number=supplier_number).exists():
			if state:
				state = State.objects.filter(state_name=state).first()
			if state is None or state == "":
				state = State.objects.filter(state_name="-").first()

			if city:
				city = City.objects.filter(city_name=city, state=state).first()
			if city is None or city == "":
				city = City.objects.filter(city_name="-").first()

			jsondata = {"country":country.id, "phone_number":supplier_number, "invited_from":companyName, "state":state.id, "city":city.id}
			jsondata_res = common_user_registration(jsondata, None, "send_invitee_sms")

		if Invitee.objects.filter(invite__company=loginCompany, invite__relationship_type="supplier", invitation_type="Supplier", country=country, invitee_number=supplier_number).exists():
			err = "You have already requested this supplier for approval"
			if is_raise_error:
				raise serializers.ValidationError({"supplier_number":err})
			else:
				logger.info(err)
				return None

		inviteobj = Invite.objects.create(relationship_type="supplier", company=loginCompany ,user=loginUser)
		inviteeObj = Invitee.objects.create(invitee_company=supplier_name,invitee_name=supplier_name,country=country,invitee_number=supplier_number,invite=inviteobj, status="invited", invite_type="userinvitation", invitation_type="Supplier")
		buyer = Buyer.objects.create(buying_company = loginCompany, status='supplier_registrationpending', invitee=inviteeObj, group_type=group_type, user=loginUser, buying_company_name=loginCompany.name, supplier_person_name=supplier_name, buying_person_name=loginCompany.name)
		#output = sendInvite(country.phone_code+supplier_number, str(companyName))
		return None

	selling_company = Company.objects.filter(country=country, phone_number=supplier_number).first()

	if Company.objects.filter(country=country, phone_number=supplier_number, id=loginCompany.id).exists():
		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"You can not add your own user number"})
		else:
			logger.info("You can not add your own user number")
			return selling_company

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exclude(Q(status="approved")|Q(status="rejected")).exists():
		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"You have already requested this supplier for approval"})
		else:
			logger.info("You have already requested this supplier for approval")
			return selling_company

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany, status="approved").exists():
		logger.info("Supplier approved!")
		return selling_company

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exists():
		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"You are rejected by this supplier"})
		else:
			logger.info("You are rejected by this supplier")
			#logger.info("Supplier has already responded")
			return selling_company

	inviteobj = Invite.objects.create(relationship_type="supplier", company=loginCompany ,user=loginUser)
	inviteeObj = Invitee.objects.create(invitee_company=selling_company.name,invitee_name=supplier_name,country=country,invitee_number=supplier_number,invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Supplier")

	status='supplier_pending'
	if selling_company.connections_preapproved == True:
		status='approved'

	payment_duration = 0
	discount = cash_discount = credit_limit = Decimal('0.00')
	cbg_buyer_type = companyBuyerGroupType(group_type.name)
	cbgObj = CompanyBuyerGroup.objects.filter(company=selling_company, buyer_type=cbg_buyer_type).first()
	if cbgObj:
		print "cbgObj------", cbgObj
		discount = cbgObj.discount
		cash_discount = cbgObj.cash_discount
		credit_limit = cbgObj.credit_limit
		payment_duration = cbgObj.payment_duration

	buyer = Buyer.objects.create(selling_company = selling_company, buying_company = loginCompany, status=status, group_type=group_type, invitee=inviteeObj, user=loginUser, buying_company_name=loginCompany.name, supplier_person_name=supplier_name, buying_person_name=loginCompany.name, discount=discount, cash_discount=cash_discount, credit_limit=credit_limit, payment_duration=payment_duration)

	if sendmessages:
		requestNotification(buyer.buying_company, country.phone_code+supplier_number, "supplier", buyer, buyer.selling_company, status)

	return selling_company


def add_supplier(loginUser, loginCompany, supplier_name, country, supplier_number, group_type, is_raise_error, state=None, city=None, sendmessages=True):
	from django.contrib.auth.models import User, Group
	from api.models import *
	from api.v1.serializers import *
	from api.v0.serializers import RegisterSerializer

	print "add_supplier"

	companyName = loginCompany.name

	compnumber = getCompanyNumberFromNumber(country, supplier_number)
	country = compnumber[0]
	supplier_number = compnumber[1]

	if not Company.objects.filter(country=country, phone_number=supplier_number).exists():
		otpno = random.randrange(100000, 999999, 1)
		username = str(country.phone_code)+str(supplier_number)
		username = username.replace("+", "")

		if state:
			state = State.objects.filter(state_name=state).first()
		if state is None or state == "":
			state = State.objects.filter(state_name="-").first()

		if city:
			city = City.objects.filter(city_name=city, state=state).first()
		if city is None or city == "":
			city = City.objects.filter(city_name="-").first()

		print "===state==="
		print state
		print city

		data = {"username":username, "password1": otpno, "password2": otpno, "phone_number":supplier_number, "country":country.id, "email":str(supplier_number)+"@wishbooks.io", "number_verified":"no", "is_profile_set":False, "company_name":supplier_name, "invited_from":companyName, "state":state.id, "city":city.id}
		register = RegisterSerializer(data=data)
		if register.is_valid():
			logger.info("save user register is_valid = %s"% (str(data)))
			try:
				registerObj = register.save(register)
				logger.info("registerObj = %s"% (str(registerObj)))
				sendmessages = False
			except Exception as e:
				logger.info("add_supplier registration error supplier_number = %s , error = %s"% (str(supplier_number), str(e)))
				pass
		else:
			logger.info("add_supplier is_valid() else registration error supplier_number = %s , error = %s"% (str(supplier_number), str(register.errors)))

	selling_company = Company.objects.filter(country=country, phone_number=supplier_number).first()

	if Company.objects.filter(country=country, phone_number=supplier_number, id=loginCompany.id).exists():
		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"You can not add your own user number"})
		else:
			logger.info("You can not add your own user number")
			return selling_company

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exclude(Q(status="approved")|Q(status="rejected")).exists():
		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"You have already requested this supplier for approval"})
		else:
			logger.info("You have already requested this supplier for approval")
			return selling_company

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany, status="approved").exists():
		logger.info("Supplier approved!")
		return selling_company

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exists():
		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"You are rejected by this supplier"})
		else:
			logger.info("You are rejected by this supplier")
			#logger.info("Supplier has already responded")
			return selling_company

	inviteobj = Invite.objects.create(relationship_type="supplier", company=loginCompany ,user=loginUser)
	inviteeObj = Invitee.objects.create(invitee_company=selling_company.name,invitee_name=supplier_name,country=country,invitee_number=supplier_number,invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Supplier")

	status='supplier_pending'
	if selling_company.connections_preapproved == True:
		status='approved'

	payment_duration = 0
	discount = cash_discount = credit_limit = Decimal('0.00')
	cbg_buyer_type = companyBuyerGroupType(group_type.name)
	cbgObj = CompanyBuyerGroup.objects.filter(company=selling_company, buyer_type=cbg_buyer_type).first()
	if cbgObj:
		print "cbgObj------", cbgObj
		discount = cbgObj.discount
		cash_discount = cbgObj.cash_discount
		credit_limit = cbgObj.credit_limit
		payment_duration = cbgObj.payment_duration

	buyer = Buyer.objects.create(selling_company = selling_company, buying_company = loginCompany, status=status, group_type=group_type, invitee=inviteeObj, user=loginUser, buying_company_name=loginCompany.name, supplier_person_name=supplier_name, buying_person_name=loginCompany.name, discount=discount, cash_discount=cash_discount, credit_limit=credit_limit, payment_duration=payment_duration)

	if sendmessages:
		requestNotification(buyer.buying_company, country.phone_code+supplier_number, "supplier", buyer, buyer.selling_company, status)

	return selling_company

	'''else:

		if Invitee.objects.filter(country=country, invitee_number=supplier_number, invite__relationship_type="supplier").values_list('id', flat=True).exclude(invite__isnull=True).exists():
			inviteList = Invitee.objects.filter(country=country, invitee_number=supplier_number, invite__relationship_type="supplier").values_list('id', flat=True).exclude(invite__isnull=True).distinct()
			if Buyer.objects.filter(buying_company = loginCompany, invitee__in=inviteList).exists():
				if is_raise_error:
					raise serializers.ValidationError({"supplier_number":"You have already requested this supplier for approval"})
				else:
					logger.info("You have already requested this supplier for approval")
					return

		inviteobj = Invite.objects.create(relationship_type="supplier", company=loginCompany ,user=loginUser)
		inviteeObj = Invitee.objects.create(invitee_name=supplier_name,country=country,invitee_number=supplier_number,invite=inviteobj, status="invited", invite_type="userinvitation", invitation_type="Supplier")
		buyer = Buyer.objects.create(buying_company = loginCompany, status='supplier_registrationpending', invitee=inviteeObj, group_type=group_type)

		output = sendInvite(country.phone_code+supplier_number, str(companyName))
	'''

def sendAllTypesMessage(send_type, userObjs, context):
	from django.contrib.auth.models import User, Group
	from api.models import *
	from django.db.models import Value
	from django.db.models.functions import Concat

	from django.template.loader import render_to_string
	from django.conf import settings
	from django.core.mail import send_mail
	from django.template import loader
	import random

	logger.info("in sendAllTypesMessage send_type = %s"% (send_type))
	phone_numbers = UserProfile.objects.filter(user__in=userObjs).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
	unsubscribed_numbers = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
	phone_numbers = list(set(phone_numbers) - set(unsubscribed_numbers))
	# print phone_numbers

	user_ids = userObjs.values_list('id', flat=True)
	user_ids = list(user_ids)
	# print user_ids

	rno = random.randrange(100000, 999999, 1)
	image = settings.MEDIA_URL+"logo-single.png"

	if send_type == "supplier_enquiry":
		template = smsTemplates("requestNotification_supplierenquiry")% (context['company_name'], context['catalog_title'])
		smsSend(phone_numbers, template)
		logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

		message = notificationTemplates("requestNotification_supplierenquiry")% (context['company_name'], context['catalog_title'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	logger.info("in sendAllTypesMessage send notification celery")
		# 	notificationSend.apply_async((user_ids, context['company_name']+" has added enquiry for catalog "+context['catalog_title']+" on Wishbook", {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	logger.info("in sendAllTypesMessage send notification djangoQ")
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, context['company_name']+" has added enquiry for catalog "+context['catalog_title']+" on Wishbook", {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

		'''logger.info("in sendAllTypesMessage send chat message")
		for user in userObjs:
			chat_send_message({"ofUserId":context['username'], "to":str(user.username), "message":context['company_name']+" has added enquiry for catalog "+context['catalog_title']+" on Wishbook"})'''

		emails = userObjs.exclude(email__icontains="@wishbooks.io").values_list('email',flat=True)
		if len(emails) > 0:
			try:
				logger.info("in send emails")
				html_message = loader.render_to_string('email_templates/enquiry.html', context)

				if settings.TASK_QUEUE_METHOD == 'celery':
					logger.info("in send celery")
					emailSend.apply_async(("You have 1 new enquiry on Wishbook !!!", "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message), expires=datetime.now() + timedelta(days=2))
				elif settings.TASK_QUEUE_METHOD == 'djangoQ':
					logger.info("in send djangoQ")
					task_id = async(
						'api.tasks.emailSend',
						"You have 1 new enquiry on Wishbook !!!", "", settings.DEFAULT_FROM_EMAIL, emails, html_message
					)
			except Exception:
				pass

	elif send_type == "buyersupplier_status":
		if context['buyer_type'] == "Relationship":
			# message = context['company_name']+" has changed relationship status to "+context['status']
			message = notificationTemplates("buyersupplier_status_1")% (context['company_name'], context['status'])
			'''template = smsTemplates("requestNotification_Relationship_buyersupplier_status")% (context['company_name'], context['status'])

			logger.info("in sendAllTypesMessage send bulk sms")
			smsSend(phone_numbers, template)'''
		else:
			if context['status'] in ["approved", "rejected"]:
				# message = "Your enquiry has been "+context['status']+" by "+context['company_name']
				message = notificationTemplates("buyersupplier_status_2")% (context['status'], context['company_name'])
				if context['status'] == "approved":
					#template = smsTemplates("requestNotification_approve_reject_buyersupplier_status")% (context['status'], context['company_name'])
					template = smsTemplates("requestNotification_approve_reject_buyersupplier_status")% (context['company_name'])
					smsSend(phone_numbers, template)
					logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))
			else:
				# message = "Your enquiry from "+context['company_name']+" has been updated to "+context['status']
				message = notificationTemplates("buyersupplier_status_3")% (context['company_name'], context['status'])
				#template = smsTemplates("requestNotification_enquiry_buyersupplier_status")% (context['company_name'], context['status'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "default_supplier_not_approved":
		for user in userObjs:
			phone_number = [str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)]
			phone_number = list(set(phone_number) - set(unsubscribed_numbers))
			otp = getLastOTP(user.userprofile)
			usersmsurl = 'https://app.wishbooks.io/m?type=buyer&id='+str(context['table_id'])+'&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
			usersmsurl = urlShortener(usersmsurl)

			template = smsTemplates("requestNotification_supplier")% (context['company_name'], usersmsurl)
			smsSend(phone_number, template)
			logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

		# message = context['company_name']+" has added you as a Supplier on Wishbook."
		message = notificationTemplates("requestNotification_supplier")% (context['company_name'])
		sendNotifications(user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "default_supplier_approved":
		for user in userObjs:
			phone_number = [str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)]
			phone_number = list(set(phone_number) - set(unsubscribed_numbers))
			otp = getLastOTP(user.userprofile)
			usersmsurl = 'https://app.wishbooks.io/m?type=buyer&id='+str(context['table_id'])+'&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
			usersmsurl = urlShortener(usersmsurl)

			template = smsTemplates("requestNotification_default_supplier_approved")% (context['company_name'], usersmsurl)
			smsSend(phone_number, template)
			logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

		# message = context['company_name']+" has added you as a Supplier on Wishbook."
		message = notificationTemplates("requestNotification_default_supplier_approved")% (context['company_name'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

		'''logger.info("in sendAllTypesMessage send chat message")
		for user in userObjs:
			chat_send_message({"ofUserId":context['username'], "to":str(user.username), "message":message})'''

	elif send_type == "default_buyer_not_approved":
		for user in userObjs:
			phone_number = [str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)]
			phone_number = list(set(phone_number) - set(unsubscribed_numbers))
			otp = getLastOTP(user.userprofile)
			usersmsurl = 'https://app.wishbooks.io/m?type=supplier&id='+str(context['table_id']) + '&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
			usersmsurl = urlShortener(usersmsurl)

			template = smsTemplates("requestNotification_buyer")% (context['company_name'], usersmsurl)
			smsSend(phone_number, template)
			logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

		# message = context['company_name']+" has added you as a Buyer on Wishbook"
		message = notificationTemplates("requestNotification_buyer")% (context['company_name'])
		sendNotifications(user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "default_buyer_approved":
		for user in userObjs:
			phone_number = [str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)]
			phone_number = list(set(phone_number) - set(unsubscribed_numbers))
			otp = getLastOTP(user.userprofile)
			usersmsurl = 'https://app.wishbooks.io/m?type=supplier&id='+str(context['table_id']) + '&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
			usersmsurl = urlShortener(usersmsurl)

			template = smsTemplates("requestNotification_default_buyer_approved")% (context['company_name'], usersmsurl)
			smsSend(phone_number, template)
			logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

		# message = context['company_name']+" has added you as a Buyer on Wishbook."
		message = notificationTemplates("requestNotification_default_buyer_approved")% (context['company_name'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

		'''logger.info("in sendAllTypesMessage send chat message")
		for user in userObjs:
			chat_send_message({"ofUserId":context['username'], "to":str(user.username), "message":message})'''

	elif send_type == "send_order_on_credit":
		message = notificationTemplates("send_order_on_credit")
		sendNotifications(user_ids, message, {"notId": context['table_id'], "title":context['title'], "push_type":"promotional", "table_id":context['table_id'], "image":image})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "salesorder_pending":
		logger.info("in salesorder_pending")

		#message = "You have received an order "+str(context['table_id'])
		orderObj = SalesOrder.objects.get(pk=context['table_id'])
		if not (orderObj.payment_status() == "Pending" and orderObj.order_type == "Prepaid"):
			message = notificationTemplates("salesOrder_sales")
			# if settings.TASK_QUEUE_METHOD == 'celery':
			# 	notificationSend.apply_async((user_ids, message, {"notId": context['table_id'], "title":context['title'], "push_type":"promotional", "table_id":context['table_id'], "image":image}), expires=datetime.now() + timedelta(days=2))
			# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			# 	task_id = async(
			# 		'api.tasks.notificationSend',
			# 		user_ids, message, {"notId": context['table_id'], "title":context['title'], "push_type":"promotional", "table_id":context['table_id'], "image":image}
			# 	)
			sendNotifications(user_ids, message, {"notId": context['table_id'], "title":context['title'], "push_type":"promotional", "table_id":context['table_id'], "image":image})
			logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

			for user in userObjs:
				phone_number = [str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)]
				phone_number = list(set(phone_number) - set(unsubscribed_numbers))

				otp = getLastOTP(user.userprofile)

				usersmsurl = str(context['order_url']) + '&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
				#time.sleep(1)
				usersmsurl = urlShortener(usersmsurl)

				# template = smsTemplates("salesOrder_sales")% (str(context['table_id']), context['company_info'], usersmsurl)
				template = smsTemplates("salesOrder_sales")% (usersmsurl)
				smsSend(phone_number, template)
				logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

	elif send_type == "purchaseorder_pending":
		# message = "Your order "+str(context['table_id'])+" has been successfully placed"
		message = notificationTemplates("salesOrder_purchase")% ("", str(context['table_id']), "is")
		#template = smsTemplates("salesOrder_purchase")% (str(context['table_id']))
		template = smsTemplates("salesOrder_purchase")% ("", str(context['table_id']), "is")

		orderObj = SalesOrder.objects.get(pk=context['table_id'])
		if orderObj.payment_status() == "Pending" and orderObj.order_type == "Prepaid":
			message = notificationTemplates("salesOrder_purchase_2")% ("", str(context['table_id']), "is")
			template = smsTemplates("salesOrder_purchase_2")% ("", str(context['table_id']), "is")
		sendNotifications(user_ids, message, {"notId": context['table_id'], "title":context['title'], "push_type":"promotional", "table_id":context['table_id'], "image":image})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

		smsSend(phone_numbers, template)
		logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

	elif send_type == "purchaseorder_accepted":
		logger.info("in purchaseorder_accepted")

		sendAllTypesMessage("purchaseorder_pending", userObjs, context)

		for user in userObjs:
			logger.info("in purchaseorder_accepted send email")
			if "@wishbooks.io" not in user.email:
				try:
					html_message = loader.render_to_string('email_templates/purchase_order.html', context)

					#mail_status = send_mail("Your order "+context['order_number']+" has been successfully placed", "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)
					if settings.TASK_QUEUE_METHOD == 'celery':
						emailSend.apply_async(("Your order "+str(context['table_id'])+" has been successfully placed", "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message), expires=datetime.now() + timedelta(days=2))
					elif settings.TASK_QUEUE_METHOD == 'djangoQ':
						task_id = async(
							'api.tasks.emailSend',
							"Your order "+str(context['table_id'])+" has been successfully placed", "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message
						)

				except Exception:
					pass

	elif send_type == "add_buyers_broker":
		# message = "Broker "+context['broker_name']+" connected you with "+str(context['total_buyers'])+" buyers"
		message = notificationTemplates("add_buyers_broker")% (context['broker_name'], context['total_buyers'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((user_ids, message, {"notId": context['notId'], "title":"Added buyers by broker", "push_type":"promotional", "image":image}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, message, {"notId": context['notId'], "title":"Added buyers by broker", "push_type":"promotional", "image":image}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "title":"Added buyers by broker", "push_type":"promotional", "image":image})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "add_suppliers_broker":
		# message = context['broker_name']+" connected you with "+context['supplier_name']+", You can now buy his catalogs on supplier credit from Wishbook"
		message = notificationTemplates("add_suppliers_broker")% (context['broker_name'], context['supplier_name'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((user_ids, message, {"notId": context['notId'], "title":"Added suppliers by broker", "push_type":"promotional", "image":image}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, message, {"notId": context['notId'], "title":"Added suppliers by broker", "push_type":"promotional", "image":image}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "title":"Added suppliers by broker", "push_type":"promotional", "image":image})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "salesorder_broker":
		# message = "Broker "+context['broker_name']+" just created an order for one of your catalogs. Check it out!"
		message = notificationTemplates("salesorder_broker")% (context['broker_name'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((user_ids, message, {"notId": context['notId'], "title":"Salesorder created by broker", "push_type":"promotional", "image":image}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, message, {"notId": context['notId'], "title":"Salesorder created by broker", "push_type":"promotional", "image":image}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "title":"Salesorder created by broker", "push_type":"promotional", "image":image})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "purchaseorder_broker":
		# message = context['broker_name']+" just created an order on your behalf. Check it out!"
		message = notificationTemplates("purchaseorder_broker")% (context['broker_name'])
		# if settings.TASK_QUEUE_METHOD == 'celery':
		# 	notificationSend.apply_async((user_ids, message, {"notId": context['notId'], "title":"Purchase order created by broker", "push_type":"promotional", "image":image}), expires=datetime.now() + timedelta(days=2))
		# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		# 	task_id = async(
		# 		'api.tasks.notificationSend',
		# 		user_ids, message, {"notId": context['notId'], "title":"Purchase order created by broker", "push_type":"promotional", "image":image}
		# 	)
		sendNotifications(user_ids, message, {"notId": context['notId'], "title":"Purchase order created by broker", "push_type":"promotional", "image":image})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "shipment": #copy of notifier str(notification_type) == "order-status":
		# message = "Your order "+str(context['table_id'])+" is "+context['status']+". Track details by logging into Wishbook. Thank you for choosing us."
		message = notificationTemplates("shipment_1")% (context['table_id'], context['status'])
		if context.has_key('action'):
			if context['action'] == 'update':
				# message = "Your shipment of order "+str(context['table_id'])+" is updated. Track details by logging into Wishbook. Thank you for choosing us."
				message = notificationTemplates("shipment_2")% (context['table_id'])
		sendNotifications(user_ids, message, {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "cart_payment":
		# message = "Your Cart "+str(context['table_id'])+" is "+context['status']+". Track details by logging into Wishbook. Thank you for choosing us."
		message = notificationTemplates("cart_payment")% (context['table_id'], context['status'])
		sendNotifications(user_ids, message, {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id'], "type":"tab", "other_para":{"deep_link":str(settings.GLOBAL_SITE_URL)+"?type=tab&page=order/purchaseorder/total"}})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "send_order_status": #copy of notifier str(notification_type) == "order-status":
		message = notificationTemplates("salesOrder_status")% (str(context['table_id']), context['status'])
		sendNotifications(user_ids, message, {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

		# template = smsTemplates("salesOrder_status")% (str(context['table_id']), context['status'])
		# smsSend(phone_numbers, template)

		for user in userObjs:
			phone_number = [str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)]
			phone_number = list(set(phone_number) - set(unsubscribed_numbers))

			otp = getLastOTP(user.userprofile)

			usersmsurl = str(context['order_url']) + '&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
			#time.sleep(1)
			usersmsurl = urlShortener(usersmsurl)

			template = smsTemplates("salesOrder_status")% (str(context['table_id']), context['status'], usersmsurl)
			smsSend(phone_number, template)

			logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

	elif send_type == "share":
		# message = '%s has shared with you a catalog - %s'% (context['selling_company_name'], context['message'])
		message = notificationTemplates("share")% (context['selling_company_name'], context['message'])
		sendNotifications(user_ids, message, {"push_id": context['push_id'],"notId":context['notId'],"push_type":context['push_type'],"image":context['image'], "company_image":context['company_image'], "title":context['title'], "name":context['name'], "table_id": context['table_id']})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

	elif send_type == "daily_1_share_sms":
		message = notificationTemplates("daily_1_share_sms")% (context['total_catalogs'])
		sendNotifications(user_ids, message, {"notId": rno, "title":"Catalogs Received", "push_type":"catalog", "type":"catalog", "image":context['image'], "other_para":{"ctype":"received"}})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))

		for user in userObjs:
			if "+91" not in user.userprofile.country.phone_code:
				continue

			phone_number = [str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)]
			phone_number = list(set(phone_number) - set(unsubscribed_numbers))
			# otp = getLastOTP(user.userprofile)
			otp = None
			if user.userprofile.is_profile_set == False:
				otp = getLastOTP(user.userprofile)
			if otp is None:
				otp = generateNewOTP(user.userprofile)
			usersmsurl = 'https://app.wishbooks.io/?m='+str(user.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(user.userprofile.country.id)+'&t=page&id=received'
			usersmsurl = urlShortener(usersmsurl)

			template = smsTemplates("daily_1_share_sms")% (context['total_catalogs'], usersmsurl)
			if settings.TASK_QUEUE_METHOD == 'celery':
				smsSendTextNationPromotional.apply_async((phone_number, template, True), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
					'api.tasks.smsSendTextNationPromotional',
					phone_number, template, True
				)
			logger.info("in sendAllTypesMessage send_type = %s, sms template = %s"% (send_type, template))

			usnObj, created = UserSendNotification.objects.get_or_create(user=user, created_at=date.today())
			usnObj.send_sms = usnObj.send_sms + 1
			usnObj.save()

	elif send_type == "background_task_status":
		print context
		message = notificationTemplates("background_task_status")% (context['completed_rows'], context['total_rows'], context['errors'])
		sendNotifications(user_ids, message, {"notId": context['notId'], "title":context['title'], "push_type":"promotional"})
		logger.info("in sendAllTypesMessage send_type = %s, notification message = %s"% (send_type, message))


	return True

def add_supplier_enquiry(loginUser, loginCompany, supplier_name, selling_company, details, is_raise_error, catalog, data):
	catalog_title = catalog.title
	companyName = loginCompany.name

	from django.contrib.auth.models import User, Group
	from api.models import *
	from api.v1.serializers import *
	from api.v0.serializers import RegisterSerializer


	print "add_supplier_enquiry"

	if loginCompany.id == selling_company.id:
		if is_raise_error:
			raise serializers.ValidationError({"catalog":"You can not send enquiry on your own catalog"})
		else:
			logger.info("You can not send enquiry on your own catalog")
			return

	ceObj = CatalogEnquiry.objects.create(enquiry_type="Text", catalog=catalog, selling_company=selling_company, buying_company=loginCompany, item_type=data.get('enquiry_item_type',None), item_quantity=data.get('enquiry_quantity',0))


	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exclude(Q(status="approved")|Q(status="rejected")).exists():
		buyerObj = Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exclude(Q(status="approved")|Q(status="rejected")).first()
		buyerObj.buyer_type = "Enquiry"
		buyerObj.created_type = "Enquiry"
		buyerObj.save()

		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"You have already requested this supplier for approval"})
		else:
			logger.info("You have already requested this supplier for approval")
			return

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany, status="approved").exists():
		buyerObj = Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany, status="approved").first()
		logger.info("Supplier approved!")

		jsondata = {}
		jsondata['company'] = buyerObj.selling_company.id
		jsondata['company_name'] = buyerObj.selling_company.name
		jsondata['company_chat_admin_user'] = buyerObj.selling_company.chat_admin_user.username
		jsondata['company_phone_number'] = buyerObj.selling_company.phone_number
		jsondata['success'] = "You are already connected to this supplier"
		#from rest_framework.response import Response
		return jsondata #Response(jsondata)

	if Buyer.objects.filter(selling_company = selling_company, buying_company = loginCompany).exists():
		if is_raise_error:
			raise serializers.ValidationError({"supplier_number":"Supplier has already responded"})
		else:
			logger.info("Supplier has already responded")
			return

	inviteobj = Invite.objects.create(relationship_type="supplier", company=loginCompany ,user=loginUser)
	inviteeObj = Invitee.objects.create(invitee_company=selling_company.name,invitee_name=supplier_name,country=selling_company.country,invitee_number=selling_company.phone_number, invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Supplier")

	status='supplier_pending'
	#if selling_company.connections_preapproved == True:
	#	status='approved'

	enquiry_item_type = data.get('enquiry_item_type', None)
	enquiry_quantity = data.get('enquiry_quantity', 0)

	buyer = Buyer.objects.create(selling_company = selling_company, buying_company = loginCompany, status=status, invitee=inviteeObj, buyer_type="Enquiry", created_type="Enquiry", details=details, user=loginUser, enquiry_catalog=catalog, enquiry_item_type=enquiry_item_type, enquiry_quantity=enquiry_quantity, buying_company_name=loginCompany.name, buying_person_name=loginCompany.name, supplier_person_name=supplier_name)

	#requestNotification(buyer.buying_company, country.phone_code+supplier_number, "supplier", buyer, buyer.selling_company, status)
	user1 = CompanyUser.objects.filter(company=selling_company).values_list('user', flat=True)
	user1 = User.objects.filter(id__in=user1, groups__name="administrator")
	company_image = None
	if buyer.buying_company.thumbnail:
		company_image = buyer.buying_company.thumbnail.url
	elif Brand.objects.filter(company=buyer.buying_company).exists():
		brandObj = Brand.objects.filter(company=buyer.buying_company).only('image').first()
		if brandObj:
			company_image = brandObj.image.thumbnail[settings.MEDIUM_IMAGE].url
	username = CompanyUser.objects.filter(company=buyer.buying_company).values_list('user__username', flat=True).first()
	jsonarr = {}
	jsonarr['company_name'] = buyer.buying_company.name
	jsonarr['table_id'] = buyer.id
	jsonarr['notId'] = buyer.id
	jsonarr['push_type'] = "supplier_enquiry"
	jsonarr['company_id'] = buyer.buying_company.id
	jsonarr['title'] = "Buyer Request"
	jsonarr['company_image'] = company_image
	jsonarr['username'] = username
	jsonarr['catalog_title'] = catalog_title

	sendAllTypesMessage("supplier_enquiry", user1, jsonarr)

	return True

def sendNotifications(userids, message, exjson, notification_type=None):
	logger.info("in sendNotifications function")
	if settings.TASK_QUEUE_METHOD == 'celery':
		notificationSend.apply_async((userids, message, exjson, notification_type), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		'''if isScheduledTime():
			schedule('api.tasks.notificationSend',
				userids, message, exjson, notification_type,
				schedule_type=Schedule.ONCE,
				next_run=getScheduledTime()
			)
		else:'''
		task_id = async(
			'api.tasks.notificationSend',
			userids, message, exjson, notification_type
		)

def smsSend(mobile_numbers, message, email_on_err=False, send_without_queue=False):
	from api.models import Config
	logger.info("in smsSend function, mobile_numbers = ")
	logger.info(mobile_numbers)
	logger.info(message)

	if send_without_queue:
		logger.info("send_without_queue")
		mobile_nos = mobile_numbers

		if settings.DEBUG:
			logger.info("NOT sending SMS if settings.DEBUG=True")
			return True #for local development

		PRIORITY_SMS_METHOD = Config.objects.get(key="PRIORITY_SMS_METHOD").value

		if PRIORITY_SMS_METHOD == 'smsSendSendSmart': #settings.
			logger.info("send_without_queue smsSendSendSmart")
			smsSendSendSmart(mobile_nos, message, email_on_err)
		elif PRIORITY_SMS_METHOD == 'smsSendICubes':
			logger.info("send_without_queue smsSendICubes")
			smsSendICubes(mobile_nos, message, email_on_err)
		elif PRIORITY_SMS_METHOD == 'smsSendTextNation':
			logger.info("send_without_queue smsSendTextNation")
			smsSendTextNation(mobile_nos, message, email_on_err, send_without_queue)
		else:
			logger.info("send_without_queue not send sms method")
	else:
		logger.info("send_in_queue")
		mobile_nos = []
		logger.info(mobile_numbers)
		for mn in mobile_numbers:
			#logger.info(mn)
			if "+91" in mn:
				mobile_nos.append(mn)

		logger.info("final mobile_nos only +91 = ")
		logger.info(mobile_nos)

		if len(mobile_nos) == 0:
			return True

		if settings.DEBUG:
			logger.info("NOT sending SMS if settings.DEBUG=True")
			return True #for local development

		SMS_METHOD = Config.objects.get(key="SMS_METHOD").value

		if SMS_METHOD == 'smsSendSendSmart': #settings.
			logger.info("in_queue smsSendSendSmart")
			if settings.TASK_QUEUE_METHOD == 'celery':
				smsSendSendSmart.apply_async((mobile_nos, message, email_on_err), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				if isScheduledTime():
					schedule('api.tasks.smsSendSendSmart',
						mobile_nos, message, email_on_err,
						schedule_type=Schedule.ONCE,
						next_run=getScheduledTime(),
						q_options={'broker': priority_broker}
					)
				else:
					task_id = async(
						'api.tasks.smsSendSendSmart',
						mobile_nos, message, email_on_err
					)
		elif SMS_METHOD == 'smsSendICubes':
			logger.info("in_queue smsSendICubes")
			if settings.TASK_QUEUE_METHOD == 'celery':
				smsSendICubes.apply_async((mobile_nos, message, email_on_err), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				if isScheduledTime():
					schedule('api.tasks.smsSendICubes',
						mobile_nos, message, email_on_err,
						schedule_type=Schedule.ONCE,
						next_run=getScheduledTime(),
						q_options={'broker': priority_broker}
					)
				else:
					task_id = async(
						'api.tasks.smsSendICubes',
						mobile_nos, message, email_on_err
					)
		elif SMS_METHOD == 'smsSendTextNation':
			logger.info("in_queue smsSendTextNation")
			if settings.TASK_QUEUE_METHOD == 'celery':
				smsSendTextNation.apply_async((mobile_nos, message, email_on_err, send_without_queue), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				'''if isScheduledTime():
					schedule('api.tasks.smsSendTextNation',
						mobile_nos, message, email_on_err, send_without_queue,
						schedule_type=Schedule.ONCE,
						next_run=getScheduledTime(),
						q_options={'broker': priority_broker}
					)
				else:'''
				task_id = async(
					'api.tasks.smsSendTextNation',
					mobile_nos, message, email_on_err, send_without_queue
				)
				'''if True:
					import arrow
					from django_q.tasks import schedule
					from django_q.models import Schedule

					schedule('api.tasks.smsSendTextNation',
						mobile_nos, message, email_on_err,
						schedule_type=Schedule.ONCE,
						next_run=datetime.now().replace(hour=19, minute=0)
					)
					#next_run=arrow.utcnow().replace(hour=18, minute=50)
				'''
		else:
			logger.info("in_queue not send sms")

def orderToMediator(salesorder):#, selling_company, buying_company
	#order
	from api.models import *
	print "orderToMediator"
	selling_company = salesorder.seller_company
	buying_company = salesorder.company

	buying_mapped_accout = None
	if CompanyAccount.objects.filter(company=selling_company, buyer_company=buying_company).exists():
		buying_mapped_accout = CompanyAccount.objects.filter(company=selling_company, buyer_company=buying_company).first().mapped_accout_ref

	selling_mapped_accout = None
	if CompanyAccount.objects.filter(company=buying_company, buyer_company=selling_company).exists():
		selling_mapped_accout = CompanyAccount.objects.filter(company=buying_company, buyer_company=selling_company).first().mapped_accout_ref

	jsonarr = {}
	jsonarr["order_number"] = salesorder.order_number
	jsonarr["amount"] = str(salesorder.total_rate())

	items = SalesOrderItem.objects.filter(sales_order=salesorder.id)

	headers={'Content-Type': 'application/json'}

	#sales order
	appinsObj = AppInstance.objects.filter(company=selling_company).first()
	print appinsObj
	if appinsObj is not None and appinsObj.account_url != "" and appinsObj.account_url is not None and buying_mapped_accout is not None:
		print appinsObj
		selling_account_url = appinsObj.account_url
		print selling_account_url
		#selling_account_url = AppInstance.objects.filter(company=selling_company).first().account_url
		itemarrs = []

		for item in items:
			itemarr = {}
			itemarr["quantity"] = str(item.quantity)
			itemarr["rate"] = str(item.rate)
			#itemarr["sku"] = item.product.sku
			if SKUMap.objects.filter(app_instance__company=selling_company, product=item.product).exists():
				itemarr["sku"] = SKUMap.objects.filter(app_instance__company=selling_company, product=item.product).first().external_sku
				itemarrs.append(itemarr)
		jsonarr["items"] = itemarrs

		jsonarr["order_type"] = "sales"
		#jsonarr["company_name"] = buying_company.name
		#if buying_mapped_accout is not None:
		jsonarr["company_name"] = buying_mapped_accout

		jsonarrsales = json.dumps(jsonarr)

		if len(jsonarr["items"]) > 0:
			response = requests.request("POST", selling_account_url+"salesorder/", data=jsonarrsales, headers=headers)

			print jsonarrsales
			print response
			response = response.json()
			print response
			print response['id']
			salesorder.sales_reference_id = response['id']
			salesorder.save()

	#purchase order
	appinsObj = AppInstance.objects.filter(company=buying_company).first()
	if appinsObj is not None and appinsObj.account_url != "" and appinsObj.account_url is not None and selling_mapped_accout is not None:
		buying_account_url = appinsObj.account_url
		#buying_account_url = AppInstance.objects.filter(company=buying_company).first().account_url
		itemarrs = []

		for item in items:
			itemarr = {}
			itemarr["quantity"] = str(item.quantity)
			itemarr["rate"] = str(item.rate)
			#itemarr["sku"] = item.product.sku
			if SKUMap.objects.filter(app_instance__company=buying_company, product=item.product).exists():
				itemarr["sku"] = SKUMap.objects.filter(app_instance__company=buying_company, product=item.product).first().external_sku
				itemarrs.append(itemarr)
		jsonarr["items"] = itemarrs

		jsonarr["order_type"] = "purchase"
		#jsonarr["company_name"] = selling_company.name
		#if selling_mapped_accout is not None:
		jsonarr["company_name"] = selling_mapped_accout

		jsonarrpurchase = json.dumps(jsonarr)

		if len(jsonarr["items"]) > 0:
			response = requests.request("POST", buying_account_url+"purchaseorder/", data=jsonarrpurchase, headers=headers)

			response = response.json()
			print response['id']
			salesorder.purchase_reference_id = response['id']
			salesorder.save()

def inventoryUpdateFromServer(company):
	#from api.models import *
	from api.models import Warehouse, SKUMap
	from api.v1.serializers import *
	print "inventoryUpdateFromServer"

	headers={'Content-Type': 'application/json'}
	response = requests.request("GET", "http://127.0.0.1:8001/api/inventory/", headers=headers)

	warehouse = Warehouse.objects.filter(company=company).first()
	jsonarr = {}
	jsonarr['date'] = date.today()
	jsonarr['warehouse'] = warehouse.id

	openingstockqty = []

	response = response.json()
	#print response
	for skupro in response:
		stock = {}
		stock['in_stock'] = int(skupro['stock'])
		skumap = SKUMap.objects.filter(app_instance__company=company, external_sku=skupro['sku']).first()
		if skumap:
			stock['product'] = skumap.product.id
		else:
			continue
			'''product = Product.objects.filter(sku=skupro['sku']).first()
			if product:
				stock['product'] = product.id
			else:
				continue'''
		openingstockqty.append(stock)

	jsonarr['openingstockqty_set'] = openingstockqty

	print jsonarr
	oss = OpeningStockSerializer(data=jsonarr)
	if oss.is_valid():
		print "valid"
		oss.save()

	else:
		print "not valid error="
		print oss.errors
	#oss.save()

'''def updateOrderStatus(salesorder):
	#order
	from api.models import *
	print "updateOrderStatus"
	selling_company = salesorder.seller_company
	buying_company = salesorder.company

	buying_mapped_accout = None
	if CompanyAccount.objects.filter(company=selling_company, buyer_company=buying_company).exists():
		buying_mapped_accout = CompanyAccount.objects.filter(company=selling_company, buyer_company=buying_company).first().mapped_accout_ref

	selling_mapped_accout = None
	if CompanyAccount.objects.filter(company=buying_company, buyer_company=selling_company).exists():
		selling_mapped_accout = CompanyAccount.objects.filter(company=buying_company, buyer_company=selling_company).first().mapped_accout_ref'''

def updateOrderStatus(company):
	#from api.models import *
	from api.models import SalesOrder
	from api.v1.serializers import *
	print "updateOrderStatus"

	sales_reference_id = SalesOrder.objects.filter(seller_company=company, processing_status__in=('Pending', 'Accepted')).exclude(sales_reference_id__isnull=True).values_list('sales_reference_id', flat=True).distinct().order_by('sales_reference_id')
	purchase_reference_id = SalesOrder.objects.filter(company=company, processing_status__in=('Pending', 'Accepted')).exclude(purchase_reference_id__isnull=True).values_list('purchase_reference_id', flat=True).distinct().order_by('purchase_reference_id')
	sales_reference_id = list(sales_reference_id)
	purchase_reference_id = list(purchase_reference_id)
	print sales_reference_id

	if len(sales_reference_id) > 0:
		jsonarr={}
		jsonarr['vno'] = ", ".join([str(rid) for rid in sales_reference_id])
		jsonarrsales = json.dumps(jsonarr)

		headers={'Content-Type': 'application/json'}
		response = requests.request("GET", "http://127.0.0.1:8001/api/status/", data=jsonarrsales, headers=headers)
		response = response.json()
		print response

		for obj in response:
			print obj['vno']
			SalesOrder.objects.filter(sales_reference_id=obj['vno']).update(processing_status='Dispatched')

		print response

	if len(purchase_reference_id) > 0:
		jsonarr={}
		jsonarr['vno'] = ", ".join([str(rid) for rid in purchase_reference_id])
		jsonarrsales = json.dumps(jsonarr)

		headers={'Content-Type': 'application/json'}
		response = requests.request("GET", "http://127.0.0.1:8001/api/status/", data=jsonarrsales, headers=headers)
		response = response.json()
		print response

		for obj in response:
			print obj['vno']
			SalesOrder.objects.filter(purchase_reference_id=obj['vno']).update(processing_status='Dispatched')

		print response

def generateOrderToInvoice(order_id, amount, mode, fulljson, user, transaction_id=None, todaydate=date.today(), details=None):
	from api.models import *
	from datetime import datetime, date, time, timedelta
	from api.v1.serializers import InvoiceSerializer
	# # from api.v0.notifications import *
	# from notifier.shortcuts import send_notification
	# from api.v0.notifier_backend import *

	##order = SalesOrder.objects.get(pk=int(order_id))
	order = None
	invoice = Invoice.objects.filter(id=int(order_id)).first()
	if invoice is None:
		#order = SalesOrder.objects.get(pk=int(order_id))
		order = SalesOrder.objects.filter(id=int(order_id)).first()
		if order is None:
			raise serializers.ValidationError({"invoice":"Order not found. Please try again later"})

		if not Invoice.objects.filter(order=order).exists():
			#invoice = Invoice.objects.create(order=order, amount=order.total_rate(), total_qty=order.total_item(), paid_amount=float(0), pending_amount=order.total_rate(), payment_status="Pending")
			print "========creating invoice using serializer"
			invoiceitems = []
			for item in order.items.all():
				invoiceitems.append({"order_item":item.id, "qty":item.pending_quantity})

			jsondata = {"order":order.id, "invoiceitem_set":invoiceitems}
			invser = InvoiceSerializer(data=jsondata)
			if invser.is_valid():
				print "invser.save()"
				invoice = invser.save()
			else:
				print "invser.errors"
				invoice = invser.errors
				print invoice
				raise serializers.ValidationError({"invoice":"Invoice not found. Please try again later"})

		else:
			invoice = Invoice.objects.filter(order=order).first()
	else:
		order = invoice.order

	'''invoice = None
	if not Invoice.objects.filter(order=order).exists():
		invoice = Invoice.objects.create(order=order, amount=order.total_rate(), total_qty=order.total_item(), paid_amount=float(0), pending_amount=order.total_rate(), payment_status="Pending")
	else:
		invoice = Invoice.objects.filter(order=order).first()'''

	pending_amount = float(invoice.pending_amount)-float(amount)

	if mode == "PayTM":
		if fulljson['STATUS'] == "TXN_SUCCESS":
			payment_status = 'Success'
		else:
			payment_status = 'Failure'
	elif mode == "Mobikwik":
		if int(fulljson['statuscode']) == 0:
			payment_status = 'Success'
		else:
			payment_status = 'Failure'
	elif mode == "Zaakpay":
		if int(fulljson['responseCode']) == 100:
			payment_status = 'Success'
		else:
			payment_status = 'Failure'
	else:
		payment_status = 'Success'

	if pending_amount < float(1) and payment_status == 'Success':
		order_payment_status = "Paid"
	else:
		order_payment_status = "Pending"

	order_payment_details = "Mode : "+str(mode)+"\n"+"Status : "+order_payment_status+"\n"

	if transaction_id:
		order_payment_details = order_payment_details + "TransactionId : "+str(transaction_id)+"\n"

	if details:
		order_payment_details = order_payment_details + "Details : "+str(details)+"\n"

	if order_payment_status == "Paid":
		order.customer_status = "Paid"

	order.payment_details = order_payment_details
	order.payment_date = todaydate

	order.save()

	#~ if payment_status == 'Failure':
		#~ invoice.status = "Cancelled"

	if payment_status == 'Success':
		invoice.paid_amount = float(invoice.paid_amount) + float(amount)
		invoice.pending_amount = pending_amount

	invoice.payment_status = order_payment_status
	invoice.save()

	for item in order.items.all():
		InvoiceItem.objects.get_or_create(invoice=invoice, order_item=item, qty=item.quantity)

	if mode == "PayTM":
		payment_details = fulljson
	elif mode == "Zaakpay":
		payment_details = fulljson
	else:
		payment_details = order_payment_details

	if mode.lower() == "other":
		mode = "Other"

	paymentObj = Payment.objects.create(mode=mode, by_company=order.company, to_company=order.seller_company, amount=amount, status=payment_status, details=payment_details, transaction_reference=transaction_id)#, user=user
	paymentObj.invoice = [invoice.id]
	paymentObj.save()
	#PaymentInvoice.objects.create(invoice=invoice, amount=amount, transaction_reference=transaction_id)
	if payment_status == 'Success':
		jsonarr = {}
		jsonarr['order_number'] = order.order_number
		jsonarr['table_id'] = order.id
		jsonarr['status'] = order.payment_status() #"Paid"
		jsonarr['title'] = "Sales Order "+order.payment_status()+" "+str(amount)
		jsonarr['order_url'] = str(settings.GLOBAL_SITE_URL)+'?type=sales&id='+str(order.id)

		broker_users = []
		if order.broker_company is not None:
			broker_users=CompanyUser.objects.filter(company=order.broker_company).values_list('user', flat=True).distinct()

		user1 = order.seller_company.company_users.values_list('user', flat=True)
		user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson")

		# send_notification('order-status', user1, jsonarr)
		sendAllTypesMessage("send_order_status", user1, jsonarr)

def generateInvoicePayment(invoice_id, amount, mode, fulljson, payment_status, user, transaction_id=None, todaydate=date.today(), details=None, offline_payment=False):
	logger.info("In generateInvoicePayment() function invoice_id = %s, todaydate = %s, amount = %s, mode = %s"% (invoice_id, todaydate, amount, mode))
	from api.models import *
	from datetime import datetime, date, time, timedelta
	# # from api.v0.notifications import *
	# from notifier.shortcuts import send_notification
	# from api.v0.notifier_backend import *

	#from api.v1.serializers import *
	#invoice = Invoice.objects.get(pk=int(invoice_id))
	invoice = Invoice.objects.filter(id=int(invoice_id)).last()
	if invoice is None:
		return
	order = invoice.order

	pending_amount = float(invoice.pending_amount)-float(amount)
	# offline_payment = False

	# if mode == "PayTM":
	# 	if fulljson['STATUS'] == "TXN_SUCCESS":
	# 		payment_status = 'Success'
	# 	else:
	# 		payment_status = 'Failure'
	# elif mode == "Mobikwik":
	# 	if int(fulljson['statuscode']) == 0:
	# 		payment_status = 'Success'
	# 	else:
	# 		payment_status = 'Failure'
	if mode == "Zaakpay":
		# if int(fulljson['responseCode']) == 100:
		# 	payment_status = 'Success'
		# else:
		# 	payment_status = 'Failure'

		if amount < invoice.total_amount:
			amount10per = invoice.total_amount * 10 /100
			codAmnt = amount10per
			if 500 > amount10per:
				codAmnt = 500
			#codAmnt = 500 > (invoice.total_amount * 10 /100) ? 500 : (invoice.total_amount * 10 /100)

			if int(amount) == int(codAmnt):
				mode = "COD"
				#invoice.mode = "COD"
			logger.info("generateInvoicePayment amount10per = %s, codAmnt = %s, amount = %s, mode = %s"% (amount10per, codAmnt, amount, mode))
	# elif mode == "COD":#only for cart to order on COD mode
	# 	if int(fulljson['responseCode']) == 100:
	# 		payment_status = 'Success'
	# 	else:
	# 		payment_status = 'Failure'
	# else:#staus pending
	# 	#payment_status = 'Success'
	# 	if user.is_staff:
	# 		payment_status = 'Success'
	# 	else:
	# 		payment_status = 'Pending' #changes for cheque, neft, other, .. payment status should be pending
	# 		offline_payment = True



	if pending_amount < float(1) and payment_status == 'Success':
		order_payment_status = "Paid"
	elif mode == "COD" and invoice.pending_amount > 0:
		order_payment_status = "Partially Paid"
	else:
		order_payment_status = "Pending"

	order_payment_details = "Mode : "+str(mode)+"\n"+"Status : "+order_payment_status+"\n"

	if transaction_id:
		order_payment_details = order_payment_details + "TransactionId : "+str(transaction_id)+"\n"

	if details:
		try:
			order_payment_details = order_payment_details + "Details : "+str(details)+"\n"
		except Exception as e:
			logger.info("in generateInvoicePayment order_payment_details error = %s" % (str(e)))
			pass

	if mode == "COD":
		order_payment_details = order_payment_details +"Paid Amount: "+str(amount)+"\nPending Amount: "+str(pending_amount)+"\n"

	if order_payment_status == "Paid":
		order.customer_status = "Paid"

	order.payment_details = order_payment_details
	order.payment_date = todaydate

	if mode == "COD" and payment_status == "Success":
		if order.processing_status in ["Cart", "Draft", "Pending"]:
			order.processing_status = "COD Verification Pending"
	elif payment_status == "Success" or offline_payment == True:
		if order.processing_status in ["Cart", "Draft"]:
			order.processing_status = "Pending"

	order.save()

	#~ if payment_status == 'Failure':
		#~ invoice.status = "Cancelled"

	if payment_status == 'Success' or offline_payment == True:
		invoice.paid_amount = float(invoice.paid_amount) + float(amount)
		invoice.pending_amount = pending_amount


	invoice.payment_status = order_payment_status
	invoice.save()

	if mode == "PayTM":
		payment_details = fulljson
	elif mode == "Zaakpay" or mode == "COD":
		payment_details = fulljson
	else:
		payment_details = order_payment_details

	if mode.lower() == "other":
		mode = "Other"

	paymentObj = Payment.objects.create(mode=mode, by_company=order.company, to_company=order.seller_company, amount=amount, status=payment_status, details=payment_details, transaction_reference=transaction_id)#, user=user
	paymentObj.invoice = [invoice.id]
	paymentObj.save()

	if payment_status == 'Success' or offline_payment == True:
		jsonarr = {}
		jsonarr['order_number'] = order.order_number
		jsonarr['table_id'] = order.id
		jsonarr['status'] = order.payment_status() #"Paid"
		jsonarr['title'] = "Sales Order "+order.payment_status()+" "+str(amount)
		jsonarr['order_url'] = str(settings.GLOBAL_SITE_URL)+'?type=sales&id='+str(order.id)

		broker_users = []
		if order.broker_company is not None:
			broker_users=CompanyUser.objects.filter(company=order.broker_company).values_list('user', flat=True).distinct()

		user1 = order.seller_company.company_users.values_list('user', flat=True)
		user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson")

		# send_notification('order-status', user1, jsonarr)
		sendAllTypesMessage("send_order_status", user1, jsonarr)

		if order.cart is None: #not sending notification to buyer if order created from cart as buyer gets notification of cart so
			jsonarr['title'] = "Purchase Order "+order.payment_status()+" "+str(amount)
			jsonarr['order_url'] = str(settings.GLOBAL_SITE_URL)+'?type=purchase&id='+str(order.id)

			user1 = order.company.company_users.values_list('user', flat=True)
			user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson")

			# send_notification('order-status', user1, jsonarr)
			sendAllTypesMessage("send_order_status", user1, jsonarr)

def generateCartPayment(cart_id, amount, mode, fulljson, payment_status, user, transaction_id=None, todaydate=date.today(), details=None, offline_payment=False):
	logger.info("In generateCartPayment() function cart_id = %s, todaydate = %s, amount = %s, mode = %s"% (cart_id, todaydate, amount, mode))
	from api.models import *
	from datetime import datetime, date, time, timedelta
	# # from api.v0.notifications import *
	# from notifier.shortcuts import send_notification
	# from api.v0.notifier_backend import *
	from api.v1.order.serializers import CartPaymentSerializer

	#from api.v1.serializers import *
	#invoice = Invoice.objects.get(pk=int(invoice_id))
	# invoice = Invoice.objects.filter(id=int(invoice_id)).last()
	# if invoice is None:
	# 	return
	# order = invoice.order

	cart = Cart.objects.filter(id=int(cart_id)).last()
	if cart is None:
		return

	pending_amount = float(cart.pending_amount)-float(amount)
	# offline_payment = False

	# if mode == "PayTM":
	# 	if fulljson['STATUS'] == "TXN_SUCCESS":
	# 		payment_status = 'Success'
	# 	else:
	# 		payment_status = 'Failure'
	# elif mode == "Mobikwik":
	# 	if int(fulljson['statuscode']) == 0:
	# 		payment_status = 'Success'
	# 	else:
	# 		payment_status = 'Failure'
	if mode == "Zaakpay":
		# if int(fulljson['responseCode']) == 100:
		# 	payment_status = 'Success'
		# else:
		# 	payment_status = 'Failure'

		if amount < cart.total_amount:
			amount10per = cart.total_amount * 10 /100
			codAmnt = amount10per
			if 500 > amount10per:
				codAmnt = 500
			#codAmnt = 500 > (invoice.total_amount * 10 /100) ? 500 : (invoice.total_amount * 10 /100)

			if int(amount) == int(codAmnt):
				mode = "COD"
				#invoice.mode = "COD"
			logger.info("generateCartPayment amount10per = %s, codAmnt = %s, amount = %s, mode = %s"% (amount10per, codAmnt, amount, mode))

	# else:
	# 	if user.is_staff:
	# 		payment_status = 'Success'
	# 	else:
	# 		payment_status = 'Pending' #changes for cheque, neft, other, .. payment status should be pending
	# 		offline_payment = True



	if pending_amount < float(1) and payment_status == 'Success':
		order_payment_status = "Paid"
	elif mode == "COD" and cart.pending_amount > 0:
		order_payment_status = "Partially Paid"
	else:
		order_payment_status = "Pending"

	order_payment_details = "Mode : "+str(mode)+"\n"+"Status : "+order_payment_status+"\n"

	if transaction_id:
		order_payment_details = order_payment_details + "TransactionId : "+str(transaction_id)+"\n"

	if details:
		try:
			order_payment_details = order_payment_details + "Details : "+str(details)+"\n"
		except Exception as e:
			logger.info("in generateCartPayment order_payment_details error = %s" % (str(e)))
			pass

	if mode == "COD":
		order_payment_details = order_payment_details +"Paid Amount: "+str(amount)+"\nPending Amount: "+str(pending_amount)+"\n"

	# if order_payment_status == "Paid":
	# 	order.customer_status = "Paid"

	cart.payment_status = order_payment_status

	cart.payment_details = order_payment_details
	cart.payment_date = todaydate

	if mode == "COD" and payment_status == "Success":
		cart.processing_status = "COD Verification Pending"
	elif payment_status == "Success" or offline_payment == True:
		cart.processing_status = "Pending"

	cart.save()

	#~ if payment_status == 'Failure':
		#~ invoice.status = "Cancelled"

	# if payment_status == 'Success' or offline_payment == True:
	# 	invoice.paid_amount = float(invoice.paid_amount) + float(amount)
	# 	invoice.pending_amount = pending_amount
	#
	#
	# invoice.payment_status = order_payment_status
	# invoice.save()

	if mode == "PayTM":
		payment_details = fulljson
	elif mode == "Zaakpay" or mode == "COD":
		payment_details = fulljson
	else:
		payment_details = order_payment_details

	if mode.lower() == "other":
		mode = "Other"

	# paymentObj = Payment.objects.create(mode=mode, by_company=order.company, to_company=order.seller_company, amount=amount, status=payment_status, details=payment_details, transaction_reference=transaction_id)#, user=user
	# paymentObj.invoice = [invoice.id]
	# paymentObj.save()

	serializer = CartPaymentSerializer(data={'mode':mode, 'cart':cart.id, 'amount':amount, 'status':payment_status, 'payment_details':payment_details, 'user':user.id})
	if serializer.is_valid():
		serializer.save()
	else:
		raise serializers.ValidationError({"error":serializer.errors})

	#notification on cart payment or order creation ??

	if payment_status == 'Success' or offline_payment == True:
		jsonarr = {}
		jsonarr['order_number'] = cart.order_number
		jsonarr['table_id'] = cart.id
		jsonarr['status'] = cart.payment_status
		jsonarr['title'] = "Cart Order "+cart.payment_status+" "+str(amount)

		user1 = cart.buying_company.company_users.values_list('user', flat=True)
		user1 = User.objects.filter(Q(id__in=user1)).exclude(groups__name="salesperson")

		sendAllTypesMessage("cart_payment", user1, jsonarr)





def geocode(lat, lng):
	geo_url = "https://maps.googleapis.com/maps/api/geocode/json?key="+settings.PUSH_NOTIFICATIONS_SETTINGS['GCM_API_KEY']+"&latlng="+str(lat)+","+str(lng)

	print geo_url
	geodata = requests.get(geo_url)
	data = geodata.json()

	return data

def dfsShareNotification(sellingCompanyObj, buyingCompanyObj, pushObj, catalogObj, message, pushType, pushImage, pushName, companyImage, sendsms=True):
	from api.models import *
	from datetime import datetime, date, timedelta
	# # from api.v0.notifications import *
	# from notifier.shortcuts import send_notification
	# from api.v0.notifier_backend import *
	from django.db.models import Value
	from django.db.models.functions import Concat
	import time

	logger.info("In dfsShareNotification() function for sms n notification start at "+str(datetime.now()))
	logger.info(pushName)

	title = ""
	if pushType.lower()=="catalog":
		title = "Received new catalog"
	else:
		title = "Received new selection"

	smsurl = 'https://app.wishbooks.io/m?type=catalog&id='+str(catalogObj.id)
	#whatsappurl = 'http://app.wishbooks.io/m?type=catalog&id='+str(catalogObj.id)
	brandName = catalogObj.brand.name


	users = CompanyUser.objects.filter(company=buyingCompanyObj).values_list('user', flat=True).distinct()
	logger.info("users = %s" % (users))

	if sendsms: #for not sending last 7 notification reason
		jsonarr = {}
		jsonarr['message'] = message+" ("+brandName+")"
		jsonarr['push_id'] = pushObj.id
		jsonarr['notId'] = pushObj.id
		jsonarr['push_type'] = pushType
		jsonarr['image'] = pushImage
		jsonarr['company_image'] = companyImage
		jsonarr['title'] = title
		jsonarr['name'] = pushName
		jsonarr['table_id'] = catalogObj.id

		jsonarr['brand_name'] = brandName
		jsonarr['selling_company_name'] = sellingCompanyObj.name

		usersOjbs = User.objects.filter(id__in=users, groups__name="administrator")

		usn_user_exclude = UserSendNotification.objects.filter(user__in=usersOjbs, created_at=date.today(), send_gcm__gte = settings.SHARE_SMS_LIMIT).values_list('user', flat=True)
		usersOjbs = usersOjbs.exclude(id__in=usn_user_exclude)

		userids = usersOjbs.values_list('id', flat=True)
		#send_notification('share', usersOjbs, jsonarr)
		messagenotificiation = '%s has shared with you a catalog - %s'% (jsonarr['selling_company_name'], jsonarr['message'])
		sendNotifications(list(userids), messagenotificiation, {"push_id": jsonarr['push_id'],"notId":jsonarr['notId'],"push_type":jsonarr['push_type'],"image":jsonarr['image'], "company_image":jsonarr['company_image'], "title":jsonarr['title'], "name":jsonarr['name'], "table_id": jsonarr['table_id']})

		for userObj in usersOjbs:
			usnObj, created = UserSendNotification.objects.get_or_create(user=userObj, created_at=date.today())
			usnObj.send_gcm = usnObj.send_gcm + 1
			usnObj.save()

	logger.info("is sendsms flag = %s" % (sendsms))
	if (pushObj.sms.lower() == "yes" and pushType.lower() == "catalog") and sendsms:#to send messages always
		logger.info("in sendsms")
		usn_user_exclude = UserSendNotification.objects.filter(user__in=users, created_at=date.today(), send_sms__gte = settings.SHARE_SMS_LIMIT).values_list('user', flat=True)
		'''phone_number = UserProfile.objects.filter(user__in=users, user__groups__name="administrator").exclude(user__in=usn_user_exclude).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
		unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
		phone_number = list(set(phone_number) - set(unsubscribed_number))
		#template = smsTemplates("push")% (brandName, message, smsurl)
		template = smsTemplates("share")% (sellingCompanyObj.name, message+" ("+brandName+")", smsurl)
		print template
		smsSend(phone_number, template)'''
		unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()

		smsUser = UserProfile.objects.filter(user__in=users, user__groups__name="administrator").exclude(user__in=usn_user_exclude)

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

			template = smsTemplates("share")% (sellingCompanyObj.name, message+" ("+brandName+")", usersmsurl)
			#smsSend(phone_number, template, True
			logger.info("in_queue smsSendTextNationPromotional")
			if settings.TASK_QUEUE_METHOD == 'celery':
				smsSendTextNationPromotional.apply_async((phone_number, template, True), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
					'api.tasks.smsSendTextNationPromotional',
					phone_number, template, True
				)

			usnObj, created = UserSendNotification.objects.get_or_create(user=userPObj.user, created_at=date.today())
			usnObj.send_sms = usnObj.send_sms + 1
			usnObj.save()

def shareOnApproves(selling_company, buying_company):
	#to disable this function
	return True

	from api.models import *
	from datetime import datetime, date, time, timedelta
	# # from api.v0.notifications import *
	# from notifier.shortcuts import send_notification
	# from api.v0.notifier_backend import *
	from django.db.models import Value
	from django.db.models.functions import Concat
	from django.db.models import Sum, Min, Max, Count

	logger.info("In shareOnApproves start at "+str(datetime.now()))
	logger.info(str(selling_company.name))
	logger.info(str(buying_company.name))

	buyerRef = Buyer.objects.filter(selling_company = selling_company, buying_company=buying_company).select_related('group_type').first()
	print buyerRef
	sellingPushes = Push.objects.filter(Q(company=selling_company, to_show='yes', buyer_segmentation__group_type=buyerRef.group_type, buyer_segmentation__buyer_grouping_type="Location Wise") & Q(Q(buyer_segmentation__city__isnull=True, buyer_segmentation__category__isnull=True) | Q(buyer_segmentation__city=buying_company.city, buyer_segmentation__category=buying_company.category.all()))).values_list('id', flat=True).distinct()
	print sellingPushes
	catalogArr = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).exclude(catalog__isnull=True).values('catalog').annotate(Max('id')).values('id__max')#.distinct().values_list('id', flat=True)
	print catalogArr
	#print catalogArr
	pushUserObj = None
	print selling_company.push_downstream
	if selling_company.push_downstream.lower() == 'yes':
		logger.info("In shareOnApproves Downstream = yes")
		pushUserObj = Push_User.objects.filter(Q(buying_company=selling_company, push__push_downstream='yes') | Q(id__in=catalogArr)).exclude(push__buyer_segmentation__isnull = True).order_by('-push__time')[:7] ##[::-1] #.select_related('push__buyer_segmentation', 'catalog', 'selection', 'selling_company', 'buying_company', 'push__company')
	else:
		logger.info("In shareOnApproves Downstream = no")
		pushUserObj = Push_User.objects.filter(id__in=catalogArr).exclude(push__buyer_segmentation__isnull = True).order_by('-push__time')[:7] ##[::-1] #.select_related('push__buyer_segmentation', 'catalog', 'selection', 'selling_company', 'buying_company', 'push__company')

	if pushUserObj:
		logger.info("In shareOnApproves has pushUserObj = ")

		completedCatalog = []
		for puObj in pushUserObj:
			logger.info("In shareOnApproves in  for loop of pushUserObj")

			group_type = puObj.push.buyer_segmentation.group_type.values_list('id', flat=True)
			if puObj.push.buyer_segmentation.city.count() == 0:
				city = City.objects.all().values_list('id', flat=True)
			else:
				city = puObj.push.buyer_segmentation.city.values_list('id', flat=True)
			if puObj.push.buyer_segmentation.category.count() == 0:
				category = Category.objects.all().values_list('id', flat=True)
			else:
				category = puObj.push.buyer_segmentation.category.values_list('id', flat=True)

			buyerIds =  Buyer.objects.filter(Q(selling_company = selling_company, buying_company=buying_company, buying_company__category__in=category, group_type__in=group_type) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).distinct().select_related('selling_company', 'buying_company')

			if Push_User.objects.filter(push=puObj.push, buying_company=buying_company).exists():
				logger.info("In shareOnApproves alredy pushed to buyer company : pushId / continue")
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

				logger.info("In shareOnApproves in  for loop of pushUserObj has buyerIds")

				catalog = puObj.catalog

				if catalog:
					if catalog.id in completedCatalog:
						logger.info("In shareOnApproves alredy pushed to buyer company : catalog / continue")
						continue
					else:
						completedCatalog.append(catalog.id)

					catalogs = Catalog.objects.filter(id=catalog.id)
				else:
					catalogs = Catalog.objects.none()

				catalogSharedProducts = []
				catalogRate = []

				is_continue = False

				if catalogs:
					logger.info("In shareOnApproves catalogs")
					for catalog in catalogs:

						fixRate = 0
						percentageRate = 0

						productDObj = []

						##check push is seller_company
						if puObj.selling_company == selling_company:
							#pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=puObj.user, catalog=catalog).select_related('product')
							'''cpfNewObj = CompanyProductFlat.objects.filter(selling_company=selling_company, catalog=catalog, buying_company__isnull=False).last()

							if cpfNewObj is None:
								is_continue = True

							pushUserProduct = CompanyProductFlat.objects.filter(selling_company=selling_company, catalog=catalog, buying_company=cpfNewObj.buying_company).select_related('product')
							logger.info("pushUserProductfiltered old")
							logger.info(pushUserProduct)
							logger.info(pushUserProduct.count())'''

							pushUserProduct = PushSellerPrice.objects.filter(push=puObj.push, selling_company=selling_company, product__catalog=catalog)
							logger.info("pushUserProductfiltered")
							logger.info(pushUserProduct)
							if pushUserProduct is None:
								is_continue = True
								continue
							logger.info(pushUserProduct.count())

							for productDetail in pushUserProduct:
								productDObj.append([productDetail.product.id, productDetail.product.sku, productDetail.price])

							catalogSharedProducts.append(productDObj)

							#buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()
							catalogRate.append([0,0])
						else:
							#pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=selluser, catalog=catalog).select_related('product')
							'''cpfNewObj = CompanyProductFlat.objects.filter(selling_company=selling_company, catalog=catalog, buying_company__isnull=False).last()

							if cpfNewObj is None:
								is_continue = True

							pushUserProduct = CompanyProductFlat.objects.filter(selling_company=selling_company, catalog=catalog, buying_company=cpfNewObj.buying_company).select_related('product')
							logger.info("pushUserProductfiltered old")
							logger.info(pushUserProduct)
							logger.info(pushUserProduct.count())'''

							pushUserProduct = PushSellerPrice.objects.filter(push=puObj.push, selling_company=selling_company, product__catalog=catalog)
							logger.info("pushUserProductfiltered")
							logger.info(pushUserProduct)
							if pushUserProduct is None:
								is_continue = True
								continue
							logger.info(pushUserProduct.count())

							for productDetail in pushUserProduct:
								productDObj.append([productDetail.product.id,productDetail.product.sku, productDetail.price])

							catalogSharedProducts.append(productDObj)

							buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()

							if buyerobj is None:
								logger.info("In shareOnApproves has not approve buyer for perticuler push : selection / continue")
								continue
							catalogRate.append([buyerobj.fix_amount,buyerobj.percentage_amount])

				if is_continue:
					continue

				pushobj = puObj.push

				push_downstream = "no" #puObj.push.push_downstream

				full_catalog_orders_only = puObj.full_catalog_orders_only


				logger.info("In shareOnApproves ready for dfsPush")
				buyerIds = buyerIds.values_list('id', flat=True)
				buyerIds = list(buyerIds)

				if catalogs:
					catalogs = catalogs.values_list('id', flat=True)
				catalogs = list(catalogs)
				city = list(city)
				category = list(category)
				group_type = list(group_type)

				if settings.TASK_QUEUE_METHOD == 'celery':
					logger.info("push celery ser")
					dfsShare.apply_async((pushobj.id, selling_company.id, buyerIds, city, category, group_type, catalogs, catalogSharedProducts, full_catalog_orders_only, True, False, False), expires=datetime.now() + timedelta(days=2))
				elif settings.TASK_QUEUE_METHOD == 'djangoQ':
					print "push djangoQ ser"
					task_id = async(
						'api.tasks.dfsShare',  # func full name
						pushobj.id, selling_company.id, buyerIds, city, category, group_type, catalogs, catalogSharedProducts, full_catalog_orders_only, True, False, False
					)
					logger.info("task_id")
					logger.info(task_id)

def getSegmentationsBuyers(segmentationObjs, supplier):
	from api.models import *

	buyers = segmentationObjs.filter(buyer_grouping_type="Custom").values_list('buyers', flat=True)
	buyers = list(buyers)

	buyerSegmentationObjs = segmentationObjs.filter(buyer_grouping_type="Location Wise")
	for buyer_segmentation in buyerSegmentationObjs:
		group_type = buyer_segmentation.group_type.values_list('id', flat=True)
		if buyer_segmentation.city.count() == 0:
			city = City.objects.all().values_list('id', flat=True)
		else:
			city = buyer_segmentation.city.values_list('id', flat=True)
		if buyer_segmentation.category.count() == 0:
			category = Category.objects.all().values_list('id', flat=True)
		else:
			category = buyer_segmentation.category.values_list('id', flat=True)
		new_buyers = Buyer.objects.filter(Q(selling_company = supplier, status='approved', buying_company__category__in=category, group_type__in=group_type) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).values_list('id', flat=True).distinct()
		buyers.extend(list(new_buyers))
	print buyers
	return buyers

def pretty_date(time=False):
	"""
	Get a datetime object or a int() Epoch timestamp and return a
	pretty string like 'an hour ago', 'Yesterday', '3 months ago',
	'just now', etc
	"""
	from datetime import datetime
	from django.utils import timezone
	#now = datetime.now()
	now = timezone.now()
	if type(time) is int:
		diff = now - datetime.fromtimestamp(time)
	elif isinstance(time,datetime):
		diff = now - time
	elif not time:
		diff = now - now
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return ''

	if day_diff == 0:
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return str(second_diff) + " seconds ago"
		if second_diff < 120:
			return "a minute ago"
		if second_diff < 3600:
			return str(second_diff / 60) + " minutes ago"
		if second_diff < 7200:
			return "an hour ago"
		if second_diff < 86400:
			return str(second_diff / 3600) + " hours ago"
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(day_diff) + " days ago"
	if day_diff < 31:
		return str(day_diff / 7) + " weeks ago"
	if day_diff < 365:
		return str(day_diff / 30) + " months ago"
	return str(day_diff / 365) + " years ago"

def getDisableCatalogIds(company):
	#from api.models import *
	from api.models import Push_User, Catalog, CatalogSeller
	disableCatalogIds = Push_User.objects.filter(Q(Q(selling_company=company) | Q(buying_company=company)) & Q(Q(supplier_disabled=True) | Q(buyer_disabled=True))).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
	disableCatalogIds = list(disableCatalogIds)

	#publicAndMyDisableIds = Catalog.objects.filter(Q(view_permission="public", supplier_disabled=True) | Q(company=company, supplier_disabled=True)).values_list('id', flat=True)
	publicAndMyDisableIds = Catalog.objects.filter(company=company, supplier_disabled=True).values_list('id', flat=True)
	disableCatalogIds.extend(list(publicAndMyDisableIds))
	csCatalogIds = CatalogSeller.objects.filter(selling_company=company, status="Disable").exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
	disableCatalogIds.extend(list(csCatalogIds))
	#logger.info("getDisableCatalogIds = %s"% (str(disableCatalogIds)))
	return disableCatalogIds

def getSupplierDisableCatalogIds(company):
	#from api.models import *
	from api.models import Push_User, Catalog
	disableCatalogIds = Push_User.objects.filter(buying_company=company, supplier_disabled=True).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
	disableCatalogIds = list(disableCatalogIds)

	#to filter "disable by supplier" in mycatalog list
	publicDisableIds = Catalog.objects.filter(view_permission="public", supplier_disabled=True).values_list('id', flat=True)
	disableCatalogIds.extend(list(publicDisableIds))

	#logger.info("getDisableCatalogIds = %s"% (str(disableCatalogIds)))
	return disableCatalogIds

def getMyDisableCatalogIds(company):
	#from api.models import *
	from api.models import Push_User, Catalog, CatalogSeller
	disableCatalogIds = Push_User.objects.filter(buying_company=company, buyer_disabled=True).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
	disableCatalogIds = list(disableCatalogIds)
	publicAndMyDisableIds = Catalog.objects.filter(company=company, supplier_disabled=True).values_list('id', flat=True)
	disableCatalogIds.extend(list(publicAndMyDisableIds))
	csCatalogIds = CatalogSeller.objects.filter(selling_company=company, status="Disable").exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
	disableCatalogIds.extend(list(csCatalogIds))
	#logger.info("getDisableCatalogIds = %s"% (str(disableCatalogIds)))
	return disableCatalogIds

def orderFinalizeNotification(salesorder):
	logger.info("in orderFinalizeNotification")
	from api.models import *
	from datetime import datetime, date, time, timedelta
	# # from api.v0.notifications import *
	# from notifier.shortcuts import send_notification
	# from api.v0.notifier_backend import *

	buyer_warehouse = Warehouse.objects.filter(company=salesorder.company).first()
	buyer_company = salesorder.company

	htmlTable = []

	items = SalesOrderItem.objects.filter(sales_order=salesorder.id)
	for item in items:
		'''if not Stock.objects.filter(warehouse=seller_warehouse, product=item.product).exists():
			Stock.objects.create(warehouse=seller_warehouse, product=item.product)
		seller_stock = Stock.objects.get(warehouse=seller_warehouse, product=item.product)

		seller_stock.open_sale = seller_stock.open_sale + item.quantity
		#if seller_stock.in_stock >= item.quantity:
		#	seller_stock.blocked = seller_stock.blocked + item.quantity
		seller_stock.blocked = seller_stock.blocked + min((seller_stock.in_stock - seller_stock.blocked), item.quantity)

		seller_stock.save()'''

		if not Stock.objects.filter(company=buyer_company, product=item.product).exists():
			Stock.objects.create(company=buyer_company, product=item.product)
		buyer_stock = Stock.objects.get(company=buyer_company, product=item.product)

		buyer_stock.open_purchase = buyer_stock.open_purchase + item.quantity
		buyer_stock.save()

		htmlTable.append({"sku":item.product.sku, "rate":str(item.rate), "quantity":str(item.quantity), "image":item.product.image.thumbnail[settings.SMALL_IMAGE].url})
	#end for inventory on create

	if salesorder.source_type == "Marketplace":
		jsonarr = {}
		jsonarr['order_number'] = salesorder.order_number
		jsonarr['table_id'] = salesorder.id
		jsonarr['phone_no'] = salesorder.seller_company.country.phone_code+salesorder.seller_company.phone_number
		jsonarr['company_info'] = salesorder.company.name+', '+salesorder.company.city.city_name+', '+salesorder.company.state.state_name
		jsonarr['order_url'] = 'https://app.wishbooks.io/m?type=sales&id='+str(salesorder.id)

		payment_status = "Pending"
		if salesorder.customer_status == "Paid" or salesorder.customer_status == "Payment Confirmed":
			payment_status = "Paid"

		jsonarr['order_number'] = salesorder.order_number
		jsonarr['total_rate'] = salesorder.total_rate
		jsonarr['html_table'] = htmlTable
		jsonarr['date'] = salesorder.date
		jsonarr['payment_status'] = payment_status

		phone_number = str(salesorder.seller_company.country.phone_code) + str(salesorder.seller_company.phone_number)
		jsonarr['supplier_name'] = salesorder.seller_company.name
		jsonarr['supplier_city'] = salesorder.seller_company.city.city_name
		jsonarr['purchase_url'] = 'https://app.wishbooks.io/m?type=purchase&id='+str(salesorder.id)

		jsonarr['supplier_phone_number'] = phone_number
		jsonarr['supplier_state'] = salesorder.seller_company.state.state_name

		jsonarr['supplier_gst'] = ""
		kyc = CompanyKycTaxation.objects.filter(company=salesorder.seller_company).first()
		if kyc:
			jsonarr['supplier_gst'] = kyc.gstin

		phone_number = str(salesorder.company.country.phone_code) + str(salesorder.company.phone_number)
		jsonarr['buyer_name'] = salesorder.company.name
		jsonarr['buyer_city'] = salesorder.company.city.city_name
		jsonarr['sales_url'] = 'https://app.wishbooks.io/m?type=sales&id='+str(salesorder.id)

		jsonarr['buyer_phone_number'] = phone_number
		jsonarr['buyer_state'] = salesorder.company.state.state_name

		jsonarr['buyer_gst'] = ""
		kyc = CompanyKycTaxation.objects.filter(company=salesorder.company).first()
		if kyc:
			jsonarr['buyer_gst'] = kyc.gstin

		username = CompanyUser.objects.filter(company=salesorder.seller_company).values_list('user__username', flat=True).first()
		jsonarr['username'] = username

		broker_users = []
		if salesorder.broker_company is not None:
			broker_users=CompanyUser.objects.filter(company=salesorder.broker_company).values_list('user', flat=True).distinct()

		#deputed_users = CompanyUser.objects.filter(company=salesorder.company, deputed_from=salesorder.seller_company).values_list('user', flat=True).distinct()
		#print deputed_users

		user1 = salesorder.company.company_users.values_list('user', flat=True)
		user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)
		print user1
		jsonarr['title'] = 'Purchase Order '+salesorder.processing_status
		# send_notification('purchase-order', user1, jsonarr) #notification for buyer
		sendAllTypesMessage("purchaseorder_accepted", user1, jsonarr)


		'''username = CompanyUser.objects.filter(company=salesorder.company).values_list('user__username', flat=True).first()
		jsonarr['username'] = username

		user1 = salesorder.seller_company.company_users.values_list('user', flat=True)
		user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)
		print user1
		jsonarr['title'] = 'Sales Order '+salesorder.processing_status
		send_notification('sales-order', user1, jsonarr)#notification for supplier'''

	orderToMediator(salesorder)

def shippingChargesOnPincode(from_pincode, to_pincode, weight):
	logger.info("in shippingChargesOnPincode")
	#from api.models import *
	from api.models import PincodeZone
	frompz = PincodeZone.objects.filter(pincode=from_pincode).first()
	topz = PincodeZone.objects.filter(pincode=to_pincode).first()
	if frompz and topz:
		if frompz.city == topz.city:
			return weight*6
		elif frompz.zone == topz.zone:
			return weight*9
		else:
			return weight*12
	else:
		return weight*12

def getCatalogEAV(catalogObj, eavtype="allInJson"):
	if eavtype == "allInJson":
		#print catalogObj.eav.get_values_dict()
		att = catalogObj.eav.get_values()
		jsonarr = {}
		for v in att:
			if v.attribute.datatype == "multi":
				if jsonarr.has_key(str(v.attribute.name)):
					jsonarr[str(v.attribute.name)].append(str(v.value))
				else:
					jsonarr[str(v.attribute.name)] = [str(v.value)]
			elif v.attribute.datatype == "int":
				jsonarr[str(v.attribute.name)] = v.value
			elif v.attribute.datatype == "enum":
				jsonarr[str(v.attribute.name)] = v.value.value
			else:
				#jsonarr[str(v.attribute.name)] = str(v.value)
				jsonarr[str(v.attribute.name)] = v.value
		return jsonarr

	if eavtype == "fabricInString":
		att = catalogObj.eav.get_values()
		datastr = None
		for v in att:
			if v.attribute.name == "fabric":
				if datastr:
					datastr += ", "+str(v.value)
				else:
					datastr = str(v.value)
		return datastr

	if eavtype == "workInString":
		att = catalogObj.eav.get_values()
		datastr = None
		for v in att:
			if v.attribute.name == "work":
				if datastr:
					datastr += ", "+str(v.value)
				else:
					datastr = str(v.value)
		return datastr

def getEAVFabricWork(productObj, eavtype="all"):
	#print productObj.producteavflat_set
	from api.models import ProductEAVFlat
	#print "getEAVFabricWork", eavtype
	if eavtype == "all":
		att = productObj.eav.get_values()
		arr = []
		for v in att:
			arr.append([str(v.attribute.name), str(v.value)])
		return arr
	elif eavtype == "fabric":
		pobj = ProductEAVFlat.objects.filter(product=productObj).first()
		if pobj:
			fabric = pobj.fabric
			if fabric:
				if pobj.fabric_text:
					fabric += ", "+pobj.fabric_text
			else:
				fabric = pobj.fabric_text
			return fabric
		else:
			return None
		'''att = productObj.eav.get_values()
		datastr = None
		for v in att:
			if str(v.value).lower() == "other":
				continue
			if v.attribute.name == "fabric":
				if datastr:
					datastr += ", "+str(v.value)
				else:
					datastr = str(v.value)
			elif v.attribute.name == "fabric_text":
				if datastr:
					datastr += ", "+str(v.value)
				else:
					datastr = str(v.value)
		return datastr'''
	elif eavtype == "work":
		pobj = ProductEAVFlat.objects.filter(product=productObj).first()
		if pobj:
			work = pobj.work
			if work:
				if pobj.work_text:
					work += ", "+pobj.work_text
			else:
				work = pobj.work_text
			return work
		else:
			return None
		'''att = productObj.eav.get_values()
		datastr = None
		for v in att:
			if str(v.value).lower() == "other":
				continue
			if v.attribute.name == "work":
				if datastr:
					datastr += ", "+str(v.value)
				else:
					datastr = str(v.value)
			elif v.attribute.name == "work_text":
				if datastr:
					datastr += ", "+str(v.value)
				else:
					datastr = str(v.value)
		return datastr'''
	elif eavtype == "BothInJson":
		fabric = None
		work = None
		pobj = ProductEAVFlat.objects.filter(product=productObj).first()
		if pobj:
			fabric = pobj.fabric
			if fabric:
				if pobj.fabric_text:
					fabric += ", "+pobj.fabric_text
			else:
				fabric = pobj.fabric_text

			work = pobj.work
			if work:
				if pobj.work_text:
					work += ", "+pobj.work_text
			else:
				work = pobj.work_text

			return {"fabric":fabric, "work": work}
		else:
			return {"fabric":None, "work": None}
		'''att = productObj.eav.get_values()
		fabric = None
		work = None
		for v in att:
			if str(v.value).lower() == "other":
				continue
			if v.attribute.name == "fabric":
				if fabric:
					fabric += ", "+str(v.value)
				else:
					fabric = str(v.value)
			elif v.attribute.name == "fabric_text":
				if fabric:
					fabric += ", "+str(v.value)
				else:
					fabric = str(v.value)
			elif v.attribute.name == "work":
				if work:
					work += ", "+str(v.value)
				else:
					work = str(v.value)
			elif v.attribute.name == "work_text":
				if work:
					work += ", "+str(v.value)
				else:
					work = str(v.value)
		return {"fabric":fabric, "work": work}'''

def productEAVset(product):
	logger.info("in productEAVset")
	from api.models import ProductEAVFlat

	peavflat, is_created = ProductEAVFlat.objects.get_or_create(product=product)
	peavflat.category=product.catalog.category
	peavflat.catalog=product.catalog

	att = product.eav.get_values()

	peavflat.fabric=None
	peavflat.work=None
	peavflat.fabric_text=None
	peavflat.work_text=None

	for v in att:
		#arr.append([str(v.attribute.name), str(v.value)])
		if str(v.value).lower() == "other":
			continue
		if v.attribute.name == "fabric":
			if peavflat.fabric:
				peavflat.fabric += ", "+str(v.value)
			else:
				peavflat.fabric = str(v.value)
		elif v.attribute.name == "work":
			if peavflat.work:
				peavflat.work += ", "+str(v.value)
			else:
				peavflat.work = str(v.value)
		elif v.attribute.name == "fabric_text":
			if peavflat.fabric_text:
				peavflat.fabric_text += ", "+str(v.value)
			else:
				peavflat.fabric_text = str(v.value)
		elif v.attribute.name == "work_text":
			if peavflat.work_text:
				peavflat.work_text += ", "+str(v.value)
			else:
				peavflat.work_text = str(v.value)
	'''peavflat.fabric=str(product.eav.fabric)
	peavflat.work=str(product.eav.work)
	peavflat.fabric_text=product.eav.fabric_text
	peavflat.work_text=product.eav.work_text'''
	peavflat.save()

def catalogEAVset(catalog):
	logger.info("in catalogEAVset")
	from api.models import CatalogEAVFlat, Product
	from django.db.models import Min, Max

	att = catalog.eav.get_values()
	logger.info("in catalogEAVsetm att = %s" % (att))

	peavflat, is_created = CatalogEAVFlat.objects.get_or_create(catalog=catalog)
	peavflat.title=catalog.title
	peavflat.brand=catalog.brand
	peavflat.view_permission=catalog.view_permission
	peavflat.category=catalog.category
	peavflat.sell_full_catalog=catalog.sell_full_catalog
	#peavflat.save()

	peavflat.fabric=None
	peavflat.work=None
	peavflat.fabric_value=None
	peavflat.work_value=None

	peavflat.stitching_type=None
	peavflat.number_pcs_design_per_set=None
	peavflat.size=None
	peavflat.size_value=None
	peavflat.size_mix=None

	peavflat.style=None

	if catalog.view_permission == "public":
		min_price = Product.objects.filter(catalog=catalog).aggregate(Min('public_price')).get('public_price__min', 0)
		max_price = Product.objects.filter(catalog=catalog).aggregate(Max('public_price')).get('public_price__max', 0)
		if min_price is None:
			min_price = 0
		if max_price is None:
			max_price = 0
		peavflat.min_price=min_price
		peavflat.max_price=max_price

	for v in att:
		#arr.append([str(v.attribute.name), str(v.value)])
		if v.attribute.name == "fabric":
			if peavflat.fabric:
				peavflat.fabric += ", "+str(v.value_enum_id)
			else:
				peavflat.fabric = str(v.value_enum_id)

			if peavflat.fabric_value:
				peavflat.fabric_value += ", "+str(v.value)
			else:
				peavflat.fabric_value = str(v.value)
		elif v.attribute.name == "work":
			if peavflat.work:
				peavflat.work += ", "+str(v.value_enum_id)
			else:
				peavflat.work = str(v.value_enum_id)

			if peavflat.work_value:
				peavflat.work_value += ", "+str(v.value)
			else:
				peavflat.work_value = str(v.value)
		elif v.attribute.name == "size":
			if peavflat.size:
				peavflat.size += ", "+str(v.value_enum_id)
			else:
				peavflat.size = str(v.value_enum_id)

			if peavflat.size_value:
				peavflat.size_value += ", "+str(v.value)
			else:
				peavflat.size_value = str(v.value)
		elif v.attribute.name == "stitching_type":
			if peavflat.stitching_type:
				peavflat.stitching_type += ", "+str(v.value)
			else:
				peavflat.stitching_type = str(v.value)
		elif v.attribute.name == "style":
			if peavflat.style:
				peavflat.style += ", "+str(v.value)
			else:
				peavflat.style = str(v.value)
		elif v.attribute.name == "number_pcs_design_per_set":
			if peavflat.number_pcs_design_per_set:
				peavflat.number_pcs_design_per_set += ", "+str(v.value)
			else:
				peavflat.number_pcs_design_per_set = str(v.value)
		elif v.attribute.name == "size_mix":
			if peavflat.size_mix:
				peavflat.size_mix += ", "+str(v.value)
			else:
				peavflat.size_mix = str(v.value)

	peavflat.save()

def catalogEAVProductset(catalog):
	logger.info("in catalogEAVProductset")
	from api.models import CatalogEAVFlat, Product
	from django.db.models import Min, Max

	if catalog.view_permission == "public":
		peavflat, is_created = CatalogEAVFlat.objects.get_or_create(catalog=catalog)

		min_price = Product.objects.filter(catalog=catalog).aggregate(Min('public_price')).get('public_price__min', 0)
		max_price = Product.objects.filter(catalog=catalog).aggregate(Max('public_price')).get('public_price__max', 0)
		if min_price is None:
			min_price = 0
		if max_price is None:
			max_price = 0
		peavflat.min_price=min_price
		peavflat.max_price=max_price

		peavflat.save()


def recommended_relationship(loginCompany, companyObj):
	#print "recommended_relationship"
	from django.conf import settings
	from api.models import Brand, BrandDistributor, Buyer, GroupType, CompanyType

	types_arr = []

	supplier_arr = []
	buyer_arr = []

	if CompanyType.objects.filter(company=loginCompany).exists() == False or CompanyType.objects.filter(company=companyObj).exists() == False:
		return {"buyer_types":set(buyer_arr), "supplier_types":set(supplier_arr)}

	loginCompanyType = loginCompany.company_group_flag
	recommendCompanyType = companyObj.company_group_flag
	#~ print loginCompanyType
	#~ print recommendCompanyType

	alllctTrue = loginCompanyType.manufacturer == False and loginCompanyType.wholesaler_distributor == False and loginCompanyType.retailer == False and loginCompanyType.online_retailer_reseller == False and loginCompanyType.broker == False
	#print alllctTrue

	if (alllctTrue or loginCompanyType.retailer == True or loginCompanyType.online_retailer_reseller == True) and recommendCompanyType.company.address:
		#~ record={}
		#~ record["type"]="supplier"
		#~ record["group_type"]="retailer"
		if (recommendCompanyType.wholesaler_distributor == True and recommendCompanyType.company.address.state==loginCompanyType.company.address.state) or (recommendCompanyType.broker == True and recommendCompanyType.company.address.state==loginCompanyType.company.address.state) or (recommendCompanyType.manufacturer == True):
			gtObj = GroupType.objects.filter(name="retailer").first()
			supplier_arr.append(gtObj.id)

	if (alllctTrue or loginCompanyType.wholesaler_distributor == True) and recommendCompanyType.company.address:
		if (recommendCompanyType.retailer == True and recommendCompanyType.company.address.state==loginCompanyType.company.address.state) or (recommendCompanyType.online_retailer_reseller == True and recommendCompanyType.company.address.state==loginCompanyType.company.address.state):
			gtObj = GroupType.objects.filter(name="retailer").first()
			buyer_arr.append(gtObj.id)

		if recommendCompanyType.manufacturer == True:
			gtObj = GroupType.objects.filter(name="wholesaler").first()
			supplier_arr.append(gtObj.id)

	if alllctTrue or loginCompanyType.manufacturer == True:
		if recommendCompanyType.manufacturer == True:
			gtObj = GroupType.objects.filter(name="wholesaler").first()
			buyer_arr.append(gtObj.id)

		if recommendCompanyType.retailer == True or recommendCompanyType.online_retailer_reseller == True:
			gtObj = GroupType.objects.filter(name="retailer").first()
			buyer_arr.append(gtObj.id)

		if recommendCompanyType.broker == True:
			gtObj = GroupType.objects.filter(name="broker").first()
			buyer_arr.append(gtObj.id)

	if alllctTrue or loginCompanyType.broker == True:
		if recommendCompanyType.retailer == True or recommendCompanyType.online_retailer_reseller == True:
			gtObj = GroupType.objects.filter(name="retailer").first()
			buyer_arr.append(gtObj.id)

		if recommendCompanyType.manufacturer == True:
			gtObj = GroupType.objects.filter(name="broker").first()
			supplier_arr.append(gtObj.id)

	return {"buyer_types":set(buyer_arr), "supplier_types":set(supplier_arr)}

'''def recommended_relationship22(loginCompany, companiesObj, company_map, request_type, group_type):
	from django.conf import settings
	from api.models import Brand, BrandDistributor, Buyer

	registeredContact = []
	for companyObj in companiesObj:
		record={}
		record["type"]=request_type
		record["group_type"]=group_type

		record["phone"]=company_map[str(companyObj.id)]
		record["name"]=contact_map[company_map[str(companyObj.id)]]# contact['name']

		record["company_name"]=companyObj.name
		record["company_image"]=settings.MEDIA_URL+"logo-single.png"
		if companyObj.thumbnail:
			record["company_image"]=companyObj.thumbnail.url
		else:
			if Brand.objects.filter(company=companyObj.id).exists():
				brand = Brand.objects.filter(company=companyObj.id).first()
				record["company_image"]=brand.image.thumbnail['150x150'].url
			else:
				brandIds = BrandDistributor.objects.filter(company=companyObj.id).values_list('brand', flat=True).distinct()
				if Brand.objects.filter(id__in=brandIds).exists():
					brand = Brand.objects.filter(id__in=brandIds).first()
					record["company_image"]=brand.image.thumbnail['150x150'].url

		record["connected_as"] = ""
		if Buyer.objects.filter(selling_company=loginCompany, buying_company=companyObj).exists():
			record["connected_as"]="buyer"
		if Buyer.objects.filter(selling_company=companyObj, buying_company=loginCompany).exists():
			record["connected_as"]="supplier"

		if companyObj.chat_admin_user is not None:
			record["chat_user"]=companyObj.chat_admin_user.username
		else:
			record["chat_user"]=None

		registeredContact.append(record)
	return registeredContact'''

def myCatalogs(company):
	from api.models import CatalogSeller, Catalog
	#myDisableCatalogIds = getMyDisableCatalogIds(company)
	disableCatalogIds = getDisableCatalogIds(company)
	cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
	totalCatalog = Catalog.objects.filter(Q(company=company) | Q(id__in=cscatalogids)).exclude(id__in=disableCatalogIds).count()
	return totalCatalog

def getUniqueItems(iterable):
	result = []
	for item in iterable:
		if item not in result:
			result.append(item)
	return result

def is_manufacturer(obj):
	res = False
	if obj.manufacturer == True and obj.wholesaler_distributor == False and obj.retailer == False and obj.online_retailer_reseller == False and obj.broker == False:
		res = True
	#print res
	return res

def get_user_company(user):
	try:
		company = user.companyuser.company
		return company
	except Exception as e:
		return None

def add_registration_id(request, user, registration_id):
	from push_notifications.models import GCMDevice ,APNSDevice
	logger.info("in add_registration_id===")
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

def login_tracker(request, user):
	from api.models import CompanyUser, Buyer, Company
	from datetime import datetime
	from django.utils import timezone

	logger.info("in login_tracker===")
	if user.userprofile.first_login is None:
		user.userprofile.first_login = timezone.now()
		user.userprofile.save()

		cu = CompanyUser.objects.filter(user=user).first()
		if cu:
			company = cu.company

			buyerarr = []
			suppliers = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True)

			sellingCompanys = Company.objects.filter(id__in=suppliers)
			print sellingCompanys
			for sellingCompany in sellingCompanys:
				shareOnApproves(sellingCompany, company)

	data = request.data
	login_for = data.get('login_for', None)

	user_agent = request.META.get('HTTP_USER_AGENT', None)
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

def common_user_registration(data, request, otp_action="send_otp"):
	from django.conf import settings
	from api.models import *
	import random
	from api.v1.serializers import makeBuyerSupplierFromInvitee

	country = data.get('country', None)
	phone_number = data.get('phone_number', None)

	otp = data.get('otp', None)
	password = data.get('password', None)

	registration_id = data.get('registration_id', None)


	state = data.get('state', None)
	city = data.get('city', None)
	company_name = data.get('company_name', phone_number)
	#company_type = data.get('company_type', None) #if company_name
	manufacturer = data.get('manufacturer', False)
	wholesaler_distributor = data.get('wholesaler_distributor', False)
	retailer = data.get('retailer', False)
	online_retailer_reseller = data.get('online_retailer_reseller', False)
	broker = data.get('broker', False)
	#
	company_id = data.get('company_id', None)
	user_group_type = data.get('user_group_type', None) #if company_id
	#
	first_name = data.get('first_name', None)
	email = data.get('email', None)
	#
	invite_as = data.get('invite_as', None) # buyer, supplier
	invite_group_type = data.get('invite_group_type', None)
	connect_supplier = data.get('connect_supplier', None) #for broker only
	meeting = data.get('meeting', None)

	refered_by = data.get('refered_by', None)

	is_guest_user_registration = data.get('is_guest_user_registration', False)
	is_invitee_full_registration = data.get('is_invitee_full_registration', False)

	invited_from = data.get('invited_from', 'Wishbook')

	print "is_guest_user_registration === ", is_guest_user_registration

	user = None
	'''
	is_guest_user_registration = None
	user = request.user
	print "==========user====",user
	if user.is_authenticated():
		print "authenticated"
		if not CompanyUser.objects.filter(user=user).exists():
			is_guest_user_registration = True'''


	phone_number_len = len(str(phone_number))
	if phone_number_len != 10:
		raise serializers.ValidationError({"phone_number":"Enter valid mobile number"})

	if int(phone_number[0]) in [0,1,2,3,4,5]:
		raise serializers.ValidationError({"phone_number":"Mobile number is not valid : "+str(phone_number)})

	country = Country.objects.filter(id=country).first()
	if country is None:
		raise serializers.ValidationError({"country":"Enter valid country"})


	username = str(country.phone_code)+str(phone_number)
	username = username.replace("+", "")

	#create user
	if email:
		if User.objects.filter(email=email).exclude(username=username).exists():
			raise serializers.ValidationError({"email":"A user is already registered with this e-mail address."})
	else:
		email = str(country.phone_code).replace("+", "")+str(phone_number)+"@wishbooks.io"

	if User.objects.filter(email=email).exists():
		rno = random.randrange(100000, 999999, 1)
		email = str(rno)+email

	if state is not None and state != "":
		try:
			state = State.objects.get(pk=state)
		except Exception as e:
			logger.info("common_user_registration Exception state = %s" % (e))
			state = State.objects.filter(state_name="-").first()
			pass
	if state is None or state == "":
		state = State.objects.filter(state_name="-").first()

	if city is not None and city != "":
		try:
			city = City.objects.get(pk=city)
		except Exception as e:
			logger.info("common_user_registration Exception city = %s" % (e))
			city = City.objects.filter(city_name="-").first()
			pass
	if city is None or city == "":
		city = City.objects.filter(city_name="-").first()


	if is_guest_user_registration is False and not User.objects.filter(username=username).exists():
		user = User.objects.create(username=username, email=email)
		if first_name:
			user.first_name=first_name[:30]
			user.save()

		UserProfile.objects.filter(user=user).update(phone_number=phone_number, country=country, is_profile_set=False)

		user = User.objects.get(pk=user.id)

		usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
		r = chat_user_registration({"userId":user.username, "deviceType":"1", "applicationId":settings.APPLOZIC_APPID, "contactNumber":usernumber})

		addressObj = Address.objects.create(name=username, city=city, state=state, country=country, user=user)
	else:
		user = User.objects.filter(userprofile__country=country, userprofile__phone_number=phone_number).first()
		if first_name:
			user.first_name=first_name[:30]
			user.save()
		if email and "wishbook" not in email:
			user.email = email
			user.save()

		usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)

	if phone_number == "6988888888":
		user.set_password("123456")
		user.save()
		user.userprofile.is_password_set = True
		user.userprofile.save()

	if company_id is None:
		#create new company. for self user registration. main registration page
		if is_guest_user_registration is False:
			groupObj = Group.objects.get(name="administrator")
			user.groups.add(groupObj)
			user.save()

		if registration_id is not None and registration_id != "":
			add_registration_id(request, user, registration_id)

		if first_name is not None or is_guest_user_registration is True: #new registration page only(logged in user behalf-registration page) or guest full registration
			if phone_number == "6988888888":#for auto testing
				user.delete()
				Company.objects.filter(phone_number=phone_number).delete()

				jsondata = {}
				jsondata["otp"] = "New user registered and OTP has been sent successfully."
				jsondata["is_password_set"] = False #user.userprofile.is_password_set
				return jsondata

			addressObj = Address.objects.filter(user=user).first()
			if addressObj is None:
				addressObj = Address.objects.create(name=company_name, city=city, state=state, country=country, user=user)
			company = Company.objects.create(name=company_name, phone_number=phone_number, city=city, state=state, country=country, chat_admin_user=user, address=addressObj, is_profile_set=False, email=email)
			category = Category.objects.all().values_list('id', flat=True)
			company.category.add(*category)
			company.save()

			#companyUser = CompanyUser.objects.create(user=user, company=company)
			if CompanyUser.objects.filter(user=user).exists():
				CompanyUser.objects.filter(user=user).update(company = company)
			else:
				CompanyUser.objects.create(user=user, company = company)

			companyType = CompanyType.objects.create(company=company, manufacturer=manufacturer, wholesaler_distributor=wholesaler_distributor, retailer=retailer, online_retailer_reseller=online_retailer_reseller, broker=broker)

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

			logger.info("in register serializer start make default buyer/supplier to call makeBuyerSupplierFromInvitee")
			##start make default buyer/supplier
			inviteeObj = Invitee.objects.filter(invitee_number=company.phone_number, country=country).update(status="registered", registered_user=user)
			makeBuyerSupplierFromInvitee(company.phone_number, country, company)
			##end make default buyer/supplier

			CompanyCatalogView.objects.filter(user=user).update(user=None, company=company)

	else:
		#new registration page only(logged in user behalf-registration page)
		groupObj = Group.objects.get(name=str(user_group_type))
		user.groups.add(groupObj)
		user.save()

		user.userprofile.user_approval_status = "Pending"
		user.userprofile.save()

		company = Company.objects.get(pk=company_id)
		#companyUser = CompanyUser.objects.create(user=user, company=company)
		if CompanyUser.objects.filter(user=user).exists():
			CompanyUser.objects.filter(user=user).update(company = company)
		else:
			CompanyUser.objects.create(user=user, company = company)

		ccvObjs = CompanyCatalogView.objects.filter(user=user)
		for ccvObj in ccvObjs:
			if CompanyCatalogView.objects.filter(company=company, catalog=ccvObj.catalog, catalog_type=ccvObj.catalog_type):
				ccvObj.delete()
			else:
				ccvObj.user=None
				ccvObj.company=company
				ccvObj.save()

	try:
		loginUser = request.user
		if loginUser.groups.filter(name="salesperson").exists():
			if loginUser.companyuser.deputed_to is not None:
				loginCompany = loginUser.companyuser.deputed_to
			else:
				loginCompany = loginUser.companyuser.company

			if invite_as is not None and invite_group_type is not None and invite_as.lower() != "none":
				group_type = GroupType.objects.get(pk=invite_group_type)
				if invite_as.lower() == "buyer":
					invite_res = add_buyer_v1(loginUser, loginCompany, company.name, country, phone_number, group_type, False, None, None, False, False)
				elif invite_as.lower() == "supplier":
					invite_res = add_supplier_v1(loginUser, loginCompany, company.name, country, phone_number, group_type, False, None, None, False)
				print "invite_res =",invite_res

			if connect_supplier is not None:
				connect_supplier = Company.objects.get(pk=int(connect_supplier))

				group_type = GroupType.objects.get(name="Retailer")
				add_supplier_v1(user, company, connect_supplier.name, connect_supplier.country, connect_supplier.phone_number, group_type, False, None, None, False)

			if meeting is not None:
				meetingObj = Meeting.objects.filter(id=meeting).first()
				if meetingObj:
					meetingObj.buying_company_ref = company
					meetingObj.save()
	except Exception as e:
		pass

	if first_name is None or is_guest_user_registration is True or is_invitee_full_registration is True:
		#create new company. for self user registration. main registration page. guest user page

		if refered_by is not None:
			referedCompanyObj = getCompanyFromNumber(country, refered_by)
			if referedCompanyObj:
				company.refered_by=referedCompanyObj
				company.save()
				group_type = GroupType.objects.get(name="Retailer")
				buyingcompany = add_buyer_v1(referedCompanyObj.chat_admin_user, referedCompanyObj, phone_number, country, phone_number, group_type, True)

		if is_guest_user_registration is True:#no need to send otp as user is already logged in
			jsondata = {}
			jsondata["otp"] = "You have completed your company registration successfully"
			jsondata["is_password_set"] = user.userprofile.is_password_set

			return jsondata

		otp = random.randrange(100000, 999999, 1)
		registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otp, country=country)

		#if send_otp:
		if otp_action == "send_otp":
			sendOTP(usernumber, otp, True)

			jsondata = {}
			jsondata["otp"] = "New user registered and OTP has been sent successfully."
			jsondata["is_password_set"] = user.userprofile.is_password_set

			return jsondata

		elif otp_action == "return_otp":
			return {"otp":otp}

		elif otp_action == "send_invitee_sms":
			smsurl = 'https://app.wishbooks.io/?m='+str(user.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(user.userprofile.country.id)
			smsurl = urlShortener(smsurl)
			template = smsTemplates("user_detail_3")% (invited_from, smsurl)
			smsSend([usernumber], template, True, True)

			sendOTP(usernumber, otp, False)

			jsondata = {}
			jsondata["otp"] = "New user registered and OTP has been sent successfully."
			jsondata["is_password_set"] = user.userprofile.is_password_set

			return jsondata

		return {}
	else:
		#new registration page only(logged in user behalf-registration page)
		loginUser = request.user
		if loginUser.groups.filter(name="salesperson").exists() and loginUser.companyuser.deputed_to is not None:
			loginCompany = loginUser.companyuser.deputed_to
		else:
			loginCompany = loginUser.companyuser.company

		if invite_as is not None and invite_group_type is not None and invite_as.lower() != "none":
			group_type = GroupType.objects.get(pk=invite_group_type)
			if invite_as.lower() == "buyer":
				invite_res = add_buyer_v1(loginUser, loginCompany, company.name, country, phone_number, group_type, False, None, None, False, False)
			elif invite_as.lower() == "supplier":
				invite_res = add_supplier_v1(loginUser, loginCompany, company.name, country, phone_number, group_type, False, None, None, False)
			print "invite_res =",invite_res

		if connect_supplier is not None:
			connect_supplier = Company.objects.get(pk=int(connect_supplier))

			group_type = GroupType.objects.get(name="Retailer")
			add_supplier_v1(user, company, connect_supplier.name, connect_supplier.country, connect_supplier.phone_number, group_type, False, None, None, False)

		if meeting is not None:
			meetingObj = Meeting.objects.filter(id=meeting).first()
			if meetingObj:
				meetingObj.buying_company_ref = company
				meetingObj.save()

		template = smsTemplates("user_detail_2")% (loginCompany.name)
		usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
		smsSend([usernumber], template, True, True)

		#return Response({"success":"User is registration and message has been sent successfully."})
		jsondata = {"success":"User is registration and message has been sent successfully."}
		return jsondata

def get_story_deeplink(obj, user, company):
	from api.models import Catalog

	querysetcatalogs = Catalog.objects.all()

	urlparams = str(obj.deep_link).split("?")[1]
	print "get_story_deeplink urlparams=", urlparams

	params = dict(
		part.split("=", 1) for part in urlparams.split("&")
	)

	if "type" in params.keys() and "ctype" in params.keys():
		params["view_type"] = params["ctype"]

	print "get_story_deeplink params=", params

	catalogObjs = catalogQuerysetFilter(querysetcatalogs, company, params, user, "dropdown")

	if "limit" in params.keys() and "offset" in params.keys():
		from django.core.paginator import Paginator
		try:
			p = Paginator(catalogObjs, params['limit'])
			page = p.page(int(params['offset'])+1)
			catalogObjs = page.object_list
		except Exception as e:
			logger.info(str(e))
			pass

	print "get_story_deeplink catalogObjs =", catalogObjs
	return catalogObjs

def get_design_wise_qty(items, qty):
	totalproducts = items.count()

	logger.info("qty = %s"% (str(qty)))
	logger.info("totalproducts = %s"% (str(totalproducts)))

	design_to_decrease_by = 0
	if (qty % totalproducts) > 0:
		design_to_decrease_by = 1
		if (qty % (totalproducts - design_to_decrease_by)) > 0:
			design_to_decrease_by = 2
			if (qty % (totalproducts - design_to_decrease_by)) > 0:
				design_to_decrease_by = 0

	items = items[:totalproducts - design_to_decrease_by]

	totalproducts = items.count()

	dispatch_ind_qty = []
	for idx in range(totalproducts):
		dispatch_ind_qty.append(0)
	dividable_qty = qty
	while (dividable_qty > 0):
		for idx in range(totalproducts):
			if dividable_qty > 0:
				dispatch_ind_qty[idx] = dispatch_ind_qty[idx] + 1
				dividable_qty = dividable_qty - 1

	logger.info("dispatch_ind_qty = %s"% (dispatch_ind_qty))

	return {"items":items, "dispatch_ind_qty":dispatch_ind_qty}

def set_total_products_uploaded(catalog):
	from api.models import ProductStatus
	disableProductsIds = ProductStatus.objects.filter(product__catalog=catalog, status='Disable', company=catalog.company).values_list('product', flat=True)
	catalog.total_products_uploaded = catalog.products.all().exclude(id__in=disableProductsIds).count()
	catalog.save()


def startMarketing(instance, action="send"):
	from django.contrib.auth.models import User, Group
	from api.models import Marketing, Company, Address, Country, UserProfile, CompanyPhoneAlias, CompanyType, CompanyUser, UserPlatformInfo, UnsubscribedNumber, Config
	import random
	from django.db.models.functions import Concat
	from datetime import date, datetime, timedelta
	from api.common_functions import smsSend, urlShortener, getLastOTP, smsTemplates
	import csv
	import re
	# ~ from rest_framework import serializers
	from django.conf import settings
	# ~ from os.path import join
	# ~ import os
	from push_notifications.models import GCMDevice ,APNSDevice
	from api.models import CompanyCatalogView


	logger.info("startMarketing json = %s"% (instance))

	#instance = Marketing.objects.get(pk=marketing_id)

	companies = []
	users = []
	csv_phone_numbers = []

	countryObj = Country.objects.get(pk=1)

	if instance["to"] == "All":
		cids = Company.objects.all().values_list('id', flat=True)
		companies.extend(list(cids))

		uids = User.objects.all().values_list('id', flat=True)
		users.extend(list(uids))

	elif instance["to"] == "Location":
		if instance["state"] and instance["city"]:
			logger.info("startMarketing both state n city filter")
			cids = Company.objects.filter(state__in = instance["state"], city__in = instance["city"]).values_list('id', flat=True)
			companies.extend(list(cids))

			uids = Address.objects.filter(state__in = instance["state"], city__in = instance["city"]).exclude(user__isnull=True).values_list('user', flat=True)
			users.extend(list(uids))

		elif instance["state"]:
			logger.info("startMarketing only state filter")
			cids = Company.objects.filter(state__in = instance["state"]).values_list('id', flat=True)
			companies.extend(list(cids))

			uids = Address.objects.filter(state__in = instance["state"]).exclude(user__isnull=True).values_list('user', flat=True)
			users.extend(list(uids))

	elif instance["to"] == "Specific Numbers":
		reader = []
		if instance.get("specific_no_file", None) is None:
			print "specific_no_file from instance id"
			if "id" in instance.keys():
				instanceObj = Marketing.objects.get(pk=instance["id"])
				reader = csv.DictReader(instanceObj.specific_no_file)
		else:
			print "specific_no_file from json data"
			reader = csv.DictReader(instance["specific_no_file"])

			# ~ if "id" in instance.keys():
				# ~ instanceObj = Marketing.objects.get(pk=instance["id"])
				# ~ reader = csv.DictReader(instanceObj.specific_no_file)

		logger.info("startMarketing Specific Numbers reader = %s"% (reader))

		column = 1
		rows = 0

		try:
			temp_csv_original_phone_numbers = []
			for fields in reader:
				try:
					column += 1

					# ~ logger.info("startMarketing fields = %s"% (str(fields)))

					phone_number = fields['phone_number']
					phone_number = re.sub('[^0-9+]', '',phone_number)
					phone_number = str(phone_number)[-10:]

					if len(str(phone_number)) < 5:
						continue
					if int(phone_number[0]) in [0,1,2,3,4,5]:
						continue

					final_number = str(countryObj.phone_code)+str(phone_number)

					csv_phone_numbers.append(final_number)
					#country = Country.objects.filter(phone_code="+"+country_code).first()

					temp_csv_original_phone_numbers.append(phone_number)

					# ~ if Company.objects.filter(country=countryObj, phone_number=phone_number).exists():
						# ~ companyObj = Company.objects.filter(country=countryObj, phone_number=phone_number).first()
						# ~ companies.append(companyObj.id)
					# ~ elif UserProfile.objects.filter(country=countryObj, phone_number=phone_number).exists():
						# ~ userprofile = UserProfile.objects.filter(country=countryObj, phone_number=phone_number).first()
						# ~ users.append(userprofile.user.id)
						# ~ if CompanyUser.objects.filter(user=userprofile.user).exists():
							# ~ companyObj = userprofile.user.companyuser.company
							# ~ companies.append(companyObj.id)
					# ~ elif CompanyPhoneAlias.objects.filter(country=countryObj, alias_number=phone_number, status="Approved").exists():
						# ~ companyalias = CompanyPhoneAlias.objects.filter(country=countryObj, alias_number=phone_number, status="Approved").first()
						# ~ companyObj = companyalias.company
						# ~ companies.append(companyObj.id)

				except Exception as e:
					logger.info("startMarketing Inloop Exception - Check csv file and found something wrong around row no =  %s , and error = %s"% (str(column), str(e)))
					continue

			company_nmber_ids = Company.objects.filter(country=countryObj, phone_number__in=temp_csv_original_phone_numbers).values_list('id', flat=True)
			companies.extend(list(company_nmber_ids))
			user_nmber_ids = UserProfile.objects.filter(country=countryObj, phone_number__in=temp_csv_original_phone_numbers).values_list('user', flat=True)
			users.extend(list(user_nmber_ids))
			company_nmber_ids = CompanyUser.objects.filter(user__in=user_nmber_ids).values_list('company', flat=True)
			companies.extend(list(company_nmber_ids))
			company_nmber_ids = CompanyPhoneAlias.objects.filter(country=countryObj, alias_number__in=temp_csv_original_phone_numbers, status="Approved").values_list('company', flat=True)
			companies.extend(list(company_nmber_ids))

		except Exception as e:
			logger.info("startMarketing Exception - Check csv file and found something wrong around row no = "+str(column))
			logger.info(str(e))

		logger.info("startMarketing Specific Numbers companies len = %s"% (len(companies)))
		logger.info("startMarketing Specific Numbers users len = %s"% (len(users)))

	companies_type = []
	guestuser_type = []
	is_companies_type_filter = False
	is_guestuser_type_filter = False
	phonebooknumbers_type = []


	if instance["to"] in ["All", "Location"] and instance.get("company_number_type_manufactures", None) == True:
		ct=CompanyType.objects.filter(company__in=companies, manufacturer=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	if instance["to"] in ["All", "Location"] and instance.get("company_number_type_wholesalers_agents", None) == True:
		ct=CompanyType.objects.filter(company__in=companies, wholesaler_distributor=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	if instance["to"] in ["All", "Location"] and instance.get("company_number_type_retailers", None) == True:
		ct=CompanyType.objects.filter(company__in=companies, retailer=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	if instance["to"] in ["All", "Location"] and instance.get("company_number_type_online_retailer_reseller", None) == True:
		ct=CompanyType.objects.filter(company__in=companies, online_retailer_reseller=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	if instance["to"] in ["All", "Location"] and instance.get("company_number_type_broker", None) == True:
		ct=CompanyType.objects.filter(company__in=companies, broker=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True

	if is_companies_type_filter:
		companies = companies_type

	if instance["to"] in ["All", "Location"] and instance.get("company_number_type_guestusers", None) == True:
		companyusers = CompanyUser.objects.all().values_list('user', flat=True)
		guestusers = User.objects.filter(id__in=users).exclude(id__in=companyusers).values_list('id', flat=True)
		guestuser_type = list(guestusers)

		users = guestuser_type

		if is_companies_type_filter == False:
			companies = []

		is_guestuser_type_filter = True

	if is_companies_type_filter == True and is_guestuser_type_filter == False:
		users = []

	if instance.get("by_in_app_notifications", False) is False and instance["to"] in ["All"] and instance.get("company_number_type_inphonebook", None) == True:
		nosmsuserids = UserProfile.objects.filter(send_sms_to_contacts=False).values_list('user', flat=True)
		nosmsuserids_query = ""
		if len(nosmsuserids) > 0:
			nosmsuserids = map(str, nosmsuserids)
			nosmsuserids = ", ".join(nosmsuserids)
			nosmsuserids_query = "and api_usercontact.user_id not in ("+nosmsuserids+")"

		USER_CONTACT_REGEX = Config.objects.get(key="USER_CONTACT_REGEX").value
		from django.db import connection
		# query = "select group_concat(api_usercontact.number) as contacts from api_usercontact join api_companyuser on api_companyuser.user_id=api_usercontact.user_id join api_company on api_company.id=api_companyuser.company_id where api_usercontact.name REGEXP 'retail|shop|Vastra|Saree|saari|saaree|kurti|lehenga|Lahenga|lehnga|lahnga|blouse|suit|agent|adhat|dalal|fashion|fasion|fashon|feshon|feshion|ethnic|ethanic|ethnik|textile|txtl|textl|market|markt|Online|resaler|Reseller|reseler|agenc' and api_usercontact.name not like '%wishbook%' and api_company.name not like '%wishbook%' "+nosmsuserids_query
		query = "select group_concat(api_usercontact.number) as contacts from api_usercontact join api_companyuser on api_companyuser.user_id=api_usercontact.user_id join api_company on api_company.id=api_companyuser.company_id where api_usercontact.name REGEXP '" + USER_CONTACT_REGEX +"' and api_usercontact.name not like '%wishbook%' and api_company.name not like '%wishbook%' "+nosmsuserids_query

		logger.info("startMarketing company_number_type_inphonebook query = %s"% (query))

		cursor = connection.cursor()
		cursor.execute(query)

		row = cursor.fetchone()
		inphonebookusers = []
		if row[0]:
			inphonebookusers = row[0].split(',')

		for phone_number in list(inphonebookusers):
			phone_number = re.sub('[^0-9+]', '',phone_number)
			phone_number = str(phone_number)[-10:]

			if len(str(phone_number)) < 5:
				continue
			if int(phone_number[0]) in [0,1,2,3,4,5]:
				continue

			final_number = str(countryObj.phone_code)+str(phone_number)

			phonebooknumbers_type.append(final_number)

		if is_companies_type_filter == False:
			companies = []
		if is_guestuser_type_filter == False:
			users = []

	if instance.get("categories", None):
		min_views = instance.get("minimum_category_views", 0)
		category_list = instance["categories"]

		logger.info("startMarketing has categories = %s"% (category_list))

		ccv_users = CompanyCatalogView.objects.filter(catalog__category__in=category_list, clicks__gte=min_views, user__in=users).values_list('user', flat=True).distinct()
		users = list(ccv_users)

		ccv_companies = CompanyCatalogView.objects.filter(catalog__category__in=category_list, clicks__gte=min_views, company__in=companies).values_list('company', flat=True).distinct()
		companies = list(ccv_companies)

	logger.info("startMarketing companies len = %s"% (len(companies)))
	logger.info("startMarketing users len = %s"% (len(users)))
	logger.info("startMarketing csv_phone_numbers len = %s"% (len(csv_phone_numbers)))
	logger.info("startMarketing phonebooknumbers_type len = %s"% (len(phonebooknumbers_type)))

	userids = CompanyUser.objects.filter(company__in=companies).values_list('user', flat=True)
	users.extend(list(userids))

	if instance.get("app_version", None):
		users = UserPlatformInfo.objects.filter(user__in=users, app_version=instance["app_version"]).values_list('user', flat=True)

	if instance.get("last_login_platform", None):
		users = UserProfile.objects.filter(user__in=users, last_login_platform=instance["last_login_platform"]).values_list('user', flat=True)

	#logger.info("startMarketing instance[state] = %s"% (instance.get("state", None)))
	#logger.info("startMarketing instance[test_users] = %s"% (instance.get("test_users", None)))

	if instance.get("test_users", None):
		if len(list(instance["test_users"])) > 0:
			#users = instance.test_users.all().values_list('id', flat=True).distinct()
			users = instance["test_users"]
			csv_phone_numbers = []
			phonebooknumbers_type = []

	users = list(set(users))
	#users = set(users)
	logger.info("startMarketing final users len = %s"% (len(users)))

	notification_image = ""
	if instance.get("image", None):
		notification_image = instance["image"] #instance.image.url

	count_json = {}
	if instance.get("by_in_app_notifications", None) == True or instance.get("by_in_app_notifications", None) == "true":
		rno = random.randrange(100000, 999999, 1)

		not_json = {"notId": rno, "title":instance["campaign_text"], "push_type":"promotional", "image":notification_image}
		if instance.get("deep_link", None):
			not_json["other_para"] = {"deep_link":str(instance["deep_link"])}

		logger.info("startMarketing send notification json = %s"% (not_json))

		#count_json["total_notification_users"] = len(users)

		if action == "count":
			gcm_count = GCMDevice.objects.filter(user__in=users, active=True).count()
			fcm_count = APNSDevice.objects.filter(user__in=users, active=True).count()
			count_json["total_notification_users"] = "Android = "+str(gcm_count)+", IOS = "+str(fcm_count)

			logger.info("startMarketing send notification user len = %s"% (count_json["total_notification_users"]))


		if action == "send":
			if len(users) > 0:
				logger.info("startMarketing send sendNotifications")
				# if settings.TASK_QUEUE_METHOD == 'celery':
				# 	notificationSend.apply_async((users, instance["campaign_html"], not_json), expires=datetime.now() + timedelta(days=2))
				# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				# 	task_id = async(
				# 		'api.tasks.notificationSend',
				# 		users, instance["campaign_html"], not_json
				# 	)
				sendNotifications(users, instance["campaign_html"], not_json)

	if instance.get("by_sms", None) == True or instance.get("by_sms", None) == "true":
		phone_numbers = UserProfile.objects.filter(user__in=users).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
		phone_numbers = list(phone_numbers)

		if len(csv_phone_numbers) > 0:
			phone_numbers.extend(list(csv_phone_numbers))
		unsubscribed_numbers = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()

		phone_numbers = list(set(phone_numbers) - set(unsubscribed_numbers))
		phonebooknumbers_type = list(set(phonebooknumbers_type) - set(unsubscribed_numbers))

		logger.info("startMarketing final phone_numbers len = %s"% (len(phone_numbers)))
		logger.info("startMarketing final phonebooknumbers_type len = %s"% (len(phonebooknumbers_type)))

		count_json["total_sms_phone_numbers"] = len(phone_numbers)+len(phonebooknumbers_type)

		logger.info("startMarketing send sms len = %s"% (count_json["total_sms_phone_numbers"]))

		if action == "send":
			not_logged_in_phone_numbers = UserProfile.objects.filter(user__in=users, user__last_login__isnull=True).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
			not_logged_in_phone_numbers = list(set(not_logged_in_phone_numbers) - set(unsubscribed_numbers))
			logger.info("startMarketing send")
			phone_numbers = list(set(phone_numbers) - set(not_logged_in_phone_numbers))
			if len(phone_numbers) > 0:
				logger.info("startMarketing send smsSend")

				#WB-1713: SuperAdmin: Marketing tool - option to append deeplink at the end of msg
				if instance["login_url_in_sms"]:
					for phonenumber in phone_numbers:
						user_profile = UserProfile.objects.filter(phone_number=phonenumber[-10:]).first()

						print('common fun: startMarketing send smsSend: users: Sending smss to 1 at a time %s' % user_profile )
						smsurl = get_login_url_for_user(name = 'marketing', userprofile = user_profile)
						print('startMarketing send smsSend: %s' % instance["campaign_text"] + ' ' + str(smsurl))
						smsSend([phonenumber], instance["campaign_text"] + ' ' + str(smsurl), True)
				else:
					logger.info('common fun: startMarketing send smsSend: users: Sending smss to all user')
					logger.info(instance["campaign_text"])
					smsSend(phone_numbers, instance["campaign_text"], True)

			phonebooknumbers_type.extend(list(not_logged_in_phone_numbers))
			#print "action send phonebooknumbers_type =",phonebooknumbers_type
			if len(phonebooknumbers_type) > 0:
				logger.info("startMarketing send smsSendTextNationPromotional")
				if settings.TASK_QUEUE_METHOD == 'celery':
					smsSendTextNationPromotional.apply_async((phonebooknumbers_type, instance["campaign_text"], True), expires=datetime.now() + timedelta(days=2))
				elif settings.TASK_QUEUE_METHOD == 'djangoQ':
					task_id = async(
						'api.tasks.smsSendTextNationPromotional',
						phonebooknumbers_type, instance["campaign_text"], True
					)

	logger.info("startMarketing final count_json = %s"% (count_json))

	return count_json

def filterOrderPaymentStatus(queryset, order_status):
	pendingarr = []
	paidarr = []
	partial_paidarr = []

	salesorders = queryset

	for salesorder in salesorders:
		invoices = salesorder.invoice_set.all()
		#print "common function invoices ==", invoices
		invoices_count = invoices.count()
		if invoices_count == 0:
			status = "Pending"
			pendingarr.append(salesorder.id)
		elif invoices_count == 1:
			#if salesorder.invoice_set.first().payment_status == "Paid":
			if invoices[0].payment_status == "Paid":
				status = "Paid"
				paidarr.append(salesorder.id)
			elif invoices[0].payment_status == "Partially Paid":
				status = "Partially Paid"
				partial_paidarr.append(salesorder.id)
			else:
				status = "Pending"
				pendingarr.append(salesorder.id)
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
				paidarr.append(salesorder.id)
			elif pending == invoices_count:
				status = "Pending"
				pendingarr.append(salesorder.id)
			else:
				#status = "Partially Paid"
				#partial_paidarr.append(salesorder.id)
				if last_paid_invoice_pending_amount is not None and last_paid_invoice_pending_amount < float(1):
					status = "Paid"
					paidarr.append(salesorder.id)
				else:
					status = "Partially Paid"
					partial_paidarr.append(salesorder.id)

	if order_status == 'Pending':
		queryset = queryset.filter(id__in=pendingarr).order_by('-id')
	elif order_status == 'Paid':
		queryset = queryset.filter(id__in=paidarr).order_by('-id')
	elif order_status == 'Partially Paid':
		queryset = queryset.filter(id__in=partial_paidarr).order_by('-id')
	elif order_status == 'Paid or Partially Paid':
		queryset = queryset.filter(Q(id__in=paidarr) | Q(id__in=partial_paidarr)).order_by('-id')
	else:
		queryset = queryset.none()

	return queryset


def shippingChargeOnAddress(productids, seller_address, ship_to, total_products):
	from api.models import Product, PincodeZone

	jsonarr = {}

	weight = Product.objects.filter(id__in=productids).aggregate(Sum('weight')).get('weight__sum', 0)
	if weight is None:
		weight = 0

	logger.info("ShippingChargeOnAddress weight = %s" % (weight))
	#logger.info("ShippingChargeOnAddress order obj = %s" % (order))
	logger.info("ShippingChargeOnAddress shipto = %s" % (ship_to))

	# pincode = []
	# if ship_to:
	# 	logger.info("ShippingCharge shipto pincode = %s" % (ship_to.pincode))
	# 	pincode = PincodeZone.objects.filter(pincode=ship_to.pincode)
	#
	# 	logger.info("ShippingCharge pincode = %s" % (pincode))
	# 	if len(pincode) == 0 or pincode[0].is_servicable == False:
	# 		raise serializers.ValidationError({"pincode_not_servicable":"Sorry, our shipping partners do not deliver at the selected pincode. Please add another address or opt for Other Transportation Medium"})

	# shipcharge = 0
	# if seller_address and ship_to:
	# 	logger.info("ShippingCharge pincode[0] = %s" % (pincode[0]))
	# 	shipcharge = shippingChargesOnPincode(seller_address.pincode, ship_to.pincode, weight)

	shipcharge = 0
	# if seller_address and ship_to:
	if ship_to:
		logger.info("ShippingCharge shipto pincode = %s" % (ship_to.pincode))
		pincode = PincodeZone.objects.filter(pincode=ship_to.pincode)

		logger.info("ShippingCharge pincode = %s" % (pincode))
		if len(pincode) > 0 and pincode[0].is_servicable == True:

			logger.info("ShippingCharge pincode[0] = %s" % (pincode[0]))
			if seller_address:
				shipcharge = shippingChargesOnPincode(seller_address.pincode, ship_to.pincode, weight)
		elif total_products < 6:
			shipcharge = 179
		else:
			raise serializers.ValidationError({"pincode_not_servicable":"Sorry, our shipping partners do not deliver at the selected pincode. Please add another address or opt for Other Transportation Medium"})



	if total_products == 1:
		jsonarr['shipping_charge'] = max(shipcharge, 79)
	else:
		jsonarr['shipping_charge'] = max(shipcharge, 179)

	#jsonarr['only_wishbook_shipping'] = soObj.total_products() < 6
	if total_products < 6:
		jsonarr['only_wishbook_shipping'] = True
	return jsonarr

def getBrandWiseDiscount(selling_company, product):
	from api.models import DiscountRule

	sellerdiscoutrules = DiscountRule.objects.filter(selling_company = selling_company)

	discount_percent = Decimal(0.0)
	if sellerdiscoutrules.filter(brands=product.catalog.brand).exists():
		sdr = sellerdiscoutrules.filter(brands=product.catalog.brand).last()
		logger.info("getBrandWiseDiscount if brand exist sdr = %s"% (sdr))
		discount_percent = sdr.cash_discount

	if discount_percent <= Decimal(0.0):
		if sellerdiscoutrules.filter(all_brands=True).exists():
			sdr = sellerdiscoutrules.filter(all_brands=True).last()
			logger.info("getBrandWiseDiscount all_brands sdr = %s"% (sdr))
			discount_percent = sdr.cash_discount

	if discount_percent is None:
		discount_percent = Decimal(0.0)

	logger.info("getBrandWiseDiscount discount_percent = %s"% (discount_percent))
	return discount_percent

def getSupplierRelDiscountV2(selling_company, buying_company, is_cash_discount, product):
	from api.models import Buyer

	discount_percent = Decimal(0.0)

	buyerObj = Buyer.objects.filter(selling_company=selling_company, buying_company=buying_company, status="approved").first()
	if buyerObj:
		logger.info("getSupplierRelDiscountV2 buyerObj = %s"% (buyerObj))
		if is_cash_discount:
			discount_percent = buyerObj.final_cash_discount()
		else:
			discount_percent = buyerObj.final_discount()

	if discount_percent is None:
		discount_percent = Decimal(0.0)

	if discount_percent <= Decimal(0.0):
		discount_percent = getBrandWiseDiscount(selling_company, product)

	logger.info("getSupplierRelDiscountV2 discount_percent = %s"% (discount_percent))
	return discount_percent

def getIsCashDiscount(order):#cash or credit discount
	# from api.models import Buyer

	buyoncredit = False
	payment_details = ""
	if order.payment_details:
		payment_details = order.payment_details.lower()
	if order.processing_status=="Pending" and "buy on credit" in payment_details:
		buyoncredit = True
	if order.order_type == "Credit":
		buyoncredit = True

	is_cash_discount = order.processing_status not in ["In Progress", "Dispatched", "Delivered"] and buyoncredit==False

	# discount_percent = getSupplierRelDiscount(order.seller_company, order.company, is_cash_discount)

	logger.info("getIsCashDiscount is_cash_discount = %s"% (is_cash_discount))
	return is_cash_discount

def getSupplierRelDiscount(selling_company, buying_company, is_cash_discount):
	from api.models import Buyer, CompanyBuyerGroup

	discount_percent = Decimal(0.0)

	buyerObj = Buyer.objects.filter(selling_company=selling_company, buying_company=buying_company, status="approved").first()
	if buyerObj:
		logger.info("getSupplierRelDiscount buyerObj = %s"% (buyerObj))
		if is_cash_discount:
			#discount_percent = buyerObj.cash_discount
			discount_percent = buyerObj.final_cash_discount()
		else:
			#discount_percent = buyerObj.discount
			discount_percent = buyerObj.final_discount()

		# ~ if discount_percent is None or discount_percent <= Decimal('0.01'):
			# ~ print "DiscountRule logic"
			# ~ item = invoiceitems[0]
			# ~ order_item = item.get('order_item')
			# ~ catalog = order_item.product.catalog
			# ~ catalog_type = "Public"
			# ~ if catalog.view_permission == "push":
				# ~ catalog_type = "Private"
			# ~ buying_company = invoiceObj.order.company
			# ~ buyer_segmentations = BuyerSegmentation.objects.filter(Q(company=invoiceObj.order.seller_company) & Q(Q(buyers=buying_company) | Q(buyer_segmentation__city__isnull=True, buyer_segmentation__category__isnull=True) | Q(buyer_segmentation__city=buying_company.city, buyer_segmentation__category=buying_company.category.all()) ))
			# ~ drObj = DiscountRule.objects.filter(Q(selling_company=invoiceObj.order.seller_company, discount_type=catalog_type) & Q(Q(all_brands=True) | Q(brands=catalog.brand)) & Q(buyer_segmentations__in=buyer_segmentations) ).first()
			# ~ print drObj
	else:
		cbgObj = CompanyBuyerGroup.objects.filter(company=selling_company, buyer_type="Public").first()
		logger.info("getSupplierRelDiscount cbgObj = %s, selling_company = %s, buyer_type = %s"% (cbgObj, selling_company.id, "Public"))
		if cbgObj:
			if is_cash_discount:
				discount_percent = cbgObj.cash_discount
				#discount_percent = cbgObj.final_cash_discount()
			else:
				discount_percent = cbgObj.discount
				#discount_percent = cbgObj.final_discount()

	if discount_percent is None:
		discount_percent = Decimal(0.0)

	logger.info("getSupplierRelDiscount discount_percent = %s"% (discount_percent))
	return discount_percent

def getOrderCCDiscount(order):#cash or credit discount
	from api.models import Buyer, CompanyBuyerGroup

	buyoncredit = False
	payment_details = ""
	if order.payment_details:
		payment_details = order.payment_details.lower()
	if order.processing_status=="Pending" and "buy on credit" in payment_details:
		buyoncredit = True
	if order.order_type == "Credit":
		buyoncredit = True

	is_cash_discount = order.processing_status not in ["In Progress", "Dispatched", "Delivered"] and buyoncredit==False

	discount_percent = getSupplierRelDiscount(order.seller_company, order.company, is_cash_discount)

	logger.info("getOrderCCDiscount discount_percent = %s"% (discount_percent))
	return discount_percent

def getTaxClassObj(selling_company, buying_company, category, rate):#GST Tax
	from api.models import CategoryTaxClass, TaxClass

	location_type = ""
	if selling_company.state != buying_company.state:
		location_type = "Inter State"
	elif selling_company.state.state_type == "UT" and selling_company.state == buying_company.state:
		location_type = "UT"
	else:
		location_type = "Same State"
	logger.info("getTaxClassObj location_type = %s"% (location_type))

	tcids = CategoryTaxClass.objects.filter(category=category).values_list('tax_classes', flat=True)
	taxObjs= TaxClass.objects.filter(Q(id__in=tcids, location_type=location_type) & Q( Q(Q(from_price__lte=rate) | Q(from_price__isnull=True)) & Q(Q(to_price__gte=rate) | Q(to_price__isnull=True)) ))
	logger.info("getTaxClassObj taxObjs = %s"% (str(taxObjs)))

	return taxObjs

def catalogDeleteElesticEntry(instance):
	from api.search import CatalogIndex
	from django.core.mail import send_mail

	try:
		obj = CatalogIndex.get(id=instance.id, ignore=404)
		logger.info("catalogDeleteElesticEntry CatalogIndex = %s"% (obj))
		if obj:
			obj.delete()
		logger.info("catalogDeleteElesticEntry CatalogIndex deleted success")
	except Exception as e:
		logger.info("catalogDeleteElesticEntry CatalogIndex Exception = %s" % (e))
		if settings.DEBUG==False:
			mail_status = send_mail("catalogDeleteElesticEntry", "Error = "+str(e)+", Catalog ID = "+str(instance.id), "tech@wishbook.io", ["tech@wishbook.io"])
			logger.info(str(mail_status))
		pass

#WB-1610 : Django: If someone changes company name - then all catalog entries for that company in elastic search should be updated
def get_catalog_sellers_names(catalog_obj):
	from api.models import CatalogSeller

	return CatalogSeller.objects.filter(catalog=catalog_obj, selling_type="Public", status="Enable").values_list('selling_company__name', flat=True)

#WB-1713: SuperAdmin: Marketing tool - option to append deeplink at the end of msg
def get_login_url_for_user(name, userprofile):
	extra = ''
	otp = getLastOTP(userprofile)
	smsurl = str('https://app.wishbooks.io/?m=')+str(userprofile.phone_number)+'&o='+str(otp)+'&c='+str(userprofile.country.id)+extra
	return urlShortener(smsurl)

def getCompanyTypeArray(companytype):
	arr = []

	if companytype.manufacturer is True:
		arr.append('Manufacturer')
	if companytype.wholesaler_distributor is True:
		arr.append('Wholesaler Distributor')
	if companytype.retailer is True:
		arr.append('Retailer')
	if companytype.online_retailer_reseller is True:
		arr.append('Online Retailer Reseller')
	if companytype.broker is True:
		arr.append('Broker')

	return arr


def cartwiseProductOrderArray(catalogs, filtereditems, catalogsjson):
	from api.v1.serializers import SalesOrderItemSerializer
	from copy import copy

	products = []
	catalogsjson = copy(catalogsjson)

	for item in filtereditems:
		product = SalesOrderItemSerializer(instance=item)
		product = product.data
		products.append(product)

	catalogsjson['products'] = products
	catalogsjson['total_products'] = len(products)
	catalogs.append(catalogsjson)

def handel_catalog_eav(catalog,eav_insert):

	if eav_insert is not None and eav_insert != "":
		logger.info("CatalogSerializer create eav_insert = %s" % (eav_insert))
		for key, value in eav_insert.items():
			logger.info("catalog serializer create eav array key = %s ,value = %s"% (key, value))
			if isinstance(value, list):
				#logger.info("in isinstance(value, list)")
				for subdata in value:
					enumValue = EnumValue.objects.filter(value__iexact=subdata).first()
					if enumValue:
						setattr( catalog.eav, key, enumValue)
						catalog.save()
					else:
						return "Error with eav value %s : %s " %(key,subdata)
			else:
				enumValue = EnumValue.objects.filter(value__iexact=value).first()
				if enumValue is not None and key not in ["other"]:
					#logger.info("in if enumValue")
					setattr( catalog.eav, key, enumValue)
					catalog.save()
				else:
					#logger.info("in last setattr( catalog.eav, key, value)")
					#set text value
					setattr( catalog.eav, key, value)
					catalog.save()
	catalogEAVset(catalog)
	return None

def get_google_sheets_service():
	import os
	from googleapiclient.discovery import build
	from httplib2 import Http
	from oauth2client import file, client, tools

	SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
	configdir = os.path.expanduser('google_sheet/')
	credentials = os.path.join(configdir, 'credentials.json')
	store = file.Storage(credentials)
	creds = store.get()
	if not creds or creds.invalid:
		client_secrets = os.path.join(configdir, 'client_secret.json')
		flow = client.flow_from_clientsecrets(client_secrets, SCOPES)
		creds = tools.run_flow(flow, store)
	service = build('sheets', 'v4', http=creds.authorize(Http()))
	return service

def read_google_sheets_data(SPREADSHEET_ID, RANGE_NAME):
	service = get_google_sheets_service()
	result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
	return result

def write_data_to_google_sheets(SPREADSHEET_ID, RANGE_NAME, resource, VALUE_INPUT_OPTION = "USER_ENTERED"):
	service = get_google_sheets_service()
	service.spreadsheets().values().append(
	  spreadsheetId=SPREADSHEET_ID,
	  range=RANGE_NAME,
	  body=resource,
	  valueInputOption=VALUE_INPUT_OPTION
	).execute()

# def create_new_google_speadsheet(title):
# 	service = get_google_sheets_service()
# 	spreadsheet = {
# 			'properties': {
# 				'title': title
# 			}
# 		}
# 	spreadsheet = service.spreadsheets().create(body=spreadsheet,
# 											fields='spreadsheetId').execute()
# 	return spreadsheet.get('spreadsheetId')
#
# def overwrite_data_to_google_sheets(SPREADSHEET_ID, RANGE_NAME, resource, VALUE_INPUT_OPTION = "USER_ENTERED"):
# 	service = get_google_sheets_service()
# 	service.spreadsheets().values().update(
# 	  spreadsheetId=SPREADSHEET_ID,
# 	  range=RANGE_NAME,
# 	  body=resource,
# 	  valueInputOption=VALUE_INPUT_OPTION
# 	).execute()

from dateutil.parser import parse

def is_date(string):
	try:
		parse(string)
		return True
	except ValueError:
		return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#	WB-2163	Django: Order sheet changes
def update_individual_sheets_rows(SPREADSHEET_ID, RANGE_NAME, super_resource, VALUE_INPUT_OPTION, row_numbers):
	#import pdb; pdb.set_trace()
	#logger.info(row_numbers)
	from datetime import date, datetime, timedelta
	service = get_google_sheets_service()
	sheet_name = RANGE_NAME.split('!')[0]
	sheet_repsonse = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
	#default_format = sheet_repsonse["properties"]['defaultFormat']
	sheets_count =  len(sheet_repsonse["sheets"])
	for i in range(sheets_count):
		if sheet_repsonse["sheets"][i]["properties"]["title"].strip() == sheet_name.strip():
			sheet_id = sheet_repsonse["sheets"][i]["properties"]["sheetId"]
			break

	#logger.info("SPREADSHEET: %s", SPREADSHEET_ID)

	type_dict = {
	type(9999999999999999999999999999999999999999999999999):"numberValue",
	type(True):"boolValue",
	type(u' '):"stringValue",
	type(' '):"stringValue",
	type(1):"numberValue",
	type(None):"stringValue",
	type(0.0):"numberValue",
	}


	for row in super_resource["values"]:
		logger.info("row: %s", row[0])

		start = {
			"sheetId": sheet_id,
	  		"rowIndex":row_numbers[int(row[0])], #asumption
	  		"columnIndex": 0,
	  		}

		values = []
		for cell in row:
			# logger.info('CELL: %s' % cell)
			if type(cell) in [type(u' '),type(' ')]:
				if is_number(cell): #cell.isdigit() and
					if cell.find('.') != -1:
						cell = float(cell)
					else:
						cell = int(cell)
					enum = "NUMBER"
				elif not cell.isdigit() and is_date(cell):
					#cell = str(datetime.strptime(cell, "%d/%m/%Y"))
					enum = "DATE"
				else:
					enum = None
			else:
				enum = None
			# logger.info('CELL: %s- %s' % (cell, enum))
			type_name = type_dict.get(type(cell),"numberValue")
			celldata = {
					# "valueInputOption":{
					# "USER_ENTERED"
					# },
					"userEnteredValue": {
						type_name:cell
						},
						"userEnteredFormat": {
    						"backgroundColor": {
    						"green": 0.8
  							},
						"numberFormat": {
  								"type": enum,
  							},
  						},
						}
			values.append(celldata)
		try:
			# logger.info("row being updated: %s number: %s" % (row,row_numbers[i]))
			resource = {
					# "valueInputOption":{
					# "USER_ENTERED"
					# },
	  				"requests": [
					{
		  			"updateCells": {
					"rows": [
					{
		  			"values":values
					}
	  				],
	  				"fields": "*",
	  				"start": start,
	  					},
					}
	  				],
	  				"includeSpreadsheetInResponse": True,
	  				"responseRanges": [
					"*"
	  				],
	  				"responseIncludeGridData": True
					}
			#logger.info("row: %s" % resource)
			response=service.spreadsheets().batchUpdate(
		  spreadsheetId=SPREADSHEET_ID,
		  #range=RANGE_NAME,
		  body=resource,
		  #valueInputOption=VALUE_INPUT_OPTION
		).execute()
			#logger.info("response: %s " % (response))
		except Exception as e:
			logger.info("cf: update_individual_sheets_rows: got exception: %s" % e)

#	WB-2163	Django: Order sheet changes
def compute_order_details(queryset):
	from api.models import SalesOrder, Catalog, Invoice, Payment, CompanyKycTaxation, Shipment
	#from api.common_functions import read_google_sheets_data, get_google_sheets_service, write_data_to_google_sheets, update_individual_sheets_rows
	import csv
	import StringIO
	from django.utils import timezone

	import os
	all_data_arr = []

	for salesorder in queryset:
		payment_details = salesorder.payment_details
		if payment_details is not None and "Mode : Zaakpay" in payment_details and "Status : Pending" in payment_details:
			continue

		try:
			logger.info("in DailyOrderCSVeMailTask salesorder.id = %s"% (salesorder.id))
			catalogs = salesorder.items.all().values_list('product__catalog', flat=True).distinct()
			catalogs = Catalog.objects.filter(id__in=catalogs)

			buyer_gst_pan = ""
			if CompanyKycTaxation.objects.filter(company=salesorder.company).exists():
				kyc = salesorder.company.kyc
				if kyc.gstin:
					buyer_gst_pan += "GST - " + kyc.gstin + "\n"
				if kyc.pan:
					buyer_gst_pan += "Pan - " + kyc.pan

			seller_gst_pan = ""
			if CompanyKycTaxation.objects.filter(company=salesorder.seller_company).exists():
				kyc = salesorder.seller_company.kyc
				if kyc.gstin:
					seller_gst_pan += "GST - " + kyc.gstin + "\n"
				if kyc.pan:
					seller_gst_pan += "Pan - " + kyc.pan

			ship_to = ""
			if salesorder.ship_to:
				if salesorder.ship_to.street_address:
					ship_to = salesorder.ship_to.street_address
				if salesorder.ship_to.state:
					ship_to += ", "+salesorder.ship_to.state.state_name
				if salesorder.ship_to.city:
					ship_to += ", "+salesorder.ship_to.city.city_name

			invoices = Invoice.objects.filter(order=salesorder)
			invoice_ids = invoices.values_list('id', flat=True)
			payment_ids = Payment.objects.filter(invoice__in=invoice_ids).values_list('id', flat=True)
			trakers_and_couriers = Shipment.objects.filter(invoice__in=invoice_ids).values_list('tracking_number', 'logistics_provider')
			traking_numbers_and_courier_names = []

			for a, b in trakers_and_couriers:
				tac = 'TNo -'+str(a)+', CName - '+str(b)
				traking_numbers_and_courier_names.append(tac)

			invoice_ids = map(str, invoice_ids)
			invoice_ids = ", ".join(invoice_ids)

			traking_numbers_and_courier_names = ", \n".join(traking_numbers_and_courier_names)

			payment_ids = map(str, payment_ids)
			payment_ids = ", ".join(payment_ids)

			buyer_account_details = ""
			try:
				if salesorder.company.paytm_phone_number:
					buyer_account_details += "PayTM Number:" + str(salesorder.company.paytm_phone_number)
				if salesorder.company.bankdetail:
					if salesorder.company.bankdetail.bank_name:
						buyer_account_details += ",\n  Bank Name:" + str(salesorder.company.bankdetail.bank_name)
					if salesorder.company.bankdetail.account_name:
						buyer_account_details += ",\n  Account Holder Name:" + str(salesorder.company.bankdetail.account_name)
					if salesorder.company.bankdetail.account_number:
						buyer_account_details += ",\n  Account Number:" + str(salesorder.company.bankdetail.account_number)
					if salesorder.company.bankdetail.account_type:
						buyer_account_details += ",\n  Account Type:" + str(salesorder.company.bankdetail.account_type)
					if salesorder.company.bankdetail.ifsc_code:
						buyer_account_details += ",\n  IFSC Code:" + str(salesorder.company.bankdetail.ifsc_code)
			except Exception as e:
				logger.info("tasks: dailyUpdateOrderCSVTask: %s :sales order:buyer side: %s" % (e, salesorder))

			seller_account_details = ""
			try:
				if salesorder.seller_company.paytm_phone_number:
					seller_account_details += "PayTM Number:" + str(salesorder.seller_company.paytm_phone_number)
				if salesorder.seller_company.bankdetail:
					if salesorder.seller_company.bankdetail.bank_name:
						seller_account_details += ",\n  Bank Name:" + str(salesorder.seller_company.bankdetail.bank_name)
					if salesorder.seller_company.bankdetail.account_name:
						seller_account_details += ",\n  Account Holder Name:" + str(salesorder.seller_company.bankdetail.account_name)
					if salesorder.seller_company.bankdetail.account_number:
						seller_account_details += ",\n  Account Number:" + str(salesorder.seller_company.bankdetail.account_number)
					if salesorder.seller_company.bankdetail.account_type:
						seller_account_details += ",\n  Account Type:" + str(salesorder.seller_company.bankdetail.account_type)
					if salesorder.seller_company.bankdetail.ifsc_code:
						seller_account_details += ",\n  IFSC Code:" + str(salesorder.seller_company.bankdetail.ifsc_code)
			except Exception as e:
				logger.info("tasks: dailyUpdateOrderCSVTask: %s :sales order:seller side: %s" % (e, salesorder))

			for catalog in catalogs:
				shipping_charges = 0
				amount = 0
				total_amount = 0
				discount = 0
				taxes = 0
				qty = 0
				for invoice in invoices:
					shipping_charges += invoice.shipping_charges

					items = invoice.items.filter(order_item__product__catalog=catalog)
					for item in items:
						amount += item.amount if item.amount else 0
						total_amount += item.total_amount if item.total_amount else 0
						discount += item.discount if item.discount else 0
						taxes += item.tax_value_1 + item.tax_value_2
						qty += item.qty

				created_at = str(timezone.localtime(salesorder.created_at).strftime("%d/%m/%Y"))
				payment_date = ""
				if salesorder.payment_date:
					payment_date = str(salesorder.payment_date.strftime("%d/%m/%Y"))
				rowdata = [salesorder.pk, invoice_ids, created_at, payment_date, salesorder.payment_details, salesorder.payment_status(), catalog.sell_full_catalog, catalog.brand.name, catalog.title, qty, str(amount), str(discount), str(taxes), str(shipping_charges), str(total_amount), payment_ids, salesorder.company.name, salesorder.company.phone_number, buyer_gst_pan, salesorder.company.address.city.city_name, salesorder.company.address.state.state_name, salesorder.company.address.street_address, salesorder.seller_company.name, salesorder.seller_company.phone_number, seller_gst_pan, salesorder.seller_company.address.city.city_name, salesorder.seller_company.address.state.state_name, salesorder.note, ship_to, buyer_account_details, seller_account_details,traking_numbers_and_courier_names]

				all_data_arr.append(rowdata)
				# writer.writerow(rowdata)

		except Exception as e:
			logger.info("in DailyOrderCSVeMailTask Exception for loop error = %s"% (e))
			import traceback
			logger.info("DailyOrderCSVeMailTask Exception for loop traceback error = %s"% (traceback.format_exc()))
			pass

	return all_data_arr
