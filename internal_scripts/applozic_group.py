from django.conf import settings
import json
import requests

from api.models import *
from django.contrib.auth.models import User, Group

from django.core.mail import send_mail

users = User.objects.all().order_by('id')

for user in users:
	#create user
	print "user.id"
	print user.id
	
	url = 'register/client'
	#jsonarr = {"userId":user.username, "deviceType":"1", "applicationId":settings.APPLOZIC_APPID, "contactNumber":user.userprofile.phone_number}
	#r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	#print "user="
	#print r
	#print r.text
	
	companyuser = CompanyUser.objects.filter(user=user).first()
	
	if companyuser is None:
		continue
	
	bseg = BuyerSegmentation.objects.filter(company=companyuser.company, applozic_id__isnull=True)
	
	url = 'group/v2/create?ofUserId='+user.username
	
	#create group
	for bs in bseg:
		usrnames = Buyer.objects.filter(selling_company=bs.company, status="approved", group_type__in=bs.group_type.all(), buying_company__city__in=bs.city.all(), buying_company__category__in=bs.category.all()).exclude(buying_company__isnull=True).values_list('buying_company__chat_admin_user__username', flat=True).distinct()
		usrnames = list(usrnames)
		
		usrnames = [i for i in usrnames if i is not None]
		
		print usrnames

		jsonarr = {"ofUserId":user.username, "groupName":user.username+" "+bs.segmentation_name, "groupMemberList":usrnames, "type":"5"}
		r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
		print r
		print r.text
		
		r = r.json()
		
		if r["status"] == "error":
			mail_status = send_mail("Applozic error", "Error = "+str(r)+" <br> "+str(jsonarr), "tech@wishbooks.io", ["tech@wishbooks.io"])
		else:
			
			bs.applozic_id = r["response"]["id"]
			bs.save()
		
