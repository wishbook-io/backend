from api.models import *
#from api.v1.serializers import *
#from django.contrib.auth.models import User, Group
from datetime import datetime, date, time, timedelta


buyers = Buyer.objects.filter(Q(created_type="Enquiry") | Q(buyer_type="Enquiry")).order_by('id')
print "total enquiry = ",buyers.count()
for buyer in buyers:
	print buyer.id
	buyer.invitee.country = buyer.selling_company.country
	buyer.invitee.invitee_number = buyer.selling_company.phone_number
	buyer.invitee.save()


