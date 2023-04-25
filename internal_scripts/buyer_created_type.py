from api.models import *
from api.v0.serializers import *
from django.contrib.auth.models import User, Group

buyers = Buyer.objects.filter(buyer_type="Enquiry").order_by('id')

for buyer in buyers:
	print buyer.id
	buyer.created_type = buyer.buyer_type
	buyer.save()
