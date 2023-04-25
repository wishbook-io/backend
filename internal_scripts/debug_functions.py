from django.forms import widgets
from rest_framework import serializers
from api.models import *
from api.common_functions import *

from django.contrib.auth.models import User, Group
from rest_framework import permissions
from django.conf import settings

from push_notifications.models import GCMDevice ,APNSDevice

import requests
import grequests
from django.db.models import Sum, Min, Max, Count
import datetime
#from datetime import datetime


from django.core.exceptions import ObjectDoesNotExist

import random

from versatileimagefield.serializers import VersatileImageFieldSerializer
#from rest_framework.validators import UniqueTogetherValidator

from django.db.models import Value
from django.db.models.functions import Concat


from django.core.mail import send_mail
from django.template import loader

from rest_framework.validators import UniqueTogetherValidator
import logging
logger = logging.getLogger(__name__)


import json
import ast

import urllib
'''
from api.v0.notifications import *
from notifier.shortcuts import send_notification
#from notifier.shortcuts import create_notification
from api.v0.notifier_backend import *'''
from api.v0.serializers import *



#print Company.objects.all()

selling_company = raw_input("selling_company id: ") 
buying_company = raw_input("buying_company id: ") 

selling_company = Company.objects.get(pk=selling_company)
buying_company = Company.objects.get(pk=buying_company)

#def pushOnApproves(selling_company, buying_company):
logger.info("== pushOnApproves() ==")
#logger.info("In pushOnApproves for buyer start at "+str(datetime.now()))
logger.info(str(selling_company.name))
logger.info(str(buying_company.name))

buyerRef = Buyer.objects.filter(selling_company = selling_company, buying_company=buying_company).select_related('group_type').first()

logger.info("buyerRef")
logger.info(buyerRef)

#scPushIds = Push.objects.filter(company=selling_company, to_show='yes', buyer_segmentation__city__in=buying_company.city, buyer_segmentation__category__in=buying_company.category.all(), buyer_segmentation__group_type__in=buyerRef.group_type).values_list('id', flat=True)
sellingPushes = Push.objects.filter(company=selling_company, to_show='yes', buyer_segmentation__city=buying_company.city, buyer_segmentation__category=buying_company.category.all(), buyer_segmentation__group_type=buyerRef.group_type).values_list('id', flat=True).distinct()

logger.info("sellingPushes companys pushed list")
logger.info(sellingPushes)

#sellingPushUser = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).select_related('user').first()

catalogArr = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).exclude(catalog__isnull=True).values('catalog').annotate(Max('id')).values('id__max')#.distinct().values_list('id', flat=True)
print catalogArr
selectinArr = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).exclude(selection__isnull=True).values('selection').annotate(Max('id')).values('id__max')#.distinct().values_list('id', flat=True)
print selectinArr
sellPushUsers = Push_User.objects.filter(Q(id__in=catalogArr) | Q(id__in=selectinArr)).values_list('id', flat=True).distinct()

logger.info("sellPushUsers companys push_user first to get single user")
logger.info(sellPushUsers)
'''
sellPushUsers = []
if sellingPushUser:
	sellingUser = sellingPushUser.user
	sellPushUsers = Push_User.objects.filter(push__in=sellingPushes, user=sellingUser, selling_company=selling_company).values_list('id', flat=True).distinct()
	
	logger.info("sellPushUsers companys push_user list")
	logger.info(sellPushUsers)'''

pushUserObj = None
sellCompUser = CompanyUser.objects.filter(company = selling_company, user__groups__name="administrator").select_related('user').first()
selluser = sellCompUser.user
if selling_company.push_downstream == 'yes':
	logger.info("Downstream = yes")
	pushUserObj = Push_User.objects.filter(Q(buying_company=selling_company, push__push_downstream='yes', user=selluser) | Q(id__in=sellPushUsers)).exclude(push__buyer_segmentation__isnull = True).select_related('push__buyer_segmentation', 'catalog', 'selection', 'selling_company', 'buying_company', 'push__company').order_by('-push__time')[:7] ##[::-1]
else:
	logger.info("Downstream = no")
	pushUserObj = Push_User.objects.filter(id__in=sellPushUsers).exclude(push__buyer_segmentation__isnull = True).select_related('push__buyer_segmentation', 'catalog', 'selection', 'selling_company', 'buying_company', 'push__company').order_by('-push__time')[:7] ##[::-1]

logger.info("final pushed pushUserObj list")
logger.info(pushUserObj)

#if selling_company.push_downstream == 'yes':
	#print "push_downstream"
	#sellCompUser = CompanyUser.objects.filter(company = selling_company, user__groups__name="administrator").first()
	#selluser = sellCompUser.user
	#print selluser
	#pushUserObj = Push_User.objects.filter(Q(buying_company=selling_company, push__push_downstream='yes', user=selluser) | Q(id__in=sellPushUsers)).order_by('-push__time')[:7] ##[::-1]

if pushUserObj:
	logger.info("has pushUserObj = ")
	
	
	
	completedCatalog = []
	completedSelection = []
	
	#logger.info(str(pushUserObj))
	
	for puObj in pushUserObj:
		logger.info("in  for loop of pushUserObj")
		buyerIds =  Buyer.objects.filter(selling_company = selling_company, buying_company=buying_company, buying_company__city__in=puObj.push.buyer_segmentation.city.all(), buying_company__category__in=puObj.push.buyer_segmentation.category.all(), group_type__in=puObj.push.buyer_segmentation.group_type.all()).distinct().select_related('selling_company', 'buying_company')
		
		if Push_User.objects.filter(push=puObj.push, buying_company=buying_company).exists():
			logger.info("alredy pushed to buyer company : pushId / continue")
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
			
			logger.info("in  for loop of pushUserObj has buyerIds")
			
			catalog = puObj.catalog
			selection = puObj.selection
			
			if catalog:
				if catalog.id in completedCatalog:
					logger.info("alredy pushed to buyer company : catalog / continue")
					continue
				else:
					completedCatalog.append(catalog.id)
					
				catalogs = Catalog.objects.filter(id=catalog.id)
			else:
				catalogs = Catalog.objects.none()
				
			if selection:
				if selection.id in completedSelection:
					logger.info("alredy pushed to buyer company : selection / continue")
					continue
				else:
					completedSelection.append(selection.id)
					
				selections = Selection.objects.filter(id=selection.id)
			else:
				selections = Selection.objects.none()
				
			catalogProducts = []
			selectionProducts = []
			catalogRate = []
			selectionRate = []
			
			##	title	to	url
			
			##buyerIds = Buyer.objects.filter(selling_company=selling_company, buying_company=buying_company)#.last()#, status="approved"
			
			pushImage = ''
			pushType = ''
			catalogId = None
			pushName = ''
			
			if catalogs:
				logger.info("catalogs")
				for catalog in catalogs:
					pushName = catalog.title
					pushImage = catalog.thumbnail.thumbnail['400x562'].url
					pushType="catalog"
					table_id = catalog.id
					
					logger.info(pushName)
					
					fixRate = 0
					percentageRate = 0
					
					productDObj = []
					
					##check push is seller_company
					if puObj.selling_company == selling_company:
						pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=puObj.user, catalog=catalog).select_related('product')
						for productDetail in pushUserProduct:
							productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price, productDetail.product])
							
						catalogProducts.append(productDObj)
						
						#buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()
						catalogRate.append([0,0])
					else:
						pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=selluser, catalog=catalog).select_related('product')
						for productDetail in pushUserProduct:
							productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price, productDetail.product])
							
						catalogProducts.append(productDObj)
						
						buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()
						
						if buyerobj is None:
							logger.info("has not approve buyer for perticuler push : selection / continue")
							continue
						catalogRate.append([buyerobj.fix_amount,buyerobj.percentage_amount])
			
			if selections:
				logger.info("selections")
				for selection in selections:
					pushName = selection.name
					pushImage = ""
					if selection.products.exists():
						pushImage = selection.products.all().first().image.thumbnail['400x562'].url #[0]
					pushType="selection"
					table_id = selection.id
					
					logger.info(pushName)
					
					fixRate = 0
					percentageRate = 0
					
					productDObj = []
					
					##check push is seller_company
					if puObj.selling_company == selling_company:
						pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=puObj.user, selection=selection).select_related('product')
						for productDetail in pushUserProduct:
							productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price, productDetail.product])
							
						selectionProducts.append(productDObj)
						
						#buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()
						selectionRate.append([0,0])
						
					else:
						pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=selluser, selection=selection).select_related('product')
						for productDetail in pushUserProduct:
							productDObj.append([productDetail.product.id,productDetail.sku, productDetail.price, productDetail.product])
							
						selectionProducts.append(productDObj)
						
						buyerobj = Buyer.objects.filter(selling_company=puObj.selling_company, buying_company=puObj.buying_company, status="approved").last()
						
						if buyerobj is None:
							logger.info("has not approve buyer for perticuler push : selection / continue")
							continue
						selectionRate.append([buyerobj.fix_amount,buyerobj.percentage_amount])
			
			
			
			title = puObj.push.message
			
			pushobj = puObj.push
			
			#city = puObj.push.buyer_segmentation.city.all().values_list('id', flat=True)
			#category = puObj.push.buyer_segmentation.category.all().values_list('id', flat=True)
			#group_type = puObj.push.buyer_segmentation.group_type.all().values_list('id', flat=True)
			city = puObj.push.buyer_segmentation.city.values_list('id', flat=True)
			category = puObj.push.buyer_segmentation.category.values_list('id', flat=True)
			group_type = puObj.push.buyer_segmentation.group_type.values_list('id', flat=True)
			push_downstream = "no" #puObj.push.push_downstream
			
			company_image = None 
			if puObj.push.company.thumbnail:
				company_image = puObj.push.company.thumbnail.url
			elif Brand.objects.filter(company=puObj.push.company).exists():
				brandObj = Brand.objects.filter(company=puObj.push.company).only('image').first()
				company_image=brandObj.image.thumbnail['400x562'].url
			
			fullCatalogOrders = puObj.full_catalog_orders_only
			
			
			logger.info("ready for dfsPush")
			'''dfsPush(buyerIds, [], push_downstream, pushobj, pushType, pushImage, title, city, category, catalogs, selections, catalogProducts, selectionProducts, catalogRate, selectionRate, pushName, group_type, selling_company, fullCatalogOrders) #supplier, 
			
			
			pup = Push_User_Product.objects.bulk_create(push_user_product)
			pu = Push_User.objects.bulk_create(push_user)

			#print pup
			#print pu

			push_user_product = []
			push_user = []
			
			
			push(push_users, title, pushobj.id, pushType, pushImage, pushName, company_image, table_id, False)'''
			
			#pushPendingBuyer(peding_push_users, pushobj.id, pushType, pushName, table_id)

logger.info("== pushOnApproves DONE ============================")

