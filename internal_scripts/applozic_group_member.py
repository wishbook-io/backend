from django.conf import settings
import json
import requests

from api.models import *
from django.contrib.auth.models import User, Group


#to add buyers members in already created applogic group

companies = BuyerSegmentation.objects.all().exclude(applozic_id__isnull=True).values_list('company', flat=True).distinct().order_by('company') #[253] #

for company in companies:
	print "company.id"
	print company
	
	username = CompanyUser.objects.filter(company=company).first().user.username
	url = 'group/add/users?ofUserId='+username
	
	bsa = BuyerSegmentation.objects.filter(company=company).exclude(applozic_id__isnull=True)
	
	
	
	for bs in bsa:
		usrnames = Buyer.objects.filter(selling_company=company, status="approved", group_type__in=bs.group_type.all(), buying_company__city__in=bs.city.all(), buying_company__category__in=bs.category.all()).values_list('buying_company__chat_admin_user__username', flat=True).distinct()
		usrnames = list(usrnames)
		
		if len(usrnames) > 0:
			print bs.applozic_id
			print usrnames
			payload = {"clientGroupIds":[bs.applozic_id], "userIds":usrnames} #["team5dsfdsad25544"]
			r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(payload), headers=settings.APPLOZIC_HEADERS)
			print r
			print r.text
