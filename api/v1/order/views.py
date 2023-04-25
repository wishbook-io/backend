from api.v1.order.serializers import *
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from api.v1.permissions import *
from api.permissions import *
from rest_framework import filters
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from django.http import HttpResponse
import csv
from rest_framework.exceptions import *
from rest_framework.renderers import JSONRenderer

from rest_framework_tracking.mixins import LoggingMixin

from rest_framework.views import APIView

from rest_framework import status

from django.http import JsonResponse
from rest_framework.pagination import LimitOffsetPagination

from django.db.models import Case, When

from api.v1.serializers import SellerPolicySerializer

from copy import copy

class CustomPagination(LimitOffsetPagination):
	def get_paginated_response(self, data):
		return Response(
			 data
		)

class CartItemViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = CartItem.objects.all()
	serializer_class = CartItemSerializer
	pagination_class = CustomPagination

	def get_queryset(self):
		queryset = self.queryset.select_related('selling_company', 'product').order_by('-id')

		user = self.request.user
		company = get_user_company(user)

		queryset = queryset.filter(cart__buying_company=company)

		return queryset

class CartViewSet(LoggingMixin, viewsets.ModelViewSet):
	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
	queryset = Cart.objects.filter(cart_status="Created")
	serializer_class = CartSerializer
	pagination_class = CustomPagination

	def get_queryset(self):
		queryset = self.queryset.select_related('buying_company','user').prefetch_related('items__product__catalog__category', 'items__selling_company').order_by('-id')

		user = self.request.user
		company = get_user_company(user)

		queryset = queryset.filter(buying_company=company)

		return queryset

	def perform_create(self, serializer):
		user = self.request.user
		company = get_user_company(user)
		if company is None:
			raise serializers.ValidationError({"error":"Please register your company"})

		serializer.save(user=user, buying_company=company)

	'''def retrieve(self, request, pk=None, companies_pk=None):
		cart = self.get_object()

		shipping_charges = self.request.query_params.get('shipping_charges', None)
		if shipping_charges is not None and shipping_charges == "true":
			print cart
			calCartTaxnDiscount(cart)

		taxndiscount = self.request.query_params.get('taxndiscount', None)
		if taxndiscount is not None and taxndiscount == "true":
			#print cart
			calCartTaxnDiscount(cart)

		serializer = self.get_serializer(cart)
		return Response(serializer.data)'''

	@detail_route(methods=['POST'], serializer_class = CartSerializer)
	def payment(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()

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

		#generateInvoicePayment(pk, amount, mode, data, user, None, trasactiondate, details)
		generateCartPayment(pk, amount, mode, data, status, user, None, trasactiondate, details, offline_payment)

		# serializer = CartPaymentSerializer(data={'mode':mode, 'cart':queryset.id, 'amount':amount, 'status':'Success', 'payment_details':details})
		# if serializer.is_valid():
		# 	serializer.save(user=user)
		# else:
		# 	raise serializers.ValidationError({"error":serializer.errors})

		return Response({"success":"Payment done successfully."})

	@detail_route(methods=['POST'], permission_classes=[permissions.IsAuthenticated], url_path='delete-items')
	def delete_items(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()

		data = self.request.data
		item_ids = data.get('item_ids', None)

		queryset.items.filter(id__in=item_ids).delete()

		calCartTaxnDiscount(queryset.id)

		return Response({"success": "Items has been deleted successfully"})

	@detail_route(methods=['GET'], serializer_class = CartSerializer)
	def catalogwise(self, request, pk=None, companies_pk=None):
		queryset = self.get_object()
		cart = self.filter_queryset(queryset)

		#cart = Cart.objects.select_related('buying_company','user').prefetch_related('items__product__catalog', 'items__selling_company').get(pk=pk)

		cartjson = self.get_serializer(instance=cart)
		cartjson = cartjson.data


		catalogs = []

		groupitems = cart.items.all().values('selling_company','product__catalog','is_full_catalog', 'note').distinct()
		# print "groupitems =", groupitems

		for groupitem in groupitems:
			catalogObj = Catalog.objects.select_related('brand').get(pk=groupitem['product__catalog'])
			companyObj = Company.objects.get(pk=groupitem['selling_company'])

			catalogsjson = {}
			catalogsjson['catalog_id'] = groupitem['product__catalog']
			catalogsjson['catalog_title'] = catalogObj.title
			catalogsjson['catalog_brand'] = catalogObj.brand.name
			catalogsjson['catalog_image'] = catalogObj.thumbnail.thumbnail[settings.SMALL_IMAGE].url
			catalogsjson['catalog_eavdata'] = getCatalogEAV(catalogObj, "allInJson")

			catalogsjson['selling_company_id'] = groupitem['selling_company']
			catalogsjson['selling_company_name'] = companyObj.name
			catalogsjson['trusted_seller'] = companyObj.trusted_seller

			catalogsjson['is_full_catalog'] = groupitem['is_full_catalog']

			print "catalogsjson ===", catalogsjson
			print "note ===", groupitem['note']
			filtereditems = cart.items.filter(selling_company=groupitem['selling_company'], product__catalog=groupitem['product__catalog'], is_full_catalog=groupitem['is_full_catalog'], note=groupitem['note']).select_related('product__catalog', 'tax_class_1', 'tax_class_2')


			sellers = []
			filtereditems_first = filtereditems.first()
			if filtereditems_first is None:
				continue
			cpfORcsObjs = getAllSuppliersFromProduct(filtereditems_first.product, cart.buying_company, groupitem['is_full_catalog'])
			if cpfORcsObjs:
				for cpfORcsObj in cpfORcsObjs:
					seller = {}
					seller["company_id"] = cpfORcsObj[0].id
					seller["company_name"] = cpfORcsObj[0].name
					seller["trusted_seller"] = cpfORcsObj[0].trusted_seller
					seller['state_name'] = cpfORcsObj[0].address.state.state_name
					seller['city_name'] = cpfORcsObj[0].address.city.city_name
					# is_cash_discount = True
					# discount_percent = getSupplierRelDiscount(cpfORcsObj[0], cart.buying_company, is_cash_discount)
					# seller['discount_percent'] = discount_percent

					serializer = SellerPolicySerializer(instance=cpfORcsObj[0].sellerpolicy_set.all(), many=True)
					seller['seller_policy'] = serializer.data

					sellers.append(seller)
			catalogsjson['sellers'] = sellers

			if groupitem['is_full_catalog'] == True:
				cartwiseProductArray(catalogs, filtereditems, catalogsjson)
			else:
				for filtereditem in filtereditems:
					cartwiseProductArray(catalogs, [filtereditem], catalogsjson)

		#cartjson['catalogs'] = catalogs
		cartjson['catalogs'] = sorted(catalogs, key=lambda k: k['products'][0]['id'], reverse=True)

		return Response(cartjson)

# class CartPaymentViewSet(LoggingMixin, viewsets.ModelViewSet):
# 	logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
# 	queryset = CartPayment.objects.all()
# 	serializer_class = CartPaymentSerializer
# 	pagination_class = CustomPagination
#
# 	def get_queryset(self):
# 		queryset = self.queryset
#
# 		user = self.request.user
# 		company = get_user_company(user)
#
# 		queryset = queryset.filter(cart__buying_company=company)
#
# 		return queryset
#
# 	def perform_create(self, serializer):
# 		user = self.request.user
#
# 		serializer.save(user=user)
