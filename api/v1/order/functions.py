from api.models import *
from api.v1.serializers import SalesOrderSerializer, InvoiceSerializer, TaxClassSerializer
from api.common_functions import getSupplierRelDiscount, getSupplierRelDiscountV2

def getPriorityWiseSuppliers(cpfORcsObjs, buying_company, view_permission):
	#1=True, 0=False
	seller_arr = [] #company obj, is_full_catalog, trusted_seller, discount_percent, default sort
	idx = cpfORcsObjs.count()
	for obj in cpfORcsObjs:
		is_cash_discount = True
		discount_percent = getSupplierRelDiscount(obj.selling_company, buying_company, is_cash_discount)

		is_full_catalog = trusted_seller = 0
		if obj.selling_company.trusted_seller:
			trusted_seller = 1
		if view_permission == "public":
			if obj.sell_full_catalog:
				is_full_catalog = 1
		else:
			if Push_User.objects.filter(push=obj.push_reference, full_catalog_orders_only=True, selling_company=obj.selling_company, buying_company=buying_company).exists():
				is_full_catalog = 1

		seller_arr.append([obj.selling_company, is_full_catalog, trusted_seller, discount_percent, idx])
		idx -= 1

	print "before sort seller_arr =", seller_arr
	# seller_arr = []
	# seller_arr.append(['Ramesh', 1,0,5,2])
	# seller_arr.append(['Mahesh', 0,0,2,5])
	# seller_arr.append(['Bhavesh', 0,1,5,4])
	# seller_arr.append(['Jignesh', 0,1,2,3])
	# seller_arr.append(['Kamlesh', 1,0,5,1])
	seller_priority_arr = []
	for seller in seller_arr:
		weight = seller[2]*100 + seller[3]*10 + seller[4]
		sellerWithWeight = [seller[0], seller[1], weight]
		seller_priority_arr.append(sellerWithWeight)

	print "weightage seller_priority_arr =",seller_priority_arr

	seller_priority_arr = sorted(seller_priority_arr, key=lambda x: x[2], reverse=True)
	print "after sort seller_priority_arr =",seller_priority_arr

	return seller_priority_arr

def getAllSuppliersFromProduct(product, buying_company, is_full_catalog):
	print "getAllSuppliersFromProduct"
	catalog = product.catalog
	if catalog.view_permission == "push":
		print "getAllSuppliersFromProduct push"
		sellingCompanyObj = Buyer.objects.filter(buying_company=buying_company, status="approved").values_list('selling_company', flat=True).distinct()
		cpfObj = CompanyProductFlat.objects.filter(catalog=catalog, buying_company=buying_company, is_disable=False, selling_company__in=list(sellingCompanyObj)).exclude(selling_company=buying_company).select_related('selling_company__address__city', 'selling_company__address__state').prefetch_related('selling_company__sellerpolicy_set').order_by('-selling_company__trusted_seller','id')
		# if is_full_catalog is False:
		# 	cpfObj = cpfObj.filter(push_reference__)

		seller_priority_arr = getPriorityWiseSuppliers(cpfObj, buying_company, catalog.view_permission)

		return seller_priority_arr
		# return cpfObj
	else:
		print "getAllSuppliersFromProduct public"
		dtnow = datetime.now()
		catalgsellerObjs = CatalogSeller.objects.filter(catalog=catalog, selling_type="Public", status="Enable", expiry_date__gt=dtnow).exclude(selling_company=buying_company).select_related('selling_company__address__city', 'selling_company__address__state').prefetch_related('selling_company__sellerpolicy_set').order_by('-selling_company__trusted_seller','id')
		if is_full_catalog is False:
			catalgsellerObjs = catalgsellerObjs.filter(sell_full_catalog=False)

		seller_priority_arr = getPriorityWiseSuppliers(catalgsellerObjs, buying_company, catalog.view_permission)

		return seller_priority_arr
		# if catalgsellerObjs:
		# 	return catalgsellerObjs
	return []
	# return None

#~ def getSupplierFromProduct(product, buying_company):
	#~ catalog = product.catalog
	#~ if catalog.view_permission == "push":
		#~ sellingCompanyObj = Buyer.objects.filter(buying_company=buying_company, status="approved").values_list('selling_company', flat=True).distinct()
		#~ cpfObj = CompanyProductFlat.objects.filter(catalog=catalog, buying_company=buying_company, is_disable=False, selling_company__in=list(sellingCompanyObj)).select_related('push_reference', 'selling_company').last()
		#~ supplierObj = cpfObj.selling_company
		#~ return supplierObj
	#~ else:
		#~ dtnow = datetime.now()
		#~ catalgsellerObjs = CatalogSeller.objects.filter(catalog=catalog, selling_type="Public", status="Enable", expiry_date__gt=dtnow).order_by('-selling_company__trusted_seller','id')
		#~ csFirstObj = catalgsellerObjs.first()
		#~ if csFirstObj:
			#~ supplierObj = csFirstObj.selling_company
			#~ return supplierObj
	#~ return None

def getSupplierFromProduct(product, buying_company, is_full_catalog):
	sellersarr = getAllSuppliersFromProduct(product, buying_company, is_full_catalog)
	if len(sellersarr) > 0:
		return sellersarr[0][0]
	return None
	# cpfORcsObjs = getAllSuppliersFromProduct(product, buying_company)
	# if cpfORcsObjs:
	# 	cpfORcsObj = cpfORcsObjs.first()
	# 	return cpfORcsObj.selling_company
	# else:
	# 	return None

def converCartToOrder(cart):
	logger.info("in converCartToOrder cart = %s"% (cart))
	selling_companies = []
	cartitems = cart.items.all()
	for item in cartitems:
		if item.selling_company.id not in selling_companies:
			selling_companies.append(item.selling_company.id)

	logger.info("in converCartToOrder cart = %s, selling_companies = %s"% (cart.id, selling_companies))

	paid_amount = cart.paid_amount
	cartpayment = cart.cartpayment_set.last()
	shipping_charges = cart.shipping_charges

	for selling_company in selling_companies:
		pudata = {}
		#~ pudata['order_number'] = order_number
		#pudata['customer_status'] = 'Pending'
		pudata['processing_status'] = cart.processing_status #'Pending'
		pudata['seller_company'] = selling_company
		pudata['company'] = cart.buying_company.id
		pudata['source_type'] = 'Marketplace'
		#~ pudata['order_type'] = 'Credit'
		pudata['userid'] = cart.user.id
		pudata['cart'] = cart.id

		if cart.ship_to:
			pudata['ship_to'] = cart.ship_to.id
		pudata['shipping_charges'] = shipping_charges

		pudata['items'] = []

		#pudata['items'] = items.filter(selling_company=selling_company)
		selleritems = cartitems.filter(selling_company=selling_company)
		for selleritem in selleritems:
			pudata['items'].append({"product":selleritem.product.id,"quantity":selleritem.quantity,"rate":selleritem.rate, "pending_quantity":selleritem.quantity, "note":selleritem.note, "is_full_catalog":selleritem.is_full_catalog})

		if cart.order_type == "Credit" and cart.processing_status == "Pending":
			pudata['processing_status'] = 'Pending'
			pudata['payment_details'] = 'BUY ON CREDIT' #'buy on credit'

		logger.info("in converCartToOrder cart = %s, salesorder json pudata = %s"% (cart.id, pudata))

		salesorderser = SalesOrderSerializer(data=pudata)
		if salesorderser.is_valid():
			logger.info("in converCartToOrder order salesorderser.is_valid()")
			salesorder = salesorderser.save(user=cart.user)
			logger.info("in converCartToOrder cart = %s, salesorder = %s"% (cart.id, salesorder.id))

			shipping_charges = Decimal('0.00')


			'''invoice = Invoice.objects.create(order=salesorder)

			invoice.amount = Decimal(0.0)
			invoice.total_amount = Decimal(0.0)
			invoice.seller_discount = Decimal(0.0)
			invoice.taxes = Decimal(0.0)

			for ordreitem in salesorder.items.all():
				ciObj = cartitems.filter(product=ordreitem.product).last()
				InvoiceItem.objects.create(invoice=invoice, order_item=ordreitem, qty=ciObj.quantity, tax_class_1=ciObj.tax_class_1, tax_value_1=ciObj.tax_value_1, tax_class_2=ciObj.tax_class_2, tax_value_2=ciObj.tax_value_2, rate=ciObj.rate, amount=ciObj.amount, total_amount=ciObj.total_amount, discount=ciObj.discount)

				invoice.total_qty += ciObj.quantity
				invoice.amount += ciObj.amount
				invoice.total_amount += ciObj.total_amount
				invoice.seller_discount += ciObj.discount
				invoice.taxes += ciObj.tax_value_1 + ciObj.tax_value_2

			invoice.save()'''

			if cart.order_type == "Credit" and cart.processing_status == "Pending":
				#buy on credit so we are not creating invoice and payment
				print "continue if order type is order_type"

				#for supplier notification.
				jsonarr = {}
				jsonarr['order_number'] = salesorder.order_number
				jsonarr['table_id'] = salesorder.id
				jsonarr['title'] = "Sales Order on Credit"

				user1 = salesorder.seller_company.company_users.values_list('user', flat=True)
				user1 = User.objects.filter(id__in=user1).exclude(groups__name="salesperson")

				sendAllTypesMessage("send_order_on_credit", user1, jsonarr)

				continue
			else:
				order = SalesOrder.objects.get(pk=salesorder.id)

				invoiceitems = []
				for item in order.items.all():
					invoiceitems.append({"order_item":item.id, "qty":item.pending_quantity})

				jsondata = {"order":order.id, "invoiceitem_set":invoiceitems}
				invser = InvoiceSerializer(data=jsondata)
				if invser.is_valid():
					logger.info("in converCartToOrder invoice save is_valid")
					invoice = invser.save()
					logger.info("in converCartToOrder cart = %s, invoice = %s"% (cart.id, invoice.id))

					invoice = Invoice.objects.get(pk=invoice.id)
					amount = 0
					if invoice.total_amount <= paid_amount:
						amount = invoice.total_amount
						paid_amount = paid_amount - invoice.total_amount
					else:
						amount = paid_amount
						paid_amount = 0

					#generateOrderToInvoice(invoice.id, amount, cart.payment_method, {}, None, None, date.today(), None)
					# jsondata = {}
					# if cartpayment.mode == "PayTM":
					# 	jsondata['STATUS'] = ''
					# 	if cartpayment.status == "Success":
					# 		jsondata['STATUS'] = 'TXN_SUCCESS'
					# elif cartpayment.mode == "Mobikwik":
					# 	jsondata['statuscode'] = -1
					# 	if cartpayment.status == "Success":
					# 		jsondata['statuscode'] = 0
					# elif cartpayment.mode == "Zaakpay" or cartpayment.mode == "COD": #pass Zaakpay response on cod
					# 	jsondata['responseCode'] = -1
					# 	if cartpayment.status == "Success":
					# 		jsondata['responseCode'] = 100
					offline_payment = False
					if cartpayment.status == "Pending":
						offline_payment = True

					jsondata = cartpayment.payment_details
					details = None
					if "Mode" in jsondata and "Status" in jsondata:
						details = cartpayment.payment_details

					generateInvoicePayment(invoice.id, amount, cart.payment_method, jsondata, cartpayment.status, cart.user, None, date.today(), details, offline_payment)


					#payment entry
				else:
					err = invoice.errors.values()
					logger.info("invoice.errors === %s"% (str(err)))
					#raise serializers.ValidationError({"invoice":"Invoice not found. Please try again later"})

		else:
			err = salesorderser.errors.values()
			logger.info("in converCartToOrder errors err = %s"% (err))

	return True

def calCartTaxnDiscount(cart_id):
	cart = Cart.objects.get(pk=cart_id)
	logger.info("in calCartTaxnDiscount cart = %s"% (cart))

	selling_companies = []
	items = cart.items.all()
	for item in items:
		if item.selling_company not in selling_companies:
			selling_companies.append(item.selling_company)

	logger.info("in calCartTaxnDiscount cart = %s, selling_companies = %s"% (cart.id, selling_companies))

	cart.seller_discount = Decimal(0.0)
	cart.total_qty = 0
	cart.amount = Decimal(0.0)
	cart.paid_amount = Decimal(0.0)
	cart.taxes = Decimal(0.0)
	cart.total_amount = Decimal(0.0)
	cart.pending_amount = Decimal(0.0)
	cart.save()

	for selling_company in selling_companies:
		res = []

		totalqty = 0
		invoice_amount = Decimal(0.0)

		taxes = Decimal(0.0)
		total_amount = Decimal(0.0)

		total_seller_discount = Decimal(0.0)

		is_cash_discount = cart.order_type != "Credit"
		discount_percent = getSupplierRelDiscount(selling_company, cart.buying_company, is_cash_discount)


		cartitems = items.filter(selling_company=selling_company)

		for item in cartitems:
			logger.info("in calCartTaxnDiscount cart = %s, cartitems loop = %s"% (cart.id, item))

			# discount_percent = getSupplierRelDiscountV2(selling_company, cart.buying_company, is_cash_discount, item.product)

			#order_item = item.pop('order_item')
			#invoice = invoiceObj

			#qty = item.pop('qty')
			qty = item.quantity

			totalqty += int(qty)
			try:
				#invoice_amount += order_item.rate*order_item.quantity
				invoice_amount += item.rate*qty
			except Exception:
				pass

			#item_total_amount = Decimal(0.0)
			#jsondata = {'invoice':invoiceObj.id, 'order_item':order_item.id, 'qty':qty, 'rate':order_item.rate, 'amount':order_item.rate*qty}
			item_total_amount = item.rate*qty

			count = 1

			taxObjs = getTaxClassObj(selling_company, cart.buying_company, item.product.catalog.category, item.rate)
			logger.info("in calCartTaxnDiscount cart = %s, taxObjs = %s"% (cart.id, taxObjs))

			# if discount_percent is None:
			# 	discount_percent = Decimal(0.0)

			item_price = item.rate*qty
			item_discount = item_price * discount_percent / 100
			item_price -= item_discount
			logger.info("in calCartTaxnDiscount cart = %s, item_total_amount = %s"% (cart.id, item_total_amount))
			item_total_amount -= item_discount
			logger.info("in calCartTaxnDiscount cart = %s, item_total_amount - discount = %s"% (cart.id, item_total_amount))
			total_seller_discount += item_discount

			item.tax_value_1 = Decimal('0.00')
			item.tax_class_1 = None
			item.tax_value_2 = Decimal('0.00')
			item.tax_class_2 = None

			for taxObj in taxObjs:
				print taxObj
				if count == 1:
					#tax_value_1= (order_item.rate*order_item.quantity * taxObj.percentage)/100
					tax_value_1= (item_price * taxObj.percentage)/100
					#~ jsondata['tax_value_1'] = round(tax_value_1, 2)
					#~ jsondata['tax_class_1'] = taxObj.id

					item.tax_value_1 = round(tax_value_1, 2)
					item.tax_class_1 = taxObj

					item_total_amount += tax_value_1
					print "item_total_amount + tax = ",item_total_amount
					taxes += tax_value_1

				elif count == 2:
					#tax_value_2 = (order_item.rate*order_item.quantity * taxObj.percentage)/100
					tax_value_2 = (item_price * taxObj.percentage)/100
					#~ jsondata['tax_value_2'] = round(tax_value_2, 2)
					#~ jsondata['tax_class_2'] = taxObj.id

					item.tax_value_2 = round(tax_value_2, 2)
					item.tax_class_2 = taxObj

					item_total_amount += tax_value_2
					print "item_total_amount + tax = ",item_total_amount
					taxes += tax_value_2

				count += 1

			item.total_amount = round(item_total_amount, 2)
			logger.info("in calCartTaxnDiscount cart = %s, item.total_amount = %s"% (cart.id, item.total_amount))
			item.discount = round(item_discount, 2)
			item.discount_percent = discount_percent
			item.amount = item.rate*qty
			logger.info("in calCartTaxnDiscount cart = %s, item.amount = %s"% (cart.id, item.amount))
			item.save()

			#~ jsondata['total_amount'] = round(item_total_amount, 2)
			#~ jsondata['discount'] = round(item_discount, 2)
			#gst
			#~ logger.info("InvoiceSerializer create jsondata = %s"% (str(jsondata)))
			#~ initser = InvoiceItemSerializer(data=jsondata)
			#~ if initser.is_valid():
				#~ logger.info("InvoiceSerializer create jsondata save() is_valid true")
				#~ initser.save()
			#~ else:
				#~ logger.info("InvoiceSerializer create jsondata error = %s"% (str(initser.errors)))

		#~ if totalqty != invoiceObj.order.total_products():
			#~ invoiceObj.order.processing_status="In Progress"
			#~ invoiceObj.order.save()



		#~ if cart.seller_discount:
		cart.seller_discount = cart.seller_discount + total_seller_discount
		#~ else:
			#~ cart.seller_discount = total_seller_discount

		logger.info("in calCartTaxnDiscount cart = %s, cart.seller_discount = %s"% (cart.id, cart.seller_discount))
		cart.total_qty = cart.total_qty + totalqty

		#~ if cart.amount:
		cart.amount = cart.amount + invoice_amount
		#~ else:
			#~ cart.amount = invoice_amount

		#~ if cart.paid_amount:
		#cart.paid_amount = cart.paid_amount + Decimal(0.0)
		#~ else:
			#~ cart.paid_amount = Decimal(0.0)

		#~ if cart.taxes:
		cart.taxes = cart.taxes + taxes
		logger.info("in calCartTaxnDiscount cart = %s, cart.taxes = %s"% (cart.id, cart.taxes))
		#~ else:
			#~ cart.taxes = taxes

		#final_amount = invoice_amount + taxes - invoiceObj.seller_discount + invoiceObj.shipping_charges
		#~ final_amount = invoice_amount + taxes
		final_amount = cart.amount + cart.taxes
		if cart.seller_discount is not None:
			final_amount -= cart.seller_discount
		if cart.shipping_charges is not None:
			final_amount += cart.shipping_charges
		cart.total_amount = final_amount
		cart.pending_amount = final_amount

		logger.info("in calCartTaxnDiscount cart = %s, cart.total_amount = %s"% (cart.id, cart.total_amount))
		logger.info("in calCartTaxnDiscount cart = %s, cart.amount = %s"% (cart.id, cart.amount))

		cart.save()

	return cart

def cartwiseProductArray(catalogs, filtereditems, catalogsjson):
	from api.v1.order.serializers import CartItemSerializer
	from copy import copy

	products = []
	min_price = None
	max_price = None

	amount = 0
	total_amount = 0
	discount = 0
	discount_percent = 0
	tax_class_1 = None
	tax_class_1_percentage = 0
	tax_value_1 = 0
	tax_class_2 = None
	tax_class_2_percentage = 0
	tax_value_2 = 0

	for filtereditem in filtereditems:
		product = CartItemSerializer(instance=filtereditem)
		product = product.data
		products.append(product)

		if min_price is None or max_price is None:
			min_price = max_price = filtereditem.rate
		if filtereditem.rate < min_price:
			min_price = filtereditem.rate
		if filtereditem.rate > max_price:
			max_price = filtereditem.rate

		if filtereditem.amount:
			amount += filtereditem.amount
		if filtereditem.total_amount:
			total_amount += filtereditem.total_amount
		discount += filtereditem.discount
		discount_percent += filtereditem.discount_percent
		if filtereditem.tax_class_1:
			tax_class_1 = filtereditem.tax_class_1.tax_name
			tax_class_1_percentage += filtereditem.tax_class_1.percentage
		if filtereditem.tax_class_2:
			tax_class_2 = filtereditem.tax_class_2.tax_name
			tax_class_2_percentage += filtereditem.tax_class_2.percentage
		tax_value_1 += filtereditem.tax_value_1
		tax_value_2 += filtereditem.tax_value_2

	catalogsjson = copy(catalogsjson)
	catalogsjson['products'] = products
	catalogsjson['total_products'] = len(products)
	if min_price == max_price:
		catalogsjson['price_range'] = str(int(min_price))
	else:
		catalogsjson['price_range'] = str(int(min_price))+"-"+str(int(max_price))

	catalogsjson['catalog_amount'] = amount
	catalogsjson['catalog_total_amount'] = total_amount
	catalogsjson['catalog_discount'] = discount
	catalogsjson['catalog_discount_percent'] = discount_percent / len(products)
	catalogsjson['tax_class_1'] = tax_class_1
	catalogsjson['tax_class_2'] = tax_class_2
	catalogsjson['catalog_tax_class_1_percentage'] = tax_class_1_percentage / len(products)
	catalogsjson['catalog_tax_class_2_percentage'] = tax_class_2_percentage / len(products)
	catalogsjson['catalog_tax_value_1'] = tax_value_1
	catalogsjson['catalog_tax_value_2'] = tax_value_2

	catalogs.append(catalogsjson)

def getTotalCartItemCount(cart):
	#jsonarr['total_cart_items'] = cart.items.count()

	# total1 = cart.items.filter(is_full_catalog=True).values('selling_company','product__catalog','is_full_catalog').distinct().count()
	# total2 = cart.items.filter(is_full_catalog=False).distinct().count()
	# jsonarr['total_cart_items'] = total1 + total2

	# total1 = cart.items.filter(is_full_catalog=True).values('selling_company','product__catalog','is_full_catalog').distinct().aggregate(total_quantity=Sum('quantity')).get('total_quantity', 0)
	# total2 = cart.items.filter(is_full_catalog=False).aggregate(total_quantity=Sum('quantity')).get('total_quantity', 0)
	# print total1
	# print total2
	# if total1 is None:
	# 	total1 = 0
	# if total2 is None:
	# 	total2 = 0
	# jsonarr['total_cart_items'] = total1 + total2

	logger.info("in getTotalCartItemCount start cart = %s"% (cart.id))
	total = 0
	groupitems = cart.items.all().values('selling_company','product__catalog','is_full_catalog', 'note').distinct()
	logger.info("in getTotalCartItemCount cart = %s, groupitems = %s"% (cart.id, groupitems))
	for groupitem in groupitems:
		filtereditems = cart.items.filter(selling_company=groupitem['selling_company'], product__catalog=groupitem['product__catalog'], is_full_catalog=groupitem['is_full_catalog'], note=groupitem['note'])
		logger.info("in getTotalCartItemCount cart = %s, filtereditems = %s"% (cart.id, filtereditems))

		if groupitem['is_full_catalog'] == True:
			filtereditems_first = filtereditems.first()
			if filtereditems_first:
				total += filtereditems_first.quantity
				logger.info("in getTotalCartItemCount cart = %s, filtereditems_first.quantity = %s"% (cart.id, filtereditems_first.quantity))
		else:
			for filtereditem in filtereditems:
				total += filtereditem.quantity
				logger.info("in getTotalCartItemCount cart = %s, filtereditem.quantity = %s"% (cart.id, filtereditem.quantity))

		logger.info("in getTotalCartItemCount end cart = %s, total = %s"% (cart.id, total))
	return total
