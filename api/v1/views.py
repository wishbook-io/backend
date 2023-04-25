from django.contrib.auth.models import User, Group
from api.models import *
from api.v1.serializers import *
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from api.v1.permissions import *
from api.permissions import *
from rest_framework import filters
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from django.db.models import Q

from django.db import transaction
import glob
import re
import pdb
from django.http import HttpResponse
import csv
from rest_framework.exceptions import *
from rest_framework.renderers import JSONRenderer

from rest_framework_tracking.mixins import LoggingMixin

from rest_framework.views import APIView

from rest_framework import status
from rest_framework import mixins
#from rest_framework import generics

import hashlib
import hmac

import Checksum
import base64
import cgi
from django.http import JsonResponse

from rest_framework.pagination import LimitOffsetPagination
# from rest_framework.decorators import action
from django.db.models import Case, When

from django.utils import timezone


from rest_framework.authtoken.models import Token
from django.contrib.auth import login

from .resources import SalesOrderShipRocketResource

from django_q.brokers import get_broker
# set up a broker instance for better performance
priority_broker = get_broker('priority')

from django.db import connection
import math

#for shiprocket order and awb no. creation
from api.v1.order.ship_rocket import (create_order_on_ship_rocket,
										create_awb_on_ship_rocket,
										get_pickup_locations,
										get_tracking_details,
										check_values_from_frontend
									  )

from api.v1.order.functions import getTotalCartItemCount

class CustomPagination(LimitOffsetPagination):
	def get_paginated_response(self, data):
		return Response(
			 data
		)

import os

def randomString(size=10):
	import string
	import random
	chars=string.ascii_uppercase + string.digits
	return ''.join(random.choice(chars) for _ in range(size))

def getBuyerSupplierProductPrice(buyer, supplier, product):
	print "in getBuyerSupplierProductPrice"

	pu = Push_User.objects.filter(selling_company=supplier, buying_company=buyer, catalog=product.catalog).order_by('-push').first()
	print pu
	if pu:
		psp = PushSellerPrice.objects.filter(selling_company=supplier, product=product, push=pu.push).order_by('-created_at').first()
		print psp
		if psp:
			return psp.price

	if product.catalog.view_permission == "public":
		return product.public_price

	return None


#for admin user only
@api_view(['GET','POST'])
@permission_classes((permissions.IsAdminUser,))
def importCSVOrderInvoiceStatusAdmin(request):
	logger.info("importCSVOrderInvoiceStatusAdmin 111 ====")

	f = request.FILES['sales_order_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	# upload_file=f
	# jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Sales Order CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	# print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	# fileObject = csv.reader(upload_file)
	# row_count = sum(1 for row in fileObject)
	# jobsObj.total_rows = (row_count-1)
	# jobsObj.status = "Scheduled"
	# jobsObj.save()
	#
	# if settings.TASK_QUEUE_METHOD == 'celery':
	# 	task_id = salesOrderCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	# elif settings.TASK_QUEUE_METHOD == 'djangoQ':
	# 	task_id = async(
	# 		'api.tasks.salesOrderCSVImportJobs',
	# 		jobsObj.id,
	# 		broker = priority_broker
	# 	)
	# logger.info("importCSVOrderInvoiceStatusAdmin task_id=")
	# logger.info(str(task_id))


	reader = csv.DictReader(f)
	print "reader =",reader

	appInstanceObj = AppInstance.objects.filter(company=loginCompany).first()

	logger.info("importCSVOrderInvoiceStatusAdmin 222 ====")

	err = ""

	# errorfilename = 'jobs_error_file/order_invoice_status_admin_error_'+str(job_id)+'_'+str(randomString())+'.csv'
	# errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)

	fieldnames = ['order_id', 'invoice_id', 'order_status', 'courier_no', 'awb_no']

	column = 1
	rows = 0
	fields = {}

	csv_headers = reader.fieldnames
	print "csv_headers = ",csv_headers

	wrong_csv_uploaded = False
	for csv_header in csv_headers:
		if csv_header not in fieldnames:
			wrong_csv_uploaded = True

	if wrong_csv_uploaded:
		raise serializers.ValidationError({"File":"Please upload valid file. header doesn't match."})
	else:
		try:
			for fields in reader:
				column += 1

				logger.info(str(fields))

				order_id = fields['order_id']
				invoice_id = fields['invoice_id']
				order_status = fields['order_status']
				courier_no = fields['courier_no']
				awb_no = fields['awb_no']

				if order_id == "" and invoice_id == "":
					err = "Order Id and Invoice Id is required"
					fields["error_or_success"] = err
					writer.writerow(fields)
					continue;

				salesOrderObj = None
				invoiceObj = None

				salesOrderObj = SalesOrder.objects.filter(id=order_id).order_by('-id').first()
				if salesOrderObj is None:
					err = "Order not found"
					fields["error_or_success"] = err
					writer.writerow(fields)
					continue;

				invoiceObj = Invoice.objects.filter(id=invoice_id).order_by('-id').first()
				if invoiceObj is None:
					err = "Invoice not found"
					fields["error_or_success"] = err
					writer.writerow(fields)
					continue;

				jsondata = {}
				jsondata["id"] = salesOrderObj.id
				jsondata["processing_status"] = order_status

				serializer = SalesOrderSerializer(salesOrderObj, data=jsondata, partial=True)
				if serializer.is_valid():
					logger.info("importCSVOrderInvoiceStatusAdmin is_valid")
					serializer.save()
				else:
					logger.info("importCSVOrderInvoiceStatusAdmin serializer.errors = %s" % (serializer.errors))

				if courier_no != "":
					invoiceObj.logistics_provider = courier_no
				if awb_no != "":
					if invoiceObj.tracking_number:
						invoiceObj.tracking_number += ", "+awb_no
					else:
						invoiceObj.tracking_number = awb_no
				invoiceObj.save()


				# rows += 1
				# jobsObj.completed_rows=rows
				# jobsObj.save()


		except Exception as e:
			logger.info("shipmentDispatchCSVImportJobs start error = %s"% (str(e)))


	return Response({"success": "OrderInvoiceStatus."})


@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVOrder(request):
	logger.info("importCSVOrder 111 ====")
	#data = request.data

	#f=open("ftp/order.csv", 'r')
	#f=open("ftp/order_final.csv", 'r')



	f = request.FILES['sales_order_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Sales Order CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	#salesOrderCSVImportJobs(jobsObj.id, request)
	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = salesOrderCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.salesOrderCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
	logger.info("salesOrderCSVImportJobs task_id=")
	logger.info(str(task_id))
	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})




	'''f = request.FILES['sales_order_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	first_line = f.readline()[:-1].split(',')
	logger.info(first_line)
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	flag = True

	logger.info("importCSVOrder 222 ====")

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Sales Order CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = upload_file.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info("content_type = %s"% (filetype))
	if str(filetype) not in supportcontenttype:
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	err = ""

	csvresponse = HttpResponse(content_type='text/csv')
	csvresponse['Content-Disposition'] = 'attachment; filename="errorsalesorder.csv"'
	writer = csv.writer(csvresponse)
	writer.writerow(['order_number', 'buyer_name', 'buyer_number', 'catalog', 'sku', 'qty', 'rate', 'packing_type', 'item_remark', 'order_remark', 'broker_number', 'error or success'])

	buyer_ids = []
	products = []
	orders = []

	sellingCompanyObj = Buyer.objects.filter(buying_company=loginCompany, status="approved").values_list('selling_company', flat=True).distinct()
	catalogsIds = Push_User.objects.filter(buying_company=loginCompany, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()
	catalogsIds = list(catalogsIds)
	catalogObjs = Catalog.objects.filter(Q(company=loginCompany) | Q(id__in=catalogsIds)) # | Q(view_permission="public")

	disableCatalogIds = getDisableCatalogIds(loginCompany)
	catalogObjs = catalogObjs.exclude(id__in=disableCatalogIds)

	#last_companyObj = None
	last_order_number = None
	last_create_err = None
	soObj = None
	last_soObj_data = []

	salesorder = None


	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.save()

	def cancelOrder():
		logger.info("in cancelOrder() ========================")
		if salesorder:
			#sObj = SalesOrder.objects.get(pk=salesorder.id)
			if "Cancelled_" not in salesorder.order_number:
				salesorder.order_number = "Cancelled_"+salesorder.order_number+"_"+str(salesorder.id)
			salesorder.processing_status = "Cancelled"
			salesorder.save()
			logger.info(salesorder.processing_status)
			logger.info(salesorder.id)
			#for lsd in last_soObj_data:
			#	writer.writerow(lsd)

	column = 1
	rows = 0

	try:
		#with transaction.atomic():
		for line in f:
			try:
				if (flag==True):
					flag = False
					continue
				column += 1
				line = line[:-1].split(',')
				logger.info(str(line))
				fields = {}
				for k,v in columns.iteritems():
					k = re.sub('[^a-zA-Z0-9-_ \.]', '',k) #k.strip() #
					fields[k] = re.sub('[^a-zA-Z0-9-_ \.]', '',line[v]) #line[v].strip() #

				logger.info(str(fields))

				order_number = fields['order_number']
				buyer_name = fields['buyer_name']
				buyer_number = fields['buyer_number']
				catalog = fields['catalog']
				sku = fields['sku']
				print "qty original }}}}}}}}}}}}}}}}}}}}}}}}}}}}", fields['qty']
				qty = int(fields['qty'].split(".")[0])
				print "qty int }}}}}}}}}}}}}}}}}}}}}}}}}}}}", qty
				print "rate original }}}}}}}}}}}}}}}}}}}}}}}}}}}}", fields['rate']
				rate = Decimal(fields['rate'])
				print "rate decimal }}}}}}}}}}}}}}}}}}}}}}}}}}}}", rate
				packing_type = fields['packing_type']
				item_remark = fields['item_remark']
				order_remark = fields['order_remark']

				broker_number = fields.get('broker_number', "")

				if buyer_name == "" and buyer_number == "" and last_order_number is None:
					err = "Buyer Name or Buyer Number is required"
					writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
					continue;

				if qty == "" and rate == "":
					err = "Qty and Rate are required"
					writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
					continue;
				logger.info("processing order number = "+str(order_number)+" last order number "+ str(last_order_number))

				if order_number != last_order_number and order_number != "":
					if salesorder is not None and salesorder.processing_status == "Draft":
						salesorder.processing_status = "Accepted"
						salesorder.save()
						logger.info("Draft to Accepted = %s"% (str(salesorder.processing_status)))
						salesorder = None


					companyObj = None
					if buyer_number:
						buyerObj = Buyer.objects.filter(selling_company=loginCompany, buying_company__phone_number=buyer_number).last()
						if buyerObj is None:
							cpa = CompanyPhoneAlias.objects.filter(alias_number=buyer_number, status="Approved").last()
							if cpa:
								companyObj = cpa.company
						else:
							companyObj = buyerObj.buying_company
					if buyer_name != "" and companyObj is None:
						caObj = CompanyAccount.objects.filter(company=loginCompany, mapped_accout_ref=buyer_name).last()
						if caObj:
							companyObj = caObj.buyer_company
						else:
							buyerObj = Buyer.objects.filter(Q(selling_company=loginCompany) & Q(Q(buying_company__name=buyer_name) | Q(buying_company_name=buyer_name))).last()
							if buyerObj:
								companyObj = buyerObj.buying_company

					if companyObj is None:
						err = "Buying Company not matched"
						writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
						continue;

					#last_companyObj = companyObj

					#create new order with buyer details
					pudata = {}
					pudata['order_number'] = order_number
					pudata['customer_status'] = 'Pending'
					pudata['processing_status'] = 'Draft'
					pudata['seller_company'] = loginCompany.id
					pudata['company'] = companyObj.id
					pudata['items'] = []

					if broker_number != "":
						brokerObj = Buyer.objects.filter(selling_company=loginCompany, buying_company__phone_number=broker_number).last()
						if brokerObj:
							pudata['broker_company'] = brokerObj.buying_company.id

					logger.info("pudata json = %s"% (str(pudata)))
					salesorderser = SalesOrderSerializer(data=pudata, context={'request': request})
					if salesorderser.is_valid():
						logger.info("order save is_valid")
						salesorder = salesorderser.save(user=loginUser)

						#salesorderSalesOrder.objects.get(pk=soObj.id)

						#last_soObj_data.append([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), "Order Cancelled"])

					else:
						err = salesorderser.errors.values()
						logger.info("order save error")
						logger.info(str(err))
						#cancelOrder()
						writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
						continue;

					last_order_number = order_number

				else:
					companyObj = salesorder.company #last_companyObj

				print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
				logger.info("companyObj = %s"% (str(companyObj)))

				if catalog == "" and sku == "":
					err = "Catalog or SKU is required"
					cancelOrder()
					writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
					continue;

				aiObj = AppInstance.objects.filter(company=loginCompany).last()

				catalogObj = None
				if catalog != "":
					if aiObj:
						skumapObj=SKUMap.objects.filter(external_catalog__iexact=catalog, app_instance=aiObj).last()
						if skumapObj:
							catalogObj = skumapObj.catalog

					if catalogObj is None:
						catalogObj = catalogObjs.filter(title__iexact=catalog).last()
					logger.info("catalogObj = %s"% (str(catalogObj)))

					if catalogObj is None:
						err = "Catalog not matched"
						if Catalog.objects.filter(id__in=disableCatalogIds, title__iexact=catalog).exists():
							err = "Catalog is disabled"
						cancelOrder()
						writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
						continue;

				oproducts = []

				if sku == "":
					totalproducts = 0
					psExcludeIds = ProductStatus.objects.filter(company=loginCompany, product__catalog=catalogObj, status="Disable").values_list('product', flat=True)
					pu = Push_User.objects.filter(selling_company=loginCompany, buying_company=companyObj, catalog=catalogObj).order_by('-push').first()
					logger.info("pu = %s"% (str(pu)))
					if pu:
						totalproducts = PushSellerPrice.objects.filter(selling_company=loginCompany, product__in=catalogObj.products.all(), push=pu.push).exclude(product__in=psExcludeIds).values_list('product', flat=True).count()
					if catalogObj.view_permission == "public" and totalproducts == 0:
						totalproducts = catalogObj.products.exclude(id__in=psExcludeIds).count()

					if totalproducts == 0 and pu is None and catalogObj.view_permission == "push":
						err = "Catalog is not shared with this buyer"
						print "1 ?????????????", err
						#cancelOrder()
						#writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), err])
						#continue;
						totalproducts = catalogObj.products.exclude(id__in=psExcludeIds).count()

					#totalproducts = catalogObj.products.count()
					logger.info("totalproducts = %s"% (str(totalproducts)))
					if totalproducts == 0:
						err = "Catalog has no products"
						cancelOrder()
						writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
						continue;

					designwiseqty = float(qty)/ totalproducts

					logger.info("designwiseqty = %s"% (str(designwiseqty)))
					if (qty % totalproducts) > 0:
						#shouldbeqty = (round(designwiseqty)) * totalproducts
						#err = "Number of designs not matched (should be "+str(shouldbeqty)+", whereas qty "+str(qty)+" uploaded)"
						err = "Qty should be the multiple of "+str(totalproducts)+" (no. of designs in this catalog)"
						cancelOrder()
						writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
						continue;

					if pu is None and catalogObj.view_permission == "push":
						# for Catalog is not shared with this buyer
						err = "Catalog is not shared with this buyer"
						print "2 ?????????????", err
						for product in catalogObj.products.exclude(id__in=psExcludeIds):
							oproducts.append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
					else:
						#price matching for shared catalog
						if totalproducts > 0 and pu is not None:
							pspObjs = PushSellerPrice.objects.filter(selling_company=loginCompany, product__in=catalogObj.products.all(), push=pu.push)
							is_loop_break = False
							for pspObj in pspObjs:
								shared_price = getBuyerSupplierProductPrice(companyObj, loginCompany, pspObj.product)
								logger.info("shared_price ============= %s"% (str(shared_price)))
								if shared_price is None:
									err = "Buyer doesn't received all products of this catalog"
									cancelOrder()
									writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
									is_loop_break = True
									break
								if Decimal(shared_price) != Decimal(rate):
									err = "Price not matched (should be "+str(shared_price)+" instead of "+str(rate)+" uploaded)"
									cancelOrder()
									writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
									is_loop_break = True
									break
								oproducts.append({"product":pspObj.product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
							if is_loop_break:
								continue
						#price matching for public catalog
						else:
							is_loop_break = False
							for product in catalogObj.products.all():
								shared_price = getBuyerSupplierProductPrice(companyObj, loginCompany, product)
								logger.info("shared_price ============= %s"% (str(shared_price)))
								if Decimal(shared_price) != Decimal(rate):
									err = "Price not matched (should be "+str(shared_price)+" instead of "+str(rate)+" uploaded)"
									cancelOrder()
									writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
									#continue;
									is_loop_break = True
									break
								oproducts.append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
							if is_loop_break:
								continue
				#single sku handling
				else:
					designwiseqty = qty
					logger.info("designwiseqty = %s"% (str(designwiseqty)))

					product = None
					#aiObj = AppInstance.objects.filter(company=loginCompany).last()
					if aiObj:
						skumapObj=SKUMap.objects.filter(external_sku__iexact=sku, app_instance=aiObj).last()
						if skumapObj:
							product = skumapObj.product

					if product is None:
						if catalogObj:
							product = catalogObj.products.filter(sku__iexact=sku).last()
						else:
							product = Product.objects.filter(sku__iexact=sku, catalog__in=catalogObjs).last()

					logger.info("product = %s"% (str(product)))
					if product is None:
						err = "SKU not matched"
						cancelOrder()
						writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
						continue;
					shared_price = getBuyerSupplierProductPrice(companyObj, loginCompany, product)

					logger.info("shared_price ============= %s"% (str(shared_price)))
					if Decimal(shared_price) != Decimal(rate):
						err =  "Price not matched (should be "+str(shared_price)+" instead of "+str(rate)+" uploaded)"
						cancelOrder()
						writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
						continue;
					#products[buyer_index].append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
					oproducts.append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})

				logger.info("before saving order items: ============= %s"% (str(oproducts)))
				#print salesorder
				print salesorder.id
				#saving order items
				for product in oproducts:
					productobj = Product.objects.get(pk=product["product"])
					salesitem = SalesOrderItem.objects.get_or_create(product=productobj, quantity=product["quantity"], rate=product["rate"], sales_order = salesorder, pending_quantity=product["quantity"], note=product["note"], packing_type=product["packing_type"])
					logger.info("successfully saved order items")

				writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), "Success"])

				rows += 1
				jobsObj.completed_rows=rows
				jobsObj.save()

			except Exception as e:
				logger.info("importCSVOrder forloop error = %s"% (str(e)))
				err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}
				pass

		if salesorder is not None and salesorder.processing_status == "Draft":
			salesorder.processing_status = "Accepted"
			salesorder.save()
			salesorder = None

	except Exception as e:
		logger.info("importCSVOrder start error = %s"% (str(e)))
		err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}
		pass

	jobsObj.completed_rows=rows
	jobsObj.status = 'Completed'
	jobsObj.end_time = timezone.now()
	jobsObj.save()

	try:
		f.close()
	except Exception as e:
		logger.info(str(e))
		pass

	if err != "":
		logger.info(str(err))
		try:
			logger.info("error file save to error_file")
			#logger.info(str(csvresponse))
			#jobsObj.error_file=csvresponse
			jobsObj.status = 'Completed With Errors'
			if jobsObj.error_details is None:
				jobsObj.error_details = "Download error file and re-upload it after corrections"
			jobsObj.save()
		except Exception as e:
			logger.info(str(e))
		return csvresponse
	else:
		return Response({"success": "Successfully csv uploaded"})'''

@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVShipment(request):
	logger.info("importCSVShipment 111 ====")

	f = request.FILES['invoice_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Shipment Sales Order CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = shipmentCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.shipmentCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
	logger.info("importCSVShipment task_id=")
	logger.info(str(task_id))
	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})


@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVShipmentDispatch(request):
	logger.info("importCSVShipmentDispatch 111 ====")

	f = request.FILES['shipment_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Shipment Dispatch CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = shipmentDispatchCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.shipmentDispatchCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
	logger.info("importCSVShipmentDispatch task_id=")
	logger.info(str(task_id))
	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})



@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def syncOpeningInventoryCSV(request):
	logger.info("importCSVDataman 111 ====")

	data = request.data
	if data.get('inventory_path', None) is None:
		raise serializers.ValidationError({"Stock":"Enter csv path"})

	inventory_path = data['inventory_path']
	print inventory_path

	#f=open("ftp/dataman_ptc/Stock.csv", 'r')
	f=open(inventory_path, 'r')

	#f = request.FILES['dataman_csv[0]']
	first_line = f.readline()[:-1].split(',')
	print first_line
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	#flag = True

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	logger.info("importCSVDataman 222 ====")

	err = ""

	#csvresponse = HttpResponse(content_type='text/csv')
	#csvresponse['Content-Disposition'] = 'attachment; filename="errordataman.csv"'
	#writer = csv.writer(csvresponse)
	#writer.writerow(['Brand', 'Category', 'Catalog', 'DesignNumber', 'ProductCode', 'Stock'])

	warehouse=Warehouse.objects.filter(company=loginCompany).first()

	appInsObj = AppInstance.objects.filter(company=loginCompany).first() #, app__api_min_version="v1", app__api_max_version="v1"

	opStk = OpeningStock.objects.create(company=loginCompany)#, created_at=timezone.now()


	try:
		with transaction.atomic():

			for line in f:
				#if (flag==True):
				#	flag = False
				#	continue
				line = line[:-1].split(',')
				print line
				fields = {}
				for k,v in columns.iteritems():
					#k = re.sub('\W+', '',k)
					k = re.sub('[^a-zA-Z0-9-_ ]', '',k)
					fields[k] = re.sub('[^a-zA-Z0-9-_ ]', '',line[v])

				#logger.info(str(fields))

				brand = fields['Brand']
				category = fields['Category']
				catalog = fields['Catalog']

				design_number = fields['DesignNumber']
				product_code = fields['ProductCode']
				in_stock = int(fields['Stock'])

				print appInsObj.id
				print product_code
				if SKUMap.objects.filter(app_instance=appInsObj, external_sku=product_code).exists():
					print "IN SKUMap"
					skuMapObj = SKUMap.objects.get(app_instance=appInsObj, external_sku=product_code)

					opStkObj = OpeningStockQty.objects.create(opening_stock=opStk, product=skuMapObj.product, in_stock=in_stock)

					if not Stock.objects.filter(company=loginCompany, product=skuMapObj.product).exists():
						Stock.objects.create(company=loginCompany, product=skuMapObj.product, in_stock=in_stock, available=in_stock)
					else:
						stockObj = Stock.objects.get(company=loginCompany, product=skuMapObj.product)

						available = stockObj.available
						blocked = stockObj.blocked
						open_sale = stockObj.open_sale

						stockObj.in_stock = in_stock
						stockObj.available = max(in_stock - (open_sale + blocked), 0)
						stockObj.blocked = min(open_sale + blocked, in_stock)
						stockObj.open_sale = max(open_sale + blocked - in_stock, 0)
						stockObj.save()

						'''stockObj = Stock.objects.get(product=skuMapObj.product, warehouse = warehouse)
						oldStock = stockObj.in_stock
						stockObj.in_stock = stock
						stockObj.save()
						if oldStock < stock:
							if stockObj.blocked < stockObj.open_sale:
								stockObj.blocked = stockObj.blocked + min((stockObj.open_sale - stockObj.blocked), stockObj.in_stock)
							stockObj.save()
						else:
							stockObj.blocked = stockObj.in_stock
							stockObj.save()'''


				'''warehouseObj = Warehouse.objects.filter(company = loginCompany).first()

				productObj = Product.objects.filter(sku=product_code, catalog__brand=brand).first()

				if warehouseObj is not None and productObj is not None:
					Stock.objects.create(warehouse=warehouseObj, product=productObj, in_stock=stock)
				else:
					logger.info("dataman_csv : Enter a valid entry")
					err = {"dataman_csv":"Enter a valid entry"}
					writer.writerow([str(brand), str(category), str(catalog), str(design_number), str(product_code), str(stock),])
					continue'''

	except Exception as e:
		print e
		if err != "":
			raise serializers.ValidationError(err)
		else:
			raise serializers.ValidationError({"Stock":"Check csv file"})

	try:
		f.close()
	except Exception as e:
		logger.info(str(e))
		pass

	#if err != "":
	#	print csvresponse
	#	return csvresponse
	#else:
	return Response({"success": "Successfully sync csv"})


@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVSKUMap(request):
	logger.info("importCSVSKUMap 111 ====")

	f = request.FILES['skumap_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="SKU Map CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = skuMapCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.skuMapCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
	logger.info("importCSVSKUMap task_id=")
	logger.info(str(task_id))
	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})

@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVCompanyMap(request):
	logger.info("importCSVCompanyMap 111 ====")

	f = request.FILES['companymap_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Company Map CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = companyMapCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.companyMapCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
	logger.info("importCSVCompanyMap task_id=")
	logger.info(str(task_id))
	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})

@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVOpeningInventory(request):
	logger.info("importCSVOpeningInventory 111 ====")

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	query_params = request.query_params

	'''if query_params.get('warehouse', None) is None:
		raise serializers.ValidationError({"inventory_csv":"Select warehouse"})

	warehouse = query_params['warehouse']

	if not Warehouse.objects.filter(id=warehouse, company=loginCompany).exists():
		raise serializers.ValidationError({"inventory_csv":"Select valid warehouse"})'''

	f = request.FILES['inventory_csv[0]']
	upload_file=f
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	flag = True

	logger.info("importCSVOpeningInventory 222 ====")

	#warehouseObj = Warehouse.objects.get(pk=warehouse)
	#opStk = OpeningStock.objects.create(warehouse=warehouseObj, date=date.today(), upload_file=upload_file, user=loginUser)#, created_at=timezone.now()
	opStk = OpeningStock.objects.create(company=loginCompany, date=date.today(), upload_file=upload_file, user=loginUser)#, created_at=timezone.now()
	#appInsObj = AppInstance.objects.filter(company=loginCompany, user=loginUser).first()

	err = ""

	csvresponse = HttpResponse(content_type='text/csv')
	csvresponse['Content-Disposition'] = 'attachment; filename="errorinventory.csv"'
	writer = csv.writer(csvresponse)
	'''errorfilename = 'inventory/openinginventory_error_'+str(opStk.id)+'_'+str(randomString())+'.csv'
	errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
	errorfile = open(errorfilepath, "wb+")
	writer = csv.writer(errorfile)'''
	writer.writerow(['sku', 'in_stock', 'error'])

	try:
		#with transaction.atomic():

		for line in f:
			if (flag==True):
				flag = False
				continue
			line = line[:-1].split(',')
			fields = {}
			for k,v in columns.iteritems():
				#k = re.sub('\W+', '',k)
				k = re.sub('[^a-zA-Z0-9-_ ]', '',k)
				fields[k] = re.sub('[^a-zA-Z0-9-_ ]', '',line[v])

			logger.info(str(fields))

			sku = fields['sku']
			#warehouse = fields['warehouse']
			in_stock = int(fields['in_stock'])

			'''if not Warehouse.objects.filter(name=warehouse, company=loginCompany).exists():
				logger.info("Enter a valid warehouse")
				err = {"skumap_csv":"Enter a valid warehouse : "+warehouse}
				writer.writerow([sku, warehouse, in_stock, 'enter valid warehouse'])
				continue'''

			'''if not Product.objects.filter(sku=sku, catalog__company = loginCompany).exists():
				logger.info("Enter a valid sku")
				err = {"skumap_csv":"Enter a valid sku : "+sku}
				writer.writerow([sku, warehouse, in_stock, 'enter valid sku'])
				continue'''

			'''if not SKUMap.objects.filter(app_instance__company=loginCompany, external_sku=sku).exists():
				logger.info("Enter a valid sku")
				err = {"skumap_csv":"Enter a valid sku : "+sku}
				writer.writerow([sku, in_stock, 'enter valid sku'])
				continue

			#warehouseObj = Warehouse.objects.filter(name=warehouse, company=loginCompany).first()
			#productObj = Product.objects.filter(sku=sku, catalog__company = loginCompany).first()
			skuMapObj = SKUMap.objects.get(app_instance__company=loginCompany, external_sku=sku)'''

			sellingCompanyObj = Buyer.objects.filter(buying_company=loginCompany, status="approved").values_list('selling_company', flat=True).distinct()
			pushUserProductId = CompanyProductFlat.objects.filter(buying_company=loginCompany, selling_company__in=sellingCompanyObj).order_by('product').values_list('product', flat=True).distinct()
			companyAndPublicCatlogId = Catalog.objects.filter(Q(view_permission__icontains='public') | Q(company=loginCompany)).values_list('id', flat=True).distinct()

			if not Product.objects.filter(Q(sku=sku) & (Q(catalog__in=companyAndPublicCatlogId) | Q(id__in=pushUserProductId))).exists():
				logger.info("Enter a valid sku")
				err = {"skumap_csv":"Enter a valid sku : "+sku}
				writer.writerow([sku, in_stock, 'enter valid sku'])
				continue

			productObj = Product.objects.filter(Q(sku=sku) & (Q(catalog__in=companyAndPublicCatlogId) | Q(id__in=pushUserProductId))).first()



			opStkObj = OpeningStockQty.objects.create(opening_stock=opStk, product=productObj, in_stock=in_stock)

			if Stock.objects.filter(company=loginCompany, product=productObj).exists():
				stockObj = Stock.objects.get(company=loginCompany, product=productObj)

				available = stockObj.available
				blocked = stockObj.blocked
				open_sale = stockObj.open_sale

				stockObj.in_stock = in_stock
				stockObj.available = max(in_stock - (open_sale + blocked), 0)
				stockObj.blocked = min(open_sale + blocked, in_stock)
				stockObj.open_sale = max(open_sale + blocked - in_stock, 0)
				stockObj.save()

				'''stockObj = Stock.objects.get(product=productObj, warehouse = warehouseObj)
				oldStock = stockObj.in_stock
				stockObj.in_stock = in_stock
				stockObj.save()
				if oldStock < in_stock:
					if stockObj.blocked < stockObj.open_sale:
						stockObj.blocked = stockObj.blocked + min((stockObj.open_sale - stockObj.blocked), stockObj.in_stock)
					stockObj.save()
				else:
					stockObj.blocked = stockObj.in_stock
					stockObj.save()'''
			else:
				Stock.objects.create(company=loginCompany, product=productObj, in_stock=in_stock, available=in_stock)

			'''if Stock.objects.filter(product=productObj, warehouse = warehouseObj).exists():
				#Stock.objects.filter(product=productObj, warehouse = warehouseObj).update(in_stock=in_stock)
				stockObj = Stock.objects.get(product=productObj, warehouse = warehouseObj)
				oldStock = stockObj.in_stock
				stockObj.in_stock = in_stock
				stockObj.save()
				if oldStock < in_stock:
					if stockObj.blocked < stockObj.open_sale:
						stockObj.blocked = stockObj.blocked + min((stockObj.open_sale - stockObj.blocked), stockObj.in_stock)
					stockObj.save()
				else:
					stockObj.blocked = stockObj.in_stock
					stockObj.save()
			else:
				Stock.objects.create(product=productObj, warehouse = warehouseObj, in_stock=in_stock)'''

	except Exception as e:
		print e
		#opStk.error_file=errorfilename
		#opStk.save()
		if err != "":
			raise serializers.ValidationError(err)
		else:
			raise serializers.ValidationError({"inventory_csv":"Check csv file"})

	try:
		f.close()
	except Exception as e:
		logger.info(str(e))
		pass

	if err != "":
		'''opStk.error_file=errorfilename
		opStk.save()
		return errorfile'''
		return csvresponse
	else:
		#os.remove(errorfilepath)
		return Response({"success": "Successfully uploaded inventory csv"})

@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVAdjustmentInventory(request):
	logger.info("importCSVAdjustmentInventory 111 ====")

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	query_params = request.query_params

	'''if query_params.get('warehouse', None) is None:
		raise serializers.ValidationError({"inventory_csv":"Select warehouse"})

	warehouse = query_params['warehouse']

	if not Warehouse.objects.filter(id=warehouse, company=loginCompany).exists():
		raise serializers.ValidationError({"inventory_csv":"Select valid warehouse"})'''

	f = request.FILES['inventory_csv[0]']
	upload_file=f
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	flag = True

	logger.info("importCSVAdjustmentInventory 222 ====")

	err = ""

	csvresponse = HttpResponse(content_type='text/csv')
	csvresponse['Content-Disposition'] = 'attachment; filename="errorinventory.csv"'
	writer = csv.writer(csvresponse)
	writer.writerow(['sku', 'type', 'quantity', 'error'])

	#warehouseObj = Warehouse.objects.get(pk=warehouse)
	#invAdj = InventoryAdjustment.objects.create(warehouse=warehouseObj, date=date.today(), upload_file=upload_file, user=loginUser)#, created_at=timezone.now()
	invAdj = InventoryAdjustment.objects.create(company=loginCompany, date=date.today(), upload_file=upload_file, user=loginUser)#, created_at=timezone.now()

	try:
		#with transaction.atomic():

		for line in f:
			if (flag==True):
				flag = False
				continue
			line = line[:-1].split(',')
			fields = {}
			for k,v in columns.iteritems():
				#k = re.sub('\W+', '',k)
				k = re.sub('[^a-zA-Z0-9-_ ]', '',k)
				fields[k] = re.sub('[^a-zA-Z0-9-_ ]', '',line[v])

			logger.info(str(fields))

			sku = fields['sku']
			adjustment_type = fields['type']
			quantity = int(fields['quantity'])

			'''if not Warehouse.objects.filter(name=warehouse, company=loginCompany).exists():
				logger.info("Enter a valid warehouse")
				err = {"skumap_csv":"Enter a valid warehouse : "+warehouse}
				writer.writerow([sku, warehouse, quantity, 'enter valid warehouse'])
				continue

			if not Product.objects.filter(sku=sku, catalog__company = loginCompany).exists():
				logger.info("Enter a valid sku")
				err = {"skumap_csv":"Enter a valid sku : "+sku}
				writer.writerow([sku, warehouse, quantity, 'enter valid sku'])
				continue'''

			'''if not SKUMap.objects.filter(app_instance__company=loginCompany, external_sku=sku).exists():
				logger.info("Enter a valid sku")
				err = {"skumap_csv":"Enter a valid sku : "+sku}
				writer.writerow([sku, adjustment_type, quantity, 'enter valid sku'])
				continue

			logger.info("22")

			#warehouseObj = Warehouse.objects.filter(name=warehouse, company=loginCompany).first()
			#productObj = Product.objects.filter(sku=sku, catalog__company = loginCompany).first()
			skuMapObj = SKUMap.objects.get(app_instance__company=loginCompany, external_sku=sku)'''

			sellingCompanyObj = Buyer.objects.filter(buying_company=loginCompany, status="approved").values_list('selling_company', flat=True).distinct()
			pushUserProductId = CompanyProductFlat.objects.filter(buying_company=loginCompany, selling_company__in=sellingCompanyObj).order_by('product').values_list('product', flat=True).distinct()
			companyAndPublicCatlogId = Catalog.objects.filter(Q(view_permission__icontains='public') | Q(company=loginCompany)).values_list('id', flat=True).distinct()

			if not Product.objects.filter(Q(sku=sku) & (Q(catalog__in=companyAndPublicCatlogId) | Q(id__in=pushUserProductId))).exists():
				logger.info("Enter a valid sku")
				err = {"skumap_csv":"Enter a valid sku : "+sku}
				#writer.writerow([sku, in_stock, 'enter valid sku'])
				writer.writerow([sku, adjustment_type, quantity, 'enter valid sku'])
				continue

			productObj = Product.objects.filter(Q(sku=sku) & (Q(catalog__in=companyAndPublicCatlogId) | Q(id__in=pushUserProductId))).first()


			invAdjObj = InventoryAdjustmentQty.objects.create(inventory_adjustment=invAdj, product=productObj, quantity=quantity, adjustment_type=adjustment_type)#, to_warehouse=to_warehouse

			logger.info("33")

			if not Stock.objects.filter(company=loginCompany, product=productObj).exists():
				Stock.objects.create(company=loginCompany, product=productObj, in_stock=quantity, available=quantity)
			elif invAdjObj.adjustment_type == "Add":
				stockObj = Stock.objects.get(company=loginCompany, product=productObj)

				available = stockObj.available
				blocked = stockObj.blocked
				in_stock = stockObj.in_stock
				open_sale = stockObj.open_sale

				stockObj.available = max(in_stock + quantity - (open_sale+blocked), 0)
				stockObj.blocked = min(open_sale + blocked, (in_stock + quantity))
				stockObj.in_stock = in_stock + quantity
				stockObj.open_sale = max(open_sale + blocked - (in_stock+quantity), 0)
				stockObj.save()

				'''stockObj = Stock.objects.get(warehouse=warehouseObj, product=productObj)
				stockObj.in_stock = stockObj.in_stock + quantity
				stockObj.save()
				if stockObj.blocked < stockObj.open_sale:
					stockObj.blocked = stockObj.blocked + min((stockObj.open_sale - stockObj.blocked), stockObj.in_stock)
					stockObj.save()'''

			elif invAdjObj.adjustment_type == "Remove":
				stockObj = Stock.objects.get(company=loginCompany, product=productObj)

				available = stockObj.available
				blocked = stockObj.blocked
				in_stock = stockObj.in_stock
				open_sale = stockObj.open_sale

				stockObj.in_stock = max(in_stock - quantity, 0)
				stockObj.available = max(in_stock - quantity - (open_sale + blocked), 0)
				stockObj.blocked = min(open_sale + blocked, (in_stock - quantity))
				stockObj.open_sale = max(open_sale + blocked -(in_stock - quantity), 0)

				stockObj.save()

				'''stockObj = Stock.objects.get(warehouse=warehouseObj, product=productObj)
				stockObj.in_stock = stockObj.in_stock - quantity
				stockObj.save()

				stockObj.blocked = stockObj.in_stock
				stockObj.save()'''

	except Exception as e:
		print e
		if err != "":
			raise serializers.ValidationError(err)
		else:
			raise serializers.ValidationError({"inventory_csv":"Check csv file"})

	try:
		f.close()
	except Exception as e:
		logger.info(str(e))
		pass

	if err != "":
		return csvresponse
	else:
		return Response({"success": "Successfully uploaded inventory csv"})

@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVCatalog(request):
	logger.info("importCSVCatalog 111 ====")

	f = request.FILES['catalog_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Catalog CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = catalogCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.catalogCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
	logger.info("importCSVCatalog task_id=")
	logger.info(str(task_id))

	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})


@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importBulkCSVCatalog(request):
	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name
	f = request.FILES['catalog_csv[0]']
	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Catalog Bulk CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = catalogBulkCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.catalogBulkCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
		# task_id=catalogBulkCSVImportJobs(jobsObj.id)
	logger.info("importBulkCSVCatalog task_id=")
	logger.info(str(task_id))
	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})


@api_view(['GET','POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVProduct(request):
	logger.info("importCSVCatalog 111 ====")

	f = request.FILES['product_csv[0]']

	loginUser = request.user
	loginCompany = loginUser.companyuser.company
	companyName = loginCompany.name

	upload_file=f
	jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Product CSV", upload_file=upload_file, status="Created", start_time = timezone.now())
	print jobsObj

	filetype = f.content_type
	supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
	logger.info(str(filetype))
	#if "csv" not in str(filetype):
	if str(filetype) not in supportcontenttype:
		logger.info(str(filetype))
		jobsObj.error_details = "Please upload CSV file only"
		jobsObj.save()
		raise serializers.ValidationError({"File":"Please upload CSV file only"})

	fileObject = csv.reader(upload_file)
	row_count = sum(1 for row in fileObject)
	jobsObj.total_rows = (row_count-1)
	jobsObj.status = "Scheduled"
	jobsObj.save()

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = productCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.productCSVImportJobs',
			jobsObj.id,
			broker = priority_broker
		)
	logger.info("importCSVCatalog task_id=")
	logger.info(str(task_id))

	return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})

#classes started
#paytm checksum
class GenerateChecksum(APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		#MERCHANT_KEY = 'L&fvx%_jFpWbQHOG'
		'''print "checksum"
		form = request.POST['_content'] #cgi.FieldStorage()
		#form = json.loads(form)
		#print form['ORDER_ID']
		#form = json.loads(request.body)
		print form'''

		#form = cgi.FieldStorage()
		#print form
		print "start"
		print "body="
		print self.request.body
		print "post="
		print self.request.POST
		print "data="
		print self.request.data
		form = self.request.POST #this was final till 5 Mar 2018

		#form = self.request.data
		#form = json.loads(form)

		logger.info("GenerateChecksum form")
		logger.info(str(form))
		'''checksum_hash = self.request.POST.get('_content', None)
		print "checksum_hash"
		print checksum_hash['CHECKSUMHASH']'''

		checksum_hash = form

		respons_dict = {}

		respons_dict['MID'] = '';
		respons_dict['ORDER_ID'] = '';
		respons_dict['CUST_ID'] = '';
		respons_dict['INDUSTRY_TYPE_ID'] = '';
		respons_dict['CHANNEL_ID'] = '';
		respons_dict['TXN_AMOUNT'] = '';
		respons_dict['WEBSITE'] = '';
		#respons_dict['CALLBACK_URL'] = '';

		Orderid = "";
		for attribute, value in form.items():
			respons_dict[attribute]=value
			if attribute=='ORDER_ID':
				Orderid = value
		print Orderid
		#below code snippet is mandatory, so that no one can use your checksumgeneration url for other purpose .
		for i in respons_dict:
			if "REFUND" == respons_dict[i]:
				respons_dict = {}
				exit()
		#print respons_dict
		logger.info("GenerateChecksum respons_dict")
		logger.info(str(respons_dict))
		#respons_dict = {u'WEBSITE': u'b2b.trivenilabs.com', u'ORDER_ID': u'ORDER200009910', u'MID': u'Wishbo73946389503353', u'CHANNEL_ID': u'WAP', u'THEME': u'merchant', u'INDUSTRY_TYPE_ID': u'Retail', u'CUST_ID': u'CUST23657', u'MOBILE_NO': u'123', u'EMAIL': u'abc@gmail.com', u'TXN_AMOUNT': u'1'}
		checksum = Checksum.generate_checksum(respons_dict, settings.PAYTM_MERCHANT_KEY)

		logger.info("checksum=")
		logger.info(str(checksum))

		paramarr = {};
		paramarr['ORDER_ID'] = Orderid;
		paramarr['CHECKSUMHASH'] = checksum;
		paramarr['payt_STATUS'] = '1';

		#param_dict = json.dumps(paramarr, separators=(',', ':'))
		#print param_dict

		if 'CHECKSUMHASH' not in str(checksum_hash):
			return JsonResponse(paramarr)
		else:
			html = ''
			html += '<head>'
			html += '<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-I">'
			html += '<title>Paytm</title>'
			html += '<script type="text/javascript">'
			html += 'function response(){'
			html += 'return document.getElementById("response").value;'
			html += '}'
			html += '</script>'
			html += '</head>'
			html += 'Redirect back to the app<br>'
			html += '<form name="frm" method="post">'
			html += '<input type="hidden" id="response" name="responseField" value=\''+str(paramarr)+'\'>'
			html += '</form>'
			print html
			return HttpResponse(html)

class GenerateChecksum_V2(APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		#MERCHANT_KEY = 'L&fvx%_jFpWbQHOG'
		'''print "checksum"
		form = request.POST['_content'] #cgi.FieldStorage()
		#form = json.loads(form)
		#print form['ORDER_ID']
		#form = json.loads(request.body)
		print form'''

		#form = cgi.FieldStorage()
		#print form
		logger.info("In paytm GenerateChecksum")
		logger.info("request.body = %s"% (self.request.body))
		logger.info("request.POST = %s"% (self.request.POST))
		logger.info("request.data = %s"% (self.request.data))

		#form = self.request.POST #this was final till 5 Mar 2018

		form = self.request.data
		#form = json.loads(form)

		logger.info("final form date json = %s"% (form))
		'''checksum_hash = self.request.POST.get('_content', None)
		print "checksum_hash"
		print checksum_hash['CHECKSUMHASH']'''

		checksum_hash = form

		respons_dict = {}

		respons_dict['MID'] = '';
		respons_dict['ORDER_ID'] = '';
		respons_dict['CUST_ID'] = '';
		respons_dict['INDUSTRY_TYPE_ID'] = '';
		respons_dict['CHANNEL_ID'] = '';
		respons_dict['TXN_AMOUNT'] = '';
		respons_dict['WEBSITE'] = '';

		respons_dict['CALLBACK_URL'] = '';
		#respons_dict['EMAIL'] = '';
		#respons_dict['MOBILE_NO'] = '';

		Orderid = "";
		for attribute, value in form.items():
			respons_dict[attribute]=value
			if attribute=='ORDER_ID':
				Orderid = value
		print Orderid
		#below code snippet is mandatory, so that no one can use your checksumgeneration url for other purpose .
		for i in respons_dict:
			if "REFUND" == respons_dict[i]:
				respons_dict = {}
				exit()
		#print respons_dict
		logger.info("respons_dict json for generate checksum = %s"% (respons_dict))
		#respons_dict = {u'WEBSITE': u'b2b.trivenilabs.com', u'ORDER_ID': u'ORDER200009910', u'MID': u'Wishbo73946389503353', u'CHANNEL_ID': u'WAP', u'THEME': u'merchant', u'INDUSTRY_TYPE_ID': u'Retail', u'CUST_ID': u'CUST23657', u'MOBILE_NO': u'123', u'EMAIL': u'abc@gmail.com', u'TXN_AMOUNT': u'1'}
		checksum = Checksum.generate_checksum(respons_dict, settings.PAYTM_MERCHANT_KEY)

		logger.info("generated checksum string = %s"% (checksum))

		# ~ paramarr = {};
		# ~ paramarr['ORDER_ID'] = Orderid;
		# ~ paramarr['CHECKSUMHASH'] = checksum;
		# ~ paramarr['payt_STATUS'] = '1';

		paramarr = respons_dict
		paramarr['CHECKSUMHASH'] = checksum;

		#param_dict = json.dumps(paramarr, separators=(',', ':'))
		#print "param_dict=",param_dict

		if 'CHECKSUMHASH' not in str(checksum_hash):
			logger.info("return param_dict = %s"% (paramarr))
			return JsonResponse(paramarr)
		else:
			html = ''
			html += '<head>'
			html += '<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-I">'
			html += '<title>Paytm</title>'
			html += '<script type="text/javascript">'
			html += 'function response(){'
			html += 'return document.getElementById("response").value;'
			html += '}'
			html += '</script>'
			html += '</head>'
			html += 'Redirect back to the app<br>'
			html += '<form name="frm" method="post">'
			html += '<input type="hidden" id="response" name="responseField" value=\''+str(paramarr)+'\'>'
			html += '</form>'
			print html
			return HttpResponse(html)

class VerifyChecksum(APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		user = request.user
		#form = cgi.FieldStorage()
		form = self.request.POST

		logger.info("VerifyChecksum form")
		logger.info(str(form))
		'''logger.info("VerifyChecksum self.request.body")
		logger.info(str(self.request.body))

		logger.info("VerifyChecksum form")
		logger.info(str(form))'''

		respons_dict = {}

		checksum=''
		print "for loop for keys"
		for attribute, value in form.items():
			respons_dict[attribute]=value
			print value
			if attribute=='CHECKSUMHASH':
				checksum = value

		'''for i in form.keys():
			respons_dict[i]=form[i].value
			if i=='CHECKSUMHASH':
				checksum = form[i].value'''

		if 'GATEWAYNAME' in respons_dict:
			if respons_dict['GATEWAYNAME'] == 'WALLET':
				respons_dict['BANKNAME'] = 'null';
		#print "respons_dict"
		#print respons_dict
		#print "checksum"
		#print checksum
		#print "calling verify_checksum function"

		logger.info("VerifyChecksum checksum")
		logger.info(str(checksum))

		logger.info("VerifyChecksum respons_dict")
		logger.info(str(respons_dict))

		verify = Checksum.verify_checksum(respons_dict, settings.PAYTM_MERCHANT_KEY, checksum)
		#print verify

		logger.info("VerifyChecksum verify")
		logger.info(str(verify))

		#print "respons_dict"
		#print respons_dict


		if verify:
			respons_dict['IS_CHECKSUM_VALID'] = 'Y'

			if respons_dict.get('ORDERID', None) is not None:
				amount = respons_dict.get('TXNAMOUNT', 0)
				orderId = respons_dict['ORDERID']

				status = 'Failure'
				if respons_dict['STATUS'] == "TXN_SUCCESS":
					status = 'Success'

				if orderId is not None and "C" in orderId:
					orderId = int(orderId.strip('C'))
					generateCartPayment(orderId, amount, "PayTM", respons_dict, status, user, respons_dict.get('TXNID', None), date.today())
				else:
					generateOrderToInvoice(orderId, amount, "PayTM", respons_dict, user, respons_dict.get('TXNID', None))
					# generateOrderToInvoice(respons_dict['ORDERID'], respons_dict.get('TXNAMOUNT', 0), "PayTM", respons_dict, user, respons_dict.get('TXNID', None))

		else:
			respons_dict['IS_CHECKSUM_VALID'] = 'N'
		print respons_dict

		respons_dict = json.dumps(respons_dict)
		print respons_dict

		#param_dict = json.dumps(respons_dict, separators=(',', ':'))
		#print param_dict

		html = ''
		html += '<head>'
		html += '<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-I">'
		html += '<title>Paytm</title>'
		html += '<script type="text/javascript">'
		html += 'function response(){'
		html += 'return document.getElementById("response").value;'
		html += '}'
		html += '</script>'
		html += '</head>'
		html += 'Redirect back to the app<br>'
		html += '<form name="frm" method="post">'
		html += '<input type="hidden" id="response" name="responseField" value=\''+str(respons_dict)+'\'">'
		html += '</form>'
		print html
		'''
		print '<head>'
		print '<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-I">'
		print '<title>Paytm</title>'
		print '<script type="text/javascript">'
		print 'function response(){'
		print 'return document.getElementById("response").value;'
		print '}'
		print '</script>'
		print '</head>'
		print 'Redirect back to the app<br>'
		print '<form name="frm" method="post">'
		print '<input type="hidden" id="response" name="responseField" value="'+str(respons_dict)+'">'
		print '</form>'
		'''

		return HttpResponse(html)

class PaytmResponse(APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		form = self.request.POST
		#print form

		logger.info("PaytmResponse form")
		logger.info(str(form))

		respons_dict = {}

		checksum=''
		print "for loop for keys"
		for attribute, value in form.items():
			respons_dict[attribute]=value
			print value
			if attribute=='CHECKSUMHASH':
				checksum = value

		'''for i in form.keys():
			respons_dict[i]=form[i].value
			if i=='CHECKSUMHASH':
				checksum = form[i].value'''

		if 'GATEWAYNAME' in respons_dict:
			if respons_dict['GATEWAYNAME'] == 'WALLET':
				respons_dict['BANKNAME'] = 'null';
		#print "respons_dict"
		#print respons_dict
		#print "checksum"
		#print checksum
		#print "calling verify_checksum function"

		logger.info("PaytmResponse checksum")
		logger.info(str(checksum))

		logger.info("PaytmResponse respons_dict")
		logger.info(str(respons_dict))

		respons_dict = json.dumps(respons_dict)
		print respons_dict

		#param_dict = json.dumps(respons_dict, separators=(',', ':'))
		#print param_dict

		html = ''
		html += '<head>'
		html += '<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-I">'
		html += '<title>Paytm</title>'
		html += '<script type="text/javascript">'
		html += 'function response(){'
		html += 'return document.getElementById("response").value;'
		html += '}'
		html += '</script>'
		html += '</head>'
		html += 'Redirect back to the app<br>'
		html += '<form name="frm" method="post">'
		html += '<input type="hidden" id="response" name="responseField" value=\''+str(respons_dict)+'\'">'
		html += '</form>'
		print html

		return HttpResponse(html)

class CheckPaytmStatus(APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		#user = request.user
		#company = user.companyuser.company

		#data = request.data

		#order_id = data['order']
		order_id = self.request.query_params.get('order', None)

		if order_id is None:
			raise serializers.ValidationError({"error":"Please pass order id."})

		paytm_url=settings.PAYTM_STATUS_URL+'?JsonData={"MID":"'+str(settings.PAYTM_MID)+'","ORDERID":"'+str(order_id)+'"}'
		print paytm_url
		response = requests.request("GET", paytm_url)

		print response

		response = response.json()

		print response

		return Response(response)



#paytm checksum

#zaakpay start
class ZaakpayInitiate(APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		form = self.request.POST
		#print form

		logger.info("ZaakpayInitiate form")
		logger.info(str(form))

		respons_dict = {}

		checksum=''
		print "for loop for keys"
		for attribute, value in form.items():
			respons_dict[attribute]=value
			print value
			if attribute=='CHECKSUMHASH':
				checksum = value

		'''for i in form.keys():
			respons_dict[i]=form[i].value
			if i=='CHECKSUMHASH':
				checksum = form[i].value'''

		if 'GATEWAYNAME' in respons_dict:
			if respons_dict['GATEWAYNAME'] == 'WALLET':
				respons_dict['BANKNAME'] = 'null';
		#print "respons_dict"
		#print respons_dict
		#print "checksum"
		#print checksum
		#print "calling verify_checksum function"

		logger.info("ZaakpayInitiate checksum")
		logger.info(str(checksum))

		logger.info("ZaakpayInitiate respons_dict")
		logger.info(str(respons_dict))

		respons_dict = json.dumps(respons_dict)
		print respons_dict

		#param_dict = json.dumps(respons_dict, separators=(',', ':'))
		#print param_dict

		html = ''
		html += '<head>'
		html += '<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-I">'
		html += '<title>Paytm</title>'
		html += '<script type="text/javascript">'
		html += 'function response(){'
		html += 'return document.getElementById("response").value;'
		html += '}'
		html += '</script>'
		html += '</head>'
		html += 'Redirect back to the app<br>'
		html += '<form name="frm" method="post">'
		html += '<input type="hidden" id="response" name="responseField" value=\''+str(respons_dict)+'\'">'
		html += '</form>'
		print html

		return HttpResponse(html)


from django.http import HttpResponseRedirect
from django.shortcuts import redirect

@api_view(['POST','GET'])
@permission_classes((permissions.AllowAny,))
def ZaakpayResponse(request):
	#return HttpResponseRedirect('http://b2b.trivenilabs.com/api/v1/mobikwik/success')
	#return redirect('http://b2b.trivenilabs.com/api/v1/mobikwik/success')
	logger.info("ZaakpayResponse form")
	user = request.user
	#host = request.META.get('HTTP_ORIGIN')#request.META['HTTP_ORIGIN']
	#print host

	#urls = resolve('/api/v1/mobikwik/'+status)
	#print urls

	if request.method.lower() == "get":
		data = request.GET

	if request.method.lower() == "post":
		data = request.data

	logger.info("ZaakpayResponse data = %s"% (data))

	#if request.method.lower() == "get":
	#	return Response({})

	responsecode = data.get('responseCode', None)
	#logger.info("responseCode = ")
	#logger.info(str(responsecode))
	#logger.info(str(int(responsecode[0])))
	if responsecode is not None and int(responsecode) == 100:
		logger.info("if int(responsecode) == 100")
		status = 'Success' #'success'
		#return HttpResponseRedirect('http://b2b.trivenilabs.com/api/v1/mobikwik/success')
	elif responsecode is not None:
		logger.info("int(responsecode) else")
		status = 'Failure' #'failure'
		#return HttpResponseRedirect('http://b2b.trivenilabs.com/api/v1/mobikwik/failure')
		#logger.info(str(response))
	else:
		return Response({})

	# print "orderid="
	# print data.get('orderId', None)
	if data.get('orderId', None) is not None:
		#generateOrderToInvoice(data.get('orderid', None), data.get('amount', None), "Zaakpay", data)
		amount = data.get('amount', None)
		amount = int(amount) / 100;
		orderId = data.get('orderId', None)
		if orderId is not None and "C" in orderId:
			orderId = int(orderId.strip('C'))
			generateCartPayment(orderId, amount, "Zaakpay", data, status, user, None, date.today())
		else:
			generateInvoicePayment(orderId, amount, "Zaakpay", data, status, user, None, date.today())

	full_url = str(settings.GLOBAL_SITE_URL)+'api/v1/zaakpay/'+status.lower()+'/'

	user_agent = request.META.get('HTTP_X_REQUESTED_WITH', None)
	if user_agent:
		user_agent = user_agent.lower()
		logger.info("useragent = %s"% (str(user_agent)))

	if user_agent is None or "com.wishbook.catalog" not in user_agent:
		orderid = ""
		full_url = full_url+"/?ref="+ data.get('orderId', None)
	print full_url

	html = '<html>'
	html += '<head>'
	html += '<title>Wishbook Zaakpay Payment</title>'
	html += '<meta http-equiv="refresh" content="2; URL='+full_url+'">'
	html += '<meta name="keywords" content="automatic redirection">'
	html += '</head>'
	html += '<body>'
	html += 'If your browser doesn\'t automatically go there within a few seconds,'
	html += 'you may want to go back to '
	html += '<a href="'+full_url+'">Wishbook App</a> manually.'
	html += '</body>'
	html += '</html>'
	#print html
	return HttpResponse(html)

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def ZaakpayStatus(request):
	logger.info("Zaakpay Status")
	user = request.user

	if request.method.lower() == "get":
		data = request.GET
	logger.info(str(data))

	logger.info(str(request.get_full_path()))
	status = 0
	if 'success' in request.get_full_path():
		status = 1


	full_url = str(settings.GLOBAL_SITE_URL)
	#full_url = "http://jay.b2bios.com/"
	#full_url = "http://my.wishbooks.io/"


	orderid = ""
	invoiceRef = data.get('ref', None)
	if invoiceRef is not None:
		invoice = Invoice.objects.filter(id=invoiceRef).first()
		if invoice:
			orderid = invoice.order.id
			order_no = invoice.order.order_number
			full_url = full_url+"?type=purchase&id="+str(orderid)+"&name="+str(order_no)+"&status="+str(status)

	logger.info(str(full_url))

	html = '<html>'
	html += '<head>'
	html += '<title>Wishbook Zaakpay Payment</title>'
	html += '<meta http-equiv="refresh" content="2; URL='+full_url+'">'
	html += '<meta name="keywords" content="automatic redirection">'
	html += '</head>'
	html += '<body>'
	html += 'Redirect back to Wishbook.<br>If your browser doesn\'t automatically go there within a few seconds,'
	html += 'you may want to go back to '
	html += '<a href="'+full_url+'">Wishbook</a> manually.'
	html += '</body>'
	print html
	return HttpResponse(html)
#zaakpay end


#cashfree start
class CashFreeGenerateChecksum(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		logger.info("In CashFreeGenerateChecksum")
		logger.info("request.body = %s"% (self.request.body))
		logger.info("request.POST = %s"% (self.request.POST))
		logger.info("request.data = %s"% (self.request.data))

		form = self.request.data

		logger.info("CashFreeGenerateChecksum form json = %s"% (form))

		secretKey = "3e3f76483bed2b4b91f1bdd63210a49aa2287a46"

		mode = "TEST" # <-------Change to TEST for test server, PROD for production
		postData = {
			"appId" : form.get('appId', "9241285a7ab0db6459ef6b1429"),
			"orderId" : form.get('orderId', ""),
			"orderAmount" : form.get('orderAmount', ""),
			"orderCurrency" : form.get('orderCurrency', "INR"),
			"orderNote" : form.get('orderNote', ""),
			"customerName" : form.get('customerName', ""),
			"customerPhone" : form.get('customerPhone', ""),
			"customerEmail" : form.get('customerEmail', ""),
			# "returnUrl" : form.get('returnUrl', ""),
			# "notifyUrl" : form.get('notifyUrl', ""),
			# "paymentMode" : form.get('paymentMode', "")
		}

		logger.info("CashFreeGenerateChecksum postData = %s"% (postData))

		sortedKeys = sorted(postData)
		# signatureData = ""
		# for key in sortedKeys:
		# 	signatureData += key+postData[key]
		signatureData = []
		for key in sortedKeys:
			signatureData.append(key+"="+postData[key])

		signatureData = "&".join(signatureData)
		logger.info("CashFreeGenerateChecksum signatureData = %s"% (signatureData))

		# message = signatureData.encode('utf-8')
		message = bytes(signatureData).encode('utf-8')
		#get secret key from your config
		# secret = secretKey.encode('utf-8')
		secret = bytes(secretKey).encode('utf-8')
		signature = base64.b64encode(hmac.new(secret,message,digestmod=hashlib.sha256).digest())#.decode("utf-8")

		logger.info("CashFreeGenerateChecksum signature = %s"% (signature))

		if mode == 'PROD':
			# url = "https://www.cashfree.com/checkout/post/submit"
			url = "https://www.gocashfree.com/checkout/post/submit"
		else:
			# url = "https://test.cashfree.com/billpay/checkout/post/submit"
			url = "https://test.gocashfree.com/billpay/checkout/post/submit"
		# return render_template('request.html', postData = postData,signature = signature,url = url)
		return Response({"orderId" : postData["orderId"], "checksum" : signature, "status" : "OK"})
#cashfree end

class MultiOrder(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		logger.info("multiorder post start at "+str(datetime.now()))
		user = request.user
		company = None
		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
			else:
				raise serializers.ValidationError({"error":"Company doesn't exists."})
		except ObjectDoesNotExist:
			raise serializers.ValidationError({"error":"Company doesn't exists."})

		#company = user.companyuser.company

		suplier_ids = []
		products = []

		data = request.data

		items = data.pop('items', None)
		backorders = data.pop('backorders', None)

		for item in items:
			if item['selling_company'] not in suplier_ids:
				suplier_ids.append(item['selling_company'])
				#supplier_index = suplier_ids[-1]
				products.append([])

			supplier_index = suplier_ids.index(item['selling_company'])
			products[supplier_index].append(item)

		print suplier_ids
		print products

		order_number = data['order_number']
		for idx, suplier_id in enumerate(suplier_ids):
			pudata = data
			pudata['seller_company'] = suplier_id
			pudata['items'] = products[idx]
			pudata['order_number'] = order_number+'-'+str(idx+1)
			#pudata['customer_status'] = 'Placed'
			pudata['customer_status'] = 'Pending'

			purchaseorder = SalesOrderSerializer(data=pudata, context={'request': request})
			if purchaseorder.is_valid():
				print "save is_valid"
				#print suplier_id
				pObj = purchaseorder.save(user=self.request.user)
				#print pObj.id
				if backorders is not None and len(backorders) > 0 and backorders[0] != '':
					pObj.backorders.add(*backorders)
					pObj.save()

			else:
				print purchaseorder.errors
				raise serializers.ValidationError(purchaseorder.errors)

		return Response({"success":"Successfully backordered done."})

	def get(self, request, format=None):
		logger.info("multiorder get start at "+str(datetime.now()))
		user = request.user
		company = user.companyuser.company

		queryset = None

		selection = self.request.query_params.get('selection', None)
		if selection is not None:
			selectionObj = Selection.objects.get(pk=selection)
			queryset = selectionObj.products.all().exclude(catalog__company=company).select_related('catalog__brand')

		salesorder = self.request.query_params.get('salesorder', None)
		if salesorder is not None and salesorder != '':
			salesorder = salesorder.split(",")
			itemids = SalesOrderItem.objects.filter(sales_order__in=salesorder).exclude(product__catalog__company=company).values_list('product', flat=True)
			queryset = Product.objects.filter(id__in=itemids).exclude(catalog__company=company).select_related('catalog__brand')

		if queryset is None:
			raise serializers.ValidationError({"error":"Please enter valid parameter."})
		#print queryset
		brands = []

		logger.info("multiorder queryset end at "+str(datetime.now()))
		###pushUserObjId = Push_User_Product.objects.filter(buying_company=company, product__in=queryset).values('product', 'user','selection','selling_company').annotate(Max('id')).values('id__max')
		#pushUserObjId = CompanyProductFlat.objects.filter(buying_company=company, product__in=queryset).values('product', 'selling_company', 'selling_company__name', 'final_price').order_by('product', 'final_price', 'selling_company')
		catalogids = queryset.values_list('catalog', flat=True).distinct()

		puids = Push_User.objects.filter(buying_company=company, catalog__in = catalogids).values('catalog', 'buying_company', 'selling_company').annotate(Max('id')).values('id__max')
		#pushUserObjId = Push_User.objects.filter(buying_company=company, catalog__in = catalogids).values_list('push', flat=True)
		#pushUserSellingCompanyObjId = Push_User.objects.filter(buying_company=company, catalog__in = catalogids).values_list('selling_company', flat=True)

		pushUserObjId = Push_User.objects.filter(id__in=puids).values('push', 'selling_company')
		print "pushUserObjId", pushUserObjId

		#pushUserSellingCompanyObjId = Push_User.objects.filter(id__in=puids).values_list('selling_company', flat=True)

		#pushUserObjId = PushSellerPrice.objects.filter(push__in=pushUserObjId, selling_company__in = pushUserSellingCompanyObjId , product__in= queryset).distinct().values('push','product', 'selling_company', 'selling_company__name', 'price').order_by('product', 'price', 'selling_company')

		logger.info("multiorder pushUserObjId end at "+str(datetime.now()))
		products = []
		if pushUserObjId:
			#print pushUserObjId
			###selling_company = Push_User_Product.objects.filter(id__in=pushUserObjId).distinct().values('product', 'selling_company', 'selling_company__name', 'price').order_by('product', 'price', 'selling_company')#pushUser.selling_company.id
			selling_companys = pushUserObjId
			logger.info("multiorder selling_company end at "+str(datetime.now()))

			product = None
			current_product = None
			pushedproducts = []
			for push_sc in selling_companys:
				selling_company = PushSellerPrice.objects.filter(push = push_sc['push'], selling_company = push_sc['selling_company'] , product__in= queryset).distinct().values('push','product', 'selling_company', 'selling_company__name', 'price')
				pushedproducts.extend(selling_company)

			#sorting json custom field push_id

			pushedproducts = sorted(pushedproducts, key=lambda k: k['product'])
			for sc in pushedproducts:
					#logger.info("multiorder loop end at "+str(datetime.now()))

					if sc['product'] != current_product:
						current_product = sc['product']
						if product:
							products.append(product)

						'''for prod in queryset:
							if prod.id == sc['product']:
								product = SelectionPOSProductSerializer(instance=prod)
								product = product.data
								break'''

						product = SelectionPOSProductSerializer(instance=Product.objects.get(pk=sc['product']))
						product = product.data
						'''product = {}
						product['id'] = sc['product']'''
						product['selling_company'] = []

					if company.id == sc['selling_company']:
						continue

					scjson = {}
					scjson['id'] = sc['selling_company']
					scjson['name'] = sc['selling_company__name']
					scjson['price'] = sc['price']
					scjson['push'] = sc['push']
					product['selling_company'].append(scjson)

			products.append(product)

		brandskey = []
		brandsvalue = [] #json
		catalogskey = []

		logger.info("multiorder allprodcuts fetch end at "+str(datetime.now()))
		#if queryset:
		if salesorder is not None:
			qtyObj = SalesOrderItem.objects.filter(sales_order__in=salesorder).values('product').annotate(total_quantity=Sum('quantity'))#.get('quantity__sum', 0)
			#print qtyObj

		for curr_prod in queryset:
			if curr_prod.catalog.brand.id not in brandskey:
				brandskey.append(curr_prod.catalog.brand.id)
				brands = {}
				brands['id'] = curr_prod.catalog.brand.id
				brands['brand_name'] = curr_prod.catalog.brand.name
				brands['catalogs'] = []
				brandsvalue.append(brands)

			for bv in brandsvalue:
				if bv['id'] == curr_prod.catalog.brand.id:
					if curr_prod.catalog.id not in catalogskey:
						catalogskey.append(curr_prod.catalog.id)
						catalogs = {}
						catalogs['id'] = curr_prod.catalog.id
						catalogs['catalog_name'] = curr_prod.catalog.title
						catalogs['products'] = []
						bv['catalogs'].append(catalogs)

					for ct in bv['catalogs']:
						if ct['id'] == curr_prod.catalog.id:
							logger.info("curr_prod object == %s"% (str(curr_prod)))
							found = False
							if salesorder is not None:
								for qt in qtyObj:
									if qt['product'] == curr_prod.id:
										qty = qt['total_quantity']
								'''qty = SalesOrderItem.objects.filter(sales_order__in=salesorder, product=curr_prod.id).aggregate(Sum('quantity')).get('quantity__sum', 0)
								if qty is None:
									qty = 0'''
							logger.info("products array == %s"% (str(products)))
							for loop_prod in products:
								logger.info("product loop_prod == %s"% (str(loop_prod)))
								if loop_prod['id'] == curr_prod.id:
									if salesorder is not None:
										loop_prod['quantity'] = qty
									ct['products'].append(loop_prod)
									found = True
									break
							if not found:
								product = SelectionPOSProductSerializer(instance=curr_prod)
								product = product.data
								product['selling_company'] = []
								if salesorder is not None:
									product['quantity'] = qty
								ct['products'].append(product)
							break
					break

		for brand in brandsvalue:
			for catalog in brand['catalogs']:
				catalog['total_products'] = len(catalog['products'])
		logger.info("multiorder 3lvel fetch end at "+str(datetime.now()))
		if len(brandsvalue) == 0:
			raise serializers.ValidationError({"error":"You can not back order on your own products."})

		return Response(brandsvalue)

'''class ImportArrayInvitee(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		from api.v0.serializers import RegisterSerializer

		logger.info("== importArrayInvitee111 ==")
		#json_data = request.read()
		#data = json.loads(json_data)

		data = request.data

		inviteeArray = data['invitee']
		request_type = data['request_type']
		group_type = data['group_type']

		group_type = GroupType.objects.get(pk=group_type)

		loginUser = request.user
		loginCompany = loginUser.companyuser.company
		companyName = loginCompany.name

		logger.info("== importArrayInvitee222 ==")

		if request_type.lower() == "buyer":
			logger.info("== buyer ==")
			last_buyer_name = None
			last_buyer_company_obj = None

			for invite in inviteeArray:
				buyer_name=invite[0]
				buyer_number=str(invite[1])[-10:]
				#group_type = GroupType.objects.get(pk=invite[3])

				country = Country.objects.get(pk=1)

				if last_buyer_name is not None and last_buyer_name != "" and last_buyer_name == buyer_name:
					logger.info("last_buyer_name is matched with buyer_name")
					logger.info(str(last_buyer_company_obj))
					otpno = random.randrange(100000, 999999, 1)
					username = str(country.phone_code)+str(buyer_number)
					username = username.replace("+", "")
					data = {"username":username, "password1": otpno, "password2": otpno, "phone_number":buyer_number, "country":country.id, "email":str(buyer_number)+"@wishbooks.io", "number_verified":"no", "is_profile_set":False, "company_name":buyer_name, "invited_from":companyName, "company":last_buyer_company_obj.id, "usertype":"administrator"}
					register = RegisterSerializer(data=data, context={'request': request})
					if register.is_valid():
						logger.info("ImportArrayInvitee save register is_valid")
						logger.info(str(data))
						try:
							registerObj = register.save(register)
							print registerObj
						except Exception as e:
							logger.info("ImportArrayInvitee registration error")
							logger.info(str(buyer_number))
							logger.info(str(e))
							pass
					else:
						logger.info("ImportArrayInvitee is_valid() else registration error")
						#print register.errors
						logger.info(str(buyer_number))
						logger.info(str(register.errors))
				else:
					last_buyer_company_obj = add_buyer(loginUser, loginCompany, buyer_name, country, buyer_number, group_type, False);
				last_buyer_name = buyer_name

		elif request_type.lower() == "supplier":
			logger.info("== supplier ==")
			last_supplier_name = None
			last_supplier_company_obj = None
			for invite in inviteeArray:
				supplier_name=invite[0]
				supplier_number=str(invite[1])[-10:]
				#group_type = GroupType.objects.get(pk=invite[3])

				country = Country.objects.get(pk=1)

				if last_supplier_name is not None and last_supplier_name != "" and last_supplier_name == supplier_name:
					logger.info("last_supplier_name is matched with supplier_name")
					logger.info(str(last_supplier_company_obj))
					otpno = random.randrange(100000, 999999, 1)
					username = str(country.phone_code)+str(supplier_number)
					username = username.replace("+", "")
					data = {"username":username, "password1": otpno, "password2": otpno, "phone_number":supplier_number, "country":country.id, "email":str(supplier_number)+"@wishbooks.io", "number_verified":"no", "is_profile_set":False, "company_name":supplier_name, "invited_from":companyName, "company":last_supplier_company_obj.id, "usertype":"administrator"}
					register = RegisterSerializer(data=data, context={'request': request})
					if register.is_valid():
						logger.info("ImportArrayInvitee save register is_valid")
						logger.info(str(data))
						try:
							registerObj = register.save(register)
							print registerObj
						except Exception as e:
							logger.info("ImportArrayInvitee registration error")
							logger.info(str(supplier_number))
							logger.info(str(e))
							pass
					else:
						logger.info("ImportArrayInvitee is_valid() else registration error")
						#print register.errors
						logger.info(str(supplier_number))
						logger.info(str(register.errors))
				else:
					last_supplier_company_obj = add_supplier(loginUser, loginCompany, supplier_name, country, supplier_number, group_type, False);
				last_supplier_name = supplier_name

		return Response({"success": "Invited Contact list successfully"})'''



class ImportArrayInvitee(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		#from api.v0.serializers import RegisterSerializer

		logger.info("== importArrayInvitee111 ==")

		data = request.data

		inviteeArray = data['invitee']
		request_type = data['request_type']
		# group_type = data['group_type']
		group_type = data.get('group_type', 4)

		group_type = GroupType.objects.get(pk=group_type)

		loginUser = request.user
		loginCompany = get_user_company(loginUser) #loginUser.companyuser.company
		if loginCompany is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		companyName = loginCompany.name

		logger.info("== importArrayInvitee222 ==")

		temp_contacts = []

		if request_type.lower() == "buyer":
			logger.info("== buyer ==")
			last_buyer_name = None
			last_buyer_company_obj = None

			jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Buyer", status="Scheduled",total_rows = len(inviteeArray))
			print jobsObj

			filename = 'jobs_upload_file/buyers_mobile_enquiry_'+str(jobsObj.id)+'_'+str(randomString())+'.csv'
			filepath = os.path.join(settings.MEDIA_ROOT, filename)
			openfile = open(filepath, "wb+")
			writer = csv.writer(openfile)
			writer.writerow(['country_code', 'buyer_number', 'buyer_name', 'group_type'])

			jobsObj.upload_file = filename
			jobsObj.save()

			country = Country.objects.get(pk=1)

			phone_code = str(country.phone_code).replace("+", "")

			for invite in inviteeArray:
				try:
					buyer_name=invite[0]
					buyer_name=buyer_name.encode('utf-8').strip()
					buyer_name=str(buyer_name).rstrip('\n')
					buyer_number=str(invite[1])[-10:]

					if buyer_number in temp_contacts:
						continue
					temp_contacts.append(buyer_number)

					writer.writerow([str(phone_code), str(buyer_number), str(buyer_name), str(group_type.name),])
				except Exception as e:
					logger.info("in ImportArrayInvitee error")
					logger.info("============")
					logger.info(str(phone_code))
					logger.info(str(buyer_number))
					logger.info(str(buyer_name))
					logger.info(str(group_type.name))
					logger.info(str(e))
					pass

			jobsObj.total_rows = len(temp_contacts)
			jobsObj.save()
			if settings.TASK_QUEUE_METHOD == 'celery':
				task_id = buyerCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
					'api.tasks.buyerCSVImportJobs',
					jobsObj.id,
					broker = priority_broker
				)
			print task_id
		elif request_type.lower() == "supplier":
			logger.info("== supplier ==")
			last_supplier_name = None
			last_supplier_company_obj = None

			jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Supplier", status="Scheduled",total_rows = len(inviteeArray))
			print jobsObj

			filename = 'jobs_upload_file/suppliers_mobile_enquiry_'+str(jobsObj.id)+'_'+str(randomString())+'.csv'
			filepath = os.path.join(settings.MEDIA_ROOT, filename)
			openfile = open(filepath, "wb+")
			writer = csv.writer(openfile)
			writer.writerow(['country_code', 'supplier_number', 'supplier_name', 'group_type'])

			jobsObj.upload_file = filename
			jobsObj.save()

			country = Country.objects.get(pk=1)

			phone_code = str(country.phone_code).replace("+", "")

			for invite in inviteeArray:
				try:
					supplier_name=invite[0]
					supplier_name=supplier_name.encode('utf-8').strip()
					supplier_name=str(supplier_name).rstrip('\n')
					supplier_number=str(invite[1])[-10:]

					if supplier_number in temp_contacts:
						continue
					temp_contacts.append(supplier_number)

					writer.writerow([str(phone_code), str(supplier_number), str(supplier_name), str(group_type.name),])
				except Exception as e:
					logger.info("in ImportArrayInvitee error")
					logger.info("============")
					logger.info(str(phone_code))
					logger.info(str(supplier_number))
					logger.info(str(supplier_name))
					logger.info(str(group_type.name))
					logger.info(str(e))
					pass

			jobsObj.total_rows = len(temp_contacts)
			jobsObj.save()
			if settings.TASK_QUEUE_METHOD == 'celery':
				task_id = supplierCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
					'api.tasks.supplierCSVImportJobs',
					jobsObj.id,
					broker = priority_broker
				)
			print task_id

		return Response({"success": "Invited Contact list successfully"})

class OnWishbook(APIView): #LoggingMixin, #removed loggingmixin to solve TypeError: compile() expected string without null bytes
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		logger.info("== onWishbook ==")
		data = {}
		try:
			data = request.data
			contacts = data['contacts']
			loginUser = request.user
			loginCompany = get_user_company(loginUser) #loginUser.companyuser.company

			registeredContact = []

			country = Country.objects.get(pk=1)

			contact_map = {}

			contactNoList = []
			for contact in contacts:
				try:
					phone = re.sub('[^0-9+]', '',contact['phone'])
					#phone = str(phone)[-10:]
					contactNoList.append(phone)
					contact_map[str(phone)] =  contact['name']


					name=contact['name']
					name=name.encode('utf-8').strip()
					name=str(name).rstrip('\n')
					phone_number=contact['phone']

					ucObj, created = UserContact.objects.get_or_create(number=phone_number, user=loginUser)
					ucObj.name = name
					ucObj.save()
				except Exception as e:
					print "in OnWishbook error =", str(e)
					pass


			company_ids = []
			found_contacts = []
			company_map = {}


			company_temp = Company.objects.filter(country=country, phone_number__in=contactNoList).values_list('id', flat=True)
			company_ids.extend(company_temp)

			phone_temp = Company.objects.filter(country=country, phone_number__in=contactNoList).values_list('phone_number', flat=True)
			found_contacts.extend(phone_temp)

			#array to list subtract minus
			contactNoList = list(set(contactNoList) - set(found_contacts))

			# ~ company_temp = UserProfile.objects.filter(country=country, phone_number__in=contactNoList).exclude(Q(user__is_staff=True)|Q(user__is_superuser=True)).values_list('user', flat=True)
			# ~ company_temp = CompanyUser.objects.filter(user__in=company_temp).values_list('company', flat=True)
			# ~ company_ids.extend(company_temp)
			# ~ phone_temp = UserProfile.objects.filter(country=country, phone_number__in=contactNoList).exclude(Q(user__is_staff=True)|Q(user__is_superuser=True)).values_list('phone_number', flat=True)
			# ~ found_contacts.extend(phone_temp)

			company_temp_userids = UserProfile.objects.filter(country=country, phone_number__in=contactNoList).exclude(Q(user__is_staff=True)|Q(user__is_superuser=True)).values_list('user', flat=True)
			company_temp_companyids = CompanyUser.objects.filter(user__in=company_temp_userids).values_list('company', flat=True)
			company_ids.extend(company_temp_companyids)
			company_temp_fianl_userids = CompanyUser.objects.filter(user__in=company_temp_userids, company__in=company_temp_companyids).values_list('user', flat=True)
			phone_temp = UserProfile.objects.filter(user__in=company_temp_fianl_userids).exclude(Q(user__is_staff=True)|Q(user__is_superuser=True)).values_list('phone_number', flat=True)
			found_contacts.extend(phone_temp)

			contactNoList = list(set(contactNoList) - set(found_contacts))

			company_temp = CompanyPhoneAlias.objects.filter(country=country, alias_number__in=contactNoList, status="Approved").values_list('company', flat=True)
			company_ids.extend(company_temp)
			phone_temp = CompanyPhoneAlias.objects.filter(country=country, alias_number__in=contactNoList, status="Approved").values_list('alias_number', flat=True)
			found_contacts.extend(phone_temp)

			contactNoList = list(set(contactNoList) - set(found_contacts))

			# ~ print "company_ids = ",company_ids
			# ~ print "found_contacts = ",found_contacts

			for i in range(len(company_ids)):
				company_map[str(company_ids[i])] =  found_contacts[i]

			# ~ print "company_map=",company_map

			if Company.objects.filter(id__in=company_ids).exists():
				companiesObj = Company.objects.filter(id__in=company_ids).select_related('address__state', 'address__city', 'chat_admin_user')

				for companyObj in companiesObj:
					record={}
					record["phone"]=company_map[str(companyObj.id)]
					record["name"]=contact_map[company_map[str(companyObj.id)]]# contact['name']

					record["company_id"]=companyObj.id
					record["company_name"]=companyObj.name
					record["company_image"]=settings.MEDIA_URL+"logo-single.png"
					if companyObj.thumbnail:
						record["company_image"]=companyObj.thumbnail.url
					else:
						if Brand.objects.filter(company=companyObj.id).exists():
							brand = Brand.objects.filter(company=companyObj.id).first()
							record["company_image"]=brand.image.thumbnail[settings.SMALL_SQR_IMAGE].url
						#~ else:
							#~ brandIds = BrandDistributor.objects.filter(company=companyObj.id).values_list('brand', flat=True).distinct()
							#~ if Brand.objects.filter(id__in=brandIds).exists():
								#~ brand = Brand.objects.filter(id__in=brandIds).first()
								#~ record["company_image"]=brand.image.thumbnail[settings.SMALL_SQR_IMAGE].url

					record["connected_as"] = ""
					record["credit_reference_id"] = None
					if Buyer.objects.filter(selling_company=loginCompany, buying_company=companyObj).exists():
						record["connected_as"]="buyer"
						crObj = CreditReference.objects.filter(selling_company=loginCompany, buying_company=companyObj).first()
						if crObj:
							record["credit_reference_id"]=crObj.id
					if Buyer.objects.filter(selling_company=companyObj, buying_company=loginCompany).exists():
						record["connected_as"]="supplier"
						crObj = CreditReference.objects.filter(selling_company=companyObj, buying_company=loginCompany).first()
						if crObj:
							record["credit_reference_id"]=crObj.id

					if companyObj.chat_admin_user is not None:
						record["chat_user"]=companyObj.chat_admin_user.username
					else:
						record["chat_user"]=None

					if companyObj.address:
						record["state_name"] = companyObj.address.state.state_name
						record["city_name"] = companyObj.address.city.city_name
					else:
						record["state_name"] = companyObj.state.state_name
						record["city_name"] = companyObj.city.city_name

					companytypesrecommend = recommended_relationship(loginCompany, companyObj)
					#~ print companytypesrecommend
					#~ print len(companytypesrecommend["buyer_types"])
					#~ print len(companytypesrecommend["supplier_types"])
					if len(companytypesrecommend["buyer_types"]) > 0:
						record["type"]="buyer"
						record["group_type"]=companytypesrecommend["buyer_types"]
						registeredContact.append(record)

					if len(companytypesrecommend["supplier_types"]) > 0:
						import copy
						record = copy.deepcopy(record)
						record["type"]="supplier"
						record["group_type"]=companytypesrecommend["supplier_types"]
						registeredContact.append(record)

					if len(companytypesrecommend["buyer_types"]) == len(companytypesrecommend["supplier_types"]) == 0:
						record["type"]=""
						record["group_type"]=[]
						registeredContact.append(record)

					#registeredContact.append(record)

			'''inviteeIds = Invitee.objects.filter(country=country, invitee_number__in=contactNoList).values('invitee_number').annotate(Max('id')).values('id__max')

			inviteeObjs = Invitee.objects.filter(id__in=inviteeIds)

			contactNoList = list(set(contactNoList) - set(found_contacts))

			for invitee in inviteeObjs:
				record={}
				record["phone"]=invitee.invitee_number
				record["name"]=contact_map[str(invitee.invitee_number)]

				record["company_name"]="Invited"
				record["company_image"]=settings.MEDIA_URL+"logo-single.png"

				record["connected_as"] = ""

				record["chat_user"]=None

				record["type"]=""
				record["group_type"]=[]

				registeredContact.append(record)'''

			#sorting json custom field name
			try:
				registeredContact = sorted(registeredContact, key=lambda k: k['name'])#, reverse=True
			except Exception as e:
				print "in OnWishbook registeredContact error =", str(e)
				pass

			return Response(registeredContact)

		except Exception as e:
			print "in OnWishbook error =", str(e)

			import traceback
			mail_status = send_mail("OnWishbook", "Error = "+str(e)+", Rraceback = "+str(traceback.format_exc())+", data = "+str(data), "tech@wishbook.io", ["tech@wishbook.io"])

			return Response([])

'''
class RecommendedRelationship (LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		logger.info("== RecommendedRelationship ==")

		data = request.data
		contacts = data['contacts']
		loginUser = request.user
		loginCompany = loginUser.companyuser.company

		registeredContact = []

		country = Country.objects.get(pk=1)

		contact_map = {}

		contactNoList = []
		for contact in contacts:
			phone = re.sub('[^0-9+]', '',contact['phone'])
			phone = str(phone)[-10:]
			contactNoList.append(phone)
			contact_map[str(phone)] =  contact['name']


		company_ids = []
		found_contacts = []
		company_map = {}


		company_temp = Company.objects.filter(country=country, phone_number__in=contactNoList).values_list('id', flat=True)
		company_ids.extend(company_temp)

		phone_temp = Company.objects.filter(country=country, phone_number__in=contactNoList).values_list('phone_number', flat=True)
		found_contacts.extend(phone_temp)

		#array to list subtract minus
		contactNoList = list(set(contactNoList) - set(found_contacts))

		company_temp = UserProfile.objects.filter(country=country, phone_number__in=contactNoList).exclude(Q(user__is_staff=True)|Q(user__is_superuser=True)).values_list('user', flat=True)
		company_temp = CompanyUser.objects.filter(user__in=company_temp).values_list('company', flat=True)
		company_ids.extend(company_temp)
		phone_temp = UserProfile.objects.filter(country=country, phone_number__in=contactNoList).exclude(Q(user__is_staff=True)|Q(user__is_superuser=True)).values_list('phone_number', flat=True)
		found_contacts.extend(phone_temp)

		contactNoList = list(set(contactNoList) - set(found_contacts))

		company_temp = CompanyPhoneAlias.objects.filter(country=country, alias_number__in=contactNoList, status="Approved").values_list('company', flat=True)
		company_ids.extend(company_temp)
		phone_temp = CompanyPhoneAlias.objects.filter(country=country, alias_number__in=contactNoList, status="Approved").values_list('alias_number', flat=True)
		found_contacts.extend(phone_temp)

		contactNoList = list(set(contactNoList) - set(found_contacts))

		for i in range(len(company_ids)):
			company_map[str(company_ids[i])] =  found_contacts[i]

		loginCompanyType = loginCompany.company_group_flag
		if loginCompanyType.retailer == True or loginCompanyType.online_retailer_reseller == True:
			request_type="supplier"
			group_type="retailer"
			companytype_companyids=CompanyType.objects.filter(Q(company__in=company_ids) & Q(Q(manufacturer=True) | Q(wholesaler_distributor=True, company__address__state=loginCompany.address.state) | Q(broker=True, company__address__state=loginCompany.address.state))).values_list('company', flat=True)

			companiesObj = Company.objects.filter(id__in=companytype_companyids)

			registeredContactdata = recommended_relationship22(loginCompany, companiesObj, company_map, request_type, group_type)
			registeredContact.extend(registeredContactdata)

		if loginCompanyType.wholesaler_distributor == True:
			request_type="buyer"
			group_type="retailer"
			companytype_companyids=CompanyType.objects.filter(Q(company__in=company_ids) & Q(Q(retailer=True) | Q(online_retailer_reseller=True)) & Q(company__address__state=loginCompany.address.state)).values_list('company', flat=True)

			companiesObj = Company.objects.filter(id__in=companytype_companyids)

			registeredContactdata = recommended_relationship22(loginCompany, companiesObj, company_map, request_type, group_type)
			registeredContact.extend(registeredContactdata)


			request_type="supplier"
			group_type="wholesaler"
			companytype_companyids=CompanyType.objects.filter(company__in=company_ids, manufacturer=True).values_list('company', flat=True)

			companiesObj = Company.objects.filter(id__in=companytype_companyids)

			registeredContactdata = recommended_relationship22(loginCompany, companiesObj, company_map, request_type, group_type)
			registeredContact.extend(registeredContactdata)

		if loginCompanyType.manufacturer == True:
			request_type="buyer"
			group_type="wholesaler"
			companytype_companyids=CompanyType.objects.filter(company__in=company_ids, wholesaler_distributor=True).values_list('company', flat=True)

			companiesObj = Company.objects.filter(id__in=companytype_companyids)

			registeredContactdata = recommended_relationship22(loginCompany, companiesObj, company_map, request_type, group_type)
			registeredContact.extend(registeredContactdata)


			request_type="buyer"
			group_type="retailer"
			companytype_companyids=CompanyType.objects.filter(Q(company__in=company_ids) & Q(Q(retailer=True) | Q(online_retailer_reseller=True))).values_list('company', flat=True)

			companiesObj = Company.objects.filter(id__in=companytype_companyids)

			registeredContactdata = recommended_relationship22(loginCompany, companiesObj, company_map, request_type, group_type)
			registeredContact.extend(registeredContactdata)


			request_type="buyer"
			group_type="broker"
			companytype_companyids=CompanyType.objects.filter(company__in=company_ids, broker=True).values_list('company', flat=True)

			companiesObj = Company.objects.filter(id__in=companytype_companyids)

			registeredContactdata = recommended_relationship22(loginCompany, companiesObj, company_map, request_type, group_type)
			registeredContact.extend(registeredContactdata)

		#sorting json custom field name
		registeredContact = sorted(registeredContact, key=lambda k: k['name'])#, reverse=True

		return Response(registeredContact)
'''

class SyncData(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data
		print data
		salesorders = data['salesorders']
		print "==============================================================="
		print salesorders
		meetings = data['meetings']
		print "==============================================================="
		print meetings

		with transaction.atomic():

			user = request.user
			company = user.companyuser.company
			companyName = company.name

			print "trans..."

			for salesOrderData in salesorders:
				print "in salesorders"

				items = salesOrderData['items']
				salesOrderObj = SalesOrder.objects.create(order_number=salesOrderData['order_number'], seller_company=Company.objects.get(pk=salesOrderData['seller_company']), company=Company.objects.get(pk=salesOrderData['company']), processing_status=salesOrderData['processing_status'], customer_status="finalized", user=user)
				print salesOrderObj
				for item in items:
					salesitem = SalesOrderItem.objects.get_or_create(product=Product.objects.get(pk=item['product']), quantity=item['quantity'], rate=item['rate'],sales_order = salesOrderObj)
					print salesitem

			for meetingData in meetings:
				print "in meetings"
				mettingSalesorders = meetingData['salesorders']
				print mettingSalesorders

				print dateutil.parser.parse(meetingData['start_datetime'])

				mettingObj = Meeting.objects.create(user=user, buying_company_ref=Company.objects.get(pk=meetingData['buying_company_ref']), start_datetime=dateutil.parser.parse(meetingData['start_datetime']), end_datetime=dateutil.parser.parse(meetingData['end_datetime']), start_lat=meetingData['start_lat'], start_long=meetingData['start_long'], end_lat=meetingData['end_lat'], end_long=meetingData['end_long'], status=meetingData['status'])
				print mettingObj
				print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

				saleOrderList = []
				for salesOrderData in mettingSalesorders:
					print "in salesorders"

					items = salesOrderData['items']
					salesOrderObj = SalesOrder.objects.create(order_number=salesOrderData['order_number'], seller_company=Company.objects.get(pk=salesOrderData['seller_company']), company=Company.objects.get(pk=salesOrderData['company']), processing_status=salesOrderData['processing_status'], customer_status="finalized", user=user)
					print salesOrderObj
					for item in items:
						salesitem = SalesOrderItem.objects.get_or_create(product=Product.objects.get(pk=item['product']), quantity=item['quantity'], rate=item['rate'],sales_order = salesOrderObj)
						print salesitem

					saleOrderList.append(salesOrderObj)

				mettingObj.salesorder.add(*saleOrderList)
				mettingObj.save()
				print mettingObj

			return Response({"success": "Data has been sync."})

class Tnc(APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		tnc = {}


		tnc['main_description'] = "At Wishbook, the privacy of data is of crucial importance. Any personal Information used by Wishbook will only be set out under Privacy Policy. Please go through this Privacy Policy to learn more about Wishbook's practices of collecting or disseminating information. This Privacy policy is applicable to all the domains and sub-domains of Wishbook (Website or Mobile App), the parent company, joint or sister venture Website or Application. By accessing or using the website /app, you agree to be confined by our terms &amp; conditions. <br/> This privacy policy describes how Wishbook assembles the personal information, marked as optional or compulsory as part of our routine operation of our services; &amp; uses, declarations, and protection such data through Website /App. This comprehensive privacy policy allows you to take well-informed actions while dealing with us. Similar privacy practices are pursued by our parent, joint, and sister ventures subject to the requirement of applicable law. <br/> By registering or signing into Wishbook Application or website, you accept to agree to our complete terms and conditions, providing us consent to our use of selective revelations of your personal information accordingly with this Privacy Policy &amp; all personal information provided by you through Wishbook are under lawful contract. This Privacy policy is incorporated into and subject matter to the conditions of User Agreement. <br/> Note: Go through this policy &amp; review it periodically, as policies can possibly be modified at any time without prior notice."


		sub_description = []
		tnc['sub_description'] = sub_description


		privacy = {}

		privacy['heading'] = "Your Privacy"

		privacy['description'] = "At Wishbook, we guarantee our loyalty to protect your privacy. We try very hard to put our best to meet your expectations and requirements so that you can make use of our product and provide word of mouth recognition about Wishbook and its product and services to your family, friends, and relatives. Please read the entire policy to know how we would treat your personal information so that you can make full use of our site/app."

		sub_description.append(privacy)


		apa = {}

		apa['heading'] = "Our Privacy Assurance"

		apa['description'] = "Wishbooks vows that we will not sell or rent or misuse your personal data to any third party for their own commercial or personal use without your clear consent. We may timely update you about our statistical information of the Website/App, such as a number of app/web visitors, number and type of products or goods purchased etc. Your trust is what matters us the most."

		sub_description.append(apa)


		wc = {}

		wc['heading'] = "What informtion does Wishbook collects"

		wc['description'] = "We store your personal information when you use our web app. We collect the information to record, support, track your activities, to provide you with better experience, to notify you with the updated facts and figures, new happenings and other similar facilities offered by Wishbook, to aware you about the latest content available, special offers, to support you with customer service/helpline or technical support issues, to follow up with you for your response or usage on application/site, to firm your relationship with Wishbook, or put a stop to fraud or illegal usage. For the above-mentioned purpose, we only take your selective information that too to know you and our interests. <br/> You can visit our site/app at any point of time without giving your personal information. You are not known to us and even your activities cannot be traced by us until you login or create an account on the Site/App. Once you register with us, you are no longer stranger. You have to provide your name or personal number, email and password to make full use of our site/app. Further, the fields are marked as required or not. You always have the option to block or reject processes you no longer wish to use. We may automatically track certain activities depending upon your usage/behaviour if you provide us with your registered User name/number. We use these details to understand our clients, track your movements, gather major information and understand your purpose, and to provide better solutions to our client's problem. This information is assembled and examined overall. This information can contain the Source URL (present on Wishbook Site/App or not) you came from, the next following URL (present on Wishbook Site/App or not), your browser information and your IP Address. <br/> We track your buying and selling behaviour if you choose to buy or sell via Wishbook. <br/> We have full access to any such information, if we collect personal correspondence like emails or letters or any postings on the Website /App related to your activities by third party or by you directly. <br/> If you sign up for our website/app through a link on another website/app or you use any website/app that provides services to Wishbook or any website/app that facilitates your activity on Site/App, that website/App will direct all your information or transactions to us."

		sub_description.append(wc)


		op = {}

		op['heading'] = "Our purpose"

		op['description'] = "In order to provide you with the solution of the problems or issues you encounter, we use your personal information. We do not trade or purchase or sell any information personal of our Users. We may provide your information to affiliates such as customer care or data analysis under contract to support you in case of operation of website/App and serve you better. We may use your personal information to market to you; you are free to opt-out in such cases. <br/> Our purpose of collecting your information: settle issues/conflict; troubleshoot problems; help boost safe trade; evaluate customer interest in the services we gave, notify you regarding online and offline offers, products/ services, and updates; customize your experience; find and shield us against error, deceit and other illegal activity; impose our User Agreement, and generally to enhance the user experience and make it outstand from other e-commerce website/App; else as explained at the time of entering information. We gather and examine the demographic data, profile and usage data of our user's activities done on Website/App to improve our product or services continuously. To provide you with a easy, smooth, efficient, error free, secure and customized experience while using the Site/App, we use your personal information to improve our Site/App content &amp; product services, stop or check for fraud or abuses of our website/app and prepare it to encounter your needs. <br/> To serve you in accordance to your interest, we may use your personal information as contents to be displayed on app/site. By accepting our User Agreement, you agree to be receiving the aforesaid information. You may update your profile at any time."

		sub_description.append(op)


		odpi = {}

		odpi['heading'] = "Our Disclosure to your Personal Information"

		odpi['description'] = "Your personal information is a major component of our business and we do not deal in selling it with others. We share only to some important affiliates who are bound by this Privacy Policy or follow these practices as strongly as described. There can be also a case to disclose your information that is when your actions try to violate our terms &amp; conditions."

		sub_description.append(odpi)


		return Response(tnc)

class SyncActivityLog(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data
		logger.info("IN SyncActivityLog data=")
		logger.info(str(data))
		push_user = data.get('push_user', None)#data['push_user']
		push_user_product = data.get('push_user_product', None)#data['push_user_product']

		logger.info("push_user")
		logger.info(str(push_user))
		logger.info("push_user_product")
		logger.info(str(push_user_product))

		user = request.user
		company = get_user_company(user) #user.companyuser.company

		if company is None:
			return Response({"success": "Data has been sync."})

		if push_user is not None and len(push_user) > 0:
			#Push_User.objects.filter(id__in=push_user, buying_company=company).update(is_viewed='yes')
			catalogs = Push_User.objects.filter(id__in=push_user, buying_company=company).values_list('catalog', flat=True)
			catalogs = Catalog.objects.filter(id__in=catalogs)
			print catalogs
			for catalog in catalogs:
				# ~ ccvObj, created = CompanyCatalogView.objects.get_or_create(company=company, catalog=catalog, catalog_type=catalog.view_permission)
				# ~ if not created:
					# ~ ccvObj.created_at=datetime.now()
					# ~ ccvObj.clicks += 1
					# ~ ccvObj.save()
				if CompanyCatalogView.objects.filter(company=company, catalog=catalog, catalog_type=catalog.view_permission).count() > 0:
					ccvObj = CompanyCatalogView.objects.filter(company=company, catalog=catalog, catalog_type=catalog.view_permission).first()
					ccvObj.created_at=datetime.now()
					ccvObj.clicks += 1
					ccvObj.save()
				else:
					ccvObj, created = CompanyCatalogView.objects.get_or_create(company=company, catalog=catalog, catalog_type=catalog.view_permission)

		if push_user_product is not None and len(push_user_product) > 0:
			#CompanyProductFlat.objects.filter(id__in=push_user_product, buying_company=company).update(is_viewed='yes')
			products = CompanyProductFlat.objects.filter(id__in=push_user_product, buying_company=company).values_list('product', flat=True)
			products = Product.objects.filter(id__in=products)
			print products
			for product in products:
				CompanyProductView.objects.get_or_create(company=company, product=product)

		return Response({"success": "Data has been sync."})

class PasswordReset(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		data = request.data

		country = data.get('country')
		phone_number = data.get('phone_number')

		otp = data.get('otp', None)
		password = data.get('password', None)

		if country == 'null':
			country = 1

		try:
			country = Country.objects.get(pk=country)
		except Exception as e:
			country = Country.objects.get(pk=1)

		if not UserProfile.objects.filter(phone_number=phone_number, country=country).exists():
			raise serializers.ValidationError({'phone_number':'Phone number is not exist. Please enter valid phone number.'})

		if otp is not None:

			if RegistrationOTP.objects.filter(phone_number=phone_number, country=country).exists():
					registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-id').first()
					if str(registrationOtp.otp) == str(otp):
						registrationOtp.is_verified = "yes"
						registrationOtp.save()

						user=UserProfile.objects.filter(phone_number=phone_number, country=country).first().user
						user.set_password(password)
						user.save()

						UserProfile.objects.filter(phone_number=phone_number, country=country).update(phone_number_verified='yes')


						full_mobile_number = str(country.phone_code)+str(phone_number)
						verifyMSG91OTP(full_mobile_number, otp)

						return Response({"success": "Password has been changed successfully"})

			raise serializers.ValidationError({"otp":"Please enter valid OTP"})

		'''otpno = random.randrange(100000, 999999, 1)
		sendOTP(str(country.phone_code)+str(phone_number), str(otpno))

		registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otpno, country=country)'''
		checkAndSendOTP(phone_number, country, True)

		return Response({"success": "OTP has been sent successfully"})

class GenerateOtp(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		data = request.data

		country = data.get('country')
		phone_number = data.get('phone_number')

		country = Country.objects.get(pk=country)

		if not UserProfile.objects.filter(phone_number=phone_number, country=country).exists():
			raise serializers.ValidationError({'phone_number':'Phone number is not exist. Please enter valid phone number.'})

		'''otpno = random.randrange(100000, 999999, 1)
		sendOTP(str(country.phone_code)+str(phone_number), str(otpno))

		registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otpno, country=country)'''
		checkAndSendOTP(phone_number, country, True)

		return Response({"success": "OTP has been sent successfully"})

from api.tasks import *
class DailyShareSMS(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			dailyShareSMS.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.dailyShareSMS'

			)

		return Response({"success": "Daily Share SMS cron started successfully"})

class TrustedSortOrder(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			trustedSortOrder.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.trustedSortOrder'

			)

		return Response({"success": "Trusted sort order cron started successfully"})

class DisableCatalogCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			disableCatalog.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.disableCatalog'

			)

		return Response({"success": "Disable catalog cron started successfully"})

class ProductEAVCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			ProductEAV.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.ProductEAV'

			)
		# ProductEAV()

		return Response({"success": "Product eav cron ran successfully"})

class CatalogEAVCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			CatalogEAV.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.CatalogEAV'

			)

		return Response({"success": "Catalog eav cron ran successfully"})

class BrandTotalCatalogCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			BrandTotalCatalog.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.BrandTotalCatalog'

			)

		return Response({"success": "Brand Total Catalog eav cron ran successfully"})

class CompanySellsToStateCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			CompanySellsToStateTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.CompanySellsToStateTask'

			)

		return Response({"success": "Company Sells To State eav cron ran successfully"})

class GEOCodeLocationCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			GEOCodeLocationTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.GEOCodeLocationTask'

			)

		return Response({"success": "GEO code location cron ran successfully"})

class InActiveUserNotificationCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			InActiveUserNotificationTask.apply_async(("before7to30days"), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.InActiveUserNotificationTask',
				'before7to30days'
			)

		return Response({"success": "Notification has been sent successfully"})

class InActiveUserNotificationBefore30DaysCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			InActiveUserNotificationTask.apply_async(("before30days"), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.InActiveUserNotificationTask',
				'before30days'
			)

		return Response({"success": "Notification has been sent successfully"})

class UserContactRegistrationCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			UserContactRegistrationTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.UserContactRegistrationTask'
			)
		return Response({"success": "User contact registration cron started successfully"})


class MobileStateMappingCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			MobileStateMappingTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.MobileStateMappingTask'
			)
		return Response({"success": "Mobile State Mapping cron started successfully"})

class SellerStatisticCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			SellerStatisticTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.SellerStatisticTask'
			)
		return Response({"success": "Seller Statistic cron started successfully"})

class UserCampaignClickCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			UserCampaignClickTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.UserCampaignClickTask'
			)
		return Response({"success": "User Campaign Click cron started successfully"})

class MeetingCSVeMailCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			MeetingCSVeMailTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.MeetingCSVeMailTask'
			)
		return Response({"success": "Meetings cron started successfully"})

class SugarUpdateCron(LoggingMixin, APIView):
	"""
		it will update company,user and enquiry and make relationship
		between them.
	"""
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		logger.info("SugarUpdateCron url hit")
		if settings.DEBUG==False:
			if settings.TASK_QUEUE_METHOD == 'celery':
				SugarUpdateTask.apply_async((), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
				'api.tasks.SugarUpdateTask'
				)
		return Response({"success": "Sugar Update cron started successfully"})


class SugarCallUpdateCron(LoggingMixin, APIView):
	"""
		it will create calls in crm when user first login is null or
		date joined is for today.
	"""
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		logger.info("SugarCallUpdateCron url hit")
		if settings.DEBUG==False:
			if settings.TASK_QUEUE_METHOD == 'celery':
				SugarCallUpdateTask.apply_async((), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
				'api.tasks.SugarCallUpdateTask'
				)
		return Response({"success": "Sugar Call Update cron started successfully"})

class DailyOrderCSVeMailCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			DailyOrderCSVeMailTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.DailyOrderCSVeMailTask'
			)
		#DailyOrderCSVeMailTask()

		return Response({"success": "Daily Order CSV cron started successfully"})

class UpdateUninstallUsersCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			UpdateUninstallUsersTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.UpdateUninstallUsersTask'
			)
		#UpdateUninstallUsersTask()

		return Response({"success": "Update Uninstall Users cron started successfully"})



class Notify(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data

		company = data.get('company')
		message = data.get('message')

		ids = CompanyUser.objects.filter(company=company).values_list('user', flat=True).distinct()
		ids = list(ids)

		#print ids

		rno = random.randrange(100000, 999999, 1)
		image = settings.MEDIA_URL+"logo-single.png"

		if settings.TASK_QUEUE_METHOD == 'celery':
			notificationSend.apply_async((ids, message, {"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image}), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.notificationSend',
				ids, message, {"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image}
			)

		return Response({"success": "Message notified successfully"})

class InventoryUpdateFromServer(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data

		company = data.get('company')

		inventoryUpdateFromServer(company)

		return Response({"success": "Inventory updated successfully"})

class UpdateOrderStatus(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data

		company = data.get('company')

		updateOrderStatus(company)

		return Response({"success": "Status updated successfully"})

class SendSMSDemo(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data

		sms_method = data.get('sms_method', None)
		mobile_number = data.get('mobile_number')

		from api.tasks import *
		message = smsTemplates("share")% ("test", "message (brandName)", "https://app.wishbooks.io/?type=page&id=1")
		#message = smsTemplates("share")% ("test", "message (brandName)", "http://app.wishbooks.io/m?type=catalog&id=1&m=9586773322&o=236541")
		#message = smsTemplates("user_detail")% ("test", "http://app.wishbooks.io/m?type=catalog&id=1&m=9586773322&o=236541", "9586773322", "123456")
		#message = smsTemplates("send_user_detail")% ("123546", "ok")

		#smsSend(["+919586773322"], message, False, True)

		sms = None
		if sms_method:
			if sms_method.lower() == "sendsmart":
				sms = smsSendSendSmart([mobile_number], message, True)
			elif sms_method.lower() == "icubes":
				sms = smsSendICubes([mobile_number], message, True)
			elif sms_method.lower() == "textnation":
				sms = smsSendTextNation([mobile_number], message, True, True)
			elif sms_method.lower() == "textnationpromotional":
				sms = smsSendTextNationPromotional([mobile_number], message, True)

		print "sms send status"
		print sms

		return Response({"success": str(sms)})

	'''def get(self, request, format=None):
		from eav.models import Attribute, Value as EavValue
		from django.contrib.contenttypes.models import ContentType

		ct = ContentType.objects.get(id=26)

		product = Product.objects.get(pk=1804)
		product.eav.testmulti = EnumValue.objects.get(value="Zardosi")
		product.save()
		product.eav.testmulti = EnumValue.objects.get(value="Crochet")
		product.save()



		return Response({"success":""})'''

class SendNotificationDemo(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data

		users = data.get('users')
		message = data.get('message')
		jsonarr = data.get('jsonarr')

		#image = settings.MEDIA_URL+"logo-single.png"
		#jsonarr["image"] = image

		from api.tasks import *

		notf = notificationSend(users, message, jsonarr)

		return Response({"success": str(notf)})


from copy import copy
class AssignCatalogToCompany(LoggingMixin, APIView):
	permission_classes = (permissions.IsAdminUser,)

	def post(self, request, format=None):
		data = request.data

		user = request.user

		#print data['brand']
		catalog = data['catalog']
		company = data['company']

		catalogObj = Catalog.objects.get(pk=catalog)
		companyObj = Company.objects.get(pk=company)
		productObj = Product.objects.filter(catalog=catalog)

		if Catalog.objects.filter(title=catalogObj.title, company=companyObj).exists():
			raise serializers.ValidationError({"catalog":"catalog already exists."})

		if catalogObj is not None and companyObj is not None:
			newCatalogObj = copy(catalogObj)
			newCatalogObj.pk = None
			newCatalogObj.company = companyObj
			newCatalogObj.mirror = catalogObj
			newCatalogObj.save()

			#newCatalogObj.mirror = catalogObj
			#newCatalogObj.save()

			for prObj in productObj:
				newPrObj = copy(prObj)
				newPrObj.pk = None
				newPrObj.catalog = newCatalogObj
				newPrObj.mirror = prObj
				newPrObj.save()

				#newPrObj.mirror = prObj
				#newPrObj.save()

		return Response({"success": "Catalog has been assigned"})

class GetEnumGroup(APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		egtype = self.request.query_params.get('type', None)
		#print egtype
		queryset = []
		if egtype is not None and egtype == "fabric":
			queryset = EnumGroup.objects.filter(name="fabric").first().enums.all().values('id', 'value')
		elif egtype is not None and egtype == "work":
			queryset = EnumGroup.objects.filter(name="work").first().enums.all().values('id', 'value')
		elif egtype is not None and egtype == "style":
			queryset = EnumGroup.objects.filter(name="style").first().enums.all().values('id', 'value')
		#print queryset
		return Response(list(queryset))

class ShippingCharge(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		jsonarr = {}

		order = self.request.query_params.get('order', None)
		cart = self.request.query_params.get('cart', None)
		#weight = self.request.query_params.get('weight', None)
		if cart:
			logger.info("ShippingCharge cart id = %s" % (cart))
			cartObj = Cart.objects.get(pk=cart)

			pids = CartItem.objects.filter(cart=cartObj).values_list('product', flat=True)
			logger.info("Cart ShippingCharge product ids = %s" % (pids))
			#seller_address = cartObj.seller_company.address
			seller_address = None
			jsonarr = shippingChargeOnAddress(pids, seller_address, cartObj.ship_to, cartObj.total_products())
			return Response(jsonarr)

		logger.info("ShippingCharge order id = %s" % (order))
		soObj = SalesOrder.objects.get(pk=order)

		pids = SalesOrderItem.objects.filter(sales_order=soObj).values_list('product', flat=True)
		logger.info("Order ShippingCharge product ids = %s" % (pids))
		jsonarr = shippingChargeOnAddress(pids, soObj.seller_company.address, soObj.ship_to, soObj.total_products())
		return Response(jsonarr)

		# weight = Product.objects.filter(id__in=pids).aggregate(Sum('weight')).get('weight__sum', 0)
		# if weight is None:
		# 	weight = 0
		#
		# logger.info("ShippingCharge weight = %s" % (weight))
		# logger.info("ShippingCharge order obj = %s" % (order))
		# logger.info("ShippingCharge shipto = %s" % (soObj.ship_to))
		#
		# shipcharge = 0
		# if soObj.seller_company.address and soObj.ship_to:
		# 	logger.info("ShippingCharge shipto pincode = %s" % (soObj.ship_to.pincode))
		# 	pincode = PincodeZone.objects.filter(pincode=soObj.ship_to.pincode)
		#
		# 	logger.info("ShippingCharge pincode = %s" % (pincode))
		# 	if len(pincode) > 0 and pincode[0].is_servicable == True:
		#
		# 		logger.info("ShippingCharge pincode[0] = %s" % (pincode[0]))
		# 		shipcharge = shippingCharges(soObj.seller_company.address.pincode, soObj.ship_to.pincode, weight)
		# 	else:
		# 		raise serializers.ValidationError({"pincode_not_servicable":"Sorry, our shipping partners do not deliver at the selected pincode. Please add another address or opt for Other Transportation Medium"})
		#
		# total_products = soObj.total_products()
		# if total_products == 1:
		# 	jsonarr['shipping_charge'] = max(shipcharge, 79)
		# else:
		# 	jsonarr['shipping_charge'] = max(shipcharge, 179)
		#
		# if total_products < 6:
		# 	jsonarr['only_wishbook_shipping'] = True
		#
		# return Response(jsonarr)

#from django.http import HttpResponseRedirect
#from django.shortcuts import redirect
'''class Mobikwik(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):'''
@api_view(['POST','GET'])
@permission_classes((permissions.AllowAny,))
def Mobikwik(request):
	#return HttpResponseRedirect('http://b2b.trivenilabs.com/api/v1/mobikwik/success')
	#return redirect('http://b2b.trivenilabs.com/api/v1/mobikwik/success')
	logger.info("Mobikwik")
	user = request.user

	#host = request.META.get('HTTP_ORIGIN')#request.META['HTTP_ORIGIN']
	#print host

	#urls = resolve('/api/v1/mobikwik/'+status)
	#print urls

	if request.method.lower() == "get":
		data = request.GET

	if request.method.lower() == "post":
		data = request.data
	logger.info(str(data))

	#if request.method.lower() == "get":
	#	return Response({})

	statuscode = data.get('statuscode', None)
	logger.info("statuscode = ")
	logger.info(str(statuscode))
	if statuscode is not None and int(statuscode) == 0:
		logger.info("if int(statuscode) == 0")
		status = 'success'
		#return HttpResponseRedirect('http://b2b.trivenilabs.com/api/v1/mobikwik/success')
	elif statuscode is not None:
		logger.info("else")
		status = 'failure'
		#return HttpResponseRedirect('http://b2b.trivenilabs.com/api/v1/mobikwik/failure')
		#logger.info(str(response))
	else:
		return Response({})

	if data.get('orderid', None) is not None:
		generateOrderToInvoice(data.get('orderid', None), data.get('amount', None), "Mobikwik", data, user)

	full_url = str(settings.GLOBAL_SITE_URL)+'api/v1/mobikwik/'+status
	print full_url

	html = '<html>'
	html += '<head>'
	html += '<title>Wishbook Mobikwik Payment</title>'
	html += '<meta http-equiv="refresh" content="2; URL='+full_url+'">'
	html += '<meta name="keywords" content="automatic redirection">'
	html += '</head>'
	html += '<body>'
	html += 'If your browser doesn\'t automatically go there within a few seconds,'
	html += 'you may want to go back to '
	html += '<a href="'+full_url+'">Wishbook App</a> manually.'
	html += '</body>'
	html += '</html>'
	print html
	return HttpResponse(html)


	#return Response(data)
'''
class sendSmsError(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		data = request.data

		smserrorObjs = SmsError.objects.filter(is_sent=False).order_by('created_at')

		for smserrorObj in smserrorObjs:
			print smserrorObj
			smsSend([smserrorObj.mobile_no], smserrorObj.sms_text, True)
			smserrorObj.is_sent = True
			smserrorObj.save()

		return Response({"success": "Send error sms"})
'''
class ResetToGuestUser(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		from django.contrib.auth import login
		user = request.user

		user.userprofile.user_approval_status = "Approved"
		user.userprofile.save()

		CompanyUser.objects.filter(user=user).delete()

		return Response({"success":"Your profile has been reset successfully"})


class UserAuthentication(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def post(self, request, format=None):
		from django.contrib.auth import login

		data = request.data
		country = data.get('country', None)
		phone_number = data.get('phone_number', None)

		otp = data.get('otp', None)
		password = data.get('password', None)

		registration_id = data.get('registration_id', None)

		is_guest_user_registration = data.get('is_guest_user_registration', False)

		company_id = data.get('company_id', None)
		company_name = data.get('company_name', None)

		phone_number_len = len(str(phone_number))
		if phone_number_len != 10:
			raise serializers.ValidationError({"phone_number":"Enter valid mobile number"})

		if int(phone_number[0]) in [0,1,2,3,4,5]:
			raise serializers.ValidationError({"phone_number":"Mobile number is not valid : "+str(phone_number)})

		country = Country.objects.filter(id=country).first()
		if country is None:
			raise serializers.ValidationError({"country":"Enter valid country"})



		if country and phone_number and otp:
			userObj = User.objects.filter(userprofile__country=country, userprofile__phone_number=phone_number).first()
			print userObj
			if userObj:
				print userObj.username
				if not userObj.is_active:
					#inactive user
					raise serializers.ValidationError({"failed":"User account is disabled."})
				else:
					#check otp
					registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-id').first()
					print str(registrationOtp.otp)
					if str(registrationOtp.otp) == str(otp):
						registrationOtp.is_verified = "yes"
						registrationOtp.save()

						userObj.userprofile.phone_number_verified = "yes"
						userObj.userprofile.save()
						if CompanyUser.objects.filter(user=userObj).exists():
							cu = CompanyUser.objects.filter(user=userObj).first()
							Company.objects.filter(id=cu.company.id).update(phone_number_verified = "yes")

						if registration_id is not None and registration_id != "":
							add_registration_id(request, userObj, registration_id)

						login_tracker(request, userObj)
						#valid otp and create login and token
						#delete = Token.objects.filter(user=userObj).delete()

						token, created = Token.objects.get_or_create(user=userObj)
						print token.key

						userObj.backend = 'django.contrib.auth.backends.ModelBackend'
						login(request, userObj)

						return Response({"key":str(token.key)})

					else:
						raise serializers.ValidationError({"otp":"Please enter valid OTP"})
			else:
				raise serializers.ValidationError({"failed":"Wrong phone number or OTP"})
		elif country and phone_number and password:
			userObj = User.objects.filter(userprofile__country=country, userprofile__phone_number=phone_number).first()
			print userObj
			if userObj:
				print userObj.username
				if not userObj.is_active:
					#inactive user
					raise serializers.ValidationError({"failed":"User account is disabled."})
				else:
					#check password
					from django.contrib.auth import authenticate

					user = authenticate(username=userObj.username, password=password)
					if user:
						registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-id').first()
						registrationOtp.is_verified = "yes"
						registrationOtp.save()

						if registration_id is not None and registration_id != "":
							add_registration_id(request, userObj, registration_id)

						login_tracker(request, userObj)
						#valid password and create login and token
						#delete = Token.objects.filter(user=userObj).delete()

						token, created = Token.objects.get_or_create(user=userObj)
						print token.key

						userObj.backend = 'django.contrib.auth.backends.ModelBackend'
						login(request, userObj)

						return Response({"key":str(token.key)})
					else:
						raise serializers.ValidationError({"password":"Please enter valid Password"})
			else:
				raise serializers.ValidationError({"failed":"Wrong phone number or Password"})
		elif country and phone_number:
			userObj = User.objects.filter(userprofile__country=country, userprofile__phone_number=phone_number).first()

			if userObj is not None and CompanyUser.objects.filter(user=userObj).exists() and (company_name is not None or company_id is not None):
				logger.info("UserAuthentication company already registered phone_number = %s" % (phone_number))

				invite_as = data.get('invite_as', None) # buyer, supplier
				invite_group_type = data.get('invite_group_type', None)
				connect_supplier = data.get('connect_supplier', None) #for broker only
				meeting = data.get('meeting', None)

				company = userObj.companyuser.company

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

				# ~ template = smsTemplates("user_detail_2")% (loginCompany.name)
				# ~ usernumber = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
				# ~ smsSend([usernumber], template, True, True)

				#raise serializers.ValidationError({"phone_number":"Company with this phone number already exists"})
				jsondata = {"success":"User is registration and message has been sent successfully."}
				return Response(jsondata)

			if userObj is not None and not CompanyUser.objects.filter(user=userObj).exists() and (company_name is not None or company_id is not None):
				is_guest_user_registration = True
				logger.info("UserAuthentication login behalf user registration is_guest_user_registration = %s" % (is_guest_user_registration))
				data['is_guest_user_registration'] =  True

			if userObj and is_guest_user_registration is False:
				#user already registered
				checkAndSendOTP(userObj.userprofile.phone_number, userObj.userprofile.country, True)
				jsondata = {}
				jsondata["otp"] = "OTP has been sent successfully."
				jsondata["is_password_set"] = userObj.userprofile.is_password_set
				return Response(jsondata)
			else:
				#create user
				jsondata = common_user_registration(data, request)
				return Response(jsondata)
		else:
			raise serializers.ValidationError({"failed":"Must include 'phone number' and 'OTP'."})


class ApplozicGroupCreate(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request, format=None):
		buyersegments = BuyerSegmentation.objects.filter(applozic_id__isnull=True).order_by('id')
		#buyersegments = BuyerSegmentation.objects.filter(applozic_id__isnull=True, id=6986).order_by('id')
		logger.info("Total buyersegments = %s" % (buyersegments.count()))

		for buyersegment in buyersegments:
			logger.info("buyersegment id = %s" % (buyersegment.id))
			#user = CompanyUser.objects.filter(company=buyersegment.company).first().user
			user = buyersegment.company.chat_admin_user

			group_type = buyersegment.group_type.values_list('id', flat=True)
			if buyersegment.city.count() == 0:
				city = City.objects.all().values_list('id', flat=True)
			else:
				city = buyersegment.city.values_list('id', flat=True)
			if buyersegment.category.count() == 0:
				category = Category.objects.all().values_list('id', flat=True)
			else:
				category = buyersegment.category.values_list('id', flat=True)

			#usrnames = Buyer.objects.filter(selling_company=buyersegment.company, status="approved", group_type__in=group_type, buying_company__city__in=city, buying_company__category__in=category).values_list('buying_company__chat_admin_user__username', flat=True)
			usrnames = Buyer.objects.filter(Q(selling_company=buyersegment.company, status="approved", group_type__in=group_type, buying_company__category__in=category) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).values_list('buying_company__chat_admin_user__username', flat=True)
			usrnames = list(usrnames)

			r = chat_create_group({"ofUserId":user.username, "groupName":user.username+" "+buyersegment.segmentation_name, "groupMemberList":usrnames, "type":"5"}, {'task':'set_segmentation_applozic_id', 'company':buyersegment.company.id, 'segmentation':buyersegment.id})
			#r = r.json()
			#print r

		return Response({"success": "Applozic groups has been created"})

class Deeplink(LoggingMixin, APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self, request, format=None):
		from urlshortner.models import Link

		short_url = self.request.query_params.get('short_url', None)
		short_url = short_url.rstrip(",./")

		full_url = Link.expand(short_url)

		return Response({"url": full_url})


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def SetUserCampaignClick(request):
		user = request.user

		campaign = request.query_params.get('campaign', None)
		if campaign:
			UserCampaignClick.objects.create(user=user, campaign=campaign)

		#return Response({"success":"Thank you for showing your interest"})
		html = """<html>
			<head>
			<script>
			function loaded()
			{

				window.setTimeout(CloseMe, 1000);
			}
			function CloseMe()
			{
				window.close();
			}
			</script>
			</head>
			<body onLoad="loaded()">
			<h3>Thank you for showing your interest.</h3>
			</body></html>"""
		return HttpResponse(html)

class CompanyViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Company.objects.all()
	serializer_class = CompanySerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnlyObj, )

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', )
	search_fields = ('id', )

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetCompanySerializer

		return serializer_class

	# ~ def retrieve(self, request, pk=None):
		# ~ company = self.get_object()

		# ~ serializer = self.get_serializer(company)
		# ~ return Response(serializer.data)

	def get_queryset(self):
		queryset = Company.objects.all().prefetch_related('branches','buying_order__items','buying_order__user','buying_order__company','buying_order__seller_company', 'selling_order__items','selling_order__user','selling_order__company','selling_order__seller_company', 'meeting_buying_company__user','meeting_buying_company__buying_company_ref','meeting_buying_company__salesorder', 'category').order_by('-id')

		user = self.request.user

		'''try:
			if not user.is_authenticated():# or (user.companyuser.company is None)
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()'''



		#not being used now
		'''buyerList = self.request.query_params.get('buyerlist', None)
		if buyerList is not None and buyerList.lower()=="true":

			company = user.companyuser.company

			buyingCompany = Buyer.objects.filter(selling_company=company).values_list('buying_company', flat=True).exclude(buying_company__isnull=True).distinct()
			sellingCompany = Buyer.objects.filter(buying_company=company).values_list('selling_company', flat=True).exclude(selling_company__isnull=True).distinct()
			exceptCompany = list(set(buyingCompany)|set(sellingCompany))

			queryset = queryset.filter(company_type='nonmanufacturer').exclude(id__in=exceptCompany)'''

		company_type = self.request.query_params.get('company_type', None)
		if company_type is not None:
			queryset = queryset.filter(company_type=company_type)

		name = self.request.query_params.get('name', None)
		if name is not None:
			queryset = queryset.filter(name__icontains=name)

		state = self.request.query_params.get('state', None)
		if state is not None:
			try:
				queryset = queryset.filter(address__state=state)
			except Exception as e:
				pass

		city = self.request.query_params.get('city', None)
		if city is not None:
			try:
				queryset = queryset.filter(address__city=city)
			except Exception as e:
				pass

		relation_type = self.request.query_params.get('relation_type', None)
		if relation_type is not None and relation_type.lower() == "buyer_suppliers":
			company = get_user_company(user)

			if company is None:
				raise serializers.ValidationError({"error":"Please register your company"})

			sellers = Buyer.objects.filter(status="approved", buying_company=company).exclude(selling_company__isnull=True).values_list('selling_company', flat=True)
			buyers = Buyer.objects.filter(status="approved", selling_company=company).exclude(buying_company__isnull=True).values_list('buying_company', flat=True)
			queryset = queryset.filter(Q(id__in=sellers) |Q(id__in=buyers))

		return queryset

	'''def partial_update(self, request, pk=None, companies_pk=None):
		user = self.request.user
		instance = self.get_object()
		#data=request.data

		old_phone_number = instance.phone_number
		new_phone_number = request.data.get('phone_number', None)
		new_country = request.data.get('country', None)
		otp = request.data.get('otp', None)

		if new_phone_number is not None and old_phone_number != new_phone_number:
			if UserProfile.objects.filter(phone_number=new_phone_number, country=new_country, phone_number_verified='yes').exists() or Company.objects.filter(phone_number=new_phone_number, country=new_country, phone_number_verified='yes').exists() or CompanyPhoneAlias.objects.filter(alias_number=new_phone_number, country=new_country, status="Approved").exists():
				raise serializers.ValidationError({"phone_number":"Phone number is already exist. Please choose another Phone number"})

		serializer = self.get_serializer(instance, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			print "is valid"
			if new_phone_number is not None and old_phone_number != new_phone_number:
				instance.phone_number_verified = 'no'
				instance.save()

				otp = random.randrange(100000, 999999, 1)
				sendOTP(str(instance.country.phone_code)+str(instance.phone_number), str(otp))
				registrationOtp = RegistrationOTP.objects.create(phone_number=instance.phone_number, otp=otp, country=instance.country)

				print "not same phone number"

			if otp is not None:
				if RegistrationOTP.objects.filter(phone_number=instance.phone_number, country=instance.country).exists():
					registrationOtp = RegistrationOTP.objects.filter(phone_number=instance.phone_number, country=instance.country).order_by('-created_date').first()
					print str(registrationOtp.otp)
					print otp
					if str(registrationOtp.otp) == otp:
						registrationOtp.is_verified = "yes"
						registrationOtp.save()

						instance.phone_number_verified = 'yes'
						instance.save()

						makeBuyerSupplierFromInvitee(registrationOtp.phone_number, registrationOtp.country, instance)

						return Response({"success": "OTP is verified"})

				raise serializers.ValidationError({"otp":"Please enter valid OTP"})

			return Response(serializer.data)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

	@detail_route(methods=['PATCH'])
	def phone_number(self, request, pk=None):#, companies_pk=None
		user = request.user
		company = get_user_company(user) #user.companyuser.company

		if company is None:
			raise serializers.ValidationError({"failed":"Please register your company"})
		if int(company.id) != int(pk):
			raise serializers.ValidationError({"failed":"You are not allow to access"})

		instance = self.get_object()

		data = self.request.data

		old_phone_number = instance.phone_number
		new_phone_number = data.get('phone_number', None)
		new_country = data.get('country', None)
		otp = data.get('otp', None)

		if new_phone_number is not None and old_phone_number != new_phone_number:
			#if UserProfile.objects.filter(phone_number=new_phone_number, country=new_country, phone_number_verified='yes').exists() or Company.objects.filter(phone_number=new_phone_number, country=new_country, phone_number_verified='yes').exists() or CompanyPhoneAlias.objects.filter(alias_number=new_phone_number, country=new_country, status="Approved").exists():
			if not is_phone_number_available(new_country, new_phone_number, True):
				raise serializers.ValidationError({"phone_number":"Phone number already exists. Please choose another phone number"})

		#if otp is not None:
		if otp is not None and new_phone_number is not None and new_country is not None:
			#if RegistrationOTP.objects.filter(phone_number=instance.phone_number, country=instance.country).exists():
			new_country = Country.objects.get(pk=new_country)
			if RegistrationOTP.objects.filter(phone_number=new_phone_number, country=new_country).exists():
				#registrationOtp = RegistrationOTP.objects.filter(phone_number=instance.phone_number, country=instance.country).order_by('-created_date').first()
				registrationOtp = RegistrationOTP.objects.filter(phone_number=new_phone_number, country=new_country).order_by('-id').first()
				print str(registrationOtp.otp)
				print otp
				if str(registrationOtp.otp) == otp:
					registrationOtp.is_verified = "yes"
					registrationOtp.save()

					instance.phone_number_verified = 'yes'
					instance.phone_number = new_phone_number
					instance.country = new_country
					instance.save()

					makeBuyerSupplierFromInvitee(registrationOtp.phone_number, registrationOtp.country, instance)

					full_mobile_number = str(new_country.phone_code)+str(new_phone_number)
					verifyMSG91OTP(full_mobile_number, otp)

					return Response({"success": "OTP is verified"})

			raise serializers.ValidationError({"otp":"Please enter valid OTP"})

		if new_phone_number is not None and old_phone_number != new_phone_number:
			checkAndSendOTP(new_phone_number, Country.objects.get(pk=new_country))
			print "not same phone number"
			return Response({"success": "OTP has been sent successfully"})

		raise serializers.ValidationError({"Faild":"Something is wrong. Try again later."})
		'''serializer = self.get_serializer(instance, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			print "is valid"
			if new_phone_number is not None and old_phone_number != new_phone_number:
				instance.phone_number_verified = 'no'
				instance.save()

				checkAndSendOTP(instance.phone_number, instance.country)

				print "not same phone number"

			return Response(serializer.data)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''


	@detail_route(methods=['GET'])
	def dashboard(self, request, pk=None):#, companies_pk=None
		user = request.user
		company = get_user_company(user) #user.companyuser.company

		#if int(company.id) != int(pk):
		#	raise serializers.ValidationError({"failed":"You are not allow to access"})

		try:
			if not user.is_impersonate:
				print user.is_impersonate
				print "if not is_impersonate last_login"
				user.last_login=timezone.now()
				user.save()
		except Exception as e:
			logger.info(str(e))
			print "Exception last_login"
			user.last_login=timezone.now()
			user.save()
			pass

		dashboard = {}

		profile = {}
		dashboard['profile'] = profile

		if not CompanyUser.objects.filter(user=user).exists():
			profile['company'] = "You haven't added company details yet."

		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company
			profile['is_profile_set'] = company.is_profile_set
			if CompanyKycTaxation.objects.filter(company=company).exists():
				profile['kyc_gstin'] = company.kyc.gstin
			else:
				profile['kyc_gstin'] = None


			if not Brand.objects.filter(company=company).exists():
				if not BrandDistributor.objects.filter(company=company).exists():
					profile['brand'] = "You haven't added any brands."
			if company.company_type_filled is False:
				profile['company_type_filled'] = CompanyType.objects.filter(company=company).values_list('id', flat=True).first()
			else:
				profile['company_type_filled'] = company.company_type_filled


		contacts = {}
		dashboard['contacts'] = contacts


		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company

			totalRequest = Buyer.objects.filter(Q(selling_company=company)|Q(buying_company=company)).count()
			#if totalRequest == 0:
			#	totalRequest = "no"
			contacts['request'] = totalRequest#"You have "+str(totalRequest)+" connection requests."

			totalABuyer = Buyer.objects.filter(selling_company=company, status="approved").count()
			#if totalABuyer == 0:
			#	totalABuyer = "no"
			contacts['approved_buyer'] = totalABuyer#"You have "+str(totalABuyer)+" buyers."

			totalPBuyer = Buyer.objects.filter(selling_company=company, status__in=["buyer_registrationpending","buyer_pending","supplier_pending"]).count()
			#if totalPBuyer == 0:
			#	totalPBuyer = "no"
			contacts['pending_buyer'] = totalPBuyer#"You have "+str(totalPBuyer)+" pending buyer requests."

			totalBuyerEnquiry = Buyer.objects.filter(selling_company=company, created_type="Enquiry").count()
			contacts['total_buyer_enquiry'] = totalBuyerEnquiry

			####if company.company_type.lower() == "nonmanufacturer":
			totalASupplier = Buyer.objects.filter(buying_company=company, status="approved").count()
			#if totalASupplier == 0:
			#	totalASupplier = "no"
			contacts['approved_supplier'] = totalASupplier#"You have "+str(totalASupplier)+" suppliers."


			totalPSupplier = Buyer.objects.filter(buying_company=company, status__in=["supplier_registrationpending","buyer_pending","supplier_pending"]).count()
			contacts['pending_supplier'] = totalPSupplier

			totalSupplierEnquiry = Buyer.objects.filter(buying_company=company, created_type="Enquiry").count()
			contacts['total_supplier_enquiry'] = totalSupplierEnquiry



		catalogs = {}
		dashboard['catalogs'] = catalogs

		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company

			#myDisableCatalogIds = getMyDisableCatalogIds(company)
			myDisableCatalogIds = getDisableCatalogIds(company)

			#totalCatalog = Catalog.objects.filter(company=company).exclude(id__in=myDisableCatalogIds).count()
			#cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
			#totalCatalog = Catalog.objects.filter(Q(company=company) | Q(id__in=cscatalogids)).exclude(id__in=myDisableCatalogIds).count()

			#if totalCatalog == 0:
			#	totalCatalog = "no"
			#catalogs['uploaded_catalog'] = totalCatalog#"You have "+str(totalCatalog)+" catalogs uploaded."
			catalogs['uploaded_catalog'] = myCatalogs(company)

			totalPush = Push.objects.filter(company=company).count()
			#if totalPush == 0:
			catalogs['shared_catalog'] = totalPush#"You haven't shared any catalogs yet."

			sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
			pushUsers = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).values_list('push', flat=True).distinct().count()
			catalogs['total_shared_with_me'] = pushUsers

			myPush = Push.objects.filter(company=company).values_list('id', flat=True).distinct()
			receivedCatalog = Push_User.objects.filter(buying_company=company).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
			catalogs['shared_received_catalog'] = 0
			if Push_User.objects.filter(push__in=myPush, catalog__in=receivedCatalog, selling_company=company).exists():
				#total = Push_User.objects.filter(push__in=myPush, catalog__in=receivedCatalog, selling_company=company).count()
				catalogs['shared_received_catalog'] = 1 # total#"You haven't shared any received catalogs or selections yet."

			last_shared = {}
			catalogs['last_shared'] = last_shared

			myPush = Push.objects.filter(company=company).last()
			if Push_User.objects.filter(push=myPush, selling_company=company).exists():
				pushUser = Push_User.objects.filter(push=myPush, selling_company=company).last()
				totalViewed = Push_User.objects.filter(push=myPush, selling_company=company, is_viewed='yes').count()
				#productViewed = Push_User_Product.objects.filter(push=myPush, selling_company=company, is_viewed='yes').count()
				productViewed = CompanyProductFlat.objects.filter(push_reference=myPush, selling_company=company, is_viewed='yes').count()
				last_shared['people_viewed'] = totalViewed
				last_shared['product_viewed'] = productViewed
				if pushUser.selection is not None:
					#catalogs['total_viewed'] = "Your last "+pushUser.selection.name+" shared was opened by "+totalViewed+" people"
					##catalogs['last_shared'] = pushUser.selection.name
					last_shared['name'] = "selection "+pushUser.selection.name
				else:
					##catalogs['last_shared'] = pushUser.catalog.title
					last_shared['name'] = "catalog "+pushUser.catalog.title
					#catalogs['total_viewed'] = "Your last "+pushUser.catalog.title+" shared was opened by "+str(totalViewed)+" people"

			popular = []
			catalogs['popular'] = popular
			#~ mostSales = SalesOrderItem.objects.filter(sales_order__seller_company=company).values('product').annotate(quantity = Sum('quantity')).order_by('-quantity')

			#~ for sale in mostSales:
				#~ record={}
				#~ product = Product.objects.get(pk=sale['product'])
				#~ record["title"]=product.title
				#~ record["sku"]=product.sku
				#~ record["order_quantity"]=sale['quantity']
				#~ record["likes"]=product.product_likes()

				#~ popular.append(record)

			mycatalogs = Catalog.objects.filter(company=company).exclude(id__in=myDisableCatalogIds).order_by('-id')

			todayDate = datetime.now()
			lastDate = todayDate - timedelta(days=7)

			ccvclicks = CompanyCatalogView.objects.filter(catalog__in=mycatalogs, created_at__gte=lastDate).aggregate(Sum('clicks')).get('clicks__sum', 0)
			if ccvclicks is None:
				ccvclicks = 0
			catalogs['my_catalog_total_views'] = ccvclicks

			lastestCatalog = mycatalogs.first()
			if lastestCatalog:
				catalogs['lastest_catalog'] = {}
				catalogs['lastest_catalog']['id'] = lastestCatalog.id
				catalogs['lastest_catalog']['title'] = lastestCatalog.title
				catalogs['lastest_catalog']['image'] = lastestCatalog.thumbnail.thumbnail[settings.LARGE_IMAGE].url
				ccvclicks = CompanyCatalogView.objects.filter(catalog=lastestCatalog).aggregate(Sum('clicks')).get('clicks__sum', 0)
				if ccvclicks is None:
					ccvclicks = 0
				catalogs['lastest_catalog']['views'] = ccvclicks

			ccvCatalogIds = CompanyCatalogView.objects.filter(catalog__in=mycatalogs).values('catalog').annotate(catalog_count=Count('catalog')).order_by('-catalog_count').values_list('catalog', flat=True).distinct()
			ccvCatalogIds = list(ccvCatalogIds)
			ccvCatalogIds.extend(list(mycatalogs.values_list('id', flat=True)))
			ccvCatalogIds = ccvCatalogIds[:3]
			preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ccvCatalogIds)])
			#topmycatalogs = mycatalogs.order_by(preserved)#[:3]
			topmycatalogs = Catalog.objects.filter(id__in=ccvCatalogIds).order_by(preserved)

			catalogs['my_most_viewed_catalogs'] = []
			for mycatalog in topmycatalogs:
				record={}
				record['id'] = mycatalog.id
				record['title'] = mycatalog.title
				record['image'] = mycatalog.thumbnail.thumbnail[settings.LARGE_IMAGE].url
				ccvclicks = CompanyCatalogView.objects.filter(catalog=mycatalog).aggregate(Sum('clicks')).get('clicks__sum', 0)
				if ccvclicks is None:
					ccvclicks = 0
				record['views'] = ccvclicks
				catalogs['my_most_viewed_catalogs'].append(record)

			urlPath = "most_viewed"
			result = cache.get(urlPath)
			if result:
				print "if result"
				publicCatalogs = result
			else:
				print "else no result"
				querysetcatalogs = Catalog.objects.filter(deleted=False)

				params = {}
				params["view_type"] = "public"
				params["most_viewed"] = "true"

				catalogQuerysetFilter(querysetcatalogs, company, params, user, "list")

				publicCatalogs = cache.get(urlPath)
			# publicCatalogs = getCache("most_viewed")
			publiccatalogids = publicCatalogs.values_list('id', flat=True)
			#print "publiccatalogids = ",publiccatalogids
			catalogs['catalogs_under_most_viewed'] = mycatalogs.filter(id__in=list(publiccatalogids)).count()


		orders = {}
		dashboard['orders'] = orders
		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company
			#orders['salesorder_pending'] = 0
			#if SalesOrder.objects.filter(seller_company=company, processing_status="Pending").exists():
			orders['salesorder_pending'] = SalesOrder.objects.filter(seller_company=company, processing_status="Pending").count()
			#orders['purchaseorder_pending'] = 0
			#if SalesOrder.objects.filter(company=company, processing_status="Pending").exists():
			orders['purchaseorder_pending'] = SalesOrder.objects.filter(company=company, processing_status="Pending").count()

			orders['salesorder_dispatched'] = SalesOrder.objects.filter(seller_company=company, processing_status="Dispatched").count()
			orders['purchaseorder_dispatched'] = SalesOrder.objects.filter(company=company, processing_status="Dispatched").count()

			orders['salesorder_cancelled'] = SalesOrder.objects.filter(seller_company=company, processing_status="Cancelled").count()
			orders['purchaseorder_cancelled'] = SalesOrder.objects.filter(company=company, processing_status="Cancelled").count()

		#dashboard.append(profile)
		buyerObjs = Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True)))
		print buyerObjs
		companies = CompanyBrandFollow.objects.filter(brand__in=buyerObjs).values_list('company', flat=True).distinct()
		dashboard['total_followers'] = len(companies)

		return Response(dashboard)

	@detail_route(methods=['GET'], url_path='dashboard/buyer')
	def dashboard_buyer(self, request, pk=None):#, companies_pk=None
		user = request.user
		company = get_user_company(user) #user.companyuser.company

		#if int(company.id) != int(pk):
		#	raise serializers.ValidationError({"failed":"You are not allow to access"})

		try:
			if not user.is_impersonate:
				print user.is_impersonate
				print "if not is_impersonate last_login"
				user.last_login=timezone.now()
				user.save()
		except Exception as e:
			logger.info(str(e))
			print "Exception last_login"
			user.last_login=timezone.now()
			user.save()
			pass

		dashboard = {}

		profile = {}
		dashboard['profile'] = profile

		if not CompanyUser.objects.filter(user=user).exists():
			profile['company'] = "You haven't added company details yet."

		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company
			profile['is_profile_set'] = company.is_profile_set

			if CompanyKycTaxation.objects.filter(company=company).exists():
				profile['kyc_gstin'] = company.kyc.gstin
			else:
				profile['kyc_gstin'] = None


			if not Brand.objects.filter(company=company).exists():
				if not BrandDistributor.objects.filter(company=company).exists():
					profile['brand'] = "You haven't added any brands."
			if company.company_type_filled is False:
				profile['company_type_filled'] = CompanyType.objects.filter(company=company).values_list('id', flat=True).first()
			else:
				profile['company_type_filled'] = company.company_type_filled

			if not SolePropreitorshipKYC.objects.filter(company=company).exists():
				profile['credit_rating_score'] = None
			else:
				profile['credit_rating_score'] = 0
				if CompanyCreditRating.objects.filter(company=company).exists():
					ccrObj = CompanyCreditRating.objects.filter(company=company).last()
					if ccrObj.bureau_score is not None and ccrObj.bureau_score > 0:
						profile['credit_rating_score'] = ccrObj.bureau_score


		orders = {}
		dashboard['orders'] = orders
		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company
			orders['purchaseorder_pending'] = SalesOrder.objects.filter(company=company, processing_status="Pending").count()
			orders['purchaseorder_dispatched'] = SalesOrder.objects.filter(company=company, processing_status="Dispatched").count()
			orders['purchaseorder_cancelled'] = SalesOrder.objects.filter(company=company, processing_status="Cancelled").count()

		contacts = {}
		dashboard['contacts'] = contacts

		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company

			totalRequest = Buyer.objects.filter(Q(selling_company=company)|Q(buying_company=company)).count()
			contacts['request'] = totalRequest

			totalABuyer = Buyer.objects.filter(selling_company=company, status="approved").count()
			contacts['approved_buyer'] = totalABuyer

			totalPBuyer = Buyer.objects.filter(selling_company=company, status__in=["buyer_registrationpending","buyer_pending","supplier_pending"]).count()
			contacts['pending_buyer'] = totalPBuyer

			totalBuyerEnquiry = Buyer.objects.filter(selling_company=company, created_type="Enquiry").count()
			contacts['total_buyer_enquiry'] = totalBuyerEnquiry

			totalASupplier = Buyer.objects.filter(buying_company=company, status="approved").count()
			contacts['approved_supplier'] = totalASupplier

			totalPSupplier = Buyer.objects.filter(buying_company=company, status__in=["supplier_registrationpending","buyer_pending","supplier_pending"]).count()
			contacts['pending_supplier'] = totalPSupplier

			totalSupplierEnquiry = Buyer.objects.filter(buying_company=company, created_type="Enquiry").count()
			contacts['total_supplier_enquiry'] = totalSupplierEnquiry

		#~ catalogs = {}
		#~ dashboard['catalogs'] = catalogs

		#~ if CompanyUser.objects.filter(user=user).exists():
			#~ company = user.companyuser.company

			#~ #myDisableCatalogIds = getMyDisableCatalogIds(company)
			#~ catalogs['uploaded_catalog'] = myCatalogs(company)


		return Response(dashboard)

	@detail_route(methods=['GET'], url_path='dashboard/seller')
	def dashboard_seller(self, request, pk=None):#, companies_pk=None
		user = request.user
		company = get_user_company(user) #user.companyuser.company

		#if int(company.id) != int(pk):
		#	raise serializers.ValidationError({"failed":"You are not allow to access"})

		try:
			if not user.is_impersonate:
				print user.is_impersonate
				print "if not is_impersonate last_login"
				user.last_login=timezone.now()
				user.save()
		except Exception as e:
			logger.info(str(e))
			print "Exception last_login"
			user.last_login=timezone.now()
			user.save()
			pass

		dashboard = {}

		profile = {}
		dashboard['profile'] = profile

		if not CompanyUser.objects.filter(user=user).exists():
			profile['company'] = "You haven't added company details yet."

		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company
			profile['is_profile_set'] = company.is_profile_set
			if CompanyKycTaxation.objects.filter(company=company).exists():
				profile['kyc_gstin'] = company.kyc.gstin
			else:
				profile['kyc_gstin'] = None


			if not Brand.objects.filter(company=company).exists():
				if not BrandDistributor.objects.filter(company=company).exists():
					profile['brand'] = "You haven't added any brands."
			if company.company_type_filled is False:
				profile['company_type_filled'] = CompanyType.objects.filter(company=company).values_list('id', flat=True).first()
			else:
				profile['company_type_filled'] = company.company_type_filled

		orders = {}
		dashboard['orders'] = orders
		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company
			orders['salesorder_pending'] = SalesOrder.objects.filter(seller_company=company, processing_status="Pending").count()
			orders['salesorder_dispatched'] = SalesOrder.objects.filter(seller_company=company, processing_status="Dispatched").count()
			orders['salesorder_cancelled'] = SalesOrder.objects.filter(seller_company=company, processing_status="Cancelled").count()

		contacts = {}
		dashboard['contacts'] = contacts

		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company

			totalRequest = Buyer.objects.filter(Q(selling_company=company)|Q(buying_company=company)).count()
			contacts['request'] = totalRequest

			totalABuyer = Buyer.objects.filter(selling_company=company, status="approved").count()
			contacts['approved_buyer'] = totalABuyer

			totalPBuyer = Buyer.objects.filter(selling_company=company, status__in=["buyer_registrationpending","buyer_pending","supplier_pending"]).count()
			contacts['pending_buyer'] = totalPBuyer

			totalBuyerEnquiry = Buyer.objects.filter(selling_company=company, created_type="Enquiry").count()
			contacts['total_buyer_enquiry'] = totalBuyerEnquiry

			totalASupplier = Buyer.objects.filter(buying_company=company, status="approved").count()
			contacts['approved_supplier'] = totalASupplier

			totalPSupplier = Buyer.objects.filter(buying_company=company, status__in=["supplier_registrationpending","buyer_pending","supplier_pending"]).count()
			contacts['pending_supplier'] = totalPSupplier

			totalSupplierEnquiry = Buyer.objects.filter(buying_company=company, created_type="Enquiry").count()
			contacts['total_supplier_enquiry'] = totalSupplierEnquiry

		catalogs = {}
		dashboard['catalogs'] = catalogs

		if CompanyUser.objects.filter(user=user).exists():
			company = user.companyuser.company

			catalogs['uploaded_catalog'] = myCatalogs(company)

			#myDisableCatalogIds = getMyDisableCatalogIds(company)
			myDisableCatalogIds = getDisableCatalogIds(company)

			#catalogs['uploaded_catalog'] = myCatalogs(company)

			mycatalogs = Catalog.objects.filter(company=company).exclude(id__in=myDisableCatalogIds).order_by('-id')

			todayDate = datetime.now()
			lastDate = todayDate - timedelta(days=7)

			ccvclicks = CompanyCatalogView.objects.filter(catalog__in=mycatalogs, created_at__gte=lastDate).aggregate(Sum('clicks')).get('clicks__sum', 0)
			if ccvclicks is None:
				ccvclicks = 0

			catalogs['my_catalog_total_views'] = ccvclicks

			lastestCatalog = mycatalogs.first()
			if lastestCatalog:
				catalogs['lastest_catalog'] = {}
				catalogs['lastest_catalog']['id'] = lastestCatalog.id
				catalogs['lastest_catalog']['title'] = lastestCatalog.title
				catalogs['lastest_catalog']['image'] = lastestCatalog.thumbnail.thumbnail[settings.LARGE_IMAGE].url
				ccvclicks = CompanyCatalogView.objects.filter(catalog=lastestCatalog).aggregate(Sum('clicks')).get('clicks__sum', 0)
				if ccvclicks is None:
					ccvclicks = 0
				catalogs['lastest_catalog']['views'] = ccvclicks

			ccvCatalogIds = CompanyCatalogView.objects.filter(catalog__in=mycatalogs).values('catalog').annotate(catalog_count=Count('catalog')).order_by('-catalog_count').values_list('catalog', flat=True).distinct()
			ccvCatalogIds = list(ccvCatalogIds)
			ccvCatalogIds.extend(list(mycatalogs.values_list('id', flat=True)))
			ccvCatalogIds = ccvCatalogIds[:3]
			preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ccvCatalogIds)])
			#topmycatalogs = mycatalogs.order_by(preserved)[:3]
			topmycatalogs = Catalog.objects.filter(id__in=ccvCatalogIds).order_by(preserved)

			catalogs['my_most_viewed_catalogs'] = []
			for mycatalog in topmycatalogs:
				record={}
				record['id'] = mycatalog.id
				record['title'] = mycatalog.title
				record['image'] = mycatalog.thumbnail.thumbnail[settings.LARGE_IMAGE].url
				ccvclicks = CompanyCatalogView.objects.filter(catalog=mycatalog).aggregate(Sum('clicks')).get('clicks__sum', 0)
				if ccvclicks is None:
					ccvclicks = 0
				record['views'] = ccvclicks
				catalogs['my_most_viewed_catalogs'].append(record)

			urlPath = "most_viewed"
			result = cache.get(urlPath)
			if result:
				print "if result"
				publicCatalogs = result
			else:
				print "else no result"
				querysetcatalogs = Catalog.objects.filter(deleted=False)

				params = {}
				params["view_type"] = "public"
				params["most_viewed"] = "true"

				catalogQuerysetFilter(querysetcatalogs, company, params, user, "list")

				publicCatalogs = cache.get(urlPath)
			# publicCatalogs = getCache("most_viewed")
			publiccatalogids = publicCatalogs.values_list('id', flat=True)
			#print "publiccatalogids = ",publiccatalogids
			catalogs['catalogs_under_most_viewed'] = mycatalogs.filter(id__in=list(publiccatalogids)).count()

		buyerObjs = Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True)))
		print buyerObjs
		companies = CompanyBrandFollow.objects.filter(brand__in=buyerObjs).values_list('company', flat=True).distinct()
		dashboard['total_followers'] = len(companies)

		return Response(dashboard)

	@detail_route(methods=['get'])
	def brokers(self, request, pk=None):#, companies_pk=None
		user = request.user
		company = get_user_company(user) #user.companyuser.company

		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		#if int(company.id) != int(pk):
		#	raise serializers.ValidationError({"failed":"You are not allow to access"})

		queryset = Buyer.objects.filter(status="approved", selling_company=company, group_type=GroupType.objects.get(pk=9)).select_related('buying_company').order_by('buying_company__name')
		#queryset = self.filter_queryset(queryset)
		array = []
		for b in queryset:
			array.append({"id":b.id,"company_id":b.buying_company.id,"company_name":b.buying_company.name, "brokerage_fees":b.brokerage_fees})

		return Response(array)

	@list_route(methods=['get'], permission_classes=[permissions.AllowAny], )
	def dropdown(self, request):#, companies_pk=None
		#queryset = self.get_queryset().order_by('id')
		queryset = self.get_queryset().values('id','name').order_by('id')

		#queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

		# ~ array = []
		# ~ for co in queryset:
			# ~ array.append({"id":co.id,"name":co.name})

		# ~ return Response(array)

	@list_route(methods=['get','post'], permission_classes=[permissions.IsAdminUser], )
	def merge(self, request):
		print self.request.method

		if self.request.method == 'GET':
			print "has params GET"
			data = request.GET
			merge_from = data.get('merge_from', None)
			merge_into = data.get('merge_into', None)

			print merge_from
			print merge_into

			jsondata = {}

			if merge_from and merge_into:

				merge_from_company = Company.objects.get(pk=merge_from)
				merge_into_company = Company.objects.get(pk=merge_into)

				print merge_from_company
				print merge_into_company

				merge_from_json = {}
				merge_into_json = {}
				merge_result_json = {}

				merge_from_json['id'] = int(merge_from)
				merge_into_json['id'] = int(merge_into)

				merge_from_json['name'] = merge_from_company.name
				merge_into_json['name'] = merge_into_company.name
				merge_result_json['name'] = "Merge Result"

				ct = CompanyType.objects.get(company=merge_from)
				merge_from_ctype = []
				if ct.manufacturer is True:
					merge_from_ctype.append('Manufacturer')
				if ct.wholesaler_distributor is True:
					merge_from_ctype.append('Wholesaler Distributor')
				if ct.retailer is True:
					merge_from_ctype.append('Retailer')
				if ct.online_retailer_reseller is True:
					merge_from_ctype.append('Online Retailer Reseller')
				if ct.broker is True:
					merge_from_ctype.append('Broker')

				merge_result_ctype = merge_from_ctype
				merge_from_json['company_type'] = ', '.join(merge_from_ctype)


				ct = CompanyType.objects.get(company=merge_into)
				merge_into_ctype = []
				if ct.manufacturer is True:
					merge_into_ctype.append('Manufacturer')
					if 'Manufacturer' not in merge_result_ctype:
						merge_result_ctype.append('Manufacturer')
				if ct.wholesaler_distributor is True:
					merge_into_ctype.append('Wholesaler Distributor')
					if 'Wholesaler Distributor' not in merge_result_ctype:
						merge_result_ctype.append('Wholesaler Distributor')
				if ct.retailer is True:
					merge_into_ctype.append('Retailer')
					if 'Retailer' not in merge_result_ctype:
						merge_result_ctype.append('Retailer')
				if ct.online_retailer_reseller is True:
					merge_into_ctype.append('Online Retailer Reseller')
					if 'Online Retailer Reseller' not in merge_result_ctype:
						merge_result_ctype.append('Online Retailer Reseller')
				if ct.broker is True:
					merge_into_ctype.append('Broker')
					if 'Broker' not in merge_result_ctype:
						merge_result_ctype.append('Broker')

				merge_into_json['company_type'] = ', '.join(merge_into_ctype)


				merge_result_json['company_type'] = ', '.join(merge_result_ctype)


				merge_from_json['buyers'] = Buyer.objects.filter(selling_company=merge_from).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct().count()
				bnames = Buyer.objects.filter(selling_company=merge_from).exclude(buying_company__isnull=True).values_list('buying_company__name', flat=True).distinct()
				bnames = ', '.join(bnames)
				merge_from_json['buyers'] = str(merge_from_json['buyers'])+" ," + bnames
				merge_from_json['suppliers'] = Buyer.objects.filter(buying_company=merge_from).exclude(selling_company__isnull=True).values_list('selling_company', flat=True).distinct().count()
				merge_from_json['catalogs'] = Catalog.objects.filter(company=merge_from).count()
				merge_from_json['sales_orders'] = SalesOrder.objects.filter(seller_company=merge_from).count()
				merge_from_json['purchase_orders'] = SalesOrder.objects.filter(company=merge_from).count()
				merge_from_json['users'] = CompanyUser.objects.filter(Q(company=merge_from) | Q(deputed_to=merge_from)).count()
				merge_from_json['meetings'] = Meeting.objects.filter(company=merge_from).count()
				merge_from_json['attendance'] = Attendance.objects.filter(company=merge_from).count()
				merge_from_json['brand'] = Brand.objects.filter(Q(manufacturer_company=merge_from) | Q(company=merge_from)).count()

				merge_into_json['buyers'] = Buyer.objects.filter(selling_company=merge_into).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct().count()
				bnames = Buyer.objects.filter(selling_company=merge_into).exclude(buying_company__isnull=True).values_list('buying_company__name', flat=True).distinct()
				bnames = ', '.join(bnames)
				merge_into_json['buyers'] = str(merge_into_json['buyers'])+" ," + bnames
				merge_into_json['suppliers'] = Buyer.objects.filter(buying_company=merge_into).exclude(selling_company__isnull=True).values_list('selling_company', flat=True).distinct().count()
				merge_into_json['catalogs'] = Catalog.objects.filter(company=merge_into).count()
				merge_into_json['sales_orders'] = SalesOrder.objects.filter(seller_company=merge_into).count()
				merge_into_json['purchase_orders'] = SalesOrder.objects.filter(company=merge_into).count()
				merge_into_json['users'] = CompanyUser.objects.filter(Q(company=merge_into) | Q(deputed_to=merge_into)).count()
				merge_into_json['meetings'] = Meeting.objects.filter(company=merge_into).count()
				merge_into_json['attendance'] = Attendance.objects.filter(company=merge_into).count()
				merge_into_json['brand'] = Brand.objects.filter(Q(manufacturer_company=merge_into) | Q(company=merge_into)).count()

				merge_result_json['buyers'] = Buyer.objects.filter(Q(selling_company=merge_from) | Q(selling_company=merge_into)).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct().count()
				bnames = Buyer.objects.filter(Q(selling_company=merge_from) | Q(selling_company=merge_into)).exclude(buying_company__isnull=True).values_list('buying_company__name', flat=True).distinct()
				bnames = ', '.join(bnames)
				merge_result_json['buyers'] = str(merge_result_json['buyers'])+" ," + bnames
				merge_result_json['suppliers'] = Buyer.objects.filter(Q(buying_company=merge_from) | Q(buying_company=merge_into)).exclude(selling_company__isnull=True).values_list('selling_company', flat=True).distinct().count()
				merge_result_json['catalogs'] = Catalog.objects.filter(Q(company=merge_from) | Q(company=merge_into)).count()
				merge_result_json['sales_orders'] = SalesOrder.objects.filter(Q(seller_company=merge_from) | Q(seller_company=merge_into)).count()
				merge_result_json['purchase_orders'] = SalesOrder.objects.filter(Q(company=merge_from) | Q(company=merge_into)).count()
				merge_result_json['users'] = CompanyUser.objects.filter(Q(company=merge_from) | Q(deputed_to=merge_from) | Q(company=merge_into) | Q(deputed_to=merge_into)).count()
				merge_result_json['meetings'] = Meeting.objects.filter(Q(company=merge_from) | Q(company=merge_into)).count()
				merge_result_json['attendance'] = Attendance.objects.filter(Q(company=merge_from) | Q(company=merge_into)).count()
				merge_result_json['brand'] = Brand.objects.filter(Q(manufacturer_company=merge_from) | Q(company=merge_from) | Q(manufacturer_company=merge_into) | Q(company=merge_into)).count()

				jsondata['merge_from'] = merge_from_json
				jsondata['merge_into'] = merge_into_json
				jsondata['merge_result'] = merge_result_json

			return Response(jsondata)

		if self.request.method == 'POST':
			print "has params POST"
			data = request.data
			merge_from = data.get('merge_from', None)
			merge_into = data.get('merge_into', None)

			print merge_from
			print merge_into
			#return Response({"success": "Merged successfully."})
			if merge_from and merge_into:
				merge_from_company = Company.objects.get(pk=merge_from)
				merge_into_company = Company.objects.get(pk=merge_into)

				print merge_from_company
				print merge_into_company


				merge_from_ct = CompanyType.objects.get(company=merge_from)
				merge_into_ct = CompanyType.objects.get(company=merge_into)
				if merge_from_ct.manufacturer is True:
					merge_into_ct.manufacturer = True
				if merge_from_ct.wholesaler_distributor is True:
					merge_into_ct.wholesaler_distributor = True
				if merge_from_ct.retailer is True:
					merge_into_ct.retailer = True
				if merge_from_ct.online_retailer_reseller is True:
					merge_into_ct.online_retailer_reseller = True
				if merge_from_ct.broker is True:
					merge_into_ct.broker = True
				merge_into_ct.save()

				mi_buyers = Buyer.objects.filter(selling_company=merge_into).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct()
				print mi_buyers
				mf_buyers = Buyer.objects.filter(selling_company=merge_from, buying_company__isnull=False).exclude(Q(buying_company=merge_into) | Q(buying_company__in=list(mi_buyers))).update(selling_company=merge_into_company)#.values_list('id', flat=True).distinct()
				print mf_buyers
				#Buyer.objects.filter(id__in=list(mf_buyers)).update(selling_company=merge_into_company)


				mi_suppliers = Buyer.objects.filter(buying_company=merge_into).exclude(selling_company__isnull=True).values_list('selling_company', flat=True).distinct()
				print mi_suppliers
				mf_suppliers = Buyer.objects.filter(buying_company=merge_from, selling_company__isnull=False).exclude(Q(selling_company=merge_into) | Q(selling_company__in=list(mi_suppliers))).update(buying_company=merge_into_company)
				print mf_suppliers


				Catalog.objects.filter(company=merge_from).update(company=merge_into_company)
				SalesOrder.objects.filter(seller_company=merge_from).update(seller_company=merge_into_company)
				SalesOrder.objects.filter(company=merge_from).update(company=merge_into_company)
				CompanyUser.objects.filter(company=merge_from).update(company=merge_into_company)
				CompanyUser.objects.filter(deputed_to=merge_from).update(deputed_to=merge_into_company)

				Meeting.objects.filter(company=merge_from).update(company=merge_into_company)
				Attendance.objects.filter(company=merge_from).update(company=merge_into_company)

				Brand.objects.filter(manufacturer_company=merge_from).update(manufacturer_company=merge_into_company)
				Brand.objects.filter(company=merge_from).update(company=merge_into_company)

				#Company.objects.filter(id=merge_from).delete()

			return Response({"success": "Merged successfully."})

	@list_route(methods=['post'])
	def change_company(self, request):
		print "change_company"
		loginUser = request.user
		#loginCompany = loginUser.companyuser.company

		data = request.data
		print data

		first_name = data.get('first_name', None)
		email = data.get('email', None)
		new_company = data.get('company', None)

		if first_name:
			loginUser.first_name = first_name
			loginUser.save()

		if email:
			try:
				loginUser.email = email
				loginUser.save()
			except Exception as e:
				logger.info("change_company email error = %s" % (str(e)))

		if new_company:
			newCompanyObj = Company.objects.get(pk=new_company)

			if CompanyUser.objects.filter(user=loginUser).exists():
				CompanyUser.objects.filter(user=loginUser).update(company = newCompanyObj)
			else:
				CompanyUser.objects.create(user=loginUser, company = newCompanyObj)

			#loginUser.companyuser.company = newCompanyObj
			#loginUser.companyuser.save()

			loginUser.userprofile.user_approval_status = "Pending"
			loginUser.userprofile.save()

		return Response({"success": "Your company has been changed successfully"})

	@detail_route(methods=['get'])
	def statistics(self, request, pk=None):#, companies_pk=None
		user = request.user
		company = get_user_company(user) #user.companyuser.company

		jsonarr = {}

		if company is None:
			return Response(jsonarr)

		# jsonarr['total_salesorder'] = SalesOrder.objects.filter(visible_to_supplier=True, seller_company=company).exclude(processing_status__in=["Cart","Draft"]).count()
		jsonarr['total_salesorder'] = SalesOrder.objects.filter(visible_to_supplier=True, seller_company=company).exclude(processing_status__in=["Cart"]).count()
		jsonarr['salesorder_pending'] = SalesOrder.objects.filter(visible_to_supplier=True, seller_company=company, processing_status__in=["Draft","Pending","ordered","Accepted","In Progress", "COD Verification Pending", "Field Verification Pending"]).count()
		jsonarr['salesorder_dispatched'] = SalesOrder.objects.filter(visible_to_supplier=True, seller_company=company, processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"]).count()
		jsonarr['salesorder_cancelled'] = SalesOrder.objects.filter(visible_to_supplier=True, seller_company=company, processing_status__in=["Cancelled","Transferred"]).count()

		jsonarr['total_purchaseorder'] = SalesOrder.objects.filter(visible_to_buyer=True, company=company).exclude(processing_status__in=["Cart"]).count()
		jsonarr['purchaseorder_pending'] = SalesOrder.objects.filter(visible_to_buyer=True, company=company, processing_status__in=["Draft","Pending","ordered","Accepted","In Progress", "COD Verification Pending", "Field Verification Pending"]).count()
		jsonarr['purchaseorder_dispatched'] = SalesOrder.objects.filter(visible_to_buyer=True, company=company, processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"]).count()
		jsonarr['purchaseorder_cancelled'] = SalesOrder.objects.filter(visible_to_buyer=True, company=company, processing_status__in=["Cancelled","Transferred"]).count()

		jsonarr['total_brokerorder'] = SalesOrder.objects.filter(broker_company=company).exclude(processing_status__in=["Cart"]).count()
		jsonarr['brokerorder_pending'] = SalesOrder.objects.filter(broker_company=company, processing_status__in=["Draft","Pending","ordered","Accepted","In Progress", "COD Verification Pending", "Field Verification Pending"]).count()
		jsonarr['brokerorder_dispatched'] = SalesOrder.objects.filter(broker_company=company, processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"]).count()
		jsonarr['brokerorder_cancelled'] = SalesOrder.objects.filter(broker_company=company, processing_status__in=["Cancelled","Transferred"]).count()


		buyerObjs = Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True)))
		#cs_catalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
		disableCatalogIds = getDisableCatalogIds(company)

		companies = CompanyBrandFollow.objects.filter(brand__in=buyerObjs).values_list('company', flat=True).distinct()
		jsonarr['my_followers'] = len(companies)
		#jsonarr['my_followers'] = CompanyBrandFollow.objects.filter(brand__in=buyerObjs).count()
		#jsonarr['wishlist'] = UserWishlist.objects.filter(Q(catalog__company=company) | Q(catalog__in=cs_catalogids)).values_list('user', flat=True).distinct().count()

		#disable_cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Disable").values_list('catalog', flat=True).distinct()
		#jsonarr['wishlist'] = UserWishlist.objects.filter(user=user).exclude(Q(catalog__in=disableCatalogIds) | Q(catalog__deleted=True)).values_list('catalog', flat=True).distinct().count()
		jsonarr['wishlist'] = UserWishlist.objects.filter(user=user).exclude(catalog__deleted=True).values_list('catalog', flat=True).distinct().count()

		# ~ ccvtotal = CompanyCatalogView.objects.filter(Q(catalog__company=company) | Q(catalog__in=cs_catalogids)).aggregate(Sum('clicks')).get('clicks__sum', 0)
		# ~ if ccvtotal is None:
			# ~ ccvtotal = 0
		#jsonarr['my_viewers'] = ccvtotal
		# ~ jsonarr['my_viewers'] = CompanyCatalogView.objects.filter(Q(catalog__company=company) | Q(catalog__in=cs_catalogids)).count()

		followed_ids = CompanyBrandFollow.objects.filter(company=company).values_list('brand', flat=True).distinct()
		jsonarr['brand_i_follow'] = len(followed_ids) #CompanyBrandFollow.objects.filter(company=company).count()

		jsonarr['total_enquiry'] = Buyer.objects.filter(buying_company=company, created_type="Enquiry").count()
		jsonarr['opened_enquiry'] = Buyer.objects.filter(buying_company=company, created_type="Enquiry", buyer_type="Enquiry").count()
		jsonarr['closed_enquiry'] = Buyer.objects.filter(buying_company=company, created_type="Enquiry", buyer_type="Relationship").count()

		jsonarr['total_catalogenquiry'] = CatalogEnquiry.objects.filter(buying_company=company).count()
		jsonarr['opened_catalogenquiry'] = CatalogEnquiry.objects.filter(buying_company=company, status="Created").count()
		jsonarr['closed_catalogenquiry'] = CatalogEnquiry.objects.filter(buying_company=company, status="Resolved").count()

		jsonarr['total_lead'] = Buyer.objects.filter(selling_company=company, created_type="Enquiry").count()
		jsonarr['opened_lead'] = Buyer.objects.filter(selling_company=company, created_type="Enquiry", buyer_type="Enquiry").count()
		jsonarr['closed_lead'] = Buyer.objects.filter(selling_company=company, created_type="Enquiry", buyer_type="Relationship").count()

		jsonarr['total_cataloglead'] = CatalogEnquiry.objects.filter(selling_company=company).count()
		jsonarr['opened_cataloglead'] = CatalogEnquiry.objects.filter(selling_company=company, status="Created").count()
		jsonarr['closed_cataloglead'] = CatalogEnquiry.objects.filter(selling_company=company, status="Resolved").count()

		# ~ state = company.address.state
		# ~ buyerOwnIds = buyerObjs #Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True))).values_list('id', flat=True)
		# ~ cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
		# ~ queryset = Catalog.objects.filter(Q(company=company) | Q(id__in=cscatalogids) | Q(brand__in=buyerOwnIds, view_permission="public")).exclude(id__in=disableCatalogIds).order_by('-id')
		# ~ own_viewed_count = CompanyCatalogView.objects.filter(catalog__in=queryset, catalog__brand__in=buyerOwnIds).exclude(company=company).count()
		# ~ list_viewed_count = CompanyCatalogView.objects.filter(Q(catalog__in=queryset) & Q(Q(company__address__state=state) | Q(user__address__state=state))).exclude(Q(company=company) | Q(catalog__brand__in=buyerOwnIds)).count()
		# ~ jsonarr['my_viewers'] = own_viewed_count + list_viewed_count
		jsonarr['my_viewers'] = 0

		cart = Cart.objects.filter(buying_company=company).last()
		if cart and cart.cart_status == "Created":
			jsonarr['latest_cart_id'] = cart.id
			jsonarr['total_cart_items'] =  getTotalCartItemCount(cart)

		return Response(jsonarr)


class UserViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrUser, )
	def get_queryset(self):
		'''phone_number = self.request.query_params.get('phone_number', None)
		country = self.request.query_params.get('country', None)
		if phone_number is not None and country is not None:
			if UserProfile.objects.filter(phone_number=phone_number, country=country).exists() or Company.objects.filter(phone_number=phone_number, country=country).exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exists():
				raise serializers.ValidationError({"phone_number":"Phone number is already exist. Please choose another Phone number"})
			print "lsat"
			return Response({"success": "Phone Number is verified"})'''

		queryset = User.objects.all().select_related('userprofile','companyuser__company').prefetch_related('groups')

		typeName = self.request.query_params.get('type', None)
		if typeName is not None:
			typeName = typeName.split(",")
			queryset = queryset.filter(groups__name__in=typeName)

		user = self.request.user

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					companyUserIds = CompanyUser.objects.filter(Q(company=company)| Q(deputed_to=company)).values_list('user', flat=True).distinct()# | Q(deputed_from=company)
					#print str(datetime.utcnow())
					return queryset.filter(Q(id__in=companyUserIds) | Q(id = user.id))
			except ObjectDoesNotExist:
				return queryset.filter(id=user.id)
		else:
			return queryset.filter(id=user.id)

	def perform_create(self, serializer):
		user = self.request.user
		if user.is_staff:
			serializer.save()
		else:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				userInstance = serializer.save()
				#CompanyUser.objects.get_or_create(company=company, user=userInstance)


	def list(self, request, companies_pk=None):
		queryset = self.get_queryset()

		field = self.request.query_params.get('field', None)

		phone_number = self.request.query_params.get('phone_number', None)
		country = self.request.query_params.get('country', None)
		if country is None or country == "" or country == "null":
			country = Country.objects.get(pk=1)

		if phone_number is not None and country is not None and field is not None and field.lower() == "is_exist":
			#if UserProfile.objects.filter(phone_number=phone_number, country=country).exists() or Company.objects.filter(phone_number=phone_number, country=country).exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exists():
			if not is_phone_number_available(country, phone_number, False):
				raise serializers.ValidationError({"phone_number":"Phone number already exists. Please choose another phone number"})

			return Response({"success": "Phone Number is verified"})

		email = self.request.query_params.get('email', None)
		if email is not None and field is not None and field.lower() == "is_exist":
			if User.objects.filter(email=email).exists():
				raise serializers.ValidationError({"email":"Email Id already exists. Please choose another Email Id"})

			return Response({"success": "Email Id is verified"})

		if phone_number is not None and country is not None and field is not None and field.lower() == "get_userdetail":
			if UserProfile.objects.filter(phone_number=phone_number, country=country).exists():
				userprofile = UserProfile.objects.filter(phone_number=phone_number, country=country).first()
				return Response({"username": userprofile.user.username, "id":userprofile.user.id})
			else:
				raise serializers.ValidationError({"phone_number":"This phone number is not registered. Please enter mobile number registered with Wishbook."})

		serializer = self.get_serializer(instance=queryset, many=True)
		return Response(serializer.data)

	@list_route(methods=['get'])
	def dropdown(self, request, catalogs_pk=None):
		queryset = self.get_queryset().values('id','username')
		queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

	'''@detail_route(methods=['PATCH'])
	def phone_number(self, request, pk=None, companies_pk=None):
		user = self.request.user
		queryset = self.get_object()

		data = self.request.data
		country = data.get('country')
		phone_number = data.get('phone_number')
		otp = data.get('otp', None)

		#if UserProfile.objects.filter(phone_number=phone_number, country=country, phone_number_verified='yes').exists() or Company.objects.filter(phone_number=phone_number, country=country, phone_number_verified='yes').exists() or CompanyPhoneAlias.objects.filter(alias_number=phone_number, country=country, status="Approved").exists():
		if not is_phone_number_available(country, phone_number, True):
			raise serializers.ValidationError({"phone_number":"Phone number is already exist. Please choose another Phone number"})

		if otp is not None:
			if RegistrationOTP.objects.filter(phone_number=phone_number, country=country).exists():
					registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-created_date').first()

					if str(registrationOtp.otp) == otp:
						registrationOtp.is_verified = "yes"
						registrationOtp.save()

						queryset.userprofile.phone_number = phone_number
						queryset.userprofile.save()

						try:
							if user.companyuser is not None:
								company = user.companyuser.company
								makeBuyerSupplierFromInvitee(registrationOtp.phone_number, registrationOtp.country, company)
						except ObjectDoesNotExist:
							pass

						return Response({"success": "OTP is valid"})
			raise serializers.ValidationError({"otp":"Please enter valid OTP"})

		country = Country.objects.get(pk=country)

		otpno = random.randrange(100000, 999999, 1)
		sendOTP(str(country.phone_code)+str(phone_number), str(otpno))

		registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otpno, country=country)

		return Response({"success": "OTP has been sent successfully"})'''

	'''@detail_route(methods=['PATCH'], permission_classes=[permissions.AllowAny],)
	def password(self, request, pk=None, companies_pk=None): #not working
		queryset = self.get_object()

		data = self.request.data
		country = queryset.userprofile.country
		phone_number = queryset.userprofile.phone_number
		otp = data.get('otp', None)
		password = data.get('password', None)

		if otp is not None and password is not None:
			if RegistrationOTP.objects.filter(phone_number=phone_number, country=country).exists():
					registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-created_date').first()

					if str(registrationOtp.otp) == otp:
						registrationOtp.is_verified = "yes"
						registrationOtp.save()

						user=UserProfile.objects.filter(phone_number=phone_number, country=country).first().user
						user.set_password(password)
						user.save()

						return Response({"success": "Password has been changed successfully"})

			raise serializers.ValidationError({"otp":"Please enter valid OTP"})

		otpno = random.randrange(100000, 999999, 1)
		sendOTP(str(country.phone_code)+str(phone_number), str(otpno))

		registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otpno, country=country)
		print registrationOtp

		return Response({"success": "OTP has been sent successfully"})'''

	'''@list_route(methods=['POST'], permission_classes=[permissions.AllowAny,])
	def otp(self, request):
		data = self.request.data
		country = data.get('country')
		phone_number = data.get('phone_number')
		otp = data.get('otp')
		password = data.get('password')

		if RegistrationOTP.objects.filter(phone_number=phone_number, country=country).exists():
			registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number, country=country).order_by('-created_date').first()

			if str(registrationOtp.otp) == otp:
				registrationOtp.is_verified = "yes"
				registrationOtp.save()

				if UserProfile.objects.filter(phone_number=phone_number, country=country).exists():
					user=UserProfile.objects.filter(phone_number=phone_number, country=country).first().user
					user.set_password(password)
					user.save()
					return Response({"success": "Password has been changed successfully"})
				else:
					return Response({"success": "Please enter valid phone number"})

		raise serializers.ValidationError({"otp":"Please enter valid OTP"})'''

class BrandViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Brand.objects.all()
	serializer_class = BrandSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )

	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		view_type = self.request.query_params.get('type', None)
		if view_type is not None and view_type.lower()=="brandwisediscount":
			serializer_class = BrandDiscountRuleSerializer

		return serializer_class

	def get_queryset(self):
		'''global disableCatalogIds
		global user_group_name
		disableCatalogIds = []
		user_group_name = None'''
		user = self.request.user
		company = get_user_company(user)

		queryset = Brand.objects.all().select_related('company').order_by('name')

		name = self.request.query_params.get('name', None)
		specific_company = self.request.query_params.get('company', None) #for admin user specify company
		mycompany = self.request.query_params.get('mycompany', None)
		brand_i_follow = self.request.query_params.get('brand_i_follow', 'false')
		view_type = self.request.query_params.get('type', None)
		has_catalog = self.request.query_params.get('has_catalog', 'false')
		showAll = self.request.query_params.get('showall', None)


		if name is not None:
			queryset = queryset.filter(name__icontains=name)
			if name != "":
				addSearchQueryLog(user, "name="+name, "brand")

		if specific_company:
			company = specific_company
			#queryset = queryset.filter(company=specific_company)

		if mycompany is not None and mycompany.lower()=="true":
			return queryset.filter(company=company)

		if brand_i_follow.lower() == 'true':
			followed_ids = CompanyBrandFollow.objects.filter(company=company).values_list('brand', flat=True).distinct()
			queryset = queryset.filter(id__in=followed_ids)
			return queryset


		if view_type is not None and view_type.lower()=="my":
			brand_distributor = BrandDistributor.objects.filter(company=company).order_by('brand').values_list('brand', flat=True).distinct()
			return queryset.filter(Q(company=company) | Q(id__in=brand_distributor))

		elif company is None or (view_type is not None and view_type.lower()=="public"): #guest user or publi filter
			#cbids = Catalog.objects.filter(view_permission="public", supplier_disabled=False).values_list('brand', flat=True).distinct()

			dtnow = datetime.now()
			cids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True).distinct()
			# ~ cbids = Product.objects.filter(catalog__view_permission="public", catalog__in=cids).values_list('catalog__brand', flat=True).distinct()
			cbids = Catalog.objects.filter(view_permission="public", id__in=cids, total_products_uploaded__gt=0).values_list('brand', flat=True).distinct()

			#cbids = Product.objects.filter(catalog__view_permission="public", catalog__supplier_disabled=False).values_list('catalog__brand', flat=True).distinct()
			#print "cbids =", list(cbids)
			return queryset.filter(id__in=cbids).order_by('-total_catalog') # has_catalog == true condition doesn't need for public brand
		elif view_type is not None and view_type.lower()=="brandisell":
			brand_distributor = BrandDistributor.objects.filter(company=company).order_by('brand').values_list('brand', flat=True).distinct()
			return queryset.filter(id__in=brand_distributor)
		elif view_type is not None and view_type.lower()=="brandwisediscount":
			dr_brands = DiscountRule.objects.filter(selling_company=company).values_list('brands', flat=True).distinct()
			return queryset.filter(id__in=dr_brands)

		#commented because last if case same as expand true
		'''expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_from is not None:
					company = user.companyuser.deputed_from

				selling_company = Buyer.objects.filter(buying_company=company, status="approved").order_by('selling_company').values_list('selling_company', flat=True).exclude(selling_company__isnull=True).distinct()
				brand_distributor = BrandDistributor.objects.filter(Q(company=company) | Q(company__in=selling_company)).order_by('brand').values_list('brand', flat=True).distinct()

				return queryset.filter(Q(company=company) | Q(company__in=selling_company) | Q(id__in=brand_distributor))#Q(id__in=brand_distributor)
		'''

		disableCatalogIds = getDisableCatalogIds(company)
		selling_company = Buyer.objects.filter(buying_company=company, status="approved").order_by('selling_company').values_list('selling_company', flat=True).exclude(selling_company__isnull=True).distinct()
		sellingBrandsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=selling_company, is_disable=False).exclude(Q(catalog__isnull=True) | Q(catalog__in=disableCatalogIds)).values_list('catalog__brand', flat=True).distinct()

		if has_catalog.lower() == 'true':
			bids = Catalog.objects.filter(company=company).exclude(id__in=disableCatalogIds).values_list('brand', flat=True).distinct()
			cbids = Catalog.objects.filter(view_permission="public", supplier_disabled=False).values_list('brand', flat=True).distinct()
			print "second cbids =", list(cbids)
			print "disableCatalogIds =", list(disableCatalogIds)
			return queryset.filter(Q(id__in=bids) | Q(id__in=sellingBrandsIds) | Q(id__in=cbids))

		brand_distributor = BrandDistributor.objects.filter(Q(company=company)).order_by('brand').values_list('brand', flat=True).distinct()# | Q(company__in=selling_company)

		print "user.is_staff=",user.is_staff
		if user.is_staff or showAll is not None:
			return queryset

		return queryset.filter(Q(company=company) | Q(id__in=sellingBrandsIds) | Q(id__in=brand_distributor))

	'''def get_serializer_context(self):
		global disableCatalogIds
		global user_group_name

		return {'request': self.request, 'disableCatalogIds':disableCatalogIds, 'user_group_name':user_group_name}
		#return {'request': self.request}
	'''

	def perform_create(self, serializer):#add user on create
		user = self.request.user
		#user_company = (user.companyuser.company is not None)
		company = get_user_company(user)

		if company:
			#company = user.companyuser.company
			manufacturerCompany = None
			#if company.company_type=="manufacturer":
			if CompanyType.objects.filter(company=company, manufacturer=True).exists():
				manufacturerCompany=company

			serializer.save(company=company, manufacturer_company=manufacturerCompany, user=user)
		else:
			raise serializers.ValidationError({"error":"Please register your company"})

	'''@detail_route(methods=['GET'])
	def followers(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()

		user = request.user
		company = user.companyuser.company

		jsonarr = []
		if queryset.manufacturer_company == company or queryset.company == company:
			companies = CompanyBrandFollow.objects.filter(brand=queryset).values_list('company', flat=True)

			is_invited_arr = Buyer.objects.filter(selling_company=company, buying_company__in=companies).values_list('buying_company', flat=True)
			#is_connected_arr = Buyer.objects.filter(selling_company=company, buying_company__in=companies, status="approved").values_list('buying_company', flat=True)

			companies_values = Company.objects.filter(id__in=companies).values('id','name','phone_number')
			for company_value in companies_values:
				company_value['is_invited'] = False
				#company_value['is_connected'] = False
				if company_value['id'] in is_invited_arr:
					company_value['is_invited'] = True
				#if company_value['id'] in is_connected_arr:
				#	company_value['is_connected'] = True
				jsonarr.append(company_value)

		return Response(list(jsonarr))'''

	@list_route(methods=['GET'])
	def followers(self, request, companies_pk=None):
		user = request.user
		company = user.companyuser.company

		jsonarr = []

		buyerObjs = Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True)))#.values_list('id', flat=True)

		companies = CompanyBrandFollow.objects.filter(brand__in=buyerObjs).values_list('company', flat=True).distinct()

		is_invited_arr = Buyer.objects.filter(selling_company=company, buying_company__in=companies).order_by('id').values_list('buying_company', flat=True)
		is_invited_arr_ids = Buyer.objects.filter(selling_company=company, buying_company__in=companies).order_by('id').values_list('id', flat=True)
		is_invited_arr = list(is_invited_arr)
		is_invited_arr_ids = list(is_invited_arr_ids)

		companies_values = Company.objects.filter(id__in=companies).values('id','name','phone_number')
		for company_value in companies_values:
			company_value['is_invited'] = False
			company_value['buyer_id'] = None

			if company_value['id'] in is_invited_arr:
				company_value['is_invited'] = True
				isinvindex = is_invited_arr.index(company_value['id'])
				company_value['buyer_id'] = is_invited_arr_ids[isinvindex]

			brandnames = CompanyBrandFollow.objects.filter(brand__in=buyerObjs, company=company_value['id']).values_list('brand__name', flat=True)
			company_value['followed_brand_names'] = ", ".join(brandnames)
			jsonarr.append(company_value)

		return Response(list(jsonarr))

	@list_route(methods=['get'])
	def dropdown(self, request, companies_pk=None):
		queryset = self.get_queryset().values('id','name').order_by('name')
		queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

	@list_route(methods=['post'])
	def has_permission(self, request, companies_pk=None):
		data = request.data
		#brand_id = data['brand']
		brand_id = data.get('brand', None)

		if brand_id is None or not str(brand_id).isdigit():
			raise serializers.ValidationError({"brand":"Brand must be required."})

		user = request.user
		company = get_user_company(user) #user.companyuser.company

		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		bids = Brand.objects.filter(Q(manufacturer_company=company) | Q(company=company)).values_list('id', flat=True)
		bids = list(bids)
		tempbids = BrandDistributor.objects.filter(company=company).values_list('brand', flat=True)
		bids.extend(list(tempbids))
		print bids

		if int(brand_id) in bids:
			return Response({"success": "You have permission for this brand."})
		else:
			raise serializers.ValidationError({"brand":"This brand is not yet on your \"Brand I Sell\" list. Do you want to add this brand and sell this catalog?"})

class BrandDistributorViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = BrandDistributor.objects.all()
	serializer_class = BrandDistributorSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetBrandDistributorSerializer

		return serializer_class

	def get_queryset(self):
		queryset = BrandDistributor.objects.all()#.order_by('name')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return BrandDistributor.objects.none()
		except ObjectDoesNotExist:
			return BrandDistributor.objects.none()

import traceback
class CatalogViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Catalog.objects.filter(deleted=False) #
	serializer_class = CatalogSerializer
	permission_classes = (IsCompanyAdministratorOrAuthenticateUser, )

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'view_permission', )
	#search_fields = ('id', 'view_permission', 'title',)
	pagination_class = CustomPagination

	def retrieve(self, request, pk=None, companies_pk=None):
		try:
			#catalog = Catalog.objects.get(pk=pk)
			catalog = self.queryset.select_related('brand__company', 'brand__user', 'category', 'company').get(pk=pk)
			if catalog:
				serializer = self.get_serializer(catalog)
				return Response(serializer.data)
		except Exception as e:
			logger.info("CatalogViewSet retrieve Exception catalog ID = %s, e = %s"% (pk, traceback.format_exc()))
			if settings.DEBUG==False:
				mail_status = send_mail("CatalogViewSet retrieve Exception", "CatalogViewSet retrieve catalog ID = "+str(pk)+", Exception e = "+str(e)+", traceback Details = "+str(traceback.format_exc()), "tech@wishbook.io", ["tech@wishbook.io"])
			pass

		from rest_framework.status import HTTP_404_NOT_FOUND
		return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetCatalogSerializer

		return serializer_class

	def get_queryset(self):
		user = self.request.user
		company = get_user_company(user) #user.companyuser.company

		queryset = self.queryset

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			queryset = queryset.select_related('brand__company', 'brand__user', 'category', 'company')#.prefetch_related('products')
		else:
			queryset = queryset.select_related('brand', 'category', 'company')#.annotate(max_sort_order=Max('products__sort_order'), min_public_price=Min('products__public_price'), max_public_price=Max('products__public_price'), min_price=Min('products__price'), max_price=Max('products__price')) #annotate is working. we can user these variable in serializer fields.


		#queryset = queryset.select_related('brand__company', 'category', 'company').prefetch_related('products')#.order_by('-id')#'category',
		#print self.request.get_full_path()
		#print self.action
		params = self.request.query_params
		queryset = catalogQuerysetFilter(queryset, company, params, user, self.action)
		# print "queryset ==================4444====", queryset
		return queryset


	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)

		'''gd_client =	OAuth2Login('tech@trivenisarees.com')
		title = self.request.POST.get("title")
		accessSpecifier = 'private'
		album = createAlbum(gd_client, title, accessSpecifier)
		picasa_url = album.GetHtmlLink().href
		picasa_id = album.gphoto_id.text'''
		#picasa_url = ""
		#picasa_id = ""

		if user_company:
			company = user.companyuser.company
			serializer.save(user=user, company=company)#, picasa_url=picasa_url, picasa_id=picasa_id

	def perform_destroy(self, instance):#delete photo from picasa
		if CompanyProductFlat.objects.filter(catalog=instance).exists():
			raise serializers.ValidationError({"catalog":"You can not delete shared catalog"})
		if SalesOrderItem.objects.filter(product__catalog=instance).exists() or CartItem.objects.filter(product__catalog=instance).exists():
			raise serializers.ValidationError({"product":"You can not delete ordered catalog"})
		Product.all_objects.filter(catalog=instance).delete()
		instance.delete()

		#~ if not Push_User.all_objects.filter(catalog=instance.id).exists():
			#~ Product.all_objects.filter(catalog=instance.id).delete()
			#~ instance.delete()
		#~ else:
			#~ raise serializers.ValidationError({"catalog":"Can not delete shared catalog"})

	#def list()

	@list_route(methods=['get'])
	def suggestion(self, request, companies_pk=None):
		q_search = self.request.query_params.get('q', None)
		jsonarr = []
		if q_search:
			q_search = q_search.encode('utf-8')
			#q_search = " ".join(re.split("[^a-zA-Z0-9]*", q_search)).strip()

			from elasticsearch import Elasticsearch
			#from elasticsearch_dsl import Search
			client = Elasticsearch(settings.ELASTICSEARCH_HOST)
			items = client.search(
				index="catalog-index",
				body={
					"size" : 10000,
					"_source": False,
					"suggest": {
						"catalog_suggest" : {
							"prefix" : q_search,
							"completion" : {
								"field" : "catalog_suggest" ,
								"skip_duplicates" : True

							}
						}
					}

				}
			)

			#print items

			for hit in items["suggest"]["catalog_suggest"][0]["options"]:
				jsonarr.append(hit["text"])

		return Response(jsonarr)

	@list_route(methods=['get'])
	def search(self, request, companies_pk=None):
		queryset = self.get_queryset()
		queryset = self.filter_queryset(queryset)

		'''
		q_search = self.request.query_params.get('q', None)

		if q_search:
			q_search = q_search.encode('utf-8')
			q_search = " ".join(re.split("[^a-zA-Z0-9]*", q_search))

			user = self.request.user
			addSearchQueryLog(user, "q="+q_search, "catalog")
			#~ url = 'http://localhost:9200/catalog-index/_search?pretty=true&q='+str(q_search)+"&from="+str(offset)+"&size="+str(limit)


			#final url
			#~ url = "http://localhost:9200/catalog-index/_search?size=10000&default_operator=AND&q=*"+str(q_search)+"*"
			#~ r = requests.get(url)
			#~ items = r.json()

			from elasticsearch import Elasticsearch
			client = Elasticsearch(settings.ELASTICSEARCH_HOST)
			items = client.search(
				index="catalog-index",
				body={
				  "size" : 10000,
				  "query": {
					"query_string": {
						"query": "*"+str(q_search)+"*",
						"default_operator": "and",
						"fuzziness":"AUTO",
					}
				  }
				}
			)

			#~ url = "http://localhost:9200/catalog-index/_search?pretty=true&q=*"+str(q_search)+"*&size=10000"
			#~ jsonarr = {
			  #~ "query": {
				#~ "terms": {
				  #~ "_id": list(queryset.values_list('id', flat=True))
				#~ }
			  #~ }
			#~ }
			#~ print "jsonarr=",jsonarr
			#~ headers = {"Content-Type": "application/json"}
			#~ r = requests.get(url, data=json.dumps(jsonarr), headers=headers)

			elasticarr = []
			for item in items["hits"]["hits"]:
				elasticarr.append(item["_id"])

			#print url
			print "elasticarr=",elasticarr
			print "elasticarr len=",len(elasticarr)

			queryset = queryset.filter(id__in=elasticarr)
		'''

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

	@list_route(methods=['get'], url_path='public/near_me')
	def near_me(self, request, companies_pk=None):
		if not request.GET._mutable:
			request.GET._mutable = True
		self.request.query_params['view_type']='public'
		self.request.query_params['near_me']='true'

		queryset = self.get_queryset()
		queryset = self.filter_queryset(queryset)

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

	@list_route(methods=['GET']) #, permission_classes=[IsCompanyAdministratorOrAdmin]
	def stafdropdown(self, request):
		data = request.GET

		user = request.user

		if user.is_staff:
			queryset = Catalog.objects.filter(deleted=False).values('id','title', 'sell_full_catalog')
		else:
			queryset = Catalog.objects.none()

		view_permission = data.get('view_permission', None)
		if view_permission is not None:
			queryset = queryset.filter(view_permission=view_permission)

		brand = data.get('brand', None)
		if brand is not None:
			queryset = queryset.filter(brand=brand)

		return Response(list(queryset))

	@list_route(methods=['get'])
	def dropdown(self, request, companies_pk=None):
		data = request.GET

		view_type = data.get('view_type', None)
		title = data.get('title', None)
		brand = data.get('brand', None)
		category = data.get('category', None)
		if view_type is not None and title is not None and brand is not None and category is not None:
			#for title unique validation url
			print title, brand
			user = request.user
			company = get_user_company(user)
			queryset = Catalog.objects.filter(Q(title=title, brand=brand) | Q(title=title, company=company)).values('id','title', 'view_permission')
			print "queryset = ", queryset
			return Response(list(queryset))

		queryset = self.get_queryset().values('id','title', 'view_permission')
		queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

	@list_route(methods=['get'])
	def dropdownwithbrand(self, request, companies_pk=None):
		queryset = self.get_queryset().values('id','title', 'brand__name')
		queryset = self.filter_queryset(queryset)

		#ids = queryset.filter(total_products_uploaded__gt=0).values_list('id', flat=True)

		# ~ print "ids="
		# ~ print ids

		# ~ cataloghasproduct = Product.objects.filter(catalog__in=ids).values_list('catalog', flat=True).distinct()
		#print cataloghasproduct

		# ~ queryset = queryset.filter(id__in=cataloghasproduct)
		#queryset = queryset.filter(id__in=ids)
		queryset = queryset.filter(total_products_uploaded__gt=0)

		return Response(list(queryset))

	@detail_route(methods=['GET'])
	def suppliers(self, request, pk=None, companies_pk=None):
		#print "suppliers"
		queryset = self.get_object()
		#print queryset
		companyId = None
		try:
			catalogObj = queryset#Catalog.objects.get(pk=data['catalog'])

			#else:
			currentUser = request.user
			if currentUser.is_authenticated():
				currentUserCompany = currentUser.companyuser.company

				if currentUser.groups.filter(name="salesperson").exists():
					companyId = currentUserCompany.id
				else:
					'''pushUserObjId = Push_User.objects.filter(buying_company=currentUserCompany, catalog=catalogObj.id).values('buying_company','catalog','selling_company').annotate(Max('id')).values('id__max')#user=currentUser
					pushUser = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first()
					companyId = pushUser.selling_company.id'''

					cpfObj = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, is_disable=False, catalog=catalogObj.id).select_related('selling_company').last()
					if cpfObj:
						companyId = cpfObj.selling_company.id
			if companyId is None and catalogObj.view_permission.lower()=="public":
				companyId = catalogObj.company.id

		except Exception as e:
			raise serializers.ValidationError({"selling_company":None})
		return Response({"selling_company": companyId})

	@detail_route(methods=['GET'])
	def all_suppliers(self, request, pk=None, companies_pk=None):
		#print "all_suppliers"
		queryset = self.get_object()

		user = request.user
		company = get_user_company(user) #user.companyuser.company

		jsonarr = []
		if queryset.view_permission.lower()=="public":
			dtnow = datetime.now()
			catalgsellerObjs = CatalogSeller.objects.filter(catalog=queryset, selling_type="Public", status="Enable", expiry_date__gt=dtnow).select_related('selling_company__address__state', 'selling_company__address__city', 'selling_company__chat_admin_user').prefetch_related('selling_company__sellerpolicy_set').order_by('-selling_company__trusted_seller','id')
			for csObj in catalgsellerObjs:
				jsondata = {}
				jsondata['company_id'] = csObj.selling_company.id
				jsondata['name'] = csObj.selling_company.name
				jsondata['chat_user'] = None
				if csObj.selling_company.chat_admin_user:
					jsondata['chat_user'] = csObj.selling_company.chat_admin_user.username
				jsondata['trusted_seller'] = csObj.selling_company.trusted_seller

				jsondata['relation_id'] = None
				buyer_table_id = Buyer.objects.filter(selling_company=csObj.selling_company, buying_company=company, status="approved").values_list('id', flat=True).first()
				if buyer_table_id:
					jsondata['relation_id'] = buyer_table_id

				jsondata['seller_score'] = None
				crObj = CompanyRating.objects.filter(company=csObj.selling_company).first()
				if crObj:
					jsondata['seller_score'] = crObj.seller_score*5

				jsondata['state_name'] = csObj.selling_company.address.state.state_name
				jsondata['city_name'] = csObj.selling_company.address.city.city_name

				serializer = SellerPolicySerializer(instance=csObj.selling_company.sellerpolicy_set.all(), many=True)
				jsondata['seller_policy'] = serializer.data

				jsondata['enquiry_id'] = None
				ceObj = CatalogEnquiry.objects.filter(selling_company=csObj.selling_company, buying_company=company, catalog=queryset).first()
				if ceObj:
					jsondata['enquiry_id'] = ceObj.id

				jsonarr.append(jsondata)

		return Response(jsonarr)

	@detail_route(methods=['GET', 'POST'], permission_classes=[permissions.IsAuthenticated])
	def enable(self, request, pk=None, companies_pk=None):
		data = self.request.data
		expire_date = data.get('expire_date', None)
		logger.info("catalog enable expire_date= %s"% (str(expire_date)))

		user = request.user
		if user.is_staff:
			company = data.get('company', None)
			company = Company.objects.get(pk=company)
		else:
			company = user.companyuser.company
		#print company
		#queryset = self.get_object() ##commented because desable by all supplier can't be enable as queryset not returning any object
		queryset = self.queryset.select_related('brand', 'company').get(pk=pk)

		if queryset.company == company:
			queryset.supplier_disabled = False
			# if expire_date is not None:
			# 	queryset.expiry_date = expire_date
			queryset.save()

		csObjs = CatalogSeller.objects.filter(selling_company=company, catalog=queryset)#.update(status="Enable")
		for csObj in csObjs:
			csObj.status="Enable"
			if expire_date is not None:
				csObj.expiry_date = expire_date
			csObj.save()

		#psObj = CatalogSelectionStatus.objects.get_or_create(company=company, catalog=queryset)
		#psObj = CatalogSelectionStatus.objects.filter(company=company, catalog=queryset).first()
		psObj, created = CatalogSelectionStatus.objects.get_or_create(company=company, catalog=queryset)
		if not user.is_staff:
			psObj.user = user
		psObj.status="Enable"
		psObj.save()

		Push_User.objects.filter(selling_company=company, catalog=queryset).update(supplier_disabled=False)
		Push_User.objects.filter(buying_company=company, catalog=queryset).update(buyer_disabled=False)


		bids = Brand.objects.filter(Q(manufacturer_company=company) | Q(company=company)).values_list('id', flat=True)
		bids = list(bids)
		tempbids = BrandDistributor.objects.filter(company=company).values_list('brand', flat=True)
		bids.extend(list(tempbids))

		if queryset.brand.id not in bids:
			bdObj, created = BrandDistributor.objects.get_or_create(company=company)
			bdObj.brand.add(queryset.brand)
			bdObj.save()

		if queryset.view_permission == "public":
			deleteCache("public")

		return Response({"success": "Catalog has been enable"})

	@detail_route(methods=['GET', 'POST'], permission_classes=[permissions.IsAuthenticated])
	def disable(self, request, pk=None, companies_pk=None):
		data = self.request.data

		user = request.user
		if user.is_staff:
			company = data.get('company', None)
			company = Company.objects.get(pk=company)
		else:
			company = user.companyuser.company
		#print(company)
		queryset = self.get_object()

		csObjs = CatalogSeller.objects.filter(selling_company=company, catalog=queryset)#.update(status="Disable")
		for csObj in csObjs:
			csObj.status="Disable"
			csObj.save()

		#psObj = CatalogSelectionStatus.objects.get_or_create(company=company, catalog=queryset)
		#psObj = CatalogSelectionStatus.objects.filter(company=company, catalog=queryset).first()
		psObj, created = CatalogSelectionStatus.objects.get_or_create(company=company, catalog=queryset)
		if not user.is_staff:
			psObj.user = user
		psObj.status="Disable"
		psObj.save()

		if queryset.company == company:
			queryset.supplier_disabled = True
			queryset.save()
		Push_User.objects.filter(selling_company=company, catalog=queryset).update(supplier_disabled=True)
		Push_User.objects.filter(buying_company=company, catalog=queryset).update(buyer_disabled=True)

		#print Push_User.objects.filter(selling_company=company, catalog=queryset).values_list('supplier_disabled', flat=True)
		#print Push_User.objects.filter(buying_company=company, catalog=queryset).values_list('buyer_disabled', flat=True)

		if queryset.view_permission == "public":
			deleteCache("public")

		return Response({"success": "Catalog has been disabled"})

	@list_route(methods=['get'], url_path='recently-viewed')
	def recently_viewed(self, request, companies_pk=None):
		user = self.request.user
		company = get_user_company(user)

		catalogviewedids = []
		if company is None:
			#print "guest user"
			catalogviewedids = CompanyCatalogView.objects.filter(user=user).order_by('-id').values_list('catalog', flat=True)
		else:
			#print "company found"
			catalogviewedids = CompanyCatalogView.objects.filter(company=company).exclude(catalog__company=company).order_by('-id').values_list('catalog', flat=True)
		#print "catalogviewedids =",catalogviewedids

		if not request.GET._mutable:
			request.GET._mutable = True
		self.request.query_params['view_type']='public'

		queryset = self.get_queryset()
		#queryset = self.filter_queryset(queryset)
		queryset = queryset.filter(id__in=catalogviewedids)

		catalogviewedids = list(catalogviewedids)
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(catalogviewedids)])
		queryset = queryset.order_by(preserved)

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

	@list_route(methods=['get'], url_path='my-viewers')
	def my_viewers(self, request, companies_pk=None):
		# ~ if not request.GET._mutable:
			# ~ request.GET._mutable = True
		# ~ self.request.query_params['view_type']='mycatalogs'

		user = self.request.user
		company = get_user_company(user)

		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		state = company.address.state

		buyerOwnIds = Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True))).values_list('id', flat=True)

		# ~ queryset = self.get_queryset()
		# ~ queryset = self.filter_queryset(queryset)

		disableCatalogIds = getDisableCatalogIds(company)
		cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
		queryset = Catalog.objects.filter(Q(company=company) | Q(id__in=cscatalogids) | Q(brand__in=buyerOwnIds, view_permission="public")).exclude(id__in=disableCatalogIds).order_by('-id')
		#queryset = queryset.exclude(id__in=disableCatalogIds)

		superuser_exclude_companies = CompanyUser.objects.filter(Q(user__is_superuser=True) | Q(user__is_staff=True)).values_list('company', flat=True)
		own_viewed_cids = CompanyCatalogView.objects.filter(catalog__in=queryset, catalog__brand__in=buyerOwnIds).exclude(Q(company=company) | Q(user__is_staff=True) | Q(user__is_superuser=True) | Q(company__in=superuser_exclude_companies)).values_list('catalog', flat=True)
		list_viewed_cids = CompanyCatalogView.objects.filter(Q(catalog__in=queryset) & Q(Q(company__address__state=state) | Q(user__address__state=state))).exclude(Q(catalog__brand__in=buyerOwnIds) | Q(company=company) | Q(user__is_staff=True) | Q(user__is_superuser=True) | Q(company__in=superuser_exclude_companies)).values_list('catalog', flat=True)

		queryset = queryset.filter(Q(id__in=list(own_viewed_cids)) | Q(id__in=list(list_viewed_cids)))

		search = self.request.query_params.get('search', None)
		if search is not None and search != "":
			queryset = queryset.filter(Q(title__icontains=search) | Q(brand__name__icontains=search))


		final_queryset = queryset
		page = self.paginate_queryset(queryset)
		if page is not None:
			final_queryset = page


		jsonarr = []
		for qs in final_queryset:
			jsondata = {}
			jsondata["id"] = qs.id
			jsondata["title"] = qs.title
			jsondata["brand_name"] = qs.brand.name

			jsondata['image'] = {}
			jsondata['image']['thumbnail_small'] = qs.thumbnail.thumbnail[settings.SMALL_IMAGE].url
			jsondata['image']['thumbnail_medium'] = qs.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url

			if qs.brand.id in buyerOwnIds:
				ccvObjs = CompanyCatalogView.objects.filter(catalog=qs).exclude(Q(company=company) | Q(user__is_staff=True) | Q(user__is_superuser=True) | Q(company__in=superuser_exclude_companies))
				jsondata["brand_i_own"] = True
			else:
				ccvObjs = CompanyCatalogView.objects.filter(Q(catalog=qs) & Q(Q(company__address__state=state) | Q(user__address__state=state))).exclude(Q(company=company) | Q(user__is_staff=True) | Q(user__is_superuser=True) | Q(company__in=superuser_exclude_companies))
				jsondata["brand_i_own"] = False

			jsondata["total_viewes"] = ccvObjs.count()
			jsondata["viewers"] = "None" #"Not yet viewed"

			if jsondata["total_viewes"] > 0:
				names = ccvObjs.filter(company__isnull=False).order_by('-id').values_list('company__name', flat=True)[:3]
				pentotal = jsondata["total_viewes"] - len(names)
				#jsondata["viewers"] = "Viewed by "
				jsondata["viewers"] = ""
				jsondata["viewers"] += ", ".join(names)
				if pentotal > 0:
					jsondata["viewers"] += " & "+str(pentotal)+" Other companies"

			jsonarr.append(jsondata)

		return Response(jsonarr)

	@detail_route(methods=['get'], url_path='catalog-viewers')
	def catalog_viewers(self, request, pk=None, companies_pk=None):
		user = self.request.user
		company = get_user_company(user)

		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		state = company.address.state

		buyerOwnIds = Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True))).values_list('id', flat=True)

		disableCatalogIds = getDisableCatalogIds(company)
		cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
		queryset = Catalog.objects.filter(Q(company=company) | Q(id__in=cscatalogids) | Q(brand__in=buyerOwnIds, view_permission="public")).exclude(id__in=disableCatalogIds).order_by('-id')

		queryset = queryset.filter(id=pk).first()
		if queryset is None:
			from rest_framework.status import HTTP_404_NOT_FOUND
			return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

		superuser_exclude_companies = CompanyUser.objects.filter(Q(user__is_superuser=True) | Q(user__is_staff=True)).values_list('company', flat=True)

		brand_i_own = False
		if queryset.brand.id in buyerOwnIds:
			ccvObjs = CompanyCatalogView.objects.filter(catalog=queryset).exclude(Q(company=company) | Q(user__is_staff=True) | Q(user__is_superuser=True) | Q(company__in=superuser_exclude_companies)).order_by('-created_at') #'-company',
			brand_i_own = True
		else:
			ccvObjs = CompanyCatalogView.objects.filter(Q(catalog=queryset) & Q(Q(company__address__state=state) | Q(user__address__state=state))).exclude(Q(company=company) | Q(user__is_staff=True) | Q(user__is_superuser=True) | Q(company__in=superuser_exclude_companies)).order_by('-created_at')

		seconds = self.request.query_params.get('seconds', None)
		if seconds is not None:
			#logger.info("catalog_viewers seconds =%s"% (seconds))
			after_time = datetime.now() - timedelta(seconds=int(seconds))
			#logger.info("catalog_viewers after_time =%s"% (after_time))
			ccvObjs = ccvObjs.filter(created_at__gte=after_time)

		ccvObjs = ccvObjs.select_related('company__address__city', 'user__userprofile')
		ccvObjs = ccvObjs.extra(select={'company_null': 'company_id is null'})
		ccvObjs = ccvObjs.extra(order_by=['company_null', '-created_at'])

		final_queryset = ccvObjs
		page = self.paginate_queryset(ccvObjs)
		if page is not None:
			final_queryset = page

		viewers = []
		for ccvObj in final_queryset:
			viewerjson = {}
			viewerjson['brand_i_own'] = brand_i_own
			viewerjson['created_at'] = ccvObj.created_at
			#print ccvObj.id
			if ccvObj.company:
				viewerjson['company_id'] = ccvObj.company.id
				viewerjson['company_name'] = ccvObj.company.name
				viewerjson['state_name'] = ccvObj.company.address.state.state_name
				viewerjson['city_name'] = ccvObj.company.address.city.city_name
				viewerjson['country'] = ccvObj.company.country.id
				viewerjson['phone_number'] = ccvObj.company.phone_number

				viewerjson['is_manufacturer'] = is_manufacturer(ccvObj.company.company_group_flag)

				viewerjson["connected_as"] = ""
				viewerjson["relationship_id"] = None
				if Buyer.objects.filter(selling_company=company, buying_company=ccvObj.company, status="approved").exists():
					viewerjson["connected_as"]="buyer"
					viewerjson["relationship_id"] = Buyer.objects.filter(selling_company=company, buying_company=ccvObj.company, status="approved").first().id
				elif Buyer.objects.filter(selling_company=ccvObj.company, buying_company=company, status="approved").exists():
					viewerjson["connected_as"]="supplier"
					viewerjson["relationship_id"] = Buyer.objects.filter(selling_company=ccvObj.company, buying_company=company, status="approved").first().id

			else:
				viewerjson['company_id'] = None
				viewerjson['company_name'] = "Guest User"
				address = ccvObj.user.address_set.first()
				if address:
					viewerjson['state_name'] = address.state.state_name
					viewerjson['city_name'] = address.city.city_name
				else:
					viewerjson['state_name'] = ""
					viewerjson['city_name'] = ""

				viewerjson['country'] = ccvObj.user.userprofile.country.id
				viewerjson['phone_number'] = ccvObj.user.userprofile.phone_number


			viewers.append(viewerjson)

		return Response(viewers)

	@list_route(methods=['get'], url_path='my-viewers-live')
	def my_viewers_live(self, request, companies_pk=None):
		user = self.request.user
		company = get_user_company(user)

		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		state = company.address.state

		buyerOwnIds = Brand.objects.filter(Q(manufacturer_company=company) | Q(Q(company=company) & Q(manufacturer_company__isnull=True))).values_list('id', flat=True)

		disableCatalogIds = getDisableCatalogIds(company)
		cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
		queryset = Catalog.objects.filter(Q(company=company) | Q(id__in=cscatalogids) | Q(brand__in=buyerOwnIds, view_permission="public")).exclude(id__in=disableCatalogIds).order_by('-id')


		seconds = self.request.query_params.get('seconds', None)
		if seconds is not None:
			#logger.info("my_viewers_live seconds =%s"% (seconds))
			after_time = datetime.now() - timedelta(seconds=int(seconds))
			#logger.info("my_viewers_live after_time =%s"% (after_time))

			own_viewed_cids = CompanyCatalogView.objects.filter(catalog__in=queryset, catalog__brand__in=buyerOwnIds, created_at__gte=after_time).values_list('id', flat=True)
			list_viewed_cids = CompanyCatalogView.objects.filter(Q(catalog__in=queryset) & Q(created_at__gte=after_time) & Q(Q(company__address__state=state) | Q(user__address__state=state))).values_list('id', flat=True)
		else:
			own_viewed_cids = CompanyCatalogView.objects.filter(catalog__in=queryset, catalog__brand__in=buyerOwnIds).values_list('id', flat=True)
			list_viewed_cids = CompanyCatalogView.objects.filter(Q(catalog__in=queryset) & Q(Q(company__address__state=state) | Q(user__address__state=state))).values_list('id', flat=True)

		superuser_exclude_companies = CompanyUser.objects.filter(Q(user__is_superuser=True) | Q(user__is_staff=True)).values_list('company', flat=True)
		ccvObjs = CompanyCatalogView.objects.filter(Q(id__in=own_viewed_cids) | Q(id__in=list_viewed_cids)).exclude(Q(company=company) | Q(user__is_staff=True) | Q(user__is_superuser=True) | Q(company__in=superuser_exclude_companies)).select_related('catalog', 'company__address__city', 'user').order_by('-created_at')

		final_queryset = ccvObjs
		page = self.paginate_queryset(ccvObjs)
		if page is not None:
			final_queryset = page

		viewers = []
		for ccvObj in final_queryset:
			viewerjson = {}
			#print ccvObj.id
			viewerjson['catalog_id'] = ccvObj.catalog.id
			viewerjson['catalog_title'] = ccvObj.catalog.title
			viewerjson['catalog_image'] = ccvObj.catalog.thumbnail.thumbnail[settings.SMALL_IMAGE].url
			viewerjson['created_at'] = ccvObj.created_at

			if ccvObj.company:
				viewerjson['company_id'] = ccvObj.company.id
				viewerjson['company_name'] = ccvObj.company.name
				viewerjson['state_name'] = ccvObj.company.address.state.state_name
				viewerjson['city_name'] = ccvObj.company.address.city.city_name
				#~ viewerjson['country'] = ccvObj.company.country.id
				#~ viewerjson['phone_number'] = ccvObj.company.phone_number

				#~ viewerjson["connected_as"] = ""
				#~ viewerjson["relationship_id"] = None
				#~ if Buyer.objects.filter(selling_company=company, buying_company=ccvObj.company, status="approved").exists():
					#~ viewerjson["connected_as"]="buyer"
					#~ viewerjson["relationship_id"] = Buyer.objects.filter(selling_company=company, buying_company=ccvObj.company, status="approved").first().id
				#~ elif Buyer.objects.filter(selling_company=ccvObj.company, buying_company=company, status="approved").exists():
					#~ viewerjson["connected_as"]="supplier"
					#~ viewerjson["relationship_id"] = Buyer.objects.filter(selling_company=ccvObj.company, buying_company=company, status="approved").first().id

			else:
				viewerjson['company_id'] = None
				viewerjson['company_name'] = "Guest User"
				address = ccvObj.user.address_set.first()
				if address:
					viewerjson['state_name'] = address.state.state_name
					viewerjson['city_name'] = address.city.city_name
				else:
					viewerjson['state_name'] = ""
					viewerjson['city_name'] = ""

				#~ viewerjson['country'] = ccvObj.user.userprofile.country.id
				#~ viewerjson['phone_number'] = ccvObj.user.userprofile.phone_number


			viewers.append(viewerjson)

		return Response(viewers)


	# ~ def retrieve(self, request, pk=None, companies_pk=None):
		# ~ user = request.user

		# ~ if not user.is_authenticated():
			# ~ from rest_framework.status import HTTP_404_NOT_FOUND
			# ~ return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

		# ~ catalog = self.get_object()

		# ~ company = get_user_company(user)
		# ~ if company and company != catalog.company:
			# ~ if CompanyCatalogView.objects.filter(company=company, catalog=catalog, catalog_type=catalog.view_permission).count() > 0:
				# ~ ccvObj = CompanyCatalogView.objects.filter(company=company, catalog=catalog, catalog_type=catalog.view_permission).first()
				# ~ ccvObj.created_at=datetime.now()
				# ~ ccvObj.clicks += 1
				# ~ ccvObj.save()
			# ~ else:
				# ~ ccvObj, created = CompanyCatalogView.objects.get_or_create(company=company, catalog=catalog, catalog_type=catalog.view_permission)
		# ~ elif company is None and user:
			# ~ if CompanyCatalogView.objects.filter(user=user, catalog=catalog, catalog_type=catalog.view_permission).count() > 0:
				# ~ ccvObj = CompanyCatalogView.objects.filter(user=user, catalog=catalog, catalog_type=catalog.view_permission).first()
				# ~ ccvObj.created_at=datetime.now()
				# ~ ccvObj.clicks += 1
				# ~ ccvObj.save()
			# ~ else:
				# ~ ccvObj, created = CompanyCatalogView.objects.get_or_create(user=user, catalog=catalog, catalog_type=catalog.view_permission)

		# ~ serializer = self.get_serializer(catalog)
		# ~ return Response(serializer.data)

from eav.models import *
class ProductViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnlyProductObj, )

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'catalog', 'fabric', 'work', 'sku', 'title', )
	search_fields = ('id', 'catalog__id', 'fabric', 'work', 'sku', 'title', )

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetProductSerializer

		#if self.request.method == 'GET':
		#		serializer_class = GetProductSerializer
		return serializer_class

	def get_queryset(self):
		queryset = self.queryset
		#queryset = Product.objects.all().prefetch_related('catalog__brand', 'catalog__company').order_by('-id')
		queryset = queryset.prefetch_related('catalog__brand', 'catalog__company').order_by('-id')

		barcode = self.request.query_params.get('barcode', None)
		if barcode is not None:
			product_ids = Barcode.objects.filter(barcode=barcode).values_list('product', flat=True)
			queryset = queryset.filter(id__in=product_ids)

		warehouse = self.request.query_params.get('warehouse', None)
		if warehouse is not None:
			product_ids = Barcode.objects.filter(warehouse=warehouse).values_list('product', flat=True)
			queryset = queryset.filter(id__in=product_ids)

		selection = self.request.query_params.get('selection', None)

		user = self.request.user

		try:
			if (user.companyuser is not None): #user.is_authenticated() and
				company = user.companyuser.company

				if selection is not None:

					if Selection.objects.filter(user=user, id=selection).exists():
						ProductId = Selection.objects.filter(user=user, id=selection).values_list('products').distinct()
						return queryset.filter(id__in=ProductId).distinct().order_by('-catalog','sort_order','id')
					else:
						sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
						productsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, is_disable=False, selection=selection).values_list('product', flat=True)

						return queryset.filter(id__in=productsIds).distinct().order_by('-catalog','sort_order','id')
				return queryset.order_by('-catalog','sort_order','id')
			else:
				return Product.objects.none()

		except ObjectDoesNotExist:
			return Product.objects.none()

	@list_route(methods=['GET', 'POST'])
	def eavfields(self, request):
		data = request.GET
		category = data.get('category', None)

		if category is None:
			raise serializers.ValidationError({"category":"please pass category parameter"})

		ceaObjs = CategoryEavAttribute.objects.filter(category=category)#.values_list('attribute', flat=True)

		jsonarr = []
		for cea in ceaObjs:
			jsonvalue = {}
			jsonvalue['is_required'] = cea.is_required
			jsonvalue['name'] = cea.attribute.name
			jsonvalue['type'] = cea.attribute.datatype

			if cea.attribute.enum_group:
				valuearr = []
				for enumvalue in cea.attribute.enum_group.enums.all():
					valuearr.append(enumvalue.value)
				jsonvalue['values'] = valuearr

			jsonarr.append(jsonvalue)

		return Response(jsonarr)

	def perform_destroy(self, instance):#delete photo from picasa
		#if not Push_User_Product.all_objects.filter(product=instance.id).exists():
		if CompanyProductFlat.objects.filter(product=instance.id).exists():
			raise serializers.ValidationError({"Product":"You can not delete shared product"})
		if SalesOrderItem.objects.filter(product=instance).exists() or CartItem.objects.filter(product=instance).exists():
			raise serializers.ValidationError({"Product":"You can not delete ordered product"})
		instance.delete()
		#~ if not CompanyProductFlat.objects.filter(product=instance.id).exists():
			#~ instance.delete()
		#~ else:
			#~ raise serializers.ValidationError({"Product":"Can not delete shared product"})

	@detail_route(methods=['GET', 'POST'])
	def enable(self, request, pk=None, catalogs_pk=None):
		user = request.user
		company = user.companyuser.company

		queryset = self.get_object()

		psObj = ProductStatus.objects.get_or_create(company=company, product=queryset)
		psObj = ProductStatus.objects.filter(company=company, product=queryset).first()
		psObj.user = user
		psObj.status="Enable"
		psObj.save()

		set_total_products_uploaded(psObj.product.catalog)

		return Response({"success": "Product has been enable"})

	@detail_route(methods=['GET', 'POST'])
	def disable(self, request, pk=None, catalogs_pk=None):
		user = request.user
		company = user.companyuser.company

		queryset = self.get_object()

		psObj = ProductStatus.objects.get_or_create(company=company, product=queryset)
		psObj = ProductStatus.objects.filter(company=company, product=queryset).first()
		psObj.user = user
		psObj.status="Disable"
		psObj.save()

		set_total_products_uploaded(psObj.product.catalog)

		return Response({"success": "Product has been disabled"})

	def list(self, request, catalogs_pk=None):

		if catalogs_pk is not None:
			instance = self.get_queryset().filter(catalog=catalogs_pk)
		else:
			instance = self.get_queryset()

		instance = self.filter_queryset(instance)
		serializer = self.get_serializer(instance, many=True)
		return Response(serializer.data)

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

	@list_route(methods=['get'])
	def dropdown(self, request, catalogs_pk=None):
		queryset = self.get_queryset().values('id','title', 'sku')
		queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

	'''def retrieve(self, request, pk=None, companies_pk=None):
		product = self.get_object()

		user = request.user
		company = user.companyuser.company
		cpvObj, created = CompanyProductView.objects.get_or_create(company=company, product=product)

		serializer = self.get_serializer(product)
		return Response(serializer.data)'''



class BuyerViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Buyer.objects.all()
	serializer_class = BuyerSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnlyBuyerSellerObj, )

	#paginate_by = 2
	#pagination_class = 'rest_framework.pagination.LimitOffsetPagination'
	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		#if self.request.method in ('PUT','PATCH'):
		#	serializer_class = BuyerSerializer
		if self.request.method in ('GET'):
			serializer_class = GetBuyerDetailSerializer

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetBuyerSerializer

		return serializer_class

	def get_queryset(self):
		user = self.request.user

		queryset = Buyer.objects.all().select_related('buying_company__chat_admin_user', 'invitee__invite', 'invitee__country', 'group_type').prefetch_related('buying_company__branches__city__state', 'buying_company__branches__state').order_by('-id')

		status = self.request.query_params.get('status', None)
		if status is not None:
			if status.lower() == "pending":
				queryset = queryset.filter(status__in=['buyer_pending','supplier_pending', 'buyer_registrationpending', 'supplier_registrationpending', 'Pending References', 'References Filled']).exclude(buyer_type="Enquiry")
			elif status.lower() == "rejected":
				queryset = queryset.filter(status__in=['rejected', 'Transferred'])
			elif status.lower() == "enquiry":
				queryset = queryset.filter(buyer_type="Enquiry")#.exclude(status='Transferred')
			elif status.lower() == "created_enquiry":
				queryset = queryset.filter(created_type="Enquiry", buyer_type="Relationship")
			elif status.lower() == "relationship":
				queryset = queryset.filter(buyer_type="Relationship")
			else:
				queryset = queryset.filter(status=status)

		buyer_status = self.request.query_params.get('buyer_status', None)
		if buyer_status is not None:
			buyer_status = buyer_status.split(",")
			buyer_status = list(buyer_status)
			print buyer_status

			queryset = queryset.filter(status__in=buyer_status)


		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(buying_company=company)

		company_name = self.request.query_params.get('company_name', None)
		if company_name is not None:
			queryset = queryset.filter(Q(buying_company__name=company_name) | Q(invitee__invitee_name=company_name))

		phone_number = self.request.query_params.get('phone_number', None)
		if phone_number is not None:
			queryset = queryset.filter(Q(buying_company__phone_number=phone_number) | Q(invitee__invitee_number=phone_number))

		search = self.request.query_params.get('search', None)
		if search is not None:
			queryset = queryset.filter(Q(buying_person_name__icontains=search) | Q(buying_company_name__icontains=search) | Q(buying_company__name__icontains=search) | Q(buying_company__phone_number__icontains=search) | (Q(buying_company__isnull=True) & (Q(invitee__invitee_name__icontains=search) | Q(invitee__invitee_number__icontains=search))))
			if search != "":
				addSearchQueryLog(user, "search="+search, "buyer")

		state = self.request.query_params.get('state', None)
		if state is not None:
			queryset = queryset.filter(buying_company__state=state)

		city = self.request.query_params.get('city', None)
		if city is not None:
			queryset = queryset.filter(buying_company__city=city)

		buyerSegmentation = self.request.query_params.get('buyer_segmentation', None)

		without_deputed = self.request.query_params.get('without_deputed', 'false')

		selling_company = self.request.query_params.get('selling_company', None)

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:#use_deputed is not None and use_deputed == "true" and
					if without_deputed.lower() == 'true':
						company = user.companyuser.company
					else:
						company = user.companyuser.deputed_to
				else:
					company = user.companyuser.company

				if user.groups.filter(name="salesperson").exists() and company.buyers_assigned_to_salesman == True:
					#buyers = BuyerSalesmen.objects.filter(salesman=user).values_list('buyers', flat=True)
					if AssignGroups.objects.filter(user=user).exists():
						agObj = AssignGroups.objects.get(user=user)
						'''buyers = agObj.groups.filter(buyer_grouping_type="Custom").values_list('buyers', flat=True)
						buyers = list(buyers)'''
						buyers = getSegmentationsBuyers(agObj.groups.all(), company)
						queryset = queryset.filter(buying_company__in = buyers)

				if buyerSegmentation is not None:
					buyer_segmentation = BuyerSegmentation.objects.get(pk=buyerSegmentation)

					'''city = buyer_segmentation.city.values_list('id', flat=True)
					category = buyer_segmentation.category.values_list('id', flat=True)
					group_type = buyer_segmentation.group_type.values_list('id', flat=True)'''

					if buyer_segmentation.buyer_grouping_type == "Location Wise":
						group_type = buyer_segmentation.group_type.values_list('id', flat=True)
						if buyer_segmentation.city.count() == 0:
							city = City.objects.all().values_list('id', flat=True)
						else:
							city = buyer_segmentation.city.values_list('id', flat=True)
						if buyer_segmentation.category.count() == 0:
							category = Category.objects.all().values_list('id', flat=True)
						else:
							category = buyer_segmentation.category.values_list('id', flat=True)

						queryset = queryset.filter(Q(status='approved', buying_company__city__in=city, buying_company__category__in=category, group_type__in=group_type) | Q(buying_company__in=buyer_segmentation.buyers.all())).distinct()
					else:
						queryset = queryset.filter(buying_company__in=buyer_segmentation.buyers.all()).distinct()

				if selling_company is not None:
					sellers_buying_companies = Buyer.objects.filter(selling_company=selling_company, broker_company=company).values_list('buying_company', flat=True)
					print sellers_buying_companies
					queryset = queryset.filter(buying_company__in=sellers_buying_companies)

					queryset = queryset.filter(selling_company=selling_company)
				else:
					queryset = queryset.filter(selling_company=company)

					#added by jay
				if company.id == 229 and user.groups.filter(name="salesperson").exists() and queryset.count() == 0:
					queryset = Buyer.objects.filter(selling_company=company, status="approved")[:1]

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

	def create(self, request, companies_pk=None):
		loginUser = request.user

		loginCompany = get_user_company(loginUser) #loginUser.companyuser.company
		#companyName = loginCompany.name

		if loginCompany is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		content_type = request.META.get('CONTENT_TYPE')

		print content_type
		if "multipart/form-data" in content_type:
			logger.info("content_type if multipart/form-data")
			f = request.FILES['buyer_csv[0]']

			upload_file=f
			jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Buyer", upload_file=upload_file, status="Created", action_note="company_registration")
			print jobsObj

			filetype = f.content_type
			supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
			logger.info(str(filetype))
			#if "csv" not in str(filetype):
			if str(filetype) not in supportcontenttype:
				jobsObj.error_details = "Please upload CSV file only"
				jobsObj.save()
				raise serializers.ValidationError({"File":"Please upload CSV file only"})

			fileObject = csv.reader(upload_file)
			row_count = sum(1 for row in fileObject)
			jobsObj.total_rows = (row_count-1)
			jobsObj.status = "Scheduled"
			jobsObj.save()

			if settings.TASK_QUEUE_METHOD == 'celery':
				task_id = buyerCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
					'api.tasks.buyerCSVImportJobs',
					jobsObj.id,
					broker = priority_broker
				)
			logger.info("buyer csv task_id = ")
			logger.info(str(task_id))
			return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})
		else:
			print "content_type else"
			data = request.data

			if data.get('buyer_name', None) is None or data.get('buyer_number', None) is None or data.get('group_type', None) is None or data.get('country', None) is None:
				raise serializers.ValidationError({"error":"Please enter valid data"})

			buyer_name=data['buyer_name']
			buyer_number=str(data['buyer_number'])[-10:]

			if int(buyer_number[0]) in [0,1,2,3,4,5]:
				raise serializers.ValidationError({"buyer_number":"Mobile number is not valid : "+str(buyer_number)})

			group_type = GroupType.objects.get(pk=data['group_type'])

			if data.get('country', None) is not None:
				country = Country.objects.get(pk=data['country'])
			else:
				country = Country.objects.get(pk=1)

			#buyingcompany = add_buyer(loginUser, loginCompany, buyer_name, country, buyer_number, group_type, True);
			#return Response({"success": "Buyer request has been sent to " + buyingcompany.name + " successfully"})
			buyingcompany = add_buyer_v1(loginUser, loginCompany, buyer_name, country, buyer_number, group_type, True);
			buyingcompany = buyingcompany[0]
			if buyingcompany is None:
				return Response({"success": "Buyer request has been sent successfully"})
			else:
				return Response({"success": "Buyer request has been sent to " + buyingcompany.name + " successfully"})

	@list_route(methods=['get'])
	def statewise(self, request, companies_pk=None):
		data = request.data

		user = request.user
		company = user.companyuser.company

		arraydata = []

		stateList = Buyer.objects.filter(selling_company=company, buying_company__isnull=False, status="approved").values_list('buying_company__state', flat=True).distinct()
		stateObj = State.objects.filter(id__in=stateList)

		for state in stateObj:
			jsondata = {}
			jsondata["state"] = state.state_name
			jsondata["state_id"] = state.id

			jsondata["total_buyers"] = Buyer.objects.filter(selling_company=company, buying_company__isnull=False, status="approved", buying_company__state=state).count()

			cities = []
			jsondata["cities"] = cities

			cityList = Buyer.objects.filter(selling_company=company, buying_company__isnull=False, status="approved", buying_company__state=state).values_list('buying_company__city', flat=True).distinct()
			cityObj = City.objects.filter(id__in=cityList)

			for city in cityObj:
				jsoncity = {}
				jsoncity["name"] = city.city_name
				jsoncity["id"] = city.id

				buyerObj = Buyer.objects.filter(selling_company=company, buying_company__isnull=False, status="approved", buying_company__state=state, buying_company__city=city).values("id","buying_company__id","buying_company__name").distinct().order_by('buying_company__name')
				#serializer = GetBuyerOnlySerializer(instance=buyerObj, many=True)
				jsoncity["buyers"] = list(buyerObj)#serializer.data



				cities.append(jsoncity)


			arraydata.append(jsondata)

		return Response(arraydata)

	@list_route(methods=['get'])
	def dropdown(self, request, companies_pk=None):
		user = request.user
		company = get_user_company(user) #user.companyuser.company

		state = self.request.query_params.get('state', None)
		city = self.request.query_params.get('city', None)
		#added by jay
		if company and company.id == 229 and user.groups.filter(name="salesperson").exists() : #245: #229:
			array = []
			if state and city:#only for wishbook support company
				print "return all company"

				queryset = Company.objects.filter(address__state=state, address__city=city)
				for b in queryset:
					#~ buyerObj = Buyer.objects.filter(selling_company=company, buying_company=b).last()

					#~ buying_person_name = b.name
					#~ buying_company_name = b.name
					#~ bid = None
					#~ if buyerObj:
						#~ buying_person_name = buyerObj.buying_person_name
						#~ if buying_person_name == "":
							#~ buying_person_name = b.name

						#~ buying_company_name = buyerObj.buying_company_name
						#~ if buying_company_name == "":
							#~ buying_company_name = b.name

						#~ bid = buyerObj.id

					#~ array.append({"id":bid,"company_id":b.id,"company_name":b.name, "broker_id":None, "phone_number":b.phone_number, "buying_person_name":buying_person_name, "buying_company_name":buying_company_name})
					array.append({"id":b.id,"company_id":b.id,"company_name":b.name, "broker_id":None, "phone_number":b.phone_number, "buying_person_name":b.name, "buying_company_name":b.name})

				return Response(array)
			#elif state:
			#	return Response(array)
			else:
				raise serializers.ValidationError({"please_note":"Must select state and city"})

		#inventoryUpdateFromServer(companies_pk)
		queryset = self.get_queryset().filter(status="approved").exclude(buying_company__isnull=True).select_related('buying_company', 'broker_company').order_by('buying_company_name')
		queryset = self.filter_queryset(queryset)
		array = []
		for b in queryset:
			broker = None
			if b.broker_company is not None:
				broker = b.broker_company.id
			'''if b.buying_company.city.city_name != "-" and b.buying_company.state.state_name != "-":
				company_name = b.buying_company.name+", "+b.buying_company.city.city_name+", "+b.buying_company.state.state_name
			else:
				company_name = b.buying_company.name'''

			if b.buying_company_name is not None and b.buying_person_name is not None:
				if b.buying_person_name.title() != b.buying_company_name.title():
					company_name = b.buying_person_name.title()+" ("+b.buying_company_name.title()+")"
				else:
					company_name = b.buying_person_name.title()
			else:
				company_name = b.buying_company.name

			buying_person_name = b.buying_person_name
			if buying_person_name == "":
				buying_person_name = b.buying_company.name

			buying_company_name = b.buying_company_name
			if buying_company_name == "":
				buying_company_name = b.buying_company.name
			'''if b.invitee:
				if b.invitee.invitee_name.title() != b.buying_company.name.title() and b.invitee.invitation_type == "Buyer":
					company_name = b.invitee.invitee_name.title()+", "+b.buying_company.name.title()'''
			array.append({"id":b.id,"company_id":b.buying_company.id,"company_name":company_name, "broker_id":broker, "phone_number":b.buying_company.phone_number, "buying_person_name":buying_person_name, "buying_company_name":buying_company_name})

		return Response(array)

	@list_route(methods=['post'])
	def resend(self, request, companies_pk=None):
		data = request.data
		buyers = data.get('buyers', None)

		if buyers is not None:
			user = request.user
			company = user.companyuser.company

			for buyer in buyers:
				buyerObj = Buyer.objects.get(pk=buyer)

				if buyerObj.status.lower() == "buyer_registrationpending":
					sendInvite(buyerObj.invitee.country.phone_code+buyerObj.invitee.invitee_number, str(company.name))
				elif buyerObj.status.lower() == "buyer_pending":
					requestNotification(buyerObj.selling_company, buyerObj.buying_company.country.phone_code+buyerObj.buying_company.phone_number, "buyer", buyerObj, buyerObj.buying_company, buyerObj.status)

		return Response({"success": "Buyer request has been resent successfully"})

	@detail_route(methods=['POST'])
	def transfer(self, request, pk=None, companies_pk=None):
		user = request.user
		#company = user.companyuser.company

		data = request.data
		sc = data.get('selling_company')
		print sc
		if isinstance(sc, list):
			sc = sc[0]
		print sc
		oldobj = self.get_object()

		obj = self.get_object()

		if Buyer.objects.filter(selling_company=Company.objects.get(pk=sc), buying_company=obj.buying_company).exists():
			raise serializers.ValidationError({"error":"This Suplier has already relation with this buyer."})

		Buyer.objects.create(selling_company=Company.objects.get(pk=sc), buying_company=obj.buying_company, status="supplier_pending", invitee=obj.invitee, buyer_approval=True, buyer_type="Enquiry", created_type="Enquiry", details=obj.details, user=user, enquiry_catalog=obj.enquiry_catalog, buying_company_name=obj.buying_company.name, buying_person_name=obj.buying_company.name)

		'''obj.selling_company = Company.objects.get(pk=sc)
		obj.pk = None
		obj.save()'''

		newjson = {}
		newjson['transfer_id'] = int(obj.id)

		try:
			details = oldobj.details
			details = details.replace("u'", '"')
			details = details.replace("'", '"')
			details = json.loads(details)
			print details
			newjson['catalog'] = details["catalog"]
		except Exception as e:
			logger.info("in transfer(): except Exception as e:")
			logger.info(str(e))
			pass
		#print newjson

		oldobj.status = "Transferred"
		oldobj.details = newjson
		oldobj.save()

		return Response({"success": "Buyer has been transfered."})

	@detail_route(methods=['POST'])
	def add_suppliers(self, request, pk=None, companies_pk=None):
		loginUser = request.user
		loginCompany = loginUser.companyuser.company

		queryset = self.get_object()

		broker = None
		if loginCompany.company_group_flag.broker:
			broker = loginCompany

		data = request.data
		logger.info("add_suppliers data= %s"% (str(data)))

		selling_companies_ids = data.get('selling_companies')
		selling_companies_ids = list(selling_companies_ids)
		print selling_companies_ids
		selling_companies = Company.objects.filter(id__in=selling_companies_ids)

		group_type = GroupType.objects.filter(name="Wholesaler").first()

		buying_user = queryset.buying_company.chat_admin_user

		for selling_company in selling_companies:
			if not Buyer.objects.filter(selling_company = selling_company, buying_company = queryset.buying_company).exists():
				inviteobj = Invite.objects.create(relationship_type="supplier", company=queryset.buying_company ,user=buying_user)
				inviteeObj = Invitee.objects.create(invitee_company=selling_company.name,invitee_name=selling_company.name,country=selling_company.country,invitee_number=selling_company.phone_number,invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Supplier")

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

				buyer = Buyer.objects.create(selling_company = selling_company, buying_company = queryset.buying_company, status=status, group_type=group_type, invitee=inviteeObj, user=buying_user, buying_company_name=queryset.buying_company.name, buying_person_name=queryset.buying_company.name, discount=discount, cash_discount=cash_discount, credit_limit=credit_limit, payment_duration=payment_duration, broker_company=broker, supplier_person_name=selling_company.name)
				requestNotification(queryset.buying_company, selling_company.country.phone_code+selling_company.phone_number, "supplier", buyer, selling_company, status)
			else:
				Buyer.objects.filter(selling_company = selling_company, buying_company = queryset.buying_company).update(broker_company=broker)

			rno = random.randrange(100000, 999999, 1)
			jsonarr = {}
			jsonarr['broker_name'] = loginCompany.name
			jsonarr['supplier_name'] = selling_company.name
			jsonarr['notId'] = rno
			user1 = CompanyUser.objects.filter(company=queryset.buying_company).values_list('user', flat=True)
			user1 = User.objects.filter(id__in=user1, groups__name="administrator")
			sendAllTypesMessage("add_suppliers_broker", user1, jsonarr)

		return Response({"success": "Suppliers added successfully."})

	@detail_route(methods=['POST'])
	def remove_suppliers(self, request, pk=None, companies_pk=None):
		loginUser = request.user
		loginCompany = loginUser.companyuser.company

		queryset = self.get_object()

		data = request.data
		logger.info("remove_suppliers data= %s"% (str(data)))

		selling_companies_ids = data.get('selling_companies')
		selling_companies_ids = list(selling_companies_ids)
		print selling_companies_ids

		Buyer.objects.filter(buying_company = queryset.buying_company, selling_company__in = selling_companies_ids).update(broker_company=None, brokerage_fees=Decimal('0.00'))

		return Response({"success": "Suppliers removed successfully."})

	@detail_route(methods=['GET'])
	def suggested_brokers(self, request, pk=None, companies_pk=None):
		loginUser = request.user
		loginCompany = loginUser.companyuser.company

		queryset = self.get_object()

		suppliers_brokers = Buyer.objects.filter(selling_company=queryset.selling_company, status="approved", group_type__name="Broker").exclude(buying_company=queryset.buying_company).values_list('buying_company',flat=True)

		buyers_suppliers = Buyer.objects.filter(buying_company=queryset.buying_company, status="approved").exclude(selling_company=queryset.selling_company).values_list('selling_company',flat=True)
		buyers_suppliers_brokers = CompanyType.objects.filter(company__in=buyers_suppliers, broker=True).values_list('company', flat=True)
		buyers_suppliers_brokers_set = set(buyers_suppliers_brokers)

		print suppliers_brokers
		print buyers_suppliers_brokers_set

		results = [x for x in suppliers_brokers if x in buyers_suppliers_brokers_set]

		print "results=",results
		results.extend(buyers_suppliers_brokers_set)
		print results
		results = getUniqueItems(list(results))
		print results

		json_arr = []

		for result in results:
			company = Company.objects.get(pk=result)
			jsonval = {}
			jsonval['company'] = result
			jsonval['company_name'] = company.name
			jsonval['company_phone_number'] = company.phone_number
			jsonval['company_chat_user'] = company.chat_admin_user.username

			jsonval['buying_company_name'] = company.name
			jsonval['buyer_id'] = None

			buyerObj = Buyer.objects.filter(selling_company=queryset.selling_company, status="approved", group_type__name="Broker", buying_company=result).last()
			if buyerObj:
				jsonval['buying_company_name'] = buyerObj.buying_company_name
				jsonval['buyer_id'] = buyerObj.id

			json_arr.append(jsonval)

		return Response(json_arr)

class SupplierViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Buyer.objects.all()
	serializer_class = SupplierSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnlyBuyerSellerObj, )

	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		#if self.request.method in ('PUT','PATCH'):
		#	serializer_class = SupplierSerializer

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetSupplierSerializer
		#if self.request.method == 'GET':
		#	serializer_class = GetSupplierSerializer
		return serializer_class
	def get_queryset(self):
		user = self.request.user

		queryset = Buyer.objects.all().select_related('selling_company__chat_admin_user', 'invitee__invite', 'invitee__country', 'group_type').prefetch_related('selling_company__branches__city__state', 'selling_company__branches__state').order_by('-id')

		status = self.request.query_params.get('status', None)
		if status is not None:
			if status.lower() == "pending":
				queryset = queryset.filter(status__in=['buyer_pending','supplier_pending', 'buyer_registrationpending', 'supplier_registrationpending', 'Pending References', 'References Filled']).exclude(buyer_type="Enquiry")
			elif status.lower() == "rejected":
				queryset = queryset.filter(status__in=['rejected', 'Transferred'])
			elif status.lower() == "enquiry":
				queryset = queryset.filter(buyer_type="Enquiry")#.exclude(status='Transferred')
			elif status.lower() == "created_enquiry" and user.userprofile.last_login_platform == "iOS":
				queryset = queryset.filter(buyer_type="Enquiry")
			elif status.lower() == "created_enquiry":
				queryset = queryset.filter(created_type="Enquiry", buyer_type="Relationship")
			elif status.lower() == "relationship":
				queryset = queryset.filter(buyer_type="Relationship")
			else:
				queryset = queryset.filter(status=status)

		supplier_status = self.request.query_params.get('supplier_status', None)
		if supplier_status is not None:
			supplier_status = supplier_status.split(",")
			supplier_status = list(supplier_status)
			print supplier_status

			queryset = queryset.filter(status__in=supplier_status)

		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(selling_company=company)

		company_name = self.request.query_params.get('company_name', None)
		if company_name is not None:
			queryset = queryset.filter(Q(selling_company__name=company_name) | Q(invitee__invitee_name=company_name))

		phone_number = self.request.query_params.get('phone_number', None)
		if phone_number is not None:
			queryset = queryset.filter(Q(selling_company__phone_number=phone_number) | Q(invitee__invitee_number=phone_number))

		search = self.request.query_params.get('search', None)
		if search is not None:
			#queryset = queryset.filter(Q(status__icontains=search) | Q(selling_company__name__icontains=search) | Q(invitee__invitee_name__icontains=search) | Q(selling_company__phone_number__icontains=search) | Q(invitee__invitee_number__icontains=search))
			queryset = queryset.filter(Q(supplier_person_name__icontains=search) | Q(selling_company__name__icontains=search) | Q(selling_company__phone_number__icontains=search) | (Q(selling_company__isnull=True) & (Q(invitee__invitee_name__icontains=search) | Q(invitee__invitee_number__icontains=search))))
			if search != "":
				addSearchQueryLog(user, "search="+search, "supplier")

		state = self.request.query_params.get('state', None)
		if state is not None:
			queryset = queryset.filter(selling_company__state=state)

		city = self.request.query_params.get('city', None)
		if city is not None:
			queryset = queryset.filter(selling_company__city=city)

		buying_company = self.request.query_params.get('buying_company', None)

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				catalog = self.request.query_params.get('catalog', None)
				if catalog is not None:
					'''pushUserObjId = Push_User.objects.filter(buying_company=company, catalog=catalog).values('buying_company','catalog','selling_company').annotate(Max('id')).values('id__max')#user=user
					pushUser = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first()'''

					cpfObj = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, catalog=catalog).select_related('selling_company').last()

					return queryset.filter(buying_company=company, selling_company = cpfObj.selling_company) #pushUser.selling_company

				selection = self.request.query_params.get('selection', None)
				if selection is not None:
					'''pushUserObjId = Push_User.objects.filter(buying_company=company, selection=selection).values('buying_company','selection','selling_company').annotate(Max('id')).values('id__max')#user=user
					pushUser = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first()'''

					cpfObj = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, selection=selection).select_related('selling_company').last()

					return queryset.filter(buying_company=company, selling_company = cpfObj.selling_company) #pushUser.selling_company

				if buying_company is not None:
					if user.is_staff:#using by admin
						queryset = queryset.filter(buying_company=buying_company)
					else:
						buyers_selling_companies = Buyer.objects.filter(buying_company=buying_company, broker_company=company).values_list('selling_company', flat=True)
						queryset = queryset.filter(selling_company__in=buyers_selling_companies)

						queryset = queryset.filter(buying_company=buying_company)
				else:
					queryset = queryset.filter(buying_company=company)

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
			serializer.save(buying_company=company, status='supplier_pending')

	def create(self, request, companies_pk=None):
		loginUser = request.user
		loginCompany = get_user_company(loginUser) #loginUser.companyuser.company
		#companyName = loginCompany.name

		if loginCompany is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		content_type = request.META.get('CONTENT_TYPE')

		print content_type
		if "multipart/form-data" in content_type:
			logger.info("content_type if multipart/form-data")
			f = request.FILES['supplier_csv[0]']

			upload_file=f
			jobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Supplier", upload_file=upload_file, status="Created")
			print jobsObj

			filetype = f.content_type
			supportcontenttype = ["application/vnd.ms-excel","application/csv","application/x-csv","text/plain","text/x-csv","text/csv","text/comma-separated-values","text/x-comma-separated-values","text/tab-separated-values"]
			logger.info(str(filetype))
			#if "csv" not in str(filetype):
			if str(filetype) not in supportcontenttype:
				logger.info(str(filetype))
				jobsObj.error_details = "Please upload CSV file only"
				jobsObj.save()
				raise serializers.ValidationError({"File":"Please upload CSV file only"})

			fileObject = csv.reader(upload_file)
			row_count = sum(1 for row in fileObject)
			jobsObj.total_rows = (row_count-1)
			jobsObj.status = "Scheduled"
			jobsObj.save()

			if settings.TASK_QUEUE_METHOD == 'celery':
				task_id = supplierCSVImportJobs.apply_async((jobsObj.id,), expires=datetime.now() + timedelta(days=2))
			elif settings.TASK_QUEUE_METHOD == 'djangoQ':
				task_id = async(
					'api.tasks.supplierCSVImportJobs',
					jobsObj.id,
					broker = priority_broker
				)
			logger.info("supplier task_id=")
			logger.info(str(task_id))
			return Response({"success": "Job is Scheduled. Please check Jobs table in settings for status."})
		else:
			print "content_type else"
			data = request.data
			print data.get('buyer_type', None)

			if data.get('buyer_type', None) is not None and data.get('buyer_type', None) == "Enquiry":
				print "Enquiry"
				#buyer_type = data.get('buyer_type', None)
				details = data.get('details', None)
				print details
				import json
				detailsjson =  json.loads(details) #should not be commented #use in server
				#detailsjson =  details #should be in commented #use in local testing time

				print detailsjson
				#json.dumps(details, sort_keys=True, indent=4)

				##selling_company = None
				catalog = Catalog.objects.get(pk=int(detailsjson['catalog']))

				selling_company = data.get('selling_company', None)
				if selling_company:
					selling_company = Company.objects.get(pk=int(selling_company))
				else:
					selling_company = catalog.company

				'''if catalog.brand.manufacturer_company:
					selling_company = catalog.brand.manufacturer_company
				else:
					selling_company = catalog.brand.company'''


				'''data['group_type'] = 1
				data['buying_company'] = loginCompany.id
				data['selling_company'] = selling_company.id
				data['status'] = 'supplier_pending'
				data['buyer_approval'] = True'''

				group_type = GroupType.objects.get(pk=1)
				supplier_name = selling_company.name
				isjson = add_supplier_enquiry(loginUser, loginCompany, supplier_name, selling_company, details, True, catalog, data)

				import types
				if type(isjson) != types.BooleanType:
					return Response(isjson)

				'''print selling_company.id
				print data
				buyser = SupplierSerializer(data=data, context={'request': request})
				if buyser.is_valid():
					print "save is_valid"
					pObj = buyser.save(buying_company=loginCompany)
				else:
					print buyser.errors
					raise serializers.ValidationError(buyser.errors)'''
			else:
				if data.get('supplier_name', None) is None or data.get('supplier_number', None) is None or data.get('group_type', None) is None or data.get('country', None) is None:
					raise serializers.ValidationError({"error":"Please enter valid data"})

				supplier_name=data['supplier_name']
				supplier_number=str(data['supplier_number'])[-10:]

				if int(supplier_number[0]) in [0,1,2,3,4,5]:
					raise serializers.ValidationError({"supplier_number":"Mobile number is not valid : "+str(supplier_number)})

				group_type = GroupType.objects.get(pk=data['group_type'])

				if data.get('country', None) is not None:
					country = Country.objects.get(pk=data['country'])
				else:
					country = Country.objects.get(pk=1)

				#sellingcompany = add_supplier(loginUser, loginCompany, supplier_name, country, supplier_number, group_type, True);
				sellingcompany = add_supplier_v1(loginUser, loginCompany, supplier_name, country, supplier_number, group_type, True);
				if sellingcompany:
					return Response({"success": "Supplier request has been sent to " + sellingcompany.name + " successfully"})
				else:
					return Response({"success": "Supplier request has been sent successfully"})

			return Response({"success": "Supplier request has been sent successfully"})

	@list_route(methods=['get'])
	def dropdown(self, request, companies_pk=None):
		queryset = self.get_queryset().filter(status="approved").exclude(selling_company__isnull=True).select_related('selling_company').order_by('selling_company__name')
		queryset = self.filter_queryset(queryset)
		array = []
		for b in queryset:
			broker = None
			if b.broker_company is not None:
				broker = b.broker_company.id
			#if b.selling_company.city.city_name != "-" and b.selling_company.state.state_name != "-":
			#	company_name = b.selling_company.name+", "+b.selling_company.city.city_name+", "+b.selling_company.state.state_name
			#else:
			#	company_name = b.selling_company.name
			company_name = b.selling_company.name
			array.append({"id":b.id,"company_id":b.selling_company.id,"company_name":company_name, "broker_id":broker, "phone_number":b.selling_company.phone_number, "brokerage_fees":b.brokerage_fees})

		return Response(array)

	@list_route(methods=['post'])
	def resend(self, request, companies_pk=None):
		data = request.data
		suppliers = data['suppliers']

		if suppliers is not None:
			user = request.user
			company = user.companyuser.company

			for supplier in suppliers:
				supplierObj = Buyer.objects.get(pk=supplier)

				if supplierObj.status.lower() == "supplier_registrationpending":
					sendInvite(supplierObj.invitee.country.phone_code+supplierObj.invitee.invitee_number, str(company.name))
				elif supplierObj.status.lower() == "supplier_pending":
					requestNotification(supplierObj.buying_company, supplierObj.selling_company.country.phone_code+supplierObj.selling_company.phone_number, "supplier", supplierObj, supplierObj.selling_company, supplierObj.status)

		return Response({"success": "Supplier request has been resent successfully"})

	@detail_route(methods=['POST'])
	def add_buyers(self, request, pk=None, companies_pk=None):
		loginUser = request.user
		loginCompany = loginUser.companyuser.company

		queryset = self.get_object()

		broker = None
		if loginCompany.company_group_flag.broker:
			broker = loginCompany

		data = request.data
		logger.info("add_buyers data= %s"% (str(data)))

		buying_companies_ids = data.get('buying_companies')
		buying_companies_ids = list(buying_companies_ids)
		print buying_companies_ids
		buying_companies = Company.objects.filter(id__in=buying_companies_ids)

		group_type = GroupType.objects.filter(name="Wholesaler").first()

		selling_user = queryset.selling_company.chat_admin_user

		for buying_company in buying_companies:
			if not Buyer.objects.filter(selling_company = queryset.selling_company, buying_company = buying_company).exists():
				inviteobj = Invite.objects.create(relationship_type="buyer", company=queryset.selling_company ,user=selling_user)
				inviteeObj = Invitee.objects.create(invitee_company=buying_company.name,invitee_name=buying_company.name,country=buying_company.country,invitee_number=buying_company.phone_number,invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Buyer")

				status='buyer_pending'
				if buying_company.connections_preapproved == True:
					status='approved'

				payment_duration = 0
				discount = cash_discount = credit_limit = Decimal('0.00')
				cbg_buyer_type = companyBuyerGroupType(group_type.name)
				cbgObj = CompanyBuyerGroup.objects.filter(company=queryset.selling_company, buyer_type=cbg_buyer_type).first()
				if cbgObj:
					print "cbgObj------", cbgObj
					discount = cbgObj.discount
					cash_discount = cbgObj.cash_discount
					credit_limit = cbgObj.credit_limit
					payment_duration = cbgObj.payment_duration

				buyer = Buyer.objects.create(selling_company = queryset.selling_company, buying_company = buying_company, status=status, group_type=group_type, invitee=inviteeObj, user=selling_user, buying_company_name=buying_company.name, buying_person_name=buying_company.name, discount=discount, cash_discount=cash_discount, credit_limit=credit_limit, payment_duration=payment_duration, broker_company=broker, supplier_person_name=queryset.selling_company.name)
				requestNotification(buyer.selling_company, buying_company.country.phone_code+buying_company.phone_number, "buyer", buyer, buying_company, status)
			else:
				Buyer.objects.filter(selling_company = queryset.selling_company, buying_company = buying_company).update(broker_company=broker)

		rno = random.randrange(100000, 999999, 1)
		jsonarr = {}
		jsonarr['broker_name'] = loginCompany.name
		jsonarr['total_buyers'] = buying_companies.count()
		jsonarr['notId'] = rno
		user1 = CompanyUser.objects.filter(company=queryset.selling_company).values_list('user', flat=True)
		user1 = User.objects.filter(id__in=user1, groups__name="administrator")
		sendAllTypesMessage("add_buyers_broker", user1, jsonarr)

		return Response({"success": "Buyers added successfully."})

	@detail_route(methods=['POST'])
	def remove_buyers(self, request, pk=None, companies_pk=None):
		loginUser = request.user
		loginCompany = loginUser.companyuser.company

		queryset = self.get_object()

		data = request.data
		logger.info("remove_buyers data= %s"% (str(data)))

		buying_companies_ids = data.get('buying_companies')
		buying_companies_ids = list(buying_companies_ids)
		print buying_companies_ids

		Buyer.objects.filter(selling_company = queryset.selling_company, buying_company__in = buying_companies_ids).update(broker_company=None, brokerage_fees=Decimal('0.00'))

		return Response({"success": "Buyers removed successfully."})

	@list_route(methods=['get'])
	def company_details(self, request, companies_pk=None):
		loginUser = request.user
		loginCompany = get_user_company(loginUser) #loginUser.companyuser.company

		company = request.query_params.get('company', None)
		print company
		companyObj = Company.objects.filter(id=company).first()

		if companyObj is None:
			raise serializers.ValidationError({"company":"company must be required."})

		json_arr = {}
		json_arr['name'] = companyObj.name
		json_arr['email'] = companyObj.email
		json_arr['phone_number'] = companyObj.phone_number
		json_arr['thumbnail'] = None
		if companyObj.thumbnail:
			json_arr['thumbnail'] = companyObj.thumbnail.url
		json_arr['chat_admin_user'] = None
		if companyObj.chat_admin_user:
			json_arr['chat_admin_user'] = companyObj.chat_admin_user.username

		# ~ activecompanycatalogids = Product.objects.filter(catalog__view_permission="public", catalog__supplier_disabled=False, catalog__company=companyObj).values_list('catalog', flat=True).distinct()
		#json_arr['total_public_catalogs'] = len(activecompanycatalogids)

		#json_arr['total_orders'] = SalesOrder.objects.filter(seller_company=companyObj, company=loginCompany).exclude(processing_status="Draft").count()

		#catalogserializer = GetNestedCatalogSerializer(instance=obj, context={'request': self.context['request']})
		obj = SalesOrder.objects.filter(seller_company=companyObj, company=loginCompany)
		serializerres = SellerSalesOrderSerializer(many=True, instance=obj, context={'request': request})
		json_arr['selling_order'] = serializerres.data

		serializerres = GetAddressSerializer(instance=companyObj.address, context={'request': request})
		json_arr['address'] = serializerres.data

		serializer = SellerPolicySerializer(instance=companyObj.sellerpolicy_set.all(), many=True)
		json_arr['seller_policy'] = serializer.data

		return Response(json_arr)


class CatalogListViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = CatalogList.objects.all()
	serializer_class = CatalogListSerializer

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		#if self.request.method in ('PUT','PATCH'):
		#	serializer_class = CatalogListSerializer

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetCatalogListSerializer

		#if self.request.method == 'GET':
		#		serializer_class = GetCatalogListSerializer
		return serializer_class

	def get_queryset(self):
		queryset = CatalogList.objects.all().select_related('user').prefetch_related('catalogs')

		user = self.request.user

		return queryset.filter(user=user)

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)

class MeetingViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Meeting.objects.all()
	serializer_class = MeetingSerializer
	#permission_classes = (IsOwnerOrReadOnly, )

	pagination_class = CustomPagination

	filter_backends = (filters.DjangoFilterBackend,)
	filter_fields = ('id', 'buying_company_ref', )

	def perform_create(self, serializer):
		user=self.request.user
		company = user.companyuser.company
		serializer.save(user=user, company=company)
	def get_queryset(self):
		queryset = Meeting.objects.all().select_related('user__companyuser__company', 'user__companyuser__deputed_to', 'buying_company_ref').prefetch_related('salesorder').order_by('-id')
		userId = self.request.query_params.get('user', None)
		if userId is not None:
			queryset = queryset.filter(user=userId)
		status = self.request.query_params.get('status', None)
		if status is not None:
			queryset = queryset.filter(status=status)

		#return queryset

		user = self.request.user
		#print queryset
		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					return queryset.filter(Q(user__companyuser__company=company) | Q(user__companyuser__deputed_to=company))
				else:
					return queryset.filter(user=user)
			else:
				return Meeting.objects.none()
		except ObjectDoesNotExist:
			return Meeting.objects.none()

	@list_route(methods=['get'])
	def report(self, request, users_pk=None):
		user = request.user
		if users_pk is not None:
				user = User.objects.get(id=users_pk)

		company = get_user_company(user) #user.companyuser.company

		dateList = []

		todayDate = date.today()

		yesterdayDate = todayDate - timedelta(days=1)

		currentWeekStartDate = todayDate - timedelta(days=todayDate.weekday())

		lastWeekEndDate = currentWeekStartDate - timedelta(days=1)
		lastWeekStartDate = lastWeekEndDate - timedelta(days=lastWeekEndDate.weekday())

		currentMonthStartDate = todayDate.replace(day=1)

		lastMonthEndDate = currentMonthStartDate - timedelta(days=1)
		lastMonthStartDate = lastMonthEndDate.replace(day=1)

		firstYearDate = todayDate.replace(year=2000)

		dateList.append(["Today",todayDate,todayDate]);
		dateList.append(["Yesterday",yesterdayDate,yesterdayDate]);
		dateList.append(["This Week",currentWeekStartDate,todayDate]);
		dateList.append(["Last Week",lastWeekStartDate,lastWeekEndDate]);
		dateList.append(["This Month",currentMonthStartDate,todayDate]);
		dateList.append(["Last Month",lastMonthStartDate,lastMonthEndDate]);
		dateList.append(["All Time",firstYearDate,todayDate]);

		jsonArr = []

		for dates in dateList:
			#salesOrderIds = Meeting.objects.filter(user=user, start_datetime__gte=datetime.combine(dates[1], time.min), start_datetime__lte=datetime.combine(dates[2], time.max)).values_list('salesorder', flat=True).distinct()
			salesOrderIds = SalesOrder.objects.filter(user=user, created_at__gte=datetime.combine(dates[1], time.min), created_at__lte=datetime.combine(dates[2], time.max)).values_list('id', flat=True).distinct()
			TotalItem = SalesOrderItem.objects.filter(sales_order__in=salesOrderIds).aggregate(Sum('quantity')).get('quantity__sum', 0)
			TotalOrders = SalesOrder.objects.filter(id__in=salesOrderIds).count()
			TotalDuration = Meeting.objects.filter(user=user, start_datetime__gte=datetime.combine(dates[1], time.min), start_datetime__lte=datetime.combine(dates[2], time.max)).aggregate(Sum('duration')).get('duration__sum', 0)
			TotalMeeting = Meeting.objects.filter(user=user, start_datetime__gte=datetime.combine(dates[1], time.min), start_datetime__lte=datetime.combine(dates[2], time.max)).count()

			TotalAmount = 0
			soObjs = SalesOrder.objects.filter(id__in=salesOrderIds)
			for soObj in soObjs:
				TotalAmount += soObj.total_rate()

			if TotalItem is None:
				TotalItem = 0
			if TotalDuration is None:
				TotalDuration = 0
			jsonArr.append({"day":dates[0],"total_items":str(TotalItem),"total_duration":str(TotalDuration),"total_meeting":str(TotalMeeting), "total_salesorder_amount":str(TotalAmount), "total_order":str(TotalOrders)})

		return Response(jsonArr)

class SalesOrderViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SalesOrder.objects.all()
	serializer_class = SalesOrderSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrUserSalesOrderObj, )

	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('GET'):
			serializer_class = GetSalesOrderSerializer

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetExpandSalesOrderSerializer

		return serializer_class

	def get_queryset(self):
		#queryset = SalesOrder.objects.filter(visible_to_supplier=True).select_related('company','seller_company','user').order_by('-id')
		queryset = SalesOrder.objects.filter(visible_to_supplier=True)
		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			queryset = queryset.select_related('company__city','company__state','company__country','company__chat_admin_user','company__companycreditrating', 'seller_company__city','seller_company__state','seller_company__country','seller_company__chat_admin_user','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related('items__product__catalog__category','invoice_set__items__order_item__product__catalog__category','invoice_set__items__tax_class_1', 'invoice_set__items__tax_class_2', 'invoice_set__shipment_set', 'invoice_set__payments').order_by('-id')
		else:
			queryset = queryset.select_related('company__city','company__state','company__country','company__companycreditrating','seller_company__city','seller_company__state','seller_company__country','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related('items__product__catalog__category','invoice_set__items__order_item__product__catalog__category').order_by('-id')

		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(company=company)

		user = self.request.user

		if user.is_staff:
			return queryset

		processing_status = self.request.query_params.get('processing_status', None)
		if processing_status is not None:
			if processing_status.lower() == "pending":
				queryset = queryset.filter(processing_status__in=["Draft","Pending","ordered","Accepted","In Progress", "COD Verification Pending", "Field Verification Pending"]).exclude(user__is_superuser=True, processing_status__in=["Draft"])
			if processing_status.lower() == "dispatch":
				queryset = queryset.filter(processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"])
			if processing_status.lower() == "cancel":
				queryset = queryset.filter(processing_status__in=["Cancelled","Transferred"])
			if processing_status.lower() == "placed":
				queryset = queryset.exclude(processing_status__in=["Cart", "Draft"])
			#pending, dispatch, cancel
		# else:
		# 	queryset = queryset.exclude(processing_status__in=["Cart", "Draft"])

		try:
			company = get_user_company(user)
			# if user.is_authenticated() and (user.companyuser.company is not None):
			if company is not None:
				'''if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					return queryset.filter(seller_company=company)#(user__companyuser__company=company)
				else:
					return queryset.filter(user=user)'''
				# company = user.companyuser.company
				is_salesperson = user.groups.filter(name="salesperson").exists()
				if is_salesperson and user.companyuser.deputed_to is not None:
					return queryset.filter(user=user)
				if is_salesperson and user.companyuser.company.buyers_assigned_to_salesman is True:
					#return queryset.filter(user=user)
					if AssignGroups.objects.filter(user=user).exists():
						agObj = AssignGroups.objects.get(user=user)
						#buyers = agObj.groups.all().values_list('buyers', flat=True)
						buyers = getSegmentationsBuyers(agObj.groups.all(), company)
						queryset = queryset.filter(company__in = buyers)
					else:
						return queryset.filter(user=user)

				return queryset.filter(seller_company=company)
			else:
				return SalesOrder.objects.none()
		except ObjectDoesNotExist:
			return SalesOrder.objects.none()

	@detail_route(methods=['GET'], serializer_class = SalesOrderSerializer)
	def catalogwise(self, request, pk=None, companies_pk=None):
		# queryset = self.get_object().select_related("company")
		# order = self.filter_queryset(queryset)
		# print order
		#order = queryset
		order = SalesOrder.objects.select_related('company__city','company__state','company__country','company__companycreditrating','seller_company__city','seller_company__state','seller_company__country','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related("items__product__catalog__category", "items__product__catalog__brand", "invoice_set").get(pk=pk)
		orderjson = self.get_serializer(instance=order)
		#orderjson = GetSalesOrderSerializer(instance=order)
		orderjson = orderjson.data


		catalogs = []

		if order.cart is None:
			catalogarr = []
			order_items = order.items.all()
			for item in order_items:
				if item.product.catalog is not None: #and item.product.catalog not in catalogarr:
					if item.product.catalog not in catalogarr:
						catalogarr.append(item.product.catalog)
					#catalogarr.append(item.product.catalog)

			for catalog in catalogarr:
				catalogsjson = {}
				catalogsjson['name'] = catalog.title
				catalogsjson['brand'] = catalog.brand.name
				catalogsjson['id'] = catalog.id
				products = []

				#for item in order_items.filter(product__catalog=catalog):
				for item in order_items:
					if item.product.catalog == catalog:
						product = SalesOrderItemSerializer(instance=item)
						product = product.data
						products.append(product)

				catalogsjson['products'] = products
				catalogsjson['total_products'] = len(products)
				catalogs.append(catalogsjson)
		else:
			groupitems = order.items.all().values('product__catalog','is_full_catalog', 'note').distinct()
			for groupitem in groupitems:
				catalog = Catalog.objects.select_related('brand').get(pk=groupitem['product__catalog'])
				catalogsjson = {}
				catalogsjson['name'] = catalog.title
				catalogsjson['brand'] = catalog.brand.name
				catalogsjson['id'] = catalog.id
				products = []

				filtereditems = order.items.filter(product__catalog=groupitem['product__catalog'], is_full_catalog=groupitem['is_full_catalog'], note=groupitem['note']).select_related('product__catalog', 'product__catalog__category')

				if groupitem['is_full_catalog'] == True:
					cartwiseProductOrderArray(catalogs, filtereditems, catalogsjson)
				else:
					for filtereditem in filtereditems:
						cartwiseProductOrderArray(catalogs, [filtereditem], catalogsjson)

		orderjson['catalogs'] = catalogs

		return Response(orderjson)

	@detail_route(methods=['GET'], serializer_class = SalesOrderSerializer)
	def catalogs(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()
		order = self.filter_queryset(queryset)
		catalogids = order.items.values_list('product__catalog', flat=True)
		catalogs = Catalog.objects.filter(id__in=catalogids).values('id','title')

		return Response(list(catalogs))

	#for placing order on shiprocket
	@detail_route(methods=['POST'], serializer_class = SalesOrderSerializer)
	def placetoship(self, request, pk=None, companies_pk=None):
		print "post_data",request.data
		print "pk",pk
		print "companies_pk",companies_pk
		if request.data.has_key('tracking') and request.data.get('tracking') == True :
			awb_code	=  request.data.get('awb_code',None)
			tracking_details = get_tracking_details(awb_code)
			return Response(tracking_details)
		awb 			 = request.data.get('awb_creation')
		combine_multiple = request.data.get('combine_multiple',False)
		order_ids 		 = request.data.get('order_ids',None)
		if  len(order_ids) > 0:
			buyers = SalesOrder.objects.filter(id__in=order_ids).values_list('company__id',flat=True).distinct()
			if len(buyers) > 1:
				print "Buyer must be same for all Orders"
				return Response({"message" : "Buyer must be same for all Orders", "status_code" : 500})

		if request.data.has_key('pickup') and request.data.get('pickup') == True :
			pickup_locations = get_pickup_locations()
			name_value_list  = check_values_from_frontend(pk)
			return Response({"pickup_locations" : pickup_locations,"name_value_list" : name_value_list})
		pickup_location = request.data.get('pickup_location',{}).get('pickup_location','')
		pickup_pincode 	= request.data.get('pickup_location',{}).get('pin_code','')
		if not awb:
			length 			= request.data.get('length')
			breadth 		= request.data.get('breadth')
			height 			= request.data.get('height')
			weight 			= request.data.get('weight')
			partial_value_list = request.data.get('value_list')
			order_response 	= create_order_on_ship_rocket(
				pk,
				length,
				breadth,
				height,
				weight,
				pickup_location,
				pickup_pincode,
				combine_multiple,
				order_ids,
				partial_value_list
			)
			print length,breadth,height,weight
		if awb:
			ship_order_id 		= request.data.get('ship_order_id')
			order_shipment_id 	= request.data.get('order_shipment_id')
			courier_id 			= request.data.get('courierid')
			order_response 		= create_awb_on_ship_rocket(pk,ship_order_id,order_shipment_id,courier_id,combine_multiple,order_ids)
			print order_response
		return Response(order_response)

	def perform_create(self, serializer):
		print "in perform_create"
		serializer.save(user=self.request.user)

	@detail_route(methods=['POST'])
	def transfer(self, request, pk=None, companies_pk=None):
		data = request.data
		seller_company = data.get('seller_company')

		oldobj = self.get_object()
		items = oldobj.items.all()

		obj = self.get_object()
		obj.seller_company = Company.objects.get(pk=seller_company)
		obj.processing_status = "Pending"
		obj.pk = None
		obj.save()

		print obj.pk

		for item in items:
			olditem = item
			olditem.pk = None
			olditem.sales_order = obj
			olditem.save()

		oldobj.processing_status = "Transferred"
		oldobj.tranferred_to = obj
		oldobj.save()

		cu = CompanyUser.objects.filter(company=obj.seller_company).first()
		group_type = GroupType.objects.get(pk=2) #default wholesaler

		#buyingcompany = add_buyer(cu.user, obj.seller_company, obj.company.name, obj.company.country, obj.company.phone_number, group_type, False);
		buyingcompany = add_buyer_v1(cu.user, obj.seller_company, obj.company.name, obj.company.country, obj.company.phone_number, group_type, False);

		#for invoice and payment changes
		if oldobj.payment_status() in ["Paid","Partially Paid"]:
			oldinvoices = oldobj.invoice_set.all()
			print oldinvoices
			for oldinvoice in oldinvoices:
				print oldinvoice
				oldinvoiceitems = oldinvoice.items.all()
				oldinvoiceid = oldinvoice.id

				newinvoice = oldinvoice
				newinvoice.order = obj
				newinvoice.pk=None
				newinvoice.save()

				for oldinvoiceitem in oldinvoiceitems:
					print oldinvoiceitem
					newinvoiceitem = oldinvoiceitem
					newinvoiceitem.invoice = newinvoice
					newinvoiceitem.order_item = SalesOrderItem.objects.filter(sales_order=obj, product=newinvoiceitem.order_item.product).first()
					newinvoiceitem.pk=None
					newinvoiceitem.save()

				Invoice.objects.filter(id=oldinvoiceid).update(status = "Cancelled")

				oldpayments = Payment.objects.filter(invoice=oldinvoiceid)
				for oldpayment in oldpayments:
					print oldpayment
					oldpaymentid = oldpayment.id

					newpayment = oldpayment
					newpayment.to_company = obj.seller_company
					newpayment.pk = None
					newpayment.save()
					newpayment.invoice = [newinvoice.id]
					newpayment.save()

					Payment.objects.filter(id=oldpaymentid).update(status="Cancelled")

		return Response({"success": "Sales order has been transfered."})

	@list_route(methods=['get'])
	def report(self, request, companies_pk=None):

		jsonArr = []

		dateList = []

		todayDate = date.today()

		yesterdayDate = todayDate - timedelta(days=1)
		OneWeekStartDate = todayDate - timedelta(days=7)
		OneMonthStartDate = todayDate - timedelta(days=30)

		dateList.append(["Avg. closure time (30 days orders)",OneMonthStartDate,todayDate]);
		dateList.append(["Conversation rate",OneMonthStartDate,todayDate]);
		dateList.append(["24 hours",todayDate,todayDate]);#min to max time
		dateList.append(["1 days old",yesterdayDate,todayDate]);
		dateList.append(["7 days old",OneWeekStartDate,todayDate]);
		dateList.append(["30 days old",OneMonthStartDate,todayDate]);

		for index, item in enumerate(dateList):
			jsondata = {}
			jsondata["details"] = item[0]

			jsondata["cart_draft"] = ""
			jsondata["pending_payment"] = ""
			jsondata["pending_acceptance_prepaid"] = ""
			jsondata["pending_acceptance_credit"] = ""
			jsondata["pending_dispatch"] = ""
			jsondata["pending_payout"] = ""
			jsondata["pending_cashback"] = ""

			if index in [2,3,4,5]:
				print index
				jsondata["cart_draft"] = SalesOrder.objects.filter(created_at__gte=item[1], processing_status__in=["Cart", "Draft"]).count()

				# ~ prepaid_query = "SELECT group_concat(id) as ids FROM `api_salesorder` WHERE (`payment_date` < `dispatch_date` or (payment_date is not null and dispatch_date is null)) order by id desc"
				# ~ cursor = connection.cursor()
				# ~ cursor.execute( prepaid_query )
				# ~ row = cursor.fetchone()

				# ~ prepaidids = []
				# ~ if row[0]:
					# ~ prepaidids = row[0].split(',')
					# ~ prepaidids = list(prepaidids)
					# ~ prepaidids = [int(i) for i in prepaidids]

				# ~ print "prepaidids =",prepaidids
				#other method to check prepaid orders..
				#order_type = Prepaid

				salesorderids = SalesOrder.objects.filter(created_at__gte=item[1], order_type="Prepaid", processing_status__in=["Draft","Pending","ordered","Accepted","In Progress", "COD Verification Pending", "Field Verification Pending"]).values_list('id', flat=True)#id__in=prepaidids,
				jsondata["pending_payment"] = Invoice.objects.filter(order__in=salesorderids, payment_status__in=["Pending", "Failure"]).values_list('order', flat=True).distinct().count()

				salesorderids = SalesOrder.objects.filter(created_at__gte=item[1], order_type="Prepaid", processing_status__in=["Pending"]).values_list('id', flat=True)#id__in=prepaidids,
				jsondata["pending_acceptance_prepaid"] = Invoice.objects.filter(order__in=salesorderids, payment_status__in=["Paid", "Success"]).values_list('order', flat=True).distinct().count()

				jsondata["pending_acceptance_credit"] = SalesOrder.objects.filter(created_at__gte=item[1], order_type="Credit", processing_status__in=["Pending"]).count()#id__in=prepaidids,

				jsondata["pending_dispatch"] = SalesOrder.objects.filter(created_at__gte=item[1], processing_status__in=["ordered","Accepted","In Progress"]).count()

				#all payment status paid n pending
				prepaidorderids = SalesOrder.objects.filter(created_at__gte=item[1], order_type="Prepaid", processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"]).values_list('id', flat=True)
				inv_ord_ids1 = Invoice.objects.filter(order__in=prepaidorderids, payment_status__in=["Paid", "Success"]).values_list('order', flat=True).distinct()

				dispatchorderids = SalesOrder.objects.filter(created_at__gte=item[1], order_type="Credit", processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"]).values_list('id', flat=True)
				inv_ord_ids2 = Invoice.objects.filter(order__in=dispatchorderids, payment_status__in=["Pending", "Failure"]).values_list('order', flat=True).distinct()

				jsondata["pending_payout"] = SalesOrder.objects.filter(Q(id__in=inv_ord_ids1) | Q(id__in=inv_ord_ids2)).count()

				salesorderids = SalesOrder.objects.filter(created_at__gte=item[1], processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"]).values_list('id', flat=True)
				jsondata["pending_cashback"] = Invoice.objects.filter(order__in=salesorderids, payment_status__in=["Paid", "Success"]).values_list('order', flat=True).distinct().count()



			jsonArr.append(jsondata)

		return Response(jsonArr)


	'''@detail_route(methods=['get'])
	def brandwise(self, request, pk=None, companies_pk=None):
		user = request.user
		company = user.companyuser.company


		queryset = self.get_object()

		brands = []

		brandarr = []
		for item in SalesOrderItem.objects.filter(sales_order=queryset.id).exclude(product__catalog__company=company).select_related('product__catalog__brand'):
			brand = item.product.catalog.brand
			if brand is not None and brand not in brandarr:
					brandarr.append(brand)

		for brand in brandarr:
			brandsjson = {}
			brandsjson['brand_name'] = brand.name
			brandsjson['id '] = brand.id

			catalogs = []
			catalogarr = []
			for item in SalesOrderItem.objects.filter(sales_order=queryset.id, product__catalog__brand=brand).exclude(product__catalog__company=company).select_related('product__catalog'):
				catalog = item.product.catalog
				if catalog is not None and catalog not in catalogarr:
						catalogarr.append(catalog)

			for catalog in catalogarr:
				catalogsjson = {}
				catalogsjson['catalog_name'] = catalog.title
				#catalogsjson['brand'] = catalog.brand.name
				catalogsjson['id'] = catalog.id
				products = []

				for item in SalesOrderItem.objects.filter(sales_order=queryset.id, product__catalog=catalog).exclude(product__catalog__company=company).select_related('product__catalog'):
					product = SelectionPOSProductSerializer(instance=item.product)
					product = product.data

					pushUserObjId = Push_User_Product.objects.filter(buying_company=company, product=item.product.id).values('user','selection','selling_company').annotate(Max('id')).values('id__max')
					pushUser = Push_User_Product.objects.filter(id__in=pushUserObjId).order_by('price').first()
					if pushUser:
						selling_company = Push_User_Product.objects.filter(id__in=pushUserObjId).distinct().values('selling_company', 'selling_company__name', 'price').order_by('price', 'selling_company')#pushUser.selling_company.id

						scarr = []
						for sc in selling_company:
							scjson = {}
							scjson['id'] = sc['selling_company']
							scjson['name'] = sc['selling_company__name']
							scjson['price'] = sc['price']
							scarr.append(scjson)

						product['selling_company'] = scarr #list(selling_company)
						product['price'] = pushUser.price
					else:
						product['selling_company'] = []

					products.append(product)

				catalogsjson['products'] = products
				catalogsjson['total_products'] = len(products)
				catalogs.append(catalogsjson)
			brandsjson['catalogs'] = catalogs
			brands.append(brandsjson)
		return Response(brands)'''

class PurchaseOrderViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SalesOrder.objects.all()
	serializer_class = SalesOrderSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrUserSalesOrderObj, )

	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('GET'):
			serializer_class = GetSalesOrderSerializer

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetExpandSalesOrderSerializer

		return serializer_class

	def get_queryset(self):
		#queryset = SalesOrder.objects.filter(visible_to_buyer=True).select_related('company','seller_company','user').order_by('-id')
		queryset = SalesOrder.objects.filter(visible_to_buyer=True)#.select_related('company__city','company__state','company__country','seller_company__city','seller_company__state','seller_company__country','user').prefetch_related("items__product__catalog__category","invoice_set__items__order_item__product__catalog__category","invoice_set__items__tax_class_1", "invoice_set__items__tax_class_2", "invoice_set__shipment_set").order_by('-id')
		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			queryset = queryset.select_related('company__city','company__state','company__country','company__chat_admin_user','company__companycreditrating', 'seller_company__city','seller_company__state','seller_company__country','seller_company__chat_admin_user','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related('items__product__catalog__category','invoice_set__items__order_item__product__catalog__category','invoice_set__items__tax_class_1', 'invoice_set__items__tax_class_2', 'invoice_set__shipment_set', 'invoice_set__payments').order_by('-id')
		else:
			queryset = queryset.select_related('company__city','company__state','company__country','company__companycreditrating','seller_company__city','seller_company__state','seller_company__country','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related('items__product__catalog__category','invoice_set__items__order_item__product__catalog__category').order_by('-id')

		user = self.request.user

		if user.is_staff:
			return queryset

		processing_status = self.request.query_params.get('processing_status', None)
		if processing_status is not None:
			if processing_status.lower() == "pending":
				queryset = queryset.filter(processing_status__in=["Draft","Pending","ordered","Accepted","In Progress", "COD Verification Pending", "Field Verification Pending"])
			if processing_status.lower() == "dispatch":
				queryset = queryset.filter(processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"])
			if processing_status.lower() == "cancel":
				queryset = queryset.filter(processing_status__in=["Cancelled","Transferred"])
			if processing_status.lower() == "placed":
				queryset = queryset.exclude(processing_status__in=["Cart"])
		# else:
		# 	queryset = queryset.exclude(processing_status__in=["Cart"])



		if user.groups.filter(name="administrator").exists():
			try:
				company = get_user_company(user)
				# user_company = (user.companyuser.company is not None)
				# if user_company:
				# 	company = user.companyuser.company
				if company is not None:
					return queryset.filter(company=company)
			except ObjectDoesNotExist:
				return SalesOrder.objects.none()
		else:
			return SalesOrder.objects.none()

	def perform_create(self, serializer):#add user on create
		serializer.save(user=self.request.user)

	@detail_route(methods=['GET'], serializer_class = SalesOrderSerializer)
	def catalogwise(self, request, pk=None, companies_pk=None):
		# queryset = self.get_object()
		# order = self.filter_queryset(queryset)
		order = SalesOrder.objects.select_related('company__city','company__state','company__country','company__companycreditrating','seller_company__city','seller_company__state','seller_company__country','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related("items__product__catalog__category", "items__product__catalog__brand", "invoice_set").get(pk=pk)
		orderjson = self.get_serializer(instance=order)
		#orderjson = GetSalesOrderSerializer(instance=order)
		orderjson = orderjson.data


		catalogs = []

		if order.cart is None:
			catalogarr = []
			order_items = order.items.all()
			for item in order_items:
				if item.product.catalog is not None:
					if item.product.catalog not in catalogarr:
						catalogarr.append(item.product.catalog)

			for catalog in catalogarr:
				catalogsjson = {}
				catalogsjson['name'] = catalog.title
				catalogsjson['brand'] = catalog.brand.name
				catalogsjson['id'] = catalog.id
				products = []

				# for item in order.items.filter(product__catalog=catalog):
				for item in order_items:
					if item.product.catalog == catalog:
						product = SalesOrderItemSerializer(instance=item)
						product = product.data
						products.append(product)

				catalogsjson['products'] = products
				catalogsjson['total_products'] = len(products)
				catalogs.append(catalogsjson)
		else:
			groupitems = order.items.all().values('product__catalog','is_full_catalog', 'note').distinct()
			for groupitem in groupitems:
				catalog = Catalog.objects.select_related('brand').get(pk=groupitem['product__catalog'])
				catalogsjson = {}
				catalogsjson['name'] = catalog.title
				catalogsjson['brand'] = catalog.brand.name
				catalogsjson['id'] = catalog.id
				products = []

				filtereditems = order.items.filter(product__catalog=groupitem['product__catalog'], is_full_catalog=groupitem['is_full_catalog'], note=groupitem['note']).select_related('product__catalog', 'product__catalog__category')

				if groupitem['is_full_catalog'] == True:
					cartwiseProductOrderArray(catalogs, filtereditems, catalogsjson)
				else:
					for filtereditem in filtereditems:
						cartwiseProductOrderArray(catalogs, [filtereditem], catalogsjson)


		orderjson['catalogs'] = catalogs

		return Response(orderjson)

	@detail_route(methods=['GET'], serializer_class = SalesOrderSerializer)
	def catalogs(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()
		order = self.filter_queryset(queryset)
		catalogids = order.items.values_list('product__catalog', flat=True)
		catalogs = Catalog.objects.filter(id__in=catalogids).values('id','title')

		return Response(list(catalogs))

	@detail_route(methods=['POST'], serializer_class = SalesOrderSerializer)
	def payment(self, request, pk=None, companies_pk=None):
		user = request.user

		data = request.data

		amount = data.get('amount', None)
		mode = data.get('mode', None)
		trasactiondate = data.get('date', None)
		details = data.get('details', None)

		generateOrderToInvoice(pk, amount, mode, data, user, None, trasactiondate, details)

		return Response({"success":"Payment done successfully."})

class BrokerageOrderViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SalesOrder.objects.all()
	serializer_class = SalesOrderSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrUserSalesOrderObj, )

	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('GET'):
			serializer_class = GetSalesOrderSerializer

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetExpandSalesOrderSerializer

		return serializer_class

	def get_queryset(self):
		#queryset = SalesOrder.objects.all().select_related('company','seller_company','user').order_by('-id')
		queryset = SalesOrder.objects.all()
		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			queryset = queryset.select_related('company__city','company__state','company__country','company__chat_admin_user','company__companycreditrating', 'seller_company__city','seller_company__state','seller_company__country','seller_company__chat_admin_user','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related('items__product__catalog__category','invoice_set__items__order_item__product__catalog__category','invoice_set__items__tax_class_1', 'invoice_set__items__tax_class_2', 'invoice_set__shipment_set', 'invoice_set__payments').order_by('-id')
		else:
			queryset = queryset.select_related('company__city','company__state','company__country','company__companycreditrating','seller_company__city','seller_company__state','seller_company__country','user','ship_to__city','ship_to__state','ship_to__country','ship_to__user').prefetch_related('items__product__catalog__category','invoice_set__items__order_item__product__catalog__category').order_by('-id')

		processing_status = self.request.query_params.get('processing_status', None)
		if processing_status is not None:
			if processing_status.lower() == "pending":
				queryset = queryset.filter(processing_status__in=["Draft","Pending","ordered","Accepted","In Progress", "COD Verification Pending", "Field Verification Pending"])
			if processing_status.lower() == "dispatch":
				queryset = queryset.filter(processing_status__in=["Dispatched","Delivered","Partially Dispatched","Closed"])
			if processing_status.lower() == "cancel":
				queryset = queryset.filter(processing_status__in=["Cancelled","Transferred"])
			if processing_status.lower() == "placed":
				queryset = queryset.exclude(processing_status__in=["Cart"])

		user = self.request.user

		if user.is_staff:
			return queryset

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(broker_company=company)
			except ObjectDoesNotExist:
				return queryset.none()
		return queryset.none()

	def perform_create(self, serializer):
		print "in perform_create"
		serializer.save(user=self.request.user)

	@detail_route(methods=['GET'], serializer_class = SalesOrderSerializer)
	def catalogwise(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()
		order = self.filter_queryset(queryset)

		orderjson = self.get_serializer(instance=order)
		#orderjson = GetSalesOrderSerializer(instance=order)
		orderjson = orderjson.data


		catalogs = []

		catalogarr = []
		for item in order.items.all():
			if item.product.catalog is not None:
				if item.product.catalog not in catalogarr:
					catalogarr.append(item.product.catalog)

		for catalog in catalogarr:
			catalogsjson = {}
			catalogsjson['name'] = catalog.title
			catalogsjson['brand'] = catalog.brand.name
			catalogsjson['id'] = catalog.id
			products = []

			for item in order.items.filter(product__catalog=catalog):
				product = SalesOrderItemSerializer(instance=item)
				product = product.data
				products.append(product)

			catalogsjson['products'] = products
			catalogsjson['total_products'] = len(products)
			catalogs.append(catalogsjson)


		orderjson['catalogs'] = catalogs

		return Response(orderjson)

	@list_route(methods=['get'])
	def report(self, request, companies_pk=None):
		loginUser = request.user

		loginCompany = loginUser.companyuser.company

		dateList = []

		todayDate = date.today()

		OneMonthStartDate = todayDate - timedelta(days=30)
		ThreeMonthStartDate = todayDate - timedelta(days=90)
		OneYearStartDate = todayDate - timedelta(days=365)

		dateList.append(["1 Month",OneMonthStartDate,todayDate]);
		dateList.append(["3 Month",ThreeMonthStartDate,todayDate]);
		dateList.append(["1 Year",OneYearStartDate,todayDate]);
		jsonArr = []

		companies = SalesOrder.objects.filter(broker_company=loginCompany, created_at__gte=datetime.combine(OneYearStartDate, time.min), created_at__lte=datetime.combine(todayDate, time.max)).values_list('seller_company', flat=True).distinct()
		for company in companies:
			print "brokerage report company=",company
			company = Company.objects.get(pk=company)

			monthlyJson = []
			OneYearBrokerageSort = 0
			for dates in dateList:
				salesOrders = SalesOrder.objects.filter(seller_company=company, broker_company=loginCompany, created_at__gte=datetime.combine(dates[1], time.min), created_at__lte=datetime.combine(dates[2], time.max))

				TotalBrokerage = 0
				for salesOrder in salesOrders:
					TotalBrokerage += salesOrder.total_rate() * salesOrder.brokerage_fees / 100

				OneYearBrokerageSort = TotalBrokerage
				monthlyJson.append({"month":dates[0],"total_brokerage":str(round(TotalBrokerage, 2))})

			if OneYearBrokerageSort > Decimal('0.1'):
				buyerObj = Buyer.objects.filter(selling_company=company, buying_company=loginCompany).first()
				supplier_id = None
				if buyerObj:
					supplier_id = buyerObj.id
				jsonArr.append({"company":company.name, "company_id":company.id, "brokerage_in":monthlyJson, "sort_by":str(round(OneYearBrokerageSort, 2)), "phone_number":company.phone_number, "state":company.state.state_name, "city":company.city.city_name, "chat_user":company.chat_admin_user.username, "supplier_id":supplier_id})

		#sorting json custom field push_id
		records = sorted(jsonArr, key=lambda k: k['sort_by'], reverse=True)
		records = records[0:5]

		return Response(records)



class ProductLikeViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = ProductLike.objects.all()
	serializer_class = ProductLikeSerializer

	def get_queryset(self):
		queryset = ProductLike.objects.all().select_related('user')

		product = self.request.query_params.get('product', None)
		if product is not None:
			queryset = queryset.filter(product=product)

		user = self.request.user

		return queryset.filter(user=user)

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)

	def list(self, request, products_pk=None):
		print products_pk
		instance = self.get_queryset().filter(product=products_pk)

		serializer = self.get_serializer(instance, many=True)
		return Response(serializer.data)


class SelectionViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Selection.objects.all()
	serializer_class = SelectionSerializer
	permission_classes = (IsOwnerOrAdmin, )

	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH','POST'):
			serializer_class = SelectionSerializer
		else:
			serializer_class = GetSelectionSerializer

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetSelectionWithProductSerializer

		return serializer_class
	def perform_create(self, serializer):
		serializer.save(user=self.request.user)

	def get_queryset(self):
		queryset = self.queryset
		queryset = queryset.select_related('user').prefetch_related('products').order_by('-id')

		buyable = self.request.query_params.get('buyable', None)
		if buyable is not None and buyable.lower() == "true":
			queryset = queryset.filter(buyable = True)
		if buyable is not None and buyable.lower() == "false":
			queryset = queryset.filter(buyable = False)

		selectionType = self.request.query_params.get('type', None)
		company = self.request.query_params.get('company', None)

		user = self.request.user

		try:
			if user.is_authenticated() and user.companyuser.company is not None:
				companyuser = user.companyuser.company

				if user.groups.filter(name="salesperson").exists():
					pushUserSelectionId = Push_User.objects.filter(selling_company=companyuser).exclude(selection__isnull=True).order_by('selection').values_list('selection', flat=True).distinct()
				else:
					if company is not None:
						sellingCompanyObj = Buyer.objects.filter(selling_company = company, buying_company=companyuser, status="approved").values_list('selling_company', flat=True).distinct()

						pushUserSelectionId = Push_User.objects.filter(buying_company=companyuser, selling_company__in=sellingCompanyObj).exclude(selection__isnull=True).order_by('selection').values_list('selection', flat=True).distinct()#user=user,
					else:
						sellingCompanyObj = Buyer.objects.filter(buying_company=companyuser, status="approved").values_list('selling_company', flat=True).distinct()

						pushUserSelectionId = Push_User.objects.filter(buying_company=companyuser, selling_company__in=sellingCompanyObj).exclude(selection__isnull=True).order_by('selection').values_list('selection', flat=True).distinct()#user=user,

				is_disable = self.request.query_params.get('is_disable', 'false')
				company = companyuser
				'''selling_company = Buyer.objects.filter(buying_company=company).exclude(selling_company__isnull=True).values_list('selling_company', flat=True).distinct().order_by('selling_company')
				selling_company = list(selling_company)
				selling_company.append(company.id)
				disableSelectionIds = CatalogSelectionStatus.objects.filter(company__in=selling_company, status='Disable').exclude(selection__isnull=True).values_list('selection', flat=True).distinct()'''
				disableSelectionIds = CatalogSelectionStatus.objects.filter(company=company, status='Disable').exclude(selection__isnull=True).values_list('selection', flat=True).distinct()
				#print selling_company
				if is_disable.lower() == 'true':
					queryset = queryset.filter(id__in=disableSelectionIds)
				#else:
				#	queryset = queryset.exclude(id__in=disableSelectionIds)


				if selectionType is not None:
					if selectionType.lower() == "push":
						return queryset.filter(id__in=pushUserSelectionId)
					elif selectionType.lower() == "my":
						return queryset.filter(user=user)

				return queryset.filter(Q(id__in=pushUserSelectionId) | Q(user=user))

		except ObjectDoesNotExist:
			return Selection.objects.none()

	def perform_destroy(self, instance):#delete photo from picasa
		if not Push_User.all_objects.filter(selection=instance.id).exists():
			instance.delete()
		else:
			raise serializers.ValidationError({"Selection":"Can not delete shared selection"})

	@detail_route(methods=['GET'])
	def suppliers(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()

		companyId = None
		try:
			selectionObj = queryset#Selection.objects.get(pk=data['selection'])
			currentUser = request.user
			if currentUser.is_authenticated():
				currentUserCompany = currentUser.companyuser.company

				if currentUser.groups.filter(name="salesperson").exists():
					companyId = currentUserCompany.id
				else:
					'''pushUserObjId = Push_User.objects.filter(buying_company=currentUserCompany, selection=selectionObj.id).values('buying_company','selection','selling_company').annotate(Max('id')).values('id__max')#user=currentUser
					pushUser = Push_User.objects.filter(id__in=pushUserObjId).order_by('total_price').first()
					companyId = pushUser.selling_company.id'''

					cpfObj = CompanyProductFlat.objects.filter(buying_company=currentUserCompany, is_disable=False, selection=selectionObj.id).select_related('selling_company').last()
					companyId = cpfObj.selling_company.id

		except Exception as e:
			raise serializers.ValidationError({"selling_company":None})
		return Response({"selling_company": companyId})

	@detail_route(methods=['GET', 'POST'])
	def enable(self, request, pk=None, companies_pk=None):
		user = request.user
		company = user.companyuser.company

		queryset = self.get_object()

		psObj = CatalogSelectionStatus.objects.get_or_create(company=company, selection=queryset)
		psObj = CatalogSelectionStatus.objects.filter(company=company, selection=queryset).first()
		psObj.user = user
		psObj.status="Enable"
		psObj.save()

		return Response({"success": "Selection has been enable"})

	@detail_route(methods=['GET', 'POST'])
	def disable(self, request, pk=None, companies_pk=None):
		user = request.user
		company = user.companyuser.company

		queryset = self.get_object()

		psObj = CatalogSelectionStatus.objects.get_or_create(company=company, selection=queryset)
		psObj = CatalogSelectionStatus.objects.filter(company=company, selection=queryset).first()
		psObj.user = user
		psObj.status="Disable"
		psObj.save()

		return Response({"success": "Selection has been disabled"})

	@list_route(methods=['get'])
	def dropdown(self, request, catalogs_pk=None):
		queryset = self.get_queryset().values('id','name')
		queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

	'''@detail_route(methods=['get'])
	def brandwise(self, request, pk=None, companies_pk=None):
		user = request.user
		company = user.companyuser.company


		queryset = self.get_object()

		brands = []

		brandarr = []
		for item in queryset.products.all().select_related('catalog__brand'):
			brand = item.catalog.brand
			if brand is not None and brand not in brandarr:
					brandarr.append(brand)

		for brand in brandarr:
			brandsjson = {}
			brandsjson['brand_name'] = brand.name
			brandsjson['id '] = brand.id

			catalogs = []
			catalogarr = []
			for item in queryset.products.filter(catalog__brand=brand).select_related('catalog'):
				catalog = item.catalog
				if catalog is not None and catalog not in catalogarr:
						catalogarr.append(catalog)

			for catalog in catalogarr:
				catalogsjson = {}
				catalogsjson['catalog_name'] = catalog.title
				#catalogsjson['brand'] = catalog.brand.name
				catalogsjson['id'] = catalog.id
				products = []

				for item in queryset.products.filter(catalog=catalog).select_related('catalog'):
					product = SelectionPOSProductSerializer(instance=item)
					product = product.data

					pushUserObjId = Push_User_Product.objects.filter(buying_company=company, product=item.id).values('user','selection','selling_company').annotate(Max('id')).values('id__max')
					pushUser = Push_User_Product.objects.filter(id__in=pushUserObjId).order_by('price').first()
					if pushUser:
						selling_company = Push_User_Product.objects.filter(id__in=pushUserObjId).distinct().values('selling_company', 'selling_company__name', 'price').order_by('price', 'selling_company')#pushUser.selling_company.id

						scarr = []
						for sc in selling_company:
							scjson = {}
							scjson['id'] = sc['selling_company']
							scjson['name'] = sc['selling_company__name']
							scjson['price'] = sc['price']
							scarr.append(scjson)

						product['selling_company'] = scarr #list(selling_company)
						product['price'] = pushUser.price
					else:
						product['selling_company'] = []

					products.append(product)

				catalogsjson['products'] = products
				catalogsjson['total_products'] = len(products)
				catalogs.append(catalogsjson)
			brandsjson['catalogs'] = catalogs
			brands.append(brandsjson)

		return Response(brands)'''

class PushViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Push.objects.all()
	serializer_class = PushSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrUserOrReadOnly, )

	pagination_class = CustomPagination

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		#if self.request.method in ('PUT','PATCH','POST','OPTIONS'):
		#		serializer_class = PushSerializer
		if self.request.method == 'GET':
				serializer_class = GetPushSerializer
		return serializer_class
	def perform_create(self, serializer):
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(user=user, company=company)
	def get_queryset(self):
		queryset = Push.objects.filter(to_show="yes").select_related('buyer_segmentation').order_by('-id')

		viewType = self.request.query_params.get('view_type', None)

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				#if viewType is not None:
				#	if viewType.lower()=="mysent":
				#		queryset = queryset.filter(user=user)

				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return Push.objects.none()
		except ObjectDoesNotExist:
			return Push.objects.none()

	@detail_route(methods=['get'])
	def buyerwise(self, request, pk=None):
		queryset = self.get_object()

		jsonArr = {}
		jsonArr['id'] = queryset.id

		jsonArr['total_products_viewed'] = queryset.total_products_viewed()

		pushUserObj = Push_User.all_objects.filter(push=queryset.id).first()

		if pushUserObj is not None and pushUserObj.catalog is not None:
			jsonArr['catalog_name'] = pushUserObj.catalog.title
		elif pushUserObj is not None and pushUserObj.selection is not None:
			jsonArr['catalog_selection'] = pushUserObj.selection.name

		buyers = []

		puids = Push_User.all_objects.filter(push=queryset.id, selling_company=queryset.company).values_list('buying_company', flat=True)
		buyerObjs = Buyer.objects.filter(selling_company=queryset.company, status='approved', buying_company__in=puids)

		for buyerObj in buyerObjs:
			buyer = {}
			buyer['buying_company_name'] = buyerObj.buying_company.name
			#buyer['total_products_viewed'] = Push_User_Product.all_objects.filter(push=queryset.id, is_viewed='yes', buying_company=buyerObj.buying_company).count()
			##buyer['total_products_viewed'] = CompanyProductFlat.objects.filter(push_reference=queryset.id, is_viewed='yes', buying_company=buyerObj.buying_company).count()
			buyer['total_products_viewed'] = 0
			if pushUserObj is not None and pushUserObj.catalog is not None:
				buyer['total_products_viewed'] = CompanyProductView.objects.filter(product__in=pushUserObj.catalog.products.all(), company=buyerObj.buying_company).count()
			buyer['push_downstream'] = queryset.push_downstream

			buyer['downstream_stats'] = {}
			buyer['downstream_stats']['total_buyers'] = Push_User.all_objects.filter(push=queryset.id, selling_company=buyerObj.buying_company).count()
			subBuyers= Push_User.all_objects.filter(push=queryset.id, selling_company=buyerObj.buying_company).values_list('buying_company', flat=True).distinct()
			#buyer['downstream_stats']['total_products_viewed'] = Push_User_Product.all_objects.filter(push=queryset.id, is_viewed='yes', selling_company=buyerObj.buying_company).count()
			##buyer['downstream_stats']['total_products_viewed'] = CompanyProductFlat.objects.filter(push_reference=queryset.id, is_viewed='yes', selling_company=buyerObj.buying_company).count()

			ccvclicks = CompanyCatalogView.objects.filter(catalog=pushUserObj.catalog, company__in=subBuyers).aggregate(Sum('clicks')).get('clicks__sum', 0)
			if ccvclicks is None:
				ccvclicks = 0

			buyer['downstream_stats']['total_products_viewed'] = ccvclicks #CompanyCatalogView.objects.filter(catalog=pushUserObj.catalog, company__in=subBuyers).count()
			'''totalbuyers = Push_User.all_objects.filter(push=queryset.id, selling_company=buyerObj.buying_company).count()
			totalProductsViewed = Push_User_Product.all_objects.filter(push=queryset.id, is_viewed='yes', selling_company=buyerObj.buying_company).count()
			subbuyersarr = Push_User.all_objects.filter(push=queryset.id, selling_company=buyerObj.buying_company).values_list('buying_company', flat=True)
			while (len(subbuyersarr) > 0):
				totalbuyers += Push_User.all_objects.filter(push=queryset.id, selling_company__in=subbuyersarr).count()
				totalProductsViewed += Push_User_Product.all_objects.filter(push=queryset.id, is_viewed='yes', selling_company__in=subbuyersarr).count()
				subbuyersarr = Push_User.all_objects.filter(push=queryset.id, selling_company__in=subbuyersarr).values_list('buying_company', flat=True)
			buyer['downstream_stats']['total_buyers'] = totalbuyers
			buyer['downstream_stats']['total_products_viewed'] = totalProductsViewed'''

			buyers.append(buyer)

		#sorting json custom field push_id
		records = sorted(buyers, key=lambda k: k['total_products_viewed'], reverse=True)

		jsonArr['buyers'] = records
		return Response(jsonArr)

	@detail_route(methods=['get'])
	def designwise(self, request, pk=None):
		queryset = self.get_object()

		jsonArr = {}
		jsonArr['id'] = queryset.id

		jsonArr['total_products_viewed'] = queryset.total_products_viewed()

		pushUserObj = Push_User.all_objects.filter(push=queryset.id).first()

		product_ids = []
		if pushUserObj is not None and pushUserObj.catalog is not None:
			jsonArr['catalog_name'] = pushUserObj.catalog.title
			product_ids = Product.objects.filter(catalog=pushUserObj.catalog).values_list('id', flat=True)
		elif pushUserObj is not None and pushUserObj.selection is not None:
			jsonArr['catalog_selection'] = pushUserObj.selection.name
			product_ids = pushUserObj.selection.products.all().values_list('id', flat=True)

		products = []

		productObjs = Product.objects.filter(id__in=product_ids)

		buyers = Push_User.all_objects.filter(push=queryset.id).values_list('buying_company', flat=True).distinct()
		#print buyers
		total_users = queryset.total_users()

		for productObj in productObjs:
			product = {}
			product['sku'] = productObj.sku
			#product['total_buyers_viewed'] = Push_User_Product.all_objects.filter(push=queryset.id, is_viewed='yes', product=productObj).count()
			##product['total_buyers_viewed'] = CompanyProductFlat.objects.filter(push_reference=queryset.id, is_viewed='yes', product=productObj).count()

			product['total_buyers_viewed'] = CompanyProductView.objects.filter(product=productObj, company__in=buyers).count()

			#product['total_shares'] = Push_User_Product.all_objects.filter(product=productObj).values('push').distinct().count()
			#product['total_shares'] = CompanyProductFlat.objects.filter(product=productObj).values('push_reference').distinct().count()
			product['total_shares'] = total_users

			products.append(product)

		#sorting json custom field push_id
		records = sorted(products, key=lambda k: k['total_buyers_viewed'], reverse=True)

		jsonArr['products'] = records
		return Response(jsonArr)

class CountryViewSet(viewsets.ModelViewSet):
	queryset = Country.objects.all()
	serializer_class = CountrySerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

class StateViewSet(viewsets.ModelViewSet):
	queryset = State.objects.all().order_by('state_name')
	serializer_class = StateSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

	def get_queryset(self):
		queryset = self.queryset

		ordering = self.request.query_params.get('ordering', None)
		if ordering is not None and ordering == "catalogwise":
			user = self.request.user
			company = get_user_company(user)

			urlPath = "state_ordering_catalogs"
			result = cache.get(urlPath)
			if result:
				queryset = result
			else:
				querysetcatalogs = Catalog.objects.filter(deleted=False)
				params = {}
				params["view_type"] = "public"
				publicCatalogs = catalogQuerysetFilter(querysetcatalogs, company, params, user, "list")

				# dtnow = datetime.now()
				# stateids = Catalog.objects.filter(deleted=False, catalog_type='catalog', expiry_date__gt=dtnow, total_products_uploaded__gt=0).values('company__state').annotate(total_catalogs = Count('id')).order_by('-total_catalogs').values_list('company__state', flat=True)
				stateids = publicCatalogs.values('company__state').annotate(total_catalogs = Count('id')).order_by('-total_catalogs').values_list('company__state', flat=True)

				preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(list(stateids))])
				queryset = queryset.filter(id__in=stateids).order_by(preserved)

				cache.set(urlPath, queryset, settings.CACHE_EXPIRE_TIME)

		return queryset

class CityViewSet(viewsets.ModelViewSet):
	queryset = City.objects.all().order_by('city_name')
	serializer_class = CitySerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
	def get_queryset(self):
		queryset = self.queryset
		queryset = queryset.select_related('state')
		'''stateId = self.request.query_params.get('state', None)
		if stateId is not None:
			queryset = queryset.filter(state=stateId)'''


		stateIds = self.request.query_params.get('state', None)
		if stateIds is not None and stateIds != "":
			stateids = stateIds.split(',')
			queryset = queryset.filter(state__in=stateids)

		return queryset

class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = Category.objects.all().prefetch_related('child_category__child_category__child_category').order_by('-sort_order', '-id')
		parentId = self.request.query_params.get('parent', None)
		if parentId is not None and parentId.lower()=="null":
			queryset = queryset.filter(parent_category__isnull=True)
		elif parentId is not None:
			queryset = queryset.filter(parent_category=parentId)

		is_home_display = self.request.query_params.get('is_home_display', None) #1 = True, 0=False
		if is_home_display is not None and is_home_display != "":
			queryset = queryset.filter(is_home_display=is_home_display)

		return queryset

class WishbookInvoiceViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = WishbookInvoice.objects.all()
	serializer_class = WishbookInvoiceSerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = WishbookInvoice.objects.all().order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return WishbookInvoice.objects.none()
		except ObjectDoesNotExist:
			return WishbookInvoice.objects.none()

class WishbookCreditViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = WishbookCredit.objects.all()
	serializer_class = WishbookCreditSerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = WishbookCredit.objects.all().order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return WishbookCredit.objects.none()
		except ObjectDoesNotExist:
			return WishbookCredit.objects.none()

class WishbookPaymentViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = WishbookPayment.objects.all()
	serializer_class = WishbookPaymentSerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = WishbookPayment.objects.all().order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return WishbookPayment.objects.none()
		except ObjectDoesNotExist:
			return WishbookPayment.objects.none()

class GroupTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = GroupType.objects.all()
	serializer_class = GroupTypeSerializer

class CompanyPhoneAliasViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyPhoneAlias.objects.all()
	serializer_class = CompanyPhoneAliasSerializer

	def get_queryset(self):
		queryset = CompanyPhoneAlias.objects.all().select_related('company').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return CompanyPhoneAlias.objects.none()
		except ObjectDoesNotExist:
			return CompanyPhoneAlias.objects.none()
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)

	def partial_update(self, request, pk=None, companies_pk=None):
		#instance = self.get_object()
		data=request.data
		print data

		companyphonealias = self.get_object()

		registrationOtp = RegistrationOTP.objects.filter(phone_number=companyphonealias.alias_number, country=companyphonealias.country).order_by('-id').first()

		otp = data.get('otp', None)

		if registrationOtp is not None and otp is not None and str(registrationOtp.otp) == otp:
			registrationOtp.is_verified = "yes"
			registrationOtp.save()

			companyphonealias.status = "Approved"
			companyphonealias.save()

			user = request.user
			company = user.companyuser.company

			##start make default buyer/supplier..copied from registration serializer
			makeBuyerSupplierFromInvitee(companyphonealias.alias_number, companyphonealias.country, company)
			##end make default buyer/supplier

			full_mobile_number = str(registrationOtp.country.phone_code)+str(registrationOtp.phone_number)
			verifyMSG91OTP(full_mobile_number, otp)

			#return Response({"success": "Number has been verified"})
			serializer = self.get_serializer(companyphonealias)
			return Response(serializer.data)
		elif otp is None:
			'''otp = random.randrange(100000, 999999, 1)

			sendOTP(str(companyphonealias.country.phone_code)+str(companyphonealias.alias_number), str(otp))

			registrationOtp = RegistrationOTP.objects.create(phone_number=companyphonealias.alias_number, otp=otp, country=companyphonealias.country)
			'''
			checkAndSendOTP(companyphonealias.alias_number, companyphonealias.country)

			return Response({"success": "OTP has been sent successfully"})

		raise serializers.ValidationError({"otp":"Please enter valid OTP"})

class CompanyPriceListViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyPriceList.objects.all()
	serializer_class = CompanyPriceListSerializer
	def get_queryset(self):
		queryset = CompanyPriceList.objects.all().select_related('company').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return CompanyPriceList.objects.none()
		except ObjectDoesNotExist:
			return CompanyPriceList.objects.none()
	def perform_create(self, serializer):
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)

class CompanyBuyerGroupViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyBuyerGroup.objects.all()
	serializer_class = CompanyBuyerGroupSerializer
	def get_queryset(self):
		queryset = CompanyBuyerGroup.objects.all().select_related('company').order_by('-id')

		user = self.request.user

		buyer_type = self.request.query_params.get('buyer_type', None)
		if buyer_type is not None and buyer_type != "":
			queryset = queryset.filter(buyer_type=buyer_type)

		supplier = self.request.query_params.get('supplier', None)
		if supplier:
			try:
				company = user.companyuser.company
				buyerObj = Buyer.objects.filter(selling_company=supplier, buying_company=company).last()
				if buyerObj is not None and buyerObj.group_type is not None:
					buyer_type = companyBuyerGroupType(buyerObj.group_type.name)
					'''buyer_type = ""
					if buyerObj.group_type.name in ["Online-Retailer","Retailer"]:
						buyer_type = "Retailer"
					elif buyerObj.group_type.name in ["Broker"]:
						buyer_type = "Broker"
					else:
						buyer_type = "Wholesaler"'''

					return queryset.filter(company=supplier, buyer_type=buyer_type)
				return queryset.filter(company=supplier, buyer_type="Public")
			except ObjectDoesNotExist:
				return queryset.none()

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		#~ user_company = (user.companyuser.company is not None)
		#~ if user_company:
			#~ company = user.companyuser.company
		company = get_user_company(user)

		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		serializer.save(company=company)

class BuyerSegmentationViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = BuyerSegmentation.objects.all()
	serializer_class = BuyerSegmentationSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		#if self.request.method in ('PUT','PATCH'):
		#		serializer_class = BuyerSegmentationSerializer
		if self.request.method == 'GET':
				serializer_class = GetBuyerSegmentationSerializer
		return serializer_class
	def perform_create(self, serializer):
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)
	def get_queryset(self):
		queryset = BuyerSegmentation.objects.all().prefetch_related('city','category','group_type').order_by('id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				if user.groups.filter(name="salesperson").exists() and company.buyers_assigned_to_salesman == True:
					if AssignGroups.objects.filter(user=user).exists():
						agObj = AssignGroups.objects.get(user=user)
						ids = agObj.groups.values_list('id', flat=True)
						queryset = queryset.filter(id__in = ids)
					else:
						queryset = queryset.none()

				return queryset.filter(company=company)
			else:
				return BuyerSegmentation.objects.none()
		except ObjectDoesNotExist:
			return BuyerSegmentation.objects.none()

	@list_route(methods=['get'])
	def dropdown(self, request, companies_pk=None):
		queryset = self.get_queryset().values('id','segmentation_name')
		queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

	'''@detail_route(methods=['get'], serializer_class = StockV1ListSerializer)
	def create_applozic_group(self, request, pk=None):
		buyersegment = self.get_object()

		#user = CompanyUser.objects.filter(company=buyersegment.company).first().user
		user = buyersegment.company.chat_admin_user

		group_type = buyersegment.group_type.values_list('id', flat=True)
		if buyersegment.city.count() == 0:
			city = City.objects.all().values_list('id', flat=True)
		else:
			city = buyersegment.city.values_list('id', flat=True)
		if buyersegment.category.count() == 0:
			category = Category.objects.all().values_list('id', flat=True)
		else:
			category = buyersegment.category.values_list('id', flat=True)

		#usrnames = Buyer.objects.filter(selling_company=buyersegment.company, status="approved", group_type__in=group_type, buying_company__city__in=city, buying_company__category__in=category).values_list('buying_company__chat_admin_user__username', flat=True)
		usrnames = Buyer.objects.filter(Q(selling_company=buyersegment.company, status="approved", group_type__in=group_type, buying_company__category__in=category) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).values_list('buying_company__chat_admin_user__username', flat=True)
		usrnames = list(usrnames)

		r = chat_create_group({"ofUserId":user.username, "groupName":user.username+" "+buyersegment.segmentation_name, "groupMemberList":usrnames, "type":"5"}, {'task':'set_segmentation_applozic_id', 'company':buyersegment.company.id, 'segmentation':buyersegment.id})
		#r = r.json()
		print r

		return Response(serializer.data)'''

class CompanyTypeListViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyType.objects.all()
	serializer_class = CompanyTypeSerializer
	def get_queryset(self):
		queryset = CompanyType.objects.filter(company__discovery_ok=True).select_related('company__city').order_by('-id')

		state = self.request.query_params.get('state', None)
		if state is not None:
			queryset = queryset.filter(company__state=state)

		city = self.request.query_params.get('city', None)
		if city is not None:
			queryset = queryset.filter(company__city=city)

		category = self.request.query_params.get('category', None)
		if category is not None:
			queryset = queryset.filter(company__category=category)

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return CompanyType.objects.none()
		except ObjectDoesNotExist:
			return CompanyType.objects.none()

class AppV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = App.objects.all()
	serializer_class = AppV1Serializer
	#versioning_class = versioning.QueryParameterVersioning
	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('name', 'api_min_version', 'api_max_version',)
	search_fields = ('name', 'api_min_version', 'api_max_version',)
	#permission_classes = (permissions.IsAdminUser,)

	'''def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH','POST'):
				serializer_class = AppV1Serializer
		elif self.request.query_params.get('instances', None):
			serializer_class = AppExpandV1Serializer
		else:
			serializer_class = AppV1Serializer
		return serializer_class'''

	'''@detail_route(methods=['get'])
	def instance(self, request, pk=None):
		#queryset = App.objects.all()
		queryset = App.objects.get(pk=pk)

		#serializer = AppExpandV1Serializer(instance=queryset, many=True)
		serializer = AppExpandV1Serializer(instance=queryset)
		return Response(serializer.data)'''

class AppMapInstanceV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = AppInstance.objects.all()
	serializer_class = AppInstanceV1Serializer
	#versioning_class = versioning.QueryParameterVersioning
	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('app', 'company', )
	search_fields = ('app__name', 'company__id', )
	#permission_classes = (permissions.IsAdminUser,)

	def get_queryset(self):
		return AppInstance.objects.filter(
			app=self.kwargs['app_id']
		)

class AppInstanceV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = AppInstance.objects.all()
	serializer_class = AppInstanceV1Serializer
	#versioning_class = versioning.QueryParameterVersioning
	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('app', 'company', )
	search_fields = ('app__name', 'company__id', )
	#permission_classes = (permissions.IsAdminUser,)

	def get_queryset(self):
		user = self.request.user
		company = user.companyuser.company

		queryset = AppInstance.objects.filter(company=company)

		return queryset

	#def get_serializer_class(self):
	#	return AppInstanceV1Serializer


'''class SKUMapSkuV1ViewSet(viewsets.ModelViewSet):
	queryset = SKUMap.objects.none()
	serializer_class = SKUMapV1Serializer
	#versioning_class = versioning.QueryParameterVersioning
	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('app_instance', 'product', 'external_sku',)
	search_fields = ('product__sku','external_sku',)
	#permission_classes = (permissions.IsAdminUser,)

	def get_queryset(self):
		return SKUMap.objects.get(
			pk = 1
			#external_sku=self.kwargs['sku']
		)'''

class SKUMapV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SKUMap.objects.none()
	serializer_class = SKUMapV1Serializer
	#versioning_class = versioning.QueryParameterVersioning
	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('app_instance', 'product', 'external_sku',)
	search_fields = ('product__sku','external_sku',)
	#permission_classes = (permissions.IsAdminUser,)

	#def get_serializer_class(self):
	#	return SKUMapV1Serializer

	def get_queryset(self):
		user = self.request.user
		#if not CompanyUser.objects.filter(user=user).exists():
		#	return self.queryset.none()

		company = user.companyuser.company

		sku = self.request.query_params.get('sku', None)

		if sku is not None:
			return SKUMap.objects.filter(external_sku = sku, app_instance__company = company)#.select_related('app_instance', 'product')

		queryset = SKUMap.objects.filter(app_instance__company = company).select_related('app_instance', 'product')

		return queryset

	'''@list_route(methods=['get'])
	def sku(self, request, pk=None):
		user = self.request.user
		company = user.companyuser.company

		queryset = SKUMap.objects.filter(app_instance__company = company).select_related('app_instance', 'product')

		serializer = SKUMapV1Serializer(instance=queryset, many=True)
		return Response(serializer.data)'''

class SalesOrderItemViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SalesOrderItem.objects.all()
	serializer_class = SalesOrderItemSerializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'sales_order', 'product', 'quantity', 'rate', 'pending_quantity', )
	search_fields = ('id', 'sales_order__id', 'product__id', 'quantity', 'rate', 'pending_quantity', )

	def get_queryset(self):
		queryset = SalesOrderItem.objects.all().select_related('product').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and user.companyuser.company is not None:
				company = user.companyuser.company
				queryset = queryset.filter(sales_order__seller_company=company)
		except ObjectDoesNotExist:
			return SalesOrderItem.objects.none()

		return queryset

class PurchaseOrderItemViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SalesOrderItem.objects.all()
	serializer_class = SalesOrderItemSerializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'sales_order', 'product', 'quantity', 'rate', 'pending_quantity', )
	search_fields = ('id', 'sales_order__id', 'product__id', 'quantity', 'rate', 'pending_quantity', )

	def get_queryset(self):
		queryset = SalesOrderItem.objects.all().select_related('product').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and user.companyuser.company is not None:
				company = user.companyuser.company
				queryset = queryset.filter(sales_order__company=company)
		except ObjectDoesNotExist:
			return SalesOrderItem.objects.none()

		return queryset

'''
class SalesOrderV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = SalesOrder.objects.all()
	serializer_class = SalesOrderV1Serializer
	permission_classes = (IsCompanyAdministratorOrAdminOrUserSalesOrderObj, )

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'order_number', 'company', 'date', 'time', 'processing_status', 'customer_status', 'user','items','sales_image','purchase_image', 'seller_company', 'note', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'broker_company', 'seller_ref',)
	search_fields = ('id', 'order_number', 'company__id', 'date', 'time', 'processing_status', 'customer_status', 'user__username', 'seller_company__id', 'note', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'broker_company__id', 'seller_ref',)

	def get_queryset(self):
		queryset = SalesOrder.objects.all().select_related('company','seller_company','user').prefetch_related('items__product').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					return queryset.filter(seller_company=company)#(user__companyuser__company=company)
				else:
					return queryset.filter(user=user)
			else:
				return SalesOrder.objects.none()
		except ObjectDoesNotExist:
			return SalesOrder.objects.none()

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class PurchaseOrderItemV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = SalesOrderItem.objects.all()
	serializer_class = SalesOrderItemV1Serializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'sales_order', 'product', 'quantity', 'rate', 'pending_quantity', )
	search_fields = ('id', 'sales_order__id', 'product__id', 'quantity', 'rate', 'pending_quantity', )

	def get_queryset(self):
		queryset = SalesOrderItem.objects.all().select_related('product').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and user.companyuser.company is not None:
				company = user.companyuser.company
				queryset = queryset.filter(sales_order__company=company)
		except ObjectDoesNotExist:
			return SalesOrderItem.objects.none()


		return queryset

class PurchaseOrderV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = SalesOrder.objects.all()
	serializer_class = SalesOrderV1Serializer
	permission_classes = (IsCompanyAdministratorOrAdminOrUserSalesOrderObj, )

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'order_number', 'company', 'date', 'time', 'processing_status', 'customer_status', 'user','items','sales_image','purchase_image', 'seller_company', 'note', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'broker_company', 'seller_ref',)
	search_fields = ('id', 'order_number', 'company__id', 'date', 'time', 'processing_status', 'customer_status', 'user__username', 'seller_company__id', 'note', 'tracking_details', 'supplier_cancel', 'buyer_cancel', 'payment_details', 'payment_date', 'dispatch_date', 'broker_company__id', 'seller_ref',)

	def get_queryset(self):
		queryset = SalesOrder.objects.all().select_related('company','seller_company','user').prefetch_related('items__product').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					return queryset.filter(company=company)#(user__companyuser__company=company)
				else:
					return queryset.filter(user=user)
			else:
				return SalesOrder.objects.none()
		except ObjectDoesNotExist:
			return SalesOrder.objects.none()

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)'''

class WarehouseV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Warehouse.objects.all()
	serializer_class = WarehouseV1Serializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'company', 'name',)
	search_fields = ('id', 'company__id', '^name',)

	def get_queryset(self):
		queryset = Warehouse.objects.all().select_related('company').order_by('-id')

		user = self.request.user

		if user.is_staff:
			supplier = self.request.query_params.get('supplier', None)
			if supplier is not None:
				return queryset.filter(company=supplier)

		try:
			if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
				return queryset.filter(company=user.companyuser.deputed_to, salesmen__in=[user.id])
			elif user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return Warehouse.objects.none()
		except ObjectDoesNotExist:
			return Warehouse.objects.none()

	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)

class StockV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Stock.objects.all()
	serializer_class = StockV1Serializer

	#permission_classes = (StockV1Permission,)

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'warehouse', 'product', 'in_stock', 'blocked', 'open_sale', 'open_purchase', )
	search_fields = ('id', 'warehouse__id', 'product__id', 'in_stock', 'blocked', 'open_sale', 'open_purchase', )
	#ordering_fields = ('id', 'warehouse', 'product', 'in_stock', 'blocked', 'open_sale', 'open_purchase', ) #'__all__'
	ordering = ('-id',)

	#paginate_by = 2
	#renderer_classes = (JSONRenderer, )

	def perform_create(self, serializer):
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetStockV1Serializer

		return serializer_class

	def get_queryset(self):
		queryset = self.queryset
		queryset = queryset.select_related('company', 'product__catalog__brand')

		user = self.request.user
		if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
			return queryset.filter(company=user.companyuser.deputed_to, warehouse__salesmen__in=[user.id])
		company = user.companyuser.company
		return queryset.filter(company=company)

		'''try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(warehouse__company=company)
			else:
				return Stock.objects.none()
		except ObjectDoesNotExist:
			return Stock.objects.none()'''

	@list_route(methods=['get'], serializer_class = StockV1ListSerializer)
	def lists(self, request):
		queryset = self.get_queryset()
		queryset = self.filter_queryset(queryset)

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)


	@detail_route(methods=['get'], serializer_class = StockV1ListSerializer)
	def details(self, request, pk=None):
		queryset = self.get_object()#self.get_queryset().get(pk=pk)

		serializer = self.get_serializer(instance=queryset)
		return Response(serializer.data)

	@list_route(methods=['get'])
	def dropdown(self, request):
		queryset = self.get_queryset().values('id','product__title')
		queryset = self.filter_queryset(queryset)

		return Response(list(queryset))

	@list_route(methods=['get'])
	def dashboard(self, request):
		queryset = self.get_queryset()
		queryset = self.filter_queryset(queryset)

		arr = {}
		arr['in_stock'] = 0
		arr['blocked'] = 0
		arr['open_sale'] = 0
		arr['open_purchase'] = 0

		for stock in queryset:
			arr['in_stock'] += stock.in_stock
			arr['blocked'] += stock.blocked
			arr['open_sale'] += stock.open_sale
			arr['open_purchase'] += stock.open_purchase


		return Response(arr)

class BarcodeV1ViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Barcode.objects.all()
	serializer_class = BarcodeV1Serializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'warehouse', 'product', 'barcode', )
	search_fields = ('id', 'warehouse__id', 'product__id', 'barcode', )

	def get_queryset(self):
		queryset = Barcode.objects.all().select_related('warehouse__company', 'product').order_by('-id')

		user = self.request.user

		try:
			if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
				return queryset.filter(warehouse__company=user.companyuser.deputed_to, warehouse__salesmen__in=[user.id])
			elif user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(warehouse__company=company)
			else:
				return Barcode.objects.none()
		except ObjectDoesNotExist:
			return Barcode.objects.none()

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

class OpeningStockViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = OpeningStock.objects.all()
	serializer_class = OpeningStockSerializer
	def get_queryset(self):
		queryset = OpeningStock.objects.all().select_related('company').order_by('-id')

		user = self.request.user

		try:
			if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
				return queryset.filter(company=user.companyuser.deputed_to, warehouse__salesmen__in=[user.id])
			elif user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return OpeningStock.objects.none()
		except ObjectDoesNotExist:
			return OpeningStock.objects.none()

	def perform_create(self, serializer):
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company, user=user)

class OpeningStockQtyViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = OpeningStockQty.objects.all()
	serializer_class = OpeningStockQtySerializer

	'''def get_serializer(self, *args, **kwargs):
		if "data" in kwargs:
			data = kwargs["data"]
			if isinstance(data, list):
				kwargs["many"] = True

		return super(OpeningStockQtyViewSet, self).get_serializer(*args, **kwargs)'''

	def get_queryset(self):
		queryset = OpeningStockQty.objects.all().select_related('opening_stock__company').order_by('-id')

		user = self.request.user

		try:
			if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
				return queryset.filter(opening_stock__company=user.companyuser.deputed_to, opening_stock__warehouse__salesmen__in=[user.id])
			elif user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(opening_stock__company=company)
			else:
				return OpeningStockQty.objects.none()
		except ObjectDoesNotExist:
			return OpeningStockQty.objects.none()

class InventoryAdjustmentViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = InventoryAdjustment.objects.all()
	serializer_class = InventoryAdjustmentSerializer
	def get_queryset(self):
		queryset = InventoryAdjustment.objects.all().select_related('company').order_by('-id')

		user = self.request.user

		try:
			if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
				return queryset.filter(company=user.companyuser.deputed_to, warehouse__salesmen__in=[user.id])
			elif user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return InventoryAdjustment.objects.none()
		except ObjectDoesNotExist:
			return InventoryAdjustment.objects.none()

	def perform_create(self, serializer):
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company, user=user)

class InventoryAdjustmentQtyViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = InventoryAdjustmentQty.objects.all()
	serializer_class = InventoryAdjustmentQtySerializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'inventory_adjustment', 'quantity', 'adjustment_type', 'product', )
	search_fields = ('id', 'inventory_adjustment', 'quantity', 'adjustment_type', 'product', )
	#ordering_fields = ('id', 'warehouse', 'product', 'in_stock', 'blocked', 'open_sale', 'open_purchase', ) #'__all__'
	ordering = ('-id',)

	'''def get_serializer(self, *args, **kwargs):
		if "data" in kwargs:
			data = kwargs["data"]
			if isinstance(data, list):
				kwargs["many"] = True

		return super(InventoryAdjustmentQtyViewSet, self).get_serializer(*args, **kwargs)'''

	def get_queryset(self):
		queryset = InventoryAdjustmentQty.objects.all().select_related('inventory_adjustment__company').order_by('-id')

		user = self.request.user

		try:
			if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
				return queryset.filter(inventory_adjustment__company=user.companyuser.deputed_to, inventory_adjustment__warehouse__salesmen__in=[user.id])
			elif user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(inventory_adjustment__company=company)
			else:
				return InventoryAdjustmentQty.objects.none()
		except ObjectDoesNotExist:
			return InventoryAdjustmentQty.objects.none()

	#def perform_create(self, serializer):
	#	invAdj = InventoryAdjustment.objects.create(warehouse=warehouse)
	#	serializer.save(inventory_adjustment=invAdj)

class AttendanceViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Attendance.objects.all()
	serializer_class = AttendanceSerializer

	def get_queryset(self):
		#queryset = self.queryset.filter(user=user).order_by('-date_time')
		queryset = self.queryset.all().order_by('-date_time')

		userId = self.request.query_params.get('user', None)
		if userId is not None:
			queryset = queryset.filter(user=userId)

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				if user.groups.filter(name="administrator").exists():
					company = user.companyuser.company
					return queryset.filter(Q(user__companyuser__company=company) | Q(user__companyuser__deputed_to=company))
				else:
					return queryset.filter(user=user)
			else:
				return Attendance.objects.none()
		except ObjectDoesNotExist:
			return Attendance.objects.none()

	def perform_create(self, serializer):
		user = self.request.user
		company = user.companyuser.company
		if user.groups.filter(name="salesperson").exists() and user.companyuser.deputed_to is not None:
			company=user.companyuser.deputed_to
		serializer.save(user=user, company=company)

class CompanyAccountViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = CompanyAccount.objects.all()
	serializer_class = CompanyAccountSerializer
	def get_queryset(self):
		queryset = CompanyAccount.objects.all().select_related('company').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return CompanyAccount.objects.none()
		except ObjectDoesNotExist:
			return CompanyAccount.objects.none()

	def perform_create(self, serializer):
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)

class InvoiceViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Invoice.objects.all()
	serializer_class = InvoiceSerializer
	permission_classes = (permissions.IsAuthenticated,)

	#filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	#filter_fields = ('id', 'order', 'invoice_number', 'status',)
	#search_fields = ('id', 'order__id', 'invoice_number', 'status',)

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			print "expand"
			serializer_class = GetInvoiceSerializer

		return serializer_class

	@detail_route(methods=['POST'])
	def dispatched(self, request, pk=None, companies_pk=None):
		print "in dispatched ---------------"
		invoice = Invoice.objects.get(pk=pk) #self.get_object()
		print invoice

		if invoice.order.processing_status == "Cancelled":
			raise serializers.ValidationError({"processing_status":"This order was Calcelled."})

		try:
			data = request.data
		except Exception as e:
			data = request["data"]	#to access data from csv import task shipmentcsvimport
		print "data =",data

		dispatch_date = data.get('dispatch_date', None)
		tracking_details = data.get('tracking_details', None)
		mode = data.get('mode', None)
		tracking_number = data.get('tracking_number', None)
		transporter_courier = data.get('transporter_courier', None)
		logistics_provider = data.get('logistics_provider', None)
		warehouse = data.get('warehouse', None)
		print "data122========================="
		print dispatch_date

		shipmentObj = Shipment.objects.create(invoice=invoice, details=tracking_details, mode=mode, tracking_number=tracking_number, transporter_courier=transporter_courier, logistics_provider=logistics_provider)
		print shipmentObj
		if dispatch_date:
			shipmentObj.datetime = dispatch_date
			shipmentObj.save()

		invoice.status = "Dispatched"
		invoice.save()

		jsonarr = {}
		jsonarr['order_number'] = invoice.order.order_number
		jsonarr['table_id'] = invoice.order.id
		jsonarr['status'] = invoice.status #invoice.order.processing_status
		jsonarr['title'] = "Purchase Order "+str(invoice.status) #str(invoice.order.processing_status)
		jsonarr['order_url'] = str(settings.GLOBAL_SITE_URL)+'?type=purchase&id='+str(invoice.order.id)

		broker_users = []
		if invoice.order.broker_company is not None:
			broker_users=CompanyUser.objects.filter(company=invoice.order.broker_company).values_list('user', flat=True).distinct()

		#deputed_users = CompanyUser.objects.filter(company=invoice.order.company, deputed_from=invoice.order.seller_company).values_list('user', flat=True).distinct()

		user1 = invoice.order.company.company_users.values_list('user', flat=True)
		user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)

		# send_notification('order-status', user1, jsonarr)
		sendAllTypesMessage("send_order_status", user1, jsonarr)


		seller_company = invoice.order.seller_company

		items = InvoiceItem.objects.filter(invoice=invoice)
		for item in items:
			if Stock.objects.filter(company=seller_company, product=item.order_item.product).exists():
				seller_stock = Stock.objects.get(company=seller_company, product=item.order_item.product)

				seller_stock.in_stock = max(seller_stock.in_stock - item.qty, 0)
				seller_stock.blocked = max(seller_stock.blocked - item.qty, 0)
				seller_stock.open_sale = max(seller_stock.open_sale - item.qty, 0)

				seller_stock.save()

			item.order_item.dispatched_qty += item.qty
			#item.order_item.pending_quantity -= item.qty
			item.order_item.save()

		if warehouse:
			seller_warehouse = Warehouse.objects.filter(company=seller_company, id=warehouse).first()
			if seller_warehouse:
				for item in items:
					if WarehouseStock.objects.filter(warehouse=seller_warehouse, product=item.order_item.product).exists():
						warehousestock = WarehouseStock.objects.get(warehouse=seller_warehouse, product=item.order_item.product)
						warehousestock.in_stock = max(warehousestock.in_stock - item.qty, 0)
						warehousestock.save()
		#else:
		#	seller_warehouse = Warehouse.objects.filter(company=invoice.order.seller_company).first()
		total_invoices = Invoice.objects.filter(order=invoice.order).count()
		logger.info("in invoice /dispatched/ url total_invoices = %s" % (total_invoices))
		if total_invoices == 1: #total pending_quantity getting more than 0 in sever somehow so
			invoice.order.processing_status = "Dispatched"
			invoice.order.save()
			if dispatch_date:
				invoice.order.dispatch_date = dispatch_date
			invoice.order.save()
		else:
			soiQty = SalesOrderItem.objects.filter(sales_order=invoice.order).aggregate(Sum('pending_quantity')).get('pending_quantity__sum', 0)
			if soiQty is None:
				soiQty = 0
			logger.info("in invoice /dispatched/ url invoice pk = %s soiQty = %s" % (pk, soiQty))
			if soiQty == 0:
				print "soiQty dispatch_date = ",dispatch_date
				invoice.order.processing_status = "Dispatched"
				invoice.order.save()
				if dispatch_date:
					invoice.order.dispatch_date = dispatch_date
				invoice.order.save()

		'''salesorder_items_ids = invoice.items.all().values_list('order_item', flat=True)
		total_pending_items = SalesOrderItem.objects.filter(sales_order=invoice.order).exclude(id__in=salesorder_items_ids).count()

		print total_pending_items
		if total_pending_items == 0:
			invoice.order.processing_status = "Dispatched"
		else:
			invoice.order.processing_status = "Partially Dispatched"
		invoice.order.save()'''

		return Response({"success":"Dispatched successfully."})

	@detail_route(methods=['POST'], serializer_class = InvoiceSerializer)
	def payment(self, request, pk=None, companies_pk=None):
		user = request.user

		data = request.data

		amount = data.get('amount', None)
		mode = data.get('mode', None)
		trasactiondate = data.get('date', None)
		details = data.get('details', None)

		status = 'Pending' #changes for cheque, neft, other, .. payment status should be pending
		offline_payment = True
		if user.is_staff:
			status = 'Success'
			offline_payment = False

		generateInvoicePayment(pk, amount, mode, data, status, user, None, trasactiondate, details, offline_payment)

		return Response({"success":"Payment done successfully."})

class CompanyCatalogViewViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyCatalogView.objects.all()
	serializer_class = CompanyCatalogViewSerializer
	permission_classes = (permissions.AllowAny,)

	def get_queryset(self):
		queryset = CompanyCatalogView.objects.all().select_related('company', 'catalog').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		company = get_user_company(user) #user.companyuser.company
		if not user.is_authenticated():
			return Response({"success": "catalog viewed successfully"})

		serializer.save(company=company, user=user)

class LanguageViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Language.objects.all().order_by('name')
	serializer_class = LanguageSerializer

class PromotionViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Promotion.objects.filter(status="Enable").order_by('-id')
	serializer_class = PromotionSerializer
	permission_classes = (permissions.IsAuthenticated,)

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('show_on_webapp', ) #?show_on_webapp=True
	search_fields = ('show_on_webapp', )

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user


		language_code = self.request.query_params.get('language_code', 'hi')
		if language_code is not None and language_code != "":
			#language_codes = language_code.split(',')
			queryset = queryset.filter(language__code=language_code)

		company = get_user_company(user)

		ctObj = CompanyType.objects.filter(company=company).first()
		if company and ctObj:
			#return queryset.filter(Q(manufacturer=False, wholesaler=False, retailer=False, broker=False) | Q(manufacturer=ctObj.manufacturer) | Q(retailer=ctObj.retailer) | Q(retailer=ctObj.online_retailer_reseller) | Q(broker=ctObj.broker) | Q(wholesaler=ctObj.wholesaler_distributor))
			pids = queryset.filter(manufacturer=False, wholesaler=False, retailer=False, broker=False).values_list('id', flat=True)
			pids = list(pids)
			pids1 = queryset.filter(manufacturer=True, wholesaler=True, retailer=True, broker=True).values_list('id', flat=True)
			pids.extend(list(pids1))
			if ctObj.manufacturer:
				ids = queryset.filter(manufacturer=ctObj.manufacturer).values_list('id', flat=True)
				pids.extend(list(ids))
			if ctObj.retailer:
				ids = queryset.filter(retailer=ctObj.retailer).values_list('id', flat=True)
				pids.extend(list(ids))
			if ctObj.online_retailer_reseller:
				ids = queryset.filter(retailer=ctObj.online_retailer_reseller).values_list('id', flat=True)
				pids.extend(list(ids))
			if ctObj.broker:
				ids = queryset.filter(broker=ctObj.broker).values_list('id', flat=True)
				pids.extend(list(ids))
			if ctObj.wholesaler_distributor:
				ids = queryset.filter(wholesaler=ctObj.wholesaler_distributor).values_list('id', flat=True)
				pids.extend(list(ids))
			print pids
			queryset = queryset.filter(id__in=pids)
			#print queryset.query

		if company is None:
			pids = queryset.filter(manufacturer=False, wholesaler=False, retailer=False, broker=False).values_list('id', flat=True)
			pids = list(pids)
			pids1 = queryset.filter(manufacturer=True, wholesaler=True, retailer=True, broker=True).values_list('id', flat=True)
			pids.extend(list(pids1))

			ids = queryset.filter(retailer=True).values_list('id', flat=True)
			pids.extend(list(ids))

			queryset = queryset.filter(id__in=pids)

		#if company and company.address.city.city_name not in ["Patna","Surat","Pune"]:
		#	queryset = queryset.exclude(active="patna_surat_pune")

		if company is not None and company.address.city.city_name not in ["Mumbai","Delhi","Hyderabad","Patna","Indore","Ahmedabad","Surat"]:
			queryset = queryset.exclude(active="codcity_guestusers")

		if UserPlatformInfo.objects.filter(user=user).exists() and CompanyUser.objects.filter(user=user).exists():
			view_version_permission = queryset.filter(active__gt = user.userplatforminfo.app_version_code).exclude(active="codcity_guestusers").values_list('id', flat=True)
			queryset = queryset.exclude(id__in=view_version_permission)
		else:
			#view_version_permission = queryset.filter(active__isnull = False).values_list('id', flat=True)
			#queryset = queryset.exclude(id__in=view_version_permission)
			view_version_permission = queryset.filter(Q(active__isnull=True) | Q(active__exact='') | Q(active="codcity_guestusers")).values_list('id', flat=True)
			queryset = queryset.filter(id__in=view_version_permission)

		return queryset

class SalesmanLocationViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = SalesmanLocation.objects.all()
	serializer_class = SalesmanLocationSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset
		queryset = queryset.select_related('salesman').prefetch_related('state', 'city').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(salesman__companyuser__company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

class BuyerSalesmenViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = BuyerSalesmen.objects.all()
	serializer_class = BuyerSalesmenSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset
		queryset = queryset.select_related('salesman').prefetch_related('buyers').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(salesman__companyuser__company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

	@list_route(methods=['post'])
	def uploadcsv(self, request, companies_pk=None):
		data = request.data
		loginUser = request.user
		loginCompany = loginUser.companyuser.company
		companyName = loginCompany.name

		logger.info("BuyerSalesmenViewSet uploadcsv 111 ====")

		content_type = request.META.get('CONTENT_TYPE')

		f = request.FILES['buyersalesmen_csv[0]']
		first_line = f.readline()[:-1].split(',')
		columns = {}
		i = 0
		for model in first_line:
			columns[model] = i
			i = i+1
		flag = True

		logger.info("BuyerSalesmenViewSet uploadcsv 222 ====")

		err = ""

		csvresponse = HttpResponse(content_type='text/csv')
		csvresponse['Content-Disposition'] = 'attachment; filename="errorbuyersalesmen.csv"'
		writer = csv.writer(csvresponse)
		writer.writerow(['salesman', 'buyer', 'error'])

		column = 1

		try:
			for line in f:
				if (flag==True):
					flag = False
					continue
				column += 1
				line = line[:-1].split(',')
				fields = {}
				for k,v in columns.iteritems():
					k = re.sub('[^a-zA-Z0-9-_ ]', '',k)
					fields[k] = re.sub('[^a-zA-Z0-9-_ ]', '',line[v])

				logger.info(str(fields))

				salesman = fields['salesman']
				buyer = fields['buyer']

				if not User.objects.filter(username=salesman, groups__name="salesperson").exists():
					logger.info("Salesmen is not exists")
					err = {"buyersalesmen_csv":"Enter a valid salesman : "+fields['salesman']}
					writer.writerow([str(salesman), str(buyer), "Enter a valid salesman",])
					continue

				salesman = User.objects.filter(username=salesman).first()
				buyerObj = Buyer.objects.filter(selling_company=loginCompany, buying_company__name=buyer).first()
				if buyerObj is None:
					logger.info("Buyer is not exists")
					err = {"buyersalesmen_csv":"Enter a valid Buyer : "+fields['buyer']}
					writer.writerow([str(salesman), str(buyer), "Enter a valid Buyer",])
					continue

				buyer = buyerObj.buying_company

				if BuyerSalesmen.objects.filter(salesman=salesman, buyers=buyer).exists():
					logger.info("Buyer salesmen exists already")
					continue

				bsObj, created = BuyerSalesmen.objects.get_or_create(salesman=salesman)
				bsObj.buyers.add(buyer.id)
				bsObj.save()

		except Exception as e:
			print "Exception"
			print e
			raise serializers.ValidationError({"buyersalesmen_csv":"Check csv file and found something wrong around row no = "+str(column)})

		try:
			f.close()
		except Exception as e:
			logger.info(str(e))
			pass

		if err != "":
			print "error file download"
			print csvresponse
			return csvresponse
		else:
			return Response({"success": "Uploaded Buyer Salesmen CSV successfully"})

class AssignGroupsViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = AssignGroups.objects.all()
	serializer_class = AssignGroupsSerializer
	permission_classes = (permissions.IsAuthenticated,)

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'user', )
	search_fields = ('id', 'user__id', )

	def get_queryset(self):
		queryset = self.queryset
		queryset = queryset.select_related('user').prefetch_related('groups').order_by('-id')

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				return queryset.filter(user__companyuser__company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

class CatalogUploadOptionViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CatalogUploadOption.objects.all()
	serializer_class = CatalogUploadOptionSerializer
	permission_classes = (permissions.IsAuthenticated, )

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		catalog = self.request.query_params.get('catalog', None)
		if catalog:
			queryset = queryset.filter(catalog=catalog)

		if user.is_staff:
			return queryset

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				return queryset.filter(catalog__company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

class CompanyKycTaxationViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyKycTaxation.objects.all()
	serializer_class = CompanyKycTaxationSerializer
	permission_classes = (permissions.IsAuthenticated, )

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				return queryset.filter(company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		company = get_user_company(user) #user.companyuser.company

		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		if CompanyKycTaxation.objects.filter(company=company).exists():
			raise serializers.ValidationError({"company":"Kyc already exists."})
		serializer.save(company=company)

class ShipmentViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Shipment.objects.all()
	serializer_class = ShipmentSerializer
	permission_classes = (permissions.IsAuthenticated, )

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'invoice', )
	search_fields = ('id', 'invoice__id', )

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		if user.is_staff:
			return queryset

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				return queryset.filter(invoice__order__seller_company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

class OrderRatingViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = OrderRating.objects.all()
	serializer_class = OrderRatingSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method == 'GET':
				serializer_class = GetOrderRatingSerializer
		return serializer_class

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		order = self.request.query_params.get('order', None)

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				if order:
					queryset = queryset.filter(order=order)

				sids = SalesOrder.objects.filter(Q(seller_company=company) | Q(company=company)).values_list('id', flat=True)

				return queryset.filter(order__in=sids)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

class CompanyBrandFollowViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyBrandFollow.objects.all()
	serializer_class = CompanyBrandFollowSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				return queryset.filter(company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		company = get_user_company(user) #user.companyuser.company
		if company:
			brand = serializer.validated_data.get('brand', None)
			if CompanyBrandFollow.objects.filter(brand=brand, company=company).exists():#, user=user
				raise serializers.ValidationError({"faild":"Already selected brand can not select again."})
			serializer.save(user=user, company=company)
		else:
			raise serializers.ValidationError({"error":"Please register your company"})

class ApprovedCreditViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = ApprovedCredit.objects.all()
	serializer_class = ApprovedCreditSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				return queryset.filter(company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

class LoanViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = Loan.objects.all()
	serializer_class = LoanSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company

				return queryset.filter(company=company)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

class PaymentMethodViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = PaymentMethod.objects.filter(status="Enable").order_by('payment_type')
	serializer_class = PaymentMethodSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		supplier = self.request.query_params.get('supplier', None)
		buyer = self.request.query_params.get('buyer', None)

		cart = self.request.query_params.get('cart', None)

		order = self.request.query_params.get('order', None)
		if order is not None:
			order = SalesOrder.objects.get(pk=order)

			buyerObj = Buyer.objects.filter(selling_company=order.seller_company, buying_company=order.company, status="approved").first()

			if buyerObj is not None and buyerObj.broker_company == user.companyuser.company:
				queryset = queryset.filter(payment_type='Credit')
			elif buyerObj:
				queryset = queryset.all()

			available_credit = order.company.credit_line.filter().aggregate(Sum('available_line')).get('available_line__sum', 0)
			if available_credit is None:
				available_credit = 0

			if order.amount > available_credit:
				queryset=queryset.exclude(name = 'creditline')


			cod_available = False
			if order.ship_to:
				if PincodeZone.objects.filter(pincode=order.ship_to.pincode, cod_available=True).exists():# and order.seller_company.cod_available==True:
					cod_available = True

			if not cod_available:
				return queryset.exclude(name="cod")

			return queryset

		if cart is not None:
			cart = Cart.objects.get(pk=cart)

			queryset = queryset.all()

			cod_available = False
			if cart.ship_to:
				if PincodeZone.objects.filter(pincode=cart.ship_to.pincode, cod_available=True).exists():
					cod_available = True

			available_credit = cart.buying_company.credit_line.filter().aggregate(Sum('available_line')).get('available_line__sum', 0)
			if available_credit is None:
				available_credit = 0
			if cart.total_amount > available_credit:
				queryset = queryset.exclude(name = 'creditline')

			if not cod_available:
				return queryset.exclude(name="cod")

			return queryset

		if supplier is not None and buyer is not None:
			buyerObj = Buyer.objects.filter(selling_company=supplier, buying_company=buyer, status="approved").first()

			if buyerObj is not None and buyerObj.broker_company == user.companyuser.company:
				return queryset.filter(payment_type='Credit').exclude(name="cod")
			elif buyerObj:
				return queryset.all().exclude(name="cod")

		return queryset.filter(payment_type__in=['Online','Offline']).exclude(name="cod")

class ConfigViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Config.objects.filter(visible_on_frontend=True)
	serializer_class = ConfigSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'key', 'value', )
	search_fields = ('id', 'key', 'value', )

class AddressViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Address.objects.all()
	serializer_class = AddressSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method == 'GET':
				serializer_class = GetAddressSerializer
		return serializer_class

	def get_queryset(self):
		queryset = self.queryset

		company = self.request.query_params.get('company', None)

		user = self.request.user

		if user.is_staff:
			buyer = self.request.query_params.get('buyer', None)
			if buyer is not None:
				return queryset.filter(user__companyuser__company=buyer)

			if company:
				return queryset.filter(user__companyuser__company=company)

		try:
			if user.is_authenticated():
				loginCompany = get_user_company(user) #user.companyuser.company

				if company:
					if Buyer.objects.filter(selling_company=loginCompany, buying_company=company, status="approved").exists() or Buyer.objects.filter(selling_company=company, buying_company=loginCompany, status="approved").exists():
						return queryset.filter(user__companyuser__company=company)
					elif int(company) == (loginCompany.id):
						return queryset.filter(user__companyuser__company=loginCompany)
					else:
						return queryset.none()

				if loginCompany:
					return queryset.filter(user__companyuser__company=loginCompany)
				else:
					return queryset.filter(user=user)
		except ObjectDoesNotExist:
			return queryset.none()
		return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		if user.is_staff:
			data = self.request.data
			company = data.get('company', None)
			if company:
				company = Company.objects.get(pk = company)
				user = company.chat_admin_user
		serializer.save(user=user)

	def destroy(self, request, pk=None, companies_pk=None):
		instance = self.get_object()
		if Company.objects.filter(address=instance).exists() or SalesOrder.objects.filter(ship_to=instance).exists() or Branch.objects.filter(address=instance).exists():
			raise serializers.ValidationError({"Delete Failed":"This Address can't be deleted, as it is used in your previous orders!"})
		instance.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class UserPlatformInfoViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = UserPlatformInfo.objects.all()
	serializer_class = UserPlatformInfoSerializer

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		try:
			if user.is_authenticated():
				return queryset.filter(user=user)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
			return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

class CategoryEavAttributeViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CategoryEavAttribute.objects.all()
	serializer_class = CategoryEavAttributeSerializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'category', 'attribute', 'is_required', )
	search_fields = ('id', 'category', 'attribute', 'is_required', )

class CompanySellsToStateViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = CompanySellsToState.objects.all()
	serializer_class = CompanySellsToStateSerializer

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		company = self.request.query_params.get('company', None)
		state = self.request.query_params.get('state', None)

		try:
			if user.is_authenticated():
				loginCompany = user.companyuser.company
				if company is not None and state is not None:
					return queryset.filter(company=company, state=state)
				if company is not None:
					return queryset.filter(company=company)
				if state is not None:
					return queryset.filter(state=state)

				return queryset.filter(company=loginCompany)
		except ObjectDoesNotExist:
			return queryset.none()
		return queryset.none()

class CatalogSellerViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = CatalogSeller.objects.all()
	serializer_class = CatalogSellerSerializer

	def get_queryset(self):
		#queryset = self.queryset
		queryset = self.queryset.select_related('selling_company')

		user = self.request.user

		try:
			if user.is_authenticated():
				loginCompany = user.companyuser.company
				return queryset.filter(selling_company=loginCompany)
		except ObjectDoesNotExist:
			return queryset.none()
		return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		company = get_user_company(user) #user.companyuser.company
		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})
		#catalog = serializer.validated_data.get('catalog', None)
		#if CatalogSeller.objects.filter(catalog=catalog, selling_company=company).exists():
		#	raise serializers.ValidationError({"faild":"Already selected catalog can not be selected again."})
		serializer.save(selling_company=company)

class CatalogSellerAdminViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CatalogSeller.objects.all()
	serializer_class = CatalogSellerAdminSerializer
	permission_classes = (permissions.IsAdminUser,)

class UserReviewViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = UserReview.objects.filter(status="Enable").order_by('-id')
	serializer_class = UserReviewSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		language_code = self.request.query_params.get('language_code', 'hi')
		if language_code is not None and language_code != "":
			#language_codes = language_code.split(',')
			queryset = queryset.filter(language__code=language_code)

		return queryset

class PromotionalTagViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = PromotionalTag.objects.all()
	serializer_class = PromotionalTagSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'status',)
	search_fields = ('id', 'status',)

#added by jay
class PreDefinedFilterViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = PreDefinedFilter.objects.all().order_by('-sort_order', '-id')
	serializer_class = PreDefinedFilterSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'name', 'category', 'status',)
	search_fields = ('id', 'name', 'category', 'status',)

	@list_route(methods=['get'])
	def categories(self, request, catalogs_pk=None):
		queryset = self.get_queryset().values_list('category', flat=True).distinct()
		categories = Category.objects.filter(id__in=queryset)
		serializer = CategorySerializer(categories, many=True)
		return Response(serializer.data)

class UserWishlistViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = UserWishlist.objects.all().order_by('-id')
	serializer_class = UserWishlistSerializer
	#permission_classes = (permissions.IsAuthenticated,)

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'user', 'catalog',)
	search_fields = ('id', 'user', 'catalog',)

	pagination_class = CustomPagination



	def list(self, request, users_pk=None):
		user = self.request.user
		company = get_user_company(user)

		# ~ disableCatalogIds = getDisableCatalogIds(company)
		# ~ disable_cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Disable").values_list('catalog', flat=True).distinct()
		#catalog_ids = UserWishlist.objects.filter(user=users_pk).exclude(Q(catalog__in=disableCatalogIds) | Q(catalog__in=disable_cscatalogids) | Q(catalog__deleted=True)).order_by('-id').values_list("catalog",flat=True)

		catalog_ids = UserWishlist.objects.filter(user=user).exclude(catalog__deleted=True).order_by('-id').values_list("catalog",flat=True)
		catalog_ids = list(catalog_ids)
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(catalog_ids)])
		catalogs = Catalog.objects.filter(id__in=catalog_ids).order_by(preserved)

		page = self.paginate_queryset(catalogs)

		if page is not None:
			serializer = CatalogSerializer(page, many=True, context={'request': request})
			return self.get_paginated_response(serializer.data)

		serializer = CatalogSerializer(catalogs, many=True, context={'request': request})
		return Response(serializer.data)

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		try:
			if user.is_authenticated():
				return queryset.filter(user=user)
			else:
				return queryset.none()
		except ObjectDoesNotExist:
				return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

class ActionLogViewSet(LoggingMixin, viewsets.ModelViewSet):
	queryset = ActionLog.objects.all()
	serializer_class = ActionLogSerializer

	def get_queryset(self):
		queryset = self.queryset

		return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

class UserSavedFilterViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = UserSavedFilter.objects.all()
	serializer_class = UserSavedFilterSerializer

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		queryset = queryset.filter(user=user)

		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

class AppVersionViewSet(viewsets.ModelViewSet):
	queryset = AppVersion.objects.all()
	serializer_class = AppVersionSerializer

	filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, )
	filter_fields = ('id', 'version_code', 'platform',)
	search_fields = ('id', 'version_code', 'platform',)

class DiscountRuleViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = DiscountRule.objects.all()
	serializer_class = DiscountRuleSerializer

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetDiscountRuleSerializer

		return serializer_class

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		queryset = queryset.filter(selling_company=user.companyuser.company)

		all_brands = self.request.query_params.get('all_brands', None)
		if all_brands is not None and all_brands.lower()=="true":
			queryset = queryset.filter(all_brands=True)

		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(selling_company=user.companyuser.company)

class MarketingViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Marketing.objects.all()
	serializer_class = MarketingSerializer

	permission_classes = (permissions.IsAdminUser,)

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		if user.is_staff:
			return queryset

		return queryset.none()

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

	@list_route(methods=['POST'])
	def total_receiver(self, request):
		data = request.data
		logger.info("total_receiver startMarketing data = %s"% (data))

		serializer = MarketingSerializer(data=data)
		print "serializer.is_valid()", serializer.is_valid()

		finaljson = serializer.data

		if "specific_no_file" in data.keys():
			logger.info("total_receiver startMarketing specific_no_file found in posted json data set")
			finaljson["specific_no_file"] = data["specific_no_file"]
		elif "specific_no_file" in finaljson.keys():
			logger.info("total_receiver startMarketing specific_no_file found in serializer delete")
			del finaljson["specific_no_file"]

		if "pk_id" in data.keys():
			finaljson["id"] = data["pk_id"]

		count_json = startMarketing(finaljson, "count")

		return Response(count_json)

class SellerPolicyViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SellerPolicy.objects.all()
	serializer_class = SellerPolicySerializer

	def get_queryset(self):
		queryset = self.queryset

		company = self.request.query_params.get('company', None)
		if company:
			queryset = queryset.filter(company=company)

		policy_type = self.request.query_params.get('policy_type', None)
		if policy_type:
			queryset = queryset.filter(policy_type=policy_type)

		return queryset

class CompanyCreditRatingViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyCreditRating.objects.all()
	serializer_class = CompanyCreditRatingSerializer

	def get_queryset(self):
		queryset = self.queryset
		queryset = queryset.filter(rating="Good") #, bureau_report_rating="Positive", financial_statement_rating="Positive"

		company = self.request.query_params.get('company', None)
		if company:
			queryset = queryset.filter(company=company)
		else:
			user = self.request.user
			company = get_user_company(user)
			queryset = queryset.filter(company=company)

		return queryset

class CreditReferenceViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CreditReference.objects.all()
	serializer_class = CreditReferenceSerializer

	def get_queryset(self):
		queryset = self.queryset

		buying_company = self.request.query_params.get('buying_company', None)
		if buying_company:
			queryset = queryset.filter(buying_company=buying_company)
		else:
			user = self.request.user
			company = get_user_company(user)
			queryset = queryset.filter(Q(selling_company=company) | Q(buying_company=company))

		return queryset

class SolePropreitorshipKYCViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = SolePropreitorshipKYC.objects.all()
	serializer_class = SolePropreitorshipKYCSerializer

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user
		company = get_user_company(user)
		queryset = queryset.filter(company=company)

		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		company = get_user_company(user)
		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})
		serializer.save(company=company)

# @api_view(['GET'])
# @permission_classes((permissions.IsAdminUser,))
def order_for_ship(request):
	ship_resource = SalesOrderShipRocketResource()
	# pdb.set_trace()
	orderids = request.GET.getlist("order_id")
	queryset	  					= SalesOrder.objects.filter(Q(id__in=orderids)).filter(Q(order_type="Prepaid") & Q(source_type="Marketplace") & (Q(processing_status="Pending") | Q(processing_status="Accepted")))
	print "order type Credit will be escaped"
	dataset 	  					= ship_resource.export(queryset)
	response 	  					= HttpResponse(dataset.csv, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="order.csv"'
	return response

class ImageTestViewSet(viewsets.ModelViewSet):
	queryset = ImageTest.objects.all()
	serializer_class = ImageTestSerializer

class StoryViewSet(viewsets.ModelViewSet):
	queryset = Story.objects.filter(is_disable=False).order_by('-sort_order')
	serializer_class = StorySerializer

	def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetStorySerializer

		return serializer_class


class CatalogEnquiryViewSet(viewsets.ModelViewSet):
	queryset = CatalogEnquiry.objects.all().order_by('-id')
	serializer_class = CatalogEnquirySerializer
	pagination_class = CustomPagination

	filter_backends = (filters.DjangoFilterBackend, )
	filter_fields = ('id', 'applogic_conversation_id', )


	'''def get_serializer_class(self):
		serializer_class = self.serializer_class

		expand = self.request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			serializer_class = GetCatalogEnquirySerializer

		return serializer_class
	'''
	def get_queryset(self):
		queryset = self.queryset.select_related('catalog', 'selling_company__chat_admin_user', 'buying_company__chat_admin_user')

		user = self.request.user

		if user.is_staff:
			return queryset

		company = get_user_company(user)
		queryset = queryset.filter(Q(selling_company=company) | Q(buying_company=company))

		selling_company = self.request.query_params.get('selling_company', None)
		if selling_company:
			queryset = queryset.filter(selling_company=selling_company)

		buying_company = self.request.query_params.get('buying_company', None)
		if buying_company:
			queryset = queryset.filter(buying_company=buying_company)

		status = self.request.query_params.get('status', None)
		if status:
			queryset = queryset.filter(status=status)

		catalog_title = self.request.query_params.get('catalog_title', None)
		if catalog_title:
			queryset = queryset.filter(catalog__title__icontains=catalog_title)

		return queryset

	@list_route(methods=['get'], url_path='buyer-leads')
	def buyer_leads(self, request, companies_pk=None):
		user = self.request.user
		company = get_user_company(user)

		queryset = self.queryset.filter(selling_company = company)

		buying_company_name = self.request.query_params.get('buying_company_name', None)
		if buying_company_name:
			queryset = queryset.filter(buying_company__name__icontains=buying_company_name)

		status_arr = ['Created', 'Resolved']
		status = self.request.query_params.get('status', None)
		if status:
			queryset = queryset.filter(status=status)
			status_arr = [status]

		companyids = queryset.values_list('buying_company', flat=True).distinct()
		companyids = getUniqueItems(list(companyids))
		preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(companyids)])

		companyObjs = Company.objects.filter(id__in=companyids).select_related('address__state', 'address__city').order_by(preserved)

		page = self.paginate_queryset(companyObjs)
		if page is not None:
			companyObjs = page

		jsonarr = []
		for qs in companyObjs:
			jsondata = {}
			jsondata["company_id"] = qs.id
			jsondata["company_name"] = qs.name
			jsondata["total_enquiry"] = self.queryset.filter(selling_company = company, buying_company=qs, status__in=status_arr).count()

			if qs.address:
				jsondata["state_name"] = qs.address.state.state_name
				jsondata["city_name"] = qs.address.city.city_name
			else:
				jsondata["state_name"] = qs.state.state_name
				jsondata["city_name"] = qs.city.city_name

			jsonarr.append(jsondata)

		return Response(jsonarr)

class ViewFollowerViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = ViewFollower.objects.all()
	serializer_class = ViewFollowerSerializer

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		queryset = queryset.filter(user=user)

		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

class UserCreditSubmissionViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = UserCreditSubmission.objects.all()
	serializer_class = UserCreditSubmissionSerializer

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user

		queryset = queryset.filter(user=user)

		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		serializer.save(user=user)

class CatalogUrlindexView(mixins.RetrieveModelMixin, generics.GenericAPIView):
	permission_classes = (permissions.AllowAny,)

	queryset = Catalog.objects.all()
	serializer_class = CatalogSerializer
	#lookup_field = 'id'

	def get(self, request, *args, **kwargs):
		#print(kwargs)
		expand = request.query_params.get('expand', None)
		if expand is not None and expand.lower()=="true":
			self.serializer_class = GetCatalogSerializer
		urlkey = kwargs['pk']
		if urlkey:
			urlindex_obj  = URLIndex.objects.filter(urlkey = urlkey).first()
			if urlindex_obj:
				self.kwargs['pk'] = Catalog.objects.filter(id = urlindex_obj.urlobject_id)
		return self.retrieve(request, *args, **kwargs)

class CompanyBankDetailsViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CompanyBankDetails.objects.all()
	#print(queryset)
	serializer_class = CompanyBankDetailsSerializer

	def get_queryset(self):
		queryset = self.queryset

		user = self.request.user
		company = get_user_company(user)
		#print(request.data)
		#print(company)
		queryset = queryset.filter(company=company)
		#print(queryset)
		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		company = get_user_company(user)
		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})
		if CompanyBankDetails.objects.filter(company=company).exists():
			raise serializers.ValidationError({"company":"Bank details already exists."})
		serializer.save(company=company)

#WB-2198 - create new function in task.py file for cron
class DailyUnsubscribedNumbersCSVreaderCron(LoggingMixin, APIView):
	permission_classes = (permissions.AllowAny,)

	def get(self, request, format=None):
		if settings.TASK_QUEUE_METHOD == 'celery':
			dailyUnsubscribedNumberCSVreaderTask.apply_async((), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			task_id = async(
				'api.tasks.dailyUnsubscribedNumberCSVreaderTask'
			)
		#dailyUnsubscribedNumberCSVreaderTask()

		return Response({"success": "Daily Unsubscribed Number CSV reader Task cron started successfully"})
