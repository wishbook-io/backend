import csv
from django.contrib.auth.models import User, Group
from api.models import *
from api.v0.serializers import *
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import versioning
from rest_framework.exceptions import *
#from django.http import HttpResponse
from django.template import loader
#from exportheli
import re
import os
import webbrowser
#import time
#from datetime import date, datetime, timedelta

import dateutil.parser

#~ import httplib2
#~ import gdata
#~ from gdata.photos.service import PhotosService
#~ import gdata.media
#~ import gdata.geo
#~ import gdata.gauth
#~ from oauth2client.client import SignedJwtAssertionCredentials
#~ from oauth2client.client import flow_from_clientsecrets
#~ from oauth2client.file import Storage

#create, update and delete to authenticated user
#from rest_framework import permissions
from api.permissions import * #IsOwnerOrReadOnly, IsAdminOrReadOnly, IsOwnerOrAdmin, IsCompanyOrAdmin, IsCompanyAdministratorOrAdmin, IsOwner, HasGroupOrPermission, IsCompanyAdministratorOrAdminOrReadOnly, IsCompanyAdministratorOrAdminOrUser, IsCompanyAdministratorOrAdminOrUserObj, IsCompanyAdministratorOrAdminOrReadOnlyObj, IsCompanyAdministratorOrAdminOrReadOnlyProductObj, IsCompanyAdministratorOrAdminOrReadOnlyBuyerSellerObj, IsCompanyAdministratorOrAdminOrUserSalesOrderObj, IsCompanyAdministratorOrAdminOrUserOrReadOnly, IsCompanyAdministratorOrAdminOrUserPushUserObj, IsCompanyAdministratorOrAdminOrUserPushRelObj, IsCompanyAdministratorOrAuthenticateUser


#from rest_framework.response import Response
import re
from django.db.models import Q

from django.core.exceptions import ObjectDoesNotExist

import json

from django_datatables_view.base_datatable_view import BaseDatatableView

from django.http import HttpResponse  #,HttpResponseBadRequest

from django.db import transaction

from django.core.validators import validate_email

from django.forms.models import model_to_dict

from django.conf import settings

from api.common_functions import *

from django.db.models import Sum, Min, Max, Count

from datetime import datetime, date, time, timedelta

from rest_framework_tracking.mixins import LoggingMixin

from rest_framework.views import APIView

from rest_framework.pagination import PageNumberPagination

#import random

#from registration.backends.default.views import RegistrationView
'''
from import_export import resources

class CatalogResource(resources.ModelResource):

	class Meta:
		model = Catalog
		skip_unchanged = True
        report_skipped = False
		fields = ('id', 'brand', 'title', 'thumbnail', 'view_permission', 'category', 'company', 'company__name')
		export_order = ('id', 'title', 'thumbnail', 'brand', 'view_permission', 'category', 'company', 'company__name')

dataset = CatalogResource().export()
print dataset.csv'''

'''from import_export import resources

class StateResource(resources.ModelResource):

	class Meta:
		model = State
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'state_name', )
		#exclude = ('id', )
		import_id_fields = ('id', )'''

#from import_export import resources
#from import_export import fields

from django.utils import timezone

from rest_framework import filters
import django_filters

#import datetime

def last_modified():
	return datetime.utcnow()
	#return	datetime.datetime(1989, 2, 15, 15, 30, 34)

from rest_framework import renderers
from rest_framework.pagination import LimitOffsetPagination 
from django.db.models import Case, When

class CustomPagination(LimitOffsetPagination):
	def get_paginated_response(self, data):
		return Response(
			 data
		)
from django.core.paginator import Paginator

class SharedByMe(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	pagination_class = CustomPagination
	
	def get(self, request, format=None):
		'''json_data = request.read()
		data = json.loads(json_data)'''
		logger.info("SharedByMe")
		user = request.user
		
		'''if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
			company = user.companyuser.deputed_to
		else:
			company = user.companyuser.company'''
		
		company = user.companyuser.company
		
		data = request.query_params
		
		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		#catalogsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, is_disable=False).exclude(catalog__isnull=True).order_by('-push_reference').values_list('catalog', flat=True).distinct()
		catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()
		##selectionsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, is_disable=False).exclude(selection__isnull=True).values_list('selection', flat=True).distinct()
		pushUserCatalogId = Push_User.objects.filter(selling_company=company, catalog__in=catalogsIds).values_list('catalog', flat=True).distinct()#.order_by('catalog')
		
		catalogsIds = list(catalogsIds)
		logger.info("catalogsIds sort by =")
		logger.info(catalogsIds)
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(catalogsIds)])
		
		catalogs = Catalog.objects.filter(id__in=pushUserCatalogId).select_related('brand').order_by(preserved).distinct()#.order_by('-id')
		
		##pushUserSelectionId = Push_User.objects.filter(selling_company=company, selection__in=selectionsIds).order_by('selection').values_list('selection', flat=True).distinct()
		##selections = Selection.objects.filter(id__in=pushUserSelectionId).prefetch_related('products', 'user__companyuser__company').distinct().order_by('-id')
		
		if data.get('brand', None) is not None:
			brand = data['brand']
			catalogs = catalogs.filter(brand = brand)
		if data.get('category', None) is not None:
			category = data['category']
			catalogs = catalogs.filter(category = category)
		
		is_disable = self.request.query_params.get('is_disable', 'false')
		disableCatalogIds = CatalogSelectionStatus.objects.filter(company=company, status='Disable').exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
		#disableSelectionIds = CatalogSelectionStatus.objects.filter(company=company, status='Disable').exclude(selection__isnull=True).values_list('selection', flat=True).distinct()
		if is_disable == 'true':
			catalogs = catalogs.filter(id__in=disableCatalogIds)
			#selections = selections.filter(id__in=disableSelectionIds)
		else:
			catalogs = catalogs.exclude(id__in=disableCatalogIds)
			#selections = selections.exclude(id__in=disableSelectionIds)
		
		catalogs = filterCatalog(catalogs, company, data)
		#selections = filterSelection(selections, company, data)
			
		paginator = CustomPagination()
		paginator.default_limit = 2000

		catalogs = paginator.paginate_queryset(catalogs, request)
		
		records = []
		
		for cid in catalogs:
			record={}
			record["id"]=cid.id
			record["type"]="catalog"
			record["title"]=cid.title
			record["image"]=cid.thumbnail.thumbnail[settings.LARGE_IMAGE].url
			record["brand_name"]=cid.brand.name
			record["brand_image"]=cid.brand.image.thumbnail[settings.SMALL_SQR_IMAGE].url
			
			#pushUserObjId = Push_User.objects.filter(selling_company=company, catalog=cid.id).values('selling_company','catalog').annotate(Max('id')).values('id__max')
			#pushUserObj = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first()
			
			#pushUserObj = Push_User.objects.filter(selling_company=company, catalog=cid.id).select_related('push', 'user').last()
			#record["total_products"] = Push_User_Product.objects.filter(push=pushUserObj.push, user=pushUserObj.user, catalog=cid.id).values('product').distinct().count()
			cpfRslt = CompanyProductFlat.objects.filter(selling_company=company, is_disable=False, catalog=cid.id).values('buying_company', 'catalog').annotate(total_products=Count('id'), push_ref=Max('push_reference')).values('total_products', 'push_ref')
			logger.info("sharedwithme cpfRslt = ")
			logger.info(cpfRslt)
			if len(cpfRslt) == 0:
				continue
			record["total_products"] = cpfRslt[0]['total_products'] #--cpfObj.count()
			pushuser = Push_User.objects.filter(selling_company=company, catalog=cid.id, push=cpfRslt[0]['push_ref']).select_related('push', 'selling_company').last()
			
			
			#record["full_catalog_orders_only"] = pushUserObj.full_catalog_orders_only
			if pushuser:
				record["full_catalog_orders_only"] = pushuser.full_catalog_orders_only
			else:
				record["full_catalog_orders_only"] = cid.sell_full_catalog
			
			'''record["is_disable"] = False #Push_User.all_objects.filter(selling_company=company, catalog=cid.id, deleted=True).exists()
			if CatalogSelectionStatus.objects.filter(company=company, catalog=cid.id, status="Disable").exists():
				record["is_disable"] = True'''
			record["is_disable"] = CatalogSelectionStatus.objects.filter(company=company, catalog=cid.id, status="Disable").exists()
			
			if pushuser:
				record["is_viewed"] = pushuser.is_viewed
			else:
				record["is_viewed"] = 'yes'
				
			record["exp_desp_date"] = None
			#pushObj = Push.objects.get(pk=cpfRslt[0]['push_ref'])
			if pushuser is not None and pushuser.push.exp_desp_date is not None:
				record["exp_desp_date"] = str(pushuser.push.exp_desp_date)
				
			min_price = CompanyProductFlat.objects.filter(buying_company=company, catalog=cid.id).aggregate(Min('final_price')).get('final_price__min', 0)
			max_price = CompanyProductFlat.objects.filter(buying_company=company, catalog=cid.id).aggregate(Max('final_price')).get('final_price__max', 0)
			#print max_order
			if min_price is None:
				min_price = 0
			if max_price is None:
				max_price = 0
				
			if min_price == max_price:
				record["price_range"] =  str(int(min_price))
			else:
				record["price_range"] =  str(int(min_price))+"-"+str(int(max_price))
			
			supplierObj = None
			if cid.view_permission.lower()=="public":
				supplierObj = cid.company
			else:
				if user.groups.filter(name="salesperson").exists():
					supplierObj = company
				elif pushuser:
					supplierObj = pushuser.selling_company
			
			if supplierObj:
				record["supplier"] = supplierObj.id
				record["supplier_name"] = supplierObj.name
			
			record["push_id"] = cpfRslt[0]['push_ref']
			
			records.append(record)
		
					
		'''for cid in selections:
			record={}
			record["id"]=cid.id
			record["type"]="selection"
			record["title"]=cid.name
			
			imageobj = cid.products.first()
			if imageobj:
				record["image"] = imageobj.image.thumbnail[settings.PRODUCT_MEDIUM_IMAGE].url
			else:
				record["image"]= ""
			
			selectionCompany = cid.user.companyuser.company
			
			record["brand_name"]=selectionCompany.name
			
			if selectionCompany.thumbnail:
				record["brand_image"]=selectionCompany.thumbnail.url
				
			elif Brand.objects.filter(company=selectionCompany).exists():
				brandObj = Brand.objects.filter(company=selectionCompany).only('name','image').first()
				#record["brand_name"]=brandObj.name
				record["brand_image"]=brandObj.image.thumbnail['150x150'].url
			else:
				record["brand_image"]=""
			
			cpfRslt = CompanyProductFlat.objects.filter(selling_company=company, is_disable=False, selection=cid.id).values('buying_company', 'selection').annotate(total_products=Count('id'), push_ref=Max('push_reference')).values('total_products', 'push_ref')
			record["total_products"] = cpfRslt[0]['total_products'] #--cpfObj.count()
			pushuser = Push_User.objects.filter(selling_company=company, selection=cid.id, push=cpfRslt[0]['push_ref']).select_related('push', 'selling_company').last()
			
			
			record["buyable"] = cid.buyable
			
			record["is_disable"] = CatalogSelectionStatus.objects.filter(company=company, selection=cid.id, status="Disable").exists()
			
			if pushuser:
				record["is_viewed"] = pushuser.is_viewed
			else:
				record["is_viewed"] = 'yes'
			
			record["exp_desp_date"] = None
			if pushuser is not None and pushuser.push.exp_desp_date is not None:
				record["exp_desp_date"] = str(pushuser.push.exp_desp_date)
			
			min_price = CompanyProductFlat.objects.filter(buying_company=company, selection=cid.id).aggregate(Min('final_price')).get('final_price__min', 0)
			max_price = CompanyProductFlat.objects.filter(buying_company=company, selection=cid.id).aggregate(Max('final_price')).get('final_price__max', 0)
			#print max_order
			if min_price is None:
				min_price = 0
			if max_price is None:
				max_price = 0
				
			if min_price == max_price:
				record["price_range"] =  str(int(min_price))
			else:
				record["price_range"] =  str(int(min_price))+"-"+str(int(max_price))
			
			supplierObj = None
			if user.groups.filter(name="salesperson").exists():
				supplierObj = company
			elif pushuser:
				supplierObj = pushuser.selling_company
			
			if supplierObj:
				record["supplier"] = supplierObj.id
				record["supplier_name"] = supplierObj.name
			
			record["push_id"] = cpfRslt[0]['push_ref']
			
			records.append(record)
		'''
		
		#records = sorted(records, key=lambda k: k['push_id'], reverse=True)

		return Response(records) #json.dumps(records)




class SharedWithMe(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	pagination_class = CustomPagination
	
	def get(self, request, format=None):
		logger.info("SharedWithMe")
		user = request.user
		company = user.companyuser.company
		
		data = request.query_params
		
		if user.groups.filter(name="salesperson").exists():
			view = SharedByMe.as_view()
			return view(request)
			
		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		##sellingCompanyObj = Buyer.objects.raw('SELECT selling_company_id FROM api_buyer where status="approved" and buying_company_id='+str(company.id))
		#catalogsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, is_disable=False).exclude(catalog__isnull=True).order_by('-push_reference').values_list('catalog', flat=True).distinct()
		catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()
		##selectionsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, is_disable=False).exclude(selection__isnull=True).values_list('selection', flat=True).distinct()
		
		catalogsIds = list(catalogsIds)
		logger.info("catalogsIds sort by =")
		logger.info(catalogsIds)
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(catalogsIds)])
		
		catalogs = Catalog.objects.filter(id__in=catalogsIds).exclude(company=company).select_related('brand').order_by(preserved).distinct()#.order_by('-id')
		##selections = Selection.objects.filter(id__in=selectionsIds).exclude(user__companyuser__company=company).prefetch_related('products', 'user__companyuser__company').distinct().order_by('-id')

		if data.get('brand', None) is not None:
			brand = data['brand']
			catalogs = catalogs.filter(brand = brand)#.order_by('-id')
		if data.get('category', None) is not None:
			category = data['category']
			catalogs = catalogs.filter(category = category)#.order_by('-id')
		
		is_disable = self.request.query_params.get('is_disable', 'false')
		disableCatalogIds = CatalogSelectionStatus.objects.filter(company=company, status='Disable').exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
		##disableSelectionIds = CatalogSelectionStatus.objects.filter(company=company, status='Disable').exclude(selection__isnull=True).values_list('selection', flat=True).distinct()
		if is_disable == 'true':
			catalogs = catalogs.filter(id__in=disableCatalogIds)
			##selections = selections.filter(id__in=disableSelectionIds)
		else:
			catalogs = catalogs.exclude(id__in=disableCatalogIds)
			##selections = selections.exclude(id__in=disableSelectionIds)
		
		
		
		catalogs = filterCatalog(catalogs, company, data)
		##selections = filterSelection(selections, company, data)
		
		paginator = CustomPagination()
		paginator.default_limit = 2000

		catalogs = paginator.paginate_queryset(catalogs, request)
		
		records = []
		
		for cid in catalogs:
			record={}
			record["id"]=cid.id
			record["type"]="catalog"
			record["title"]=cid.title
			record["image"]=cid.thumbnail.thumbnail[settings.LARGE_IMAGE].url
			
			record["brand"]=cid.brand.id
			record["brand_name"]=cid.brand.name
			record["brand_image"]=cid.brand.image.thumbnail[settings.SMALL_SQR_IMAGE].url
			
			#--pushUserObjId = Push_User.objects.filter(user=user, catalog=cid.id).values('user','catalog','selling_company').annotate(Max('id')).values('id__max')
			#pushUserObj = Push_User.objects.filter(id__in=pushUserObjId).only('push').order_by('total_price').first()
			#--pushObj = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first() #.values_list('push', flat=True)
			#--record["total_products"] = Push_User_Product.objects.filter(push=pushObj.push,user=user, catalog=cid.id).values('product').distinct().count()
			#--cpfObj = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, catalog=cid.id)
			cpfRslt = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, catalog=cid.id).values('buying_company', 'catalog').annotate(total_products=Count('id'), push_ref=Max('push_reference')).values('total_products', 'push_ref')
			logger.info("sharedwithme cpfRslt = ")
			logger.info(cpfRslt)
			if len(cpfRslt) == 0:
				continue
			record["total_products"] = cpfRslt[0]['total_products'] #--cpfObj.count()
			pushuser = Push_User.objects.filter(buying_company=company, catalog=cid.id, push=cpfRslt[0]['push_ref']).select_related('push', 'selling_company').last()
			
			#cpfObj = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, catalog=cid.id).last()
			##record["full_catalog_orders_only"] = pushuser.full_catalog_orders_only #Push_User.objects.filter(buying_company=company, catalog=cid.id, push=cpfRslt[0]['push_ref']).values_list('full_catalog_orders_only', flat=True).last()
			if pushuser:
				record["full_catalog_orders_only"] = pushuser.full_catalog_orders_only
			else:
				record["full_catalog_orders_only"] = cid.sell_full_catalog
			#--record["full_catalog_orders_only"] = pushObj.full_catalog_orders_only
			record["is_disable"] = CatalogSelectionStatus.objects.filter(company=company, catalog=cid.id, status="Disable").exists()
			
			if pushuser:
				record["is_viewed"] = pushuser.is_viewed
			else:
				record["is_viewed"] = 'yes'
			
			record["exp_desp_date"] = None
			#pushObj = Push.objects.get(pk=cpfRslt[0]['push_ref'])
			if pushuser is not None and pushuser.push.exp_desp_date is not None:
				record["exp_desp_date"] = str(pushuser.push.exp_desp_date)
			
			
			
			min_price = CompanyProductFlat.objects.filter(buying_company=company, catalog=cid.id).aggregate(Min('final_price')).get('final_price__min', 0)
			max_price = CompanyProductFlat.objects.filter(buying_company=company, catalog=cid.id).aggregate(Max('final_price')).get('final_price__max', 0)
			#print max_order
			if min_price is None:
				min_price = 0
			if max_price is None:
				max_price = 0
				
			if min_price == max_price:
				record["price_range"] =  str(int(min_price))
			else:
				record["price_range"] =  str(int(min_price))+"-"+str(int(max_price))
			
			supplierObj = None
			if cid.view_permission.lower()=="public":
				supplierObj = cid.company
			else:
				if user.groups.filter(name="salesperson").exists():
					supplierObj = company
				elif pushuser:
					supplierObj = pushuser.selling_company
			
			if supplierObj:
				record["supplier"] = supplierObj.id
				record["supplier_name"] = supplierObj.name
			
			record["push_id"] = cpfRslt[0]['push_ref']
			
			records.append(record)
		
		'''for cid in selections:
			record={}
			record["id"]=cid.id
			record["type"]="selection"
			record["title"]=cid.name
			
			imageobj = cid.products.first()
			if imageobj:
				record["image"] = imageobj.image.thumbnail[settings.PRODUCT_MEDIUM_IMAGE].url
			else:
				record["image"]= ""
			
			selectionCompany = cid.user.companyuser.company
			
			record["brand_name"]=selectionCompany.name
			
			
			if selectionCompany.thumbnail:
				record["brand_image"]=selectionCompany.thumbnail.url
				
			elif Brand.objects.filter(company=selectionCompany).exists():
				brandObj = Brand.objects.filter(company=selectionCompany).only('name','image').first()
				#record["brand_name"]=brandObj.name
				record["brand_image"]=brandObj.image.thumbnail['150x150'].url
			else:
				record["brand_image"]=""
			
			#record["total_products"] = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, selection=cid.id).count()
			cpfRslt = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, selection=cid.id).values('buying_company', 'selection').annotate(total_products=Count('id'), push_ref=Max('push_reference')).values('total_products', 'push_ref')
			record["total_products"] = cpfRslt[0]['total_products'] #--cpfObj.count()
			pushuser = Push_User.objects.filter(buying_company=company, selection=cid.id, push=cpfRslt[0]['push_ref']).select_related('push', 'selling_company').last()
			
			
			record["buyable"] = cid.buyable
			
			record["is_disable"] = CatalogSelectionStatus.objects.filter(company=company, selection=cid.id, status="Disable").exists()
			
			if pushuser:
				record["is_viewed"] = pushuser.is_viewed
			else:
				record["is_viewed"] = 'yes'
			
			record["exp_desp_date"] = None
			if pushuser is not None and pushuser.push.exp_desp_date is not None:
				record["exp_desp_date"] = str(pushuser.push.exp_desp_date)
				
			min_price = CompanyProductFlat.objects.filter(buying_company=company, selection=cid.id).aggregate(Min('final_price')).get('final_price__min', 0)
			max_price = CompanyProductFlat.objects.filter(buying_company=company, selection=cid.id).aggregate(Max('final_price')).get('final_price__max', 0)
			#print max_order
			if min_price is None:
				min_price = 0
			if max_price is None:
				max_price = 0
				
			if min_price == max_price:
				record["price_range"] =  str(int(min_price))
			else:
				record["price_range"] =  str(int(min_price))+"-"+str(int(max_price))
			
			supplierObj = None
			if user.groups.filter(name="salesperson").exists():
				supplierObj = company
			elif pushuser:
				supplierObj = pushuser.selling_company
			
			if supplierObj:
				record["supplier"] = supplierObj.id
				record["supplier_name"] = supplierObj.name
			
			record["push_id"] = cpfRslt[0]['push_ref']
			
			records.append(record)'''
		
		#sorting json custom field push_id
		#records = sorted(records, key=lambda k: k['push_id'], reverse=True)
		
		#r = Paginator(records, 2)
		#paginator = PageNumberPagination()
		#paginator.page_size = 2
		
		'''paginator = CustomPagination()
		paginator.default_limit = 2000

		result_page = paginator.paginate_queryset(records, request)
		
		return Response(result_page)'''
		return Response(records)

class BuyerViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = Buyer.objects.all()
	serializer_class = BuyerSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnlyBuyerSellerObj, )
	
	def get_queryset(self):
		queryset = Buyer.objects.all().select_related('buying_company', 'invitee__invite', 'invitee__country', 'group_type').prefetch_related('buying_company__branches__city__state', 'buying_company__branches__state').order_by('-id')
		
		status = self.request.query_params.get('status', None)
		if status is not None:
			if status.lower() == "pending":
				queryset = queryset.filter(status__in=['buyer_pending','supplier_pending', 'buyer_registrationpending', 'supplier_registrationpending'])
			else:
				queryset = queryset.filter(status=status)
		
		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(buying_company=company)
		
		buyerSegmentation = self.request.query_params.get('buyer_segmentation', None)
			
		user = self.request.user
		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				queryset = queryset.filter(selling_company=company)
				
				if buyerSegmentation is not None:
					buyer_segmentation = BuyerSegmentation.objects.get(pk=buyerSegmentation)
					
					'''city = buyer_segmentation.city.values_list('id', flat=True)
					category = buyer_segmentation.category.values_list('id', flat=True)
					group_type = buyer_segmentation.group_type.values_list('id', flat=True)'''
					
					group_type = buyer_segmentation.group_type.values_list('id', flat=True)
					if buyer_segmentation.city.count() == 0:
						city = City.objects.all().values_list('id', flat=True)
					else:
						city = buyer_segmentation.city.values_list('id', flat=True)
					if buyer_segmentation.category.count() == 0:
						category = Category.objects.all().values_list('id', flat=True)
					else:
						category = buyer_segmentation.category.values_list('id', flat=True)
					
					return queryset.filter(status='approved', buying_company__city__in=city, buying_company__category__in=category, group_type__in=group_type).distinct()
					
					
				else:
					return queryset
				
			else:
				return Buyer.objects.none()
		except ObjectDoesNotExist:
			return Buyer.objects.none()
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(selling_company=company, status='buyer_pending')

