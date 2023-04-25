from django.conf import settings
import json
import requests

from api.models import *
from django.contrib.auth.models import User, Group

companies = Company.objects.all().values_list('id', flat=True).distinct().order_by('id')

for company in companies:
	print "company id"
	print company
	
	bsa = BuyerSegmentation.objects.filter(Q(company=company) & Q(Q(segmentation_name__contains="All Buyers") | Q(segmentation_name__contains="All Distributor") | Q(segmentation_name__contains="All Wholesaler") | Q(segmentation_name__contains="All Semi-Wholesaler") | Q(segmentation_name__contains="All Retailer") | Q(segmentation_name__contains="All Online-Retailer") | Q(segmentation_name__contains="All Resellers") | Q(segmentation_name__contains="All Broker")) ).distinct().order_by('id')
	
	
	
	for bs in bsa:
		print bs.id
		print bs.segmentation_name
		
		#bs.state = []
		bs.city = []
		bs.category = []
		bs.save()
