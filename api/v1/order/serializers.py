from rest_framework import fields, serializers
from api.models import *

from rest_framework import permissions

from rest_framework.validators import UniqueTogetherValidator
import logging
logger = logging.getLogger(__name__)

from versatileimagefield.serializers import VersatileImageFieldSerializer

import json
import ast

from django.db.models import Value
from django.db.models.functions import Concat

from django_q.tasks import async, result

from api.v1.order.functions import *


class CartItemSerializer(serializers.ModelSerializer):
	# product_title = serializers.CharField(source='product.title', read_only=True)
	# product_catalog = serializers.CharField(source='product.catalog.title', read_only=True)
	product_sku = serializers.CharField(source='product.sku', read_only=True)
	product_image = serializers.CharField(source='product.image.thumbnail.150x210', read_only=True)
	product_image_medium = serializers.CharField(source='product.image.thumbnail.357x500', read_only=True)
	# product_category = serializers.CharField(source='product.catalog.category.category_name', read_only=True)

	# selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)
	selling_company_name = serializers.ReadOnlyField(source='selling_company.name', read_only=True)
	selling_company = serializers.PrimaryKeyRelatedField(required=False, queryset=Company.objects.all()) #to required false validation
	class Meta:
		model = CartItem
		validators = []

class CartSerializer(serializers.ModelSerializer):
	items = CartItemSerializer(many=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	buying_company = serializers.ReadOnlyField(source='buying_company.name', read_only=True)
	finalize = serializers.BooleanField(required=False)
	add_quantity = serializers.BooleanField(required=False)
	add_size = serializers.BooleanField(required=False)
	total_cart_items = serializers.SerializerMethodField()

	def get_total_cart_items(self, obj):
		return getTotalCartItemCount(obj)

	def create(self, validated_data):
		logger.info("in create CartSerializer")
		items = validated_data.pop('items')
		finalize = validated_data.pop('finalize', False)
		add_quantity = validated_data.pop('add_quantity', False)
		add_size = validated_data.pop('add_size', False)

		cart = Cart.objects.create(**validated_data)

		#~ if salesorder.company == salesorder.user.companyuser.company and salesorder.broker_company is None:
			#~ buyerObj = Buyer.objects.filter(selling_company=salesorder.seller_company, buying_company=salesorder.company).first()
			#~ if buyerObj is not None and buyerObj.broker_company is not None:
				#~ salesorder.broker_company = buyerObj.broker_company
				#~ salesorder.save()

		for item in items:
			if item['quantity'] > 0:# and not ProductStatus.objects.filter(company=salesorder.seller_company, product=item['product'], status="Disable").exists():
				packing_type = item.get('packing_type', None)
				note = item.get('note', None)
				is_full_catalog = item.get('is_full_catalog', False)
				selling_company = item.get('selling_company', None)

				if selling_company is None:
					selling_company = getSupplierFromProduct(item['product'], cart.buying_company, is_full_catalog)
				logger.info("create CartSerializer cartitem selling_company = %s"% (selling_company))
				if selling_company and not ProductStatus.objects.filter(company=selling_company, product=item['product'], status="Disable").exists():
					salesitem = CartItem.objects.get_or_create(product=item['product'], quantity=item['quantity'], rate=item['rate'], cart=cart, note=note, packing_type=packing_type, selling_company=selling_company, is_full_catalog=is_full_catalog)

		cart = calCartTaxnDiscount(cart.id)
		#cart = Cart.objects.get(pk=cart.id)

		return cart

	def update(self, instance, validated_data):
		logger.info("in update CartSerializer")
		items = validated_data.pop('items', [])
		finalize = validated_data.pop('finalize', False)
		add_quantity = validated_data.pop('add_quantity', False)
		add_size = validated_data.pop('add_size', False)

		for attr, value in validated_data.items():
			logger.info("update CartSerializer attr = %s, value = %s"% (attr, value))
			setattr(instance, attr, value)

		instance.save()

		print items
		if len(items) > 0:
			itemsIds = CartItem.objects.filter(cart = instance).values_list('id', flat=True)
			itemsIds = list(itemsIds)
			logger.info("update CartSerializer before item loop itemsIds = %s"% (itemsIds))
			for item in items:
				if item['quantity'] > 0:# and not ProductStatus.objects.filter(company=instance.seller_company, product=item['product'], status="Disable").exists():
					packing_type = item.get('packing_type', None)
					note = item.get('note', None)
					is_full_catalog = item.get('is_full_catalog', False)
					selling_company = item.get('selling_company', None)

					#if CartItem.objects.filter(product=item['product'],cart = instance, packing_type=packing_type).exists():
					if add_size is False and CartItem.objects.filter(product=item['product'],cart = instance, is_full_catalog=is_full_catalog, note=note).exists():
						logger.info("update CartSerializer order item updates")
						soiObj = CartItem.objects.filter(product=item['product'],cart = instance, is_full_catalog=is_full_catalog, note=note).last()
						if add_quantity:
							soiObj.quantity = soiObj.quantity + item['quantity']
						else:
							soiObj.quantity = item['quantity']

						logger.info("update CartSerializer patch qty = %s, save qty = %s" % (item['quantity'], soiObj.quantity))
						# soiObj.rate=item['rate']
						soiObj.rate=item.get('rate', soiObj.rate)
						soiObj.note=note
						soiObj.packing_type=packing_type
						print "selling_company=", selling_company
						if selling_company:
							print "selling_company=", selling_company
							soiObj.selling_company=selling_company
						soiObj.save()
						if soiObj.id in itemsIds:
							itemsIds.remove(soiObj.id)
					else:
						if selling_company is None:
							selling_company = getSupplierFromProduct(item['product'], instance.buying_company, is_full_catalog)
						logger.info("update CartSerializer selling_company = %s"% (selling_company))
						if selling_company and not ProductStatus.objects.filter(company=selling_company, product=item['product'], status="Disable").exists():
							salesitem = CartItem.objects.get_or_create(product=item['product'], quantity=item['quantity'], rate=item['rate'],cart = instance,  note=note, packing_type=packing_type, selling_company=selling_company, is_full_catalog=is_full_catalog)
			logger.info("update CartSerializer after item loop itemsIds = %s"% (itemsIds))
			if finalize:
				CartItem.objects.filter(id__in=itemsIds).delete()

		instance = calCartTaxnDiscount(instance.id)
		#instance = Cart.objects.get(pk=instance.id)

		return instance

	class Meta:
		model = Cart

class CartPaymentSerializer(serializers.ModelSerializer):
	#user = serializers.ReadOnlyField(source='user.username', read_only=True)

	def create(self, validated_data):
		logger.info("create CartPaymentSerializer")
		cart_payment = CartPayment.objects.create(**validated_data)

		#converCartToOrder(cart_payment.cart)
		cart_payment.cart.payment_date = date.today()
		#~ cart_payment.cart.payment_details = "Credit"
		cart_payment.cart.payment_method = cart_payment.mode
		cart_payment.cart.cart_status = "Converted"

		if cart_payment.status == "Success":
			cart_payment.cart.paid_amount += cart_payment.amount
			cart_payment.cart.pending_amount -= cart_payment.amount
			if cart_payment.cart.pending_amount < float(1):
				cart_payment.cart.payment_status = "Paid"
			else:
				cart_payment.cart.payment_status = "Partially Paid"

		cart_payment.cart.save()

		return cart_payment

	class Meta:
		model = CartPayment
