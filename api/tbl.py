from api.models import *
#from api.serializers import *
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q

from rest_framework import permissions
from rest_framework.views import APIView

from api.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, IsCompanyOrAdmin, IsCompanyAdministratorOrAdmin, IsOwner, HasGroupOrPermission

from django.db.models import Sum
#import datetime
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Case, When

from api.common_functions import *

from django.conf import settings

'''generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from api.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, IsCompanyOrAdmin, IsCompanyAdministrator, IsOwner, HasGroupOrPermission #owner update or delete
'''

class UserDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number','groups.name'] #Table columns
	order_columns = ['id', 'id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number','groups.name']
	search_columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number','groups.name']

	def get_initial_queryset(self):
		#Initial Queryset
		return User.objects.all()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(username__icontains=search)|qs.filter(first_name__icontains=search)|qs.filter(last_name__icontains=search)|qs.filter(email__icontains=search)|qs.filter(userprofile__phone_number__icontains=search)|qs.filter(groups__name__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		username = self.request.GET.get('columns[2][search][value]', None)
		if username:
			qs = qs.filter(username__icontains=username)

		first_name = self.request.GET.get('columns[3][search][value]', None)
		if first_name:
			qs = qs.filter(first_name__icontains=first_name)

		last_name = self.request.GET.get('columns[4][search][value]', None)
		if last_name:
			qs = qs.filter(last_name__icontains=last_name)

		email = self.request.GET.get('columns[5][search][value]', None)
		if email:
			qs = qs.filter(email__icontains=email)

		phone_number = self.request.GET.get('columns[6][search][value]', None)
		if phone_number:
			qs = qs.filter(userprofile__phone_number__icontains=phone_number)

		group_name = self.request.GET.get('columns[7][search][value]', None)
		if group_name:
			qs = qs.filter(groups__name__icontains=group_name)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			groupObj = item.groups.all().values_list('name', flat=True)
			groups = ', '.join(groupObj)

			json_data.append([
				'',
				item.id,
				item.username,
				item.first_name,
				item.last_name,
				item.email,
				item.userprofile.phone_number,
				groups
			])
		return json_data

class CityDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','city_name', 'state'] #Table columns
	order_columns = ['id', 'id','city_name', 'state']
	search_columns = ['id','city_name', 'state']

	def get_initial_queryset(self):
		#Initial Queryset
		return City.objects.all().order_by('-id')

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(state__state_name__icontains=search)|qs.filter(city_name__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		city_name = self.request.GET.get('columns[2][search][value]', None)
		if city_name:
			city_name_parts = city_name.split(' ')
			qs_params = None
			for part in city_name_parts:
				q = Q(city_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		state_name = self.request.GET.get('columns[3][search][value]', None)
		if state_name:
			state_name_parts = state_name.split(' ')
			qs_params = None
			for part in state_name_parts:
				q = Q(state__state_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			json_data.append([
				'',
				item.id,
				item.city_name,
				item.state.state_name
			])
		return json_data

class StateDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id', 'state_name'] #Table columns
	order_columns = ['id', 'id', 'state_name']
	search_columns = ['id', 'state_name']

	def get_initial_queryset(self):
		#Initial Queryset
		return State.objects.all()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(state_name__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		state_name = self.request.GET.get('columns[2][search][value]', None)
		if state_name:
			state_name_parts = state_name.split(' ')
			qs_params = None
			for part in state_name_parts:
				q = Q(state_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			json_data.append([
				'',
				item.id,
				item.state_name
			])
		return json_data

class BrandDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','name', 'company'] #Table columns
	order_columns = ['id', 'id','name', 'company']
	search_columns = ['id','name', 'company']

	def get_initial_queryset(self):
		#Initial Queryset
		return Brand.objects.all().select_related('company')

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(company__name__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		name = self.request.GET.get('columns[2][search][value]', None)
		if name:
			name_parts = name.split(' ')
			qs_params = None
			for part in name_parts:
				q = Q(name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		company = self.request.GET.get('columns[3][search][value]', None)
		if company:
			company_parts = company.split(' ')
			qs_params = None
			for part in company_parts:
				q = Q(company__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			json_data.append([
				'',
				item.id,
				item.name,
				item.company.name
			])
		return json_data


class CompanyDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','name', 'brand', 'phone_number', 'invoice_credit', 'state', 'city', 'buyer_invited', 'buyer_registered', 'buyer_accepted', 'supplier_invited', 'supplier_registered', 'supplier_accepted'] #Table columns
	order_columns = ['id','name', 'brand', 'phone_number', 'id', 'state', 'city']
	search_columns = ['id','name', 'phone_number']

	def get_initial_queryset(self):
		#Initial Queryset
		return Company.objects.all().select_related('state','city').prefetch_related('brand_set')

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(phone_number__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			name_parts = name.split(' ')
			qs_params = None
			for part in name_parts:
				q = Q(name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		phone_number = self.request.GET.get('columns[3][search][value]', None)
		if phone_number:
			phone_number_parts = phone_number.split(' ')
			qs_params = None
			for part in phone_number_parts:
				q = Q(phone_number__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		state = self.request.GET.get('columns[5][search][value]', None)
		if state:
			qs = qs.filter(state__state_name__icontains=state)

		city = self.request.GET.get('columns[6][search][value]', None)
		if city:
			qs = qs.filter(city__city_name__icontains=city)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			# brandObj = Brand.objects.filter(company=item.id).values_list('name', flat=True)
			# brands = ', '.join(brandObj)

			brands = []
			for brand in item.brand_set.all():
				brands.append(brand.name)
			brands = ', '.join(brands)

			invoice_credit = WishbookCredit.objects.filter(company=item.id, expire_date__gte=date.today()).aggregate(Sum('balance_amount')).get('balance_amount', 0)
			if invoice_credit is None:
				invoice_credit = 0

			state = None
			if item.state:
				state = item.state.state_name
			city = None
			if item.city:
				city = item.city.city_name

			json_data.append([
				item.id,
				item.name,
				brands,
				item.phone_number,
				invoice_credit,
				state,
				city,
				Invitee.objects.filter(invite__company=item.id, invite__relationship_type="buyer").count(),
				Buyer.objects.filter(selling_company=item.id, buying_company__isnull = False).count(),
				Buyer.objects.filter(selling_company=item.id, status="approved").count(),
				Invitee.objects.filter(invite__company=item.id, invite__relationship_type="supplier").count(),
				Buyer.objects.filter(buying_company=item.id, selling_company__isnull = False).count(),
				Buyer.objects.filter(buying_company=item.id, status="approved").count(),
			])
		return json_data

class MarketingDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','created', 'campaign_name', 'to', 'user__username'] #Table columns
	order_columns = ['id','created', 'campaign_name', 'to', 'user__username']
	search_columns = ['id','created', 'campaign_name', 'to', 'user__username']

	def get_initial_queryset(self):
		#Initial Queryset
		return Marketing.objects.all().select_related('user')

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(campaign_name__icontains=search)|qs.filter(to__icontains=search)|qs.filter(user__username__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		time = self.request.GET.get('columns[1][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created__lte=date[1])

		campaign_name = self.request.GET.get('columns[2][search][value]', None)
		if campaign_name:
			qs = qs.filter(campaign_name__icontains=campaign_name)

		to = self.request.GET.get('columns[3][search][value]', None)
		if to:
			qs = qs.filter(to__icontains=to)

		user = self.request.GET.get('columns[4][search][value]', None)
		if user:
			qs = qs.filter(user__username__icontains=user)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			json_data.append([
				item.id,
				str(timezone.localtime(item.created).strftime("%Y-%m-%d : %I:%M%p")),
				item.campaign_name,
				item.to,
				item.user.username
			])
		return json_data

class CompanyBuyerSupplierDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','name', 'type', 'buyer_invited', 'buyer_registered', 'buyer_accepted', 'supplier_invited', 'supplier_registered', 'supplier_accepted']
	order_columns = ['id','name']
	search_columns = ['id','name']

	def get_initial_queryset(self):

		company_id = self.request.GET.get('company_id', None)

		company_type = self.request.GET.get('company_type', None)

		queryset = Company.objects.all()

		if company_type == "buyer":
			buying_company = Buyer.objects.filter(selling_company=company_id).values_list('buying_company', flat=True)
			queryset = queryset.filter(id__in = buying_company)

		if company_type == "supplier":
			selling_company = Buyer.objects.filter(buying_company=company_id).values_list('selling_company', flat=True)
			queryset = queryset.filter(id__in = selling_company)

		return queryset

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(phone_number__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			name_parts = name.split(' ')
			qs_params = None
			for part in name_parts:
				q = Q(name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []

		company_id = self.request.GET.get('company_id', None)

		company_type = self.request.GET.get('company_type', None)

		for item in qs:
			if company_type == "buyer":
				company_type = Buyer.objects.filter(selling_company=company_id, buying_company=item.id).values_list('group_type__name', flat=True).first()

			if company_type == "supplier":
				company_type = Buyer.objects.filter(selling_company=item.id, buying_company=company_id).values_list('group_type__name', flat=True).first()#.group_type.name

			json_data.append([
				item.id,
				item.name,
				company_type,
				Invitee.objects.filter(invite__company=item.id, invite__relationship_type="buyer").count(),
				Buyer.objects.filter(selling_company=item.id, buying_company__isnull = False).count(),
				Buyer.objects.filter(selling_company=item.id, status="approved").count(),
				Invitee.objects.filter(invite__company=item.id, invite__relationship_type="supplier").count(),
				Buyer.objects.filter(buying_company=item.id, selling_company__isnull = False).count(),
				Buyer.objects.filter(buying_company=item.id, status="approved").count(),
			])
		return json_data


class CompanyPendingBuyerSupplierDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','name', 'type', 'phone number', ]
	order_columns = ['id','name', 'type', 'phone number',]
	search_columns = ['id','name', 'type', 'phone number',]

	def get_initial_queryset(self):

		company_id = self.request.GET.get('company_id', None)

		company_type = self.request.GET.get('company_type', None)

		queryset = Buyer.objects.all().select_related('invitee', 'group_type')

		if company_type == "buyer":
			return queryset.filter(selling_company=company_id, buying_company__isnull = True, invitee__isnull = False)

		if company_type == "supplier":
			return queryset.filter(buying_company=company_id, selling_company__isnull = True, invitee__isnull = False)

		return Buyer.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(invitee__invitee_name__icontains=search)|qs.filter(group_type__name__icontains=search)|qs.filter(invitee__invitee_number__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		company_name = self.request.GET.get('columns[1][search][value]', None)
		if company_name:
			qs = qs.filter(invitee__invitee_name__icontains=company_name)

		company_type = self.request.GET.get('columns[2][search][value]', None)
		if company_type:
			qs = qs.filter(group_type__name__icontains=company_type)

		invitee_number = self.request.GET.get('columns[3][search][value]', None)
		if invitee_number:
			qs = qs.filter(invitee__invitee_number__icontains=invitee_number)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []

		for item in qs:
			if item.group_type:
				group_name = item.group_type.name
			else:
				group_name=None

			json_data.append([
				item.id,
				item.invitee.invitee_name,
				group_name,
				item.invitee.invitee_number,
			])
		return json_data


class OrderDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id', 'order_number', 'time', 'seller_company', 'company', 'items', 'total_rate', 'customer_status', 'processing_status', 'id', 'id', 'id'] #Table columns
	order_columns = ['id','id','id', 'order_number','id', 'time', 'seller_company', 'company','id', 'items', 'id', 'id','id','customer_status', 'processing_status', 'id']
	search_columns = ['order_number', 'time', 'seller_company', 'company', 'items', 'total_rate', 'customer_status', 'processing_status']

	def get_initial_queryset(self):
		#Initial Queryset

		order_days = self.request.GET.get('order_days', None)
		order_status = self.request.GET.get('order_status', None)

		queryset = SalesOrder.objects.all().select_related('seller_company','company', 'tranferred_to').prefetch_related('items__product__catalog', 'invoice_set')

		#If User is Staff User
		user = self.request.user

		return queryset

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(order_number__icontains=search)|qs.filter(date__icontains=search)|qs.filter(time__icontains=search)|qs.filter(processing_status__icontains=search)|qs.filter(customer_status__icontains=search)|qs.filter(company__name__icontains=search)|qs.filter(tracking_details__icontains=search)|qs.filter(seller_company__name__icontains=search)

		'''#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)'''

		oid = self.request.GET.get('columns[2][search][value]', None)
		if oid:
			qs = qs.filter(id__icontains=oid)

		order_number = self.request.GET.get('columns[3][search][value]', None)
		if order_number:
			qs = qs.filter(order_number__icontains=order_number)

		invoice_id = self.request.GET.get('columns[4][search][value]', None)
		if invoice_id:
			orderids = Invoice.objects.filter(id__icontains=invoice_id).values_list('order_id', flat=True) #get all invoice ids
			qs = qs.filter(Q(id__in=orderids))

		time = self.request.GET.get('columns[5][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(time__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(time__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(time__lte=date[1])

		supplier_name = self.request.GET.get('columns[6][search][value]', None)
		if supplier_name:
			qs = qs.filter(Q(seller_company__name__icontains=supplier_name) | Q(seller_company__phone_number__icontains=supplier_name))

		buyer_name = self.request.GET.get('columns[7][search][value]', None)
		if buyer_name:
			qs = qs.filter(Q(company__name__icontains=buyer_name) | Q(company__phone_number__icontains=buyer_name))

		order_type = self.request.GET.get('columns[12][search][value]', None)
		if order_type:
			qs = qs.filter(order_type=order_type)

		order_status = self.request.GET.get('columns[13][search][value]', None)
		if order_status:
			qs = filterOrderPaymentStatus(qs, order_status)

		processing_status = self.request.GET.get('columns[14][search][value]', None)
		if processing_status:
			processing_status = processing_status.split(',')
			qs = qs.filter(processing_status__in=processing_status)

		tracking_details = self.request.GET.get('columns[15][search][value]', None)
		if tracking_details:
			qs = qs.filter(tracking_details__icontains=tracking_details)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			#salesOrderItemObj = SalesOrderItem.objects.filter(sales_order=item.id).values_list('product__title', flat=True)
			#salesOrderItems = ', '.join(salesOrderItemObj)

			#noOfItemObj = SalesOrderItem.objects.filter(sales_order=item.id).count()

			'''customer_status = item.customer_status
			if item.customer_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if item.customer_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)'''
			payment_status = item.payment_status()
			customer_status = payment_status
			if payment_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if payment_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)

			processing_status = item.processing_status
			if item.processing_status == "Cancelled" and item.supplier_cancel is not None and item.supplier_cancel != "":
				processing_status += "<br> Note: "+str(item.supplier_cancel)
			if (item.processing_status == "Dispatched" or item.processing_status == "Delivered") and item.tracking_details is not None and item.tracking_details != "":
				processing_status += "<br> Note: "+str(item.tracking_details)
			if item.processing_status == "Transferred" and item.tranferred_to is not None:
				processing_status += "<br> To : "+str(item.tranferred_to.seller_company.name)

			#invoices 		= Invoice.objects.filter(order=item).values_list('id', flat=True) #get all invoice ids
			invoices 		= []
			for invoice in item.invoice_set.all():
				invoices.append(invoice.id)
			'''catalog_names 	= item.items.all().values_list('product__catalog__title', flat=True).distinct()  #get all catalog name
			catalog_name_piece = []
			for catalog_name in catalog_names:
				pieces = item.items.filter(Q(product__catalog__title=catalog_name)).aggregate(Sum('quantity')).get('quantity__sum', 0)
				if pieces is None:
					pieces = 0
				catalog_name_piece.append(catalog_name + '(' + str(pieces) + ')')'''

			catalog_names = []
			catalog_quantity = []
			catalog_name_piece = []
			for orderitem in item.items.all():
				if orderitem.product.catalog.title not in catalog_names:
					catalog_names.append(orderitem.product.catalog.title)
					catalog_quantity.append(0)
				catalog_index = catalog_names.index(orderitem.product.catalog.title)
				catalog_quantity[catalog_index] += orderitem.quantity
			idx = 0
			for catalog_name in catalog_names:
				catalog_name_piece.append(catalog_name + '(' + str(catalog_quantity[idx]) + ')')
				idx += 1



			json_data.append([
				item.id,
				{"total_pending_quantity":item.total_pending_quantity(), "buying_company_id":item.company.id, "selling_company_id":item.seller_company.id, "invoices":list(invoices)},
				item.id,
				item.order_number,
				list(invoices),
				str(timezone.localtime(item.time).strftime("%Y-%m-%d : %I:%M%p")),
				item.seller_company.name,
				item.company.name,
				list(catalog_name_piece),
				item.total_item(),
				item.total_rate(),
				item.transaction_type,
				item.order_type,
				customer_status,
				processing_status,
				item.id,
				item.id,
				# {"total_pending_quantity":item.total_pending_quantity(), "buying_company_id":item.company.id, "selling_company_id":item.seller_company.id, "invoices":list(invoices)},
				#item.seller_company.id,
				#item.company.id,

				#item.tracking_details,
				#item.supplier_cancel,
				#item.buyer_cancel,
				#item.payment_details,
			])
		return json_data


class BranchDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','name', 'street_address', 'pincode', 'phone_number', 'company', 'city', 'state'] #Table columns
	order_columns = ['id','name', 'street_address', 'pincode', 'phone_number', 'company', 'city', 'state']
	search_columns = ['id','name', 'street_address', 'pincode', 'phone_number', 'company', 'city', 'state']

	def get_initial_queryset(self):
		#Initial Queryset
		return Branch.objects.all()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(street_address__icontains=search)|qs.filter(pincode__icontains=search)|qs.filter(phone_number__icontains=search)|qs.filter(company__name__icontains=search)|qs.filter(city__city_name__icontains=search)|qs.filter(state__state_name__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		name = self.request.GET.get('columns[2][search][value]', None)
		if name:
			name_parts = name.split(' ')
			qs_params = None
			for part in name_parts:
				q = Q(name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		street_address = self.request.GET.get('columns[3][search][value]', None)
		if street_address:
			street_address_parts = street_address.split(' ')
			qs_params = None
			for part in street_address_parts:
				q = Q(street_address__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		pincode = self.request.GET.get('columns[4][search][value]', None)
		if pincode:
			qs = qs.filter(pincode__icontains=pincode)

		phone_number = self.request.GET.get('columns[5][search][value]', None)
		if phone_number:
			qs = qs.filter(phone_number__icontains=phone_number)

		company = self.request.GET.get('columns[6][search][value]', None)
		if company:
			company_parts = company.split(' ')
			qs_params = None
			for part in company_parts:
				q = Q(company__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		city = self.request.GET.get('columns[7][search][value]', None)
		if city:
			qs = qs.filter(city__city_name__icontains=city)

		state = self.request.GET.get('columns[8][search][value]', None)
		if state:
			qs = qs.filter(state__state_name__icontains=state)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			json_data.append([
				'',
				item.id,
				item.name,
				item.street_address,
				item.pincode,
				item.phone_number,
				item.company.name,
				item.city.city_name,
				item.state.state_name
			])
		return json_data


class CategoryDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id','category_name', 'parent_category.category_name'] #Table columns
	order_columns = ['id','id','category_name', 'parent_category.category_name']
	search_columns = ['id','category_name', 'parent_category.category_name']

	def get_initial_queryset(self):
		#Initial Queryset
		return Category.objects.all()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(category_name__icontains=search)|qs.filter(parent_category__category_name__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		category_name = self.request.GET.get('columns[2][search][value]', None)
		if category_name:
			qs = qs.filter(category_name__icontains=category_name)

		parent_category = self.request.GET.get('columns[3][search][value]', None)
		if parent_category:
			qs = qs.filter(parent_category__category_name__icontains=parent_category)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			parent_category = ''
			if item.parent_category is not None:
				parent_category = item.parent_category.category_name

			json_data.append([
				'',
				item.id,
				item.category_name,
				parent_category
			])
		return json_data

class CatalogAdminDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','id','title', 'thumbnail', 'brand.name', 'category.category_name', 'view_permission', 'id', 'created_at', 'id', 'catalog_type'] #Table columns
	order_columns = ['id','id','title', 'id', 'brand.name', 'category.category_name', 'view_permission', 'id', 'created_at', 'id', 'catalog_type']
	search_columns = ['id','title', 'brand', 'category', 'view_permission', 'created_at']

	def get_initial_queryset(self):
		global company
		queryset = Catalog.objects.filter(deleted=False).select_related('brand', 'category', 'company')

		user = self.request.user
		company = get_user_company(user)

		if user.is_staff:
			return queryset

	def filter_queryset(self, qs):
		global company

		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(title__icontains=search)|qs.filter(brand__name__icontains=search)|qs.filter(category__category_name__icontains=search)|qs.filter(created_at__icontains=search)

		id = self.request.GET.get('columns[1][search][value]', None)
		if id:
			qs = qs.filter(id=id)

		title = self.request.GET.get('columns[2][search][value]', None)
		if title:
			title_parts = title.split(' ')
			qs_params = None
			for part in title_parts:
				q = Q(title__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		brand = self.request.GET.get('columns[4][search][value]', None)
		if brand:
			brand_parts = brand.split(' ')
			qs_params = None
			for part in brand_parts:
				q = Q(brand__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		category = self.request.GET.get('columns[5][search][value]', None)
		if category:
			qs = qs.filter(category__category_name__icontains=category)

		viewtype = self.request.GET.get('columns[6][search][value]', None)
		if viewtype:
			qs = qs.filter(view_permission=viewtype)

		seller_name = self.request.GET.get('columns[7][search][value]', None)
		if seller_name:
			catalogsellercatalogids = CatalogSeller.objects.filter(Q(catalog__in=qs, selling_type="Public") & Q(Q(selling_company__name__icontains=seller_name) | Q(selling_company__phone_number__icontains=seller_name) | Q(selling_company__id__icontains=seller_name))).values_list('catalog', flat=True)
			qs = qs.filter(Q(company__name__icontains=seller_name) | Q(id__in=catalogsellercatalogids) | Q(company__phone_number__icontains=seller_name) | Q(company__id__icontains=seller_name))

		# ~ status = self.request.GET.get('columns[6][search][value]', None)
		# ~ if status:
			# ~ if status == "Disable":
				# ~ qs = qs.filter(id__in=myDisableCatalogIds)
			# ~ elif status == "Enable":
				# ~ qs = qs.exclude(id__in=myDisableCatalogIds)

		time = self.request.GET.get('columns[8][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		catalog_type = self.request.GET.get('columns[10][search][value]', None)
		if catalog_type:
			qs = qs.filter(catalog_type=catalog_type)

		return qs

	def prepare_results(self, qs):
		global company

		json_data = []

		for item in qs:
			viewtype = item.view_permission
			if viewtype == "push":
				viewtype = "private"

			all_sellers = []
			all_sellers_data = []
			all_status = []
			all_expires = []
			if viewtype == "private":
				status = "Enable"
				myDisableCatalogIds = getMyDisableCatalogIds(item.company)
				if item.id in myDisableCatalogIds:
					status = "Disable"
				name_id = {"name" : item.company.name, "id" : item.company_id,"phone_number" : item.company.phone_number}
				all_sellers.append(name_id)
				all_status.append(status)
				#all_expires.append(str(item.expiry_date))
				all_expires.append(timezone.localtime(item.expiry_date).strftime("%Y-%m-%d"))
				all_sellers_data.append({"company_id":item.company.id, "company_name":item.company.name, "status":status})
			else:
				catalogsellers = CatalogSeller.objects.filter(catalog=item, selling_type="Public").select_related('selling_company')
				for catalogseller in catalogsellers:
					status = "Enable"
					myDisableCatalogIds = getMyDisableCatalogIds(catalogseller.selling_company)
					if item.id in myDisableCatalogIds:
						status = "Disable"
					name_id = {
						"name" : catalogseller.selling_company.name,
						"id" : catalogseller.selling_company_id,
						"phone_number" : item.company.phone_number
					}
					all_sellers.append(name_id)
					all_status.append(status)
					#all_expires.append(str(catalogseller.expiry_date))
					all_expires.append(timezone.localtime(catalogseller.expiry_date).strftime("%Y-%m-%d"))
					all_sellers_data.append({"company_id":catalogseller.selling_company.id, "company_name":catalogseller.selling_company.name, "status":status})

			# ~ view_count = CompanyCatalogView.objects.filter(catalog=item).aggregate(Sum('clicks')).get('clicks__sum', 0)
			# ~ if view_count is None:
				# ~ view_count = 0

			catalog_type = "catalogseller"
			if item.company == company:
				catalog_type = "mycatalog"

			json_data.append([
				item.id,
				item.id,
				item.title,
				item.thumbnail.thumbnail[settings.SMALL_IMAGE].url, #item.thumbnail.url,
				item.brand.name,
				item.category.category_name,
				viewtype,
				all_sellers,
				all_status,
				all_expires,
				item.catalog_type, #"",#item.products.count(),
				"",#view_count,
				{"brand":item.brand.id, "catalog_type":catalog_type, "all_sellers_data":all_sellers_data},
			])
		return json_data

class CatalogDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','title', 'thumbnail', 'brand.name', 'category.category_name', 'view_permission', 'id', 'created_at'] #Table columns
	order_columns = ['id','title', 'id', 'brand.name', 'category.category_name', 'view_permission', 'id', 'created_at']
	search_columns = ['title', 'brand', 'category', 'view_permission', 'created_at']

	def get_initial_queryset(self):
		global company
		#Initial Queryset
		queryset = Catalog.objects.filter(deleted=False, catalog_type = "catalog").select_related('brand','category','company').prefetch_related('products')

		#If User is Staff User
		user = self.request.user
		'''if user.is_staff:
			return queryset'''

		try:
			if not user.is_impersonate:
				user.last_login=timezone.now()
				user.save()
		except Exception as e:
			logger.info(str(e))
			print "Exception last_login"
			user.last_login=timezone.now()
			user.save()
			pass

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company

					cscatalogids = CatalogSeller.objects.filter(selling_company=company, selling_type="Public").values_list('catalog', flat=True)
					queryset = queryset.filter(Q(company=company) | Q(id__in=cscatalogids))
					return queryset

					#return queryset.filter(company=company)

			except ObjectDoesNotExist:
				return Catalog.objects.none()
		else:
			return Catalog.objects.none()

		'''elif user.groups.filter(name="salesperson").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(Q(brand__company=company) | Q(view_permission__icontains='public'))
			except ObjectDoesNotExist:
				return Catalog.objects.none()'''

	def filter_queryset(self, qs):
		global company
		global myDisableCatalogIds

		myDisableCatalogIds = getMyDisableCatalogIds(company)

		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(title__icontains=search)|qs.filter(brand__name__icontains=search)|qs.filter(category__category_name__icontains=search)|qs.filter(created_at__icontains=search)

		title = self.request.GET.get('columns[1][search][value]', None)
		if title:
			title_parts = title.split(' ')
			qs_params = None
			for part in title_parts:
				q = Q(title__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		brand = self.request.GET.get('columns[3][search][value]', None)
		if brand:
			brand_parts = brand.split(' ')
			qs_params = None
			for part in brand_parts:
				q = Q(brand__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		category = self.request.GET.get('columns[4][search][value]', None)
		if category:
			qs = qs.filter(category__category_name__icontains=category)

		viewtype = self.request.GET.get('columns[5][search][value]', None)
		if viewtype:
			qs = qs.filter(view_permission=viewtype)


		status = self.request.GET.get('columns[6][search][value]', None)
		if status:
			if status == "Disable":
				#catalogids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(catalog__isnull=True).values_list('catalog', flat=True)
				#qs = qs.filter(id__in=catalogids)
				qs = qs.filter(id__in=myDisableCatalogIds)
			elif status == "Enable":
				#catalogids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(catalog__isnull=True).values_list('catalog', flat=True)
				#qs = qs.exclude(id__in=catalogids)
				qs = qs.exclude(id__in=myDisableCatalogIds)

		time = self.request.GET.get('columns[7][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		return qs

	def prepare_results(self, qs):
		global company
		global myDisableCatalogIds

		#JSON array data
		json_data = []

		#disableCatalogIds = getDisableCatalogIds(company)

		for item in qs:

			#pushCatalogObj = Push_Catalog.objects.filter(catalog=item.id).values_list('push', flat=True)
			#pushIds = str(pushCatalogObj).strip('[]')

			#categoryObj = item.category.all().values_list('category_name', flat=True)
			#categories = ', '.join(categoryObj)

			status = "Enable"
			#if CatalogSelectionStatus.objects.filter(company=company, catalog=item.id, status="Disable").exists():
			if item.id in myDisableCatalogIds:
				status = "Disable"

			viewtype = item.view_permission
			if viewtype == "push":
				viewtype = "private"

			#public_view_count = None
			#if item.view_permission == "public":
			#view_count = CompanyCatalogView.objects.filter(catalog=item).count()
			view_count = CompanyCatalogView.objects.filter(catalog=item).aggregate(Sum('clicks')).get('clicks__sum', 0)
			if view_count is None:
				view_count = 0

			catalog_type = "catalogseller"
			if item.company == company:
				catalog_type = "mycatalog"

			json_data.append([
				item.id,
				item.title,
				item.thumbnail.thumbnail[settings.SMALL_IMAGE].url, #item.thumbnail.url,
				item.brand.name,
				#categories,
				item.category.category_name,
				viewtype,
				status,
				str(item.created_at),
				item.products.count(),
				view_count,
				#pushIds
				{"brand":item.brand.id, "catalog_type":catalog_type},
			])
		return json_data


class ReceivedCatalogDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','title', 'thumbnail', 'brand.name', 'category.category_name'] #Table columns
	order_columns = ['id','title', 'id', 'brand.name', 'category.category_name']
	search_columns = ['title', 'brand', 'category']

	def get_initial_queryset(self):
		global company
		global sellingCompanyObj
		#Initial Queryset
		#queryset = Catalog.objects.all().select_related('brand', 'category')
		queryset = Catalog.objects.filter(deleted=False, catalog_type = "catalog").select_related('brand', 'category')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company

					mycatalogids = Catalog.objects.filter(company=company).values_list('id', flat=True).distinct()
					queryset = queryset.exclude(id__in=mycatalogids)

					sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()

					#pushUserCatalogId = Push_User.objects.filter(selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('catalog').values_list('catalog', flat=True).distinct()
					#return queryset.filter(id__in=pushUserCatalogId).order_by('-id')

					catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()
					catalogsIds = list(catalogsIds)
					#logger.info("catalogsIds sort by =")
					#logger.info(catalogsIds)
					preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(catalogsIds)])
					queryset = queryset.filter(id__in=catalogsIds).order_by(preserved)
					return queryset


			except ObjectDoesNotExist:
				return Catalog.objects.none()
		else:
			return Catalog.objects.none()

		'''elif user.groups.filter(name="salesperson").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(Q(brand__company=company) | Q(view_permission__icontains='public'))
			except ObjectDoesNotExist:
				return Catalog.objects.none()'''

	def filter_queryset(self, qs):
		global company
		global myDisableCatalogIds

		myDisableCatalogIds = getMyDisableCatalogIds(company)

		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(title__icontains=search)|qs.filter(brand__name__icontains=search)|qs.filter(category__category_name__icontains=search)

		title = self.request.GET.get('columns[1][search][value]', None)
		if title:
			title_parts = title.split(' ')
			qs_params = None
			for part in title_parts:
				q = Q(title__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		brand = self.request.GET.get('columns[3][search][value]', None)
		if brand:
			brand_parts = brand.split(' ')
			qs_params = None
			for part in brand_parts:
				q = Q(brand__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		category = self.request.GET.get('columns[4][search][value]', None)
		if category:
			qs = qs.filter(category__category_name__icontains=category)

		soldby = self.request.GET.get('columns[5][search][value]', None)
		if soldby:
			catalogids = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, selling_company__name__icontains=soldby).values_list('catalog', flat=True)
			qs = qs.filter(id__in=catalogids)



		trusted_seller = self.request.GET.get('columns[8][search][value]', None)
		if trusted_seller:
			catalogids = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, selling_company__trusted_seller=trusted_seller).values_list('catalog', flat=True)
			qs = qs.filter(id__in=catalogids)

		status = self.request.GET.get('columns[9][search][value]', None)
		if status:
			if status == "Disable":
				#catalogids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(catalog__isnull=True).values_list('catalog', flat=True)
				#qs = qs.filter(id__in=catalogids)
				qs = qs.filter(id__in=myDisableCatalogIds)
			elif status == "Enable":
				#catalogids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(catalog__isnull=True).values_list('catalog', flat=True)
				#qs = qs.exclude(id__in=catalogids)
				qs = qs.exclude(id__in=myDisableCatalogIds)

		return qs

	def prepare_results(self, qs):
		global company
		global sellingCompanyObj
		global myDisableCatalogIds

		#JSON array data
		json_data = []

		for item in qs:

			#pushCatalogObj = Push_Catalog.objects.filter(catalog=item.id).values_list('push', flat=True)
			#pushIds = str(pushCatalogObj).strip('[]')

			#categoryObj = item.category.all().values_list('category_name', flat=True)
			#categories = ', '.join(categoryObj)
			status = "Enable"
			#if CatalogSelectionStatus.objects.filter(company=company, catalog=item.id, status="Disable").exists():
			if item.id in myDisableCatalogIds:
				status = "Disable"

			cpfObj = CompanyProductFlat.objects.filter(catalog=item, buying_company=company, is_disable=False, selling_company__in=sellingCompanyObj).select_related('selling_company__chat_admin_user', 'push_reference').last()
			selling_company = None
			selling_company_id = None
			chat_admin_user = None
			received_date = ""
			is_trusted_seller = "No"
			if cpfObj:
				selling_company =  cpfObj.selling_company.name
				selling_company_id =  cpfObj.selling_company.id
				if cpfObj.selling_company.chat_admin_user:
					chat_admin_user =  cpfObj.selling_company.chat_admin_user.username
				if cpfObj.push_reference.date:
					received_date = cpfObj.push_reference.date
				if cpfObj.selling_company.trusted_seller:
					is_trusted_seller = "Yes"

			total_products = CompanyProductFlat.objects.filter(catalog=item, buying_company=company, is_disable=False, selling_company__in=sellingCompanyObj).count()




			json_data.append([
				item.id,
				item.title,
				item.thumbnail.thumbnail[settings.SMALL_IMAGE].url, #item.thumbnail.url,
				item.brand.name,
				#categories,
				item.category.category_name,
				selling_company,
				str(received_date),
				total_products,
				is_trusted_seller,
				status,
				{"selling_company":selling_company_id, "selling_company_chat_user":chat_admin_user, "selling_company_name":selling_company},
				#pushIds
			])

		return json_data

class PublicCatalogDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','title', 'thumbnail', 'brand.name', 'category.category_name', 'company.name', 'created_at', 'id', 'company.trusted_seller']
	order_columns = ['id','title', 'id', 'brand.name', 'category.category_name', 'company.name', 'created_at', 'id', 'company.trusted_seller']
	search_columns = ['title', 'brand', 'category', 'company', 'created_at', 'company.trusted_seller']

	def get_initial_queryset(self):
		#Initial Queryset
		global company
		#queryset = Catalog.objects.all().select_related('brand', 'category')
		queryset = Catalog.objects.filter(deleted=False, catalog_type = "catalog").select_related('brand', 'category', 'company__chat_admin_user')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company

					dtnow = datetime.now()
					# ~ cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True)
					# ~ productcatalogs = Product.objects.filter(catalog__view_permission="public", catalog__in=cscatalogids).values_list('catalog', flat=True).distinct()
					cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow, catalog__view_permission="public", catalog__total_products_uploaded__gt=0).values_list('catalog', flat=True)

					#~ productcatalogs = Product.objects.filter(catalog__view_permission="public").values_list('catalog', flat=True).distinct()
					# ~ queryset = queryset.filter(id__in=productcatalogs).order_by('-sort_order')
					queryset = queryset.filter(id__in=cscatalogids).order_by('-sort_order')

					#~ sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
					#~ catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()

					#~ exclude_list = queryset.filter(Q(company=company) | Q(id__in=catalogsIds)).order_by('-id').distinct()
					#~ cids = exclude_list.values_list('id', flat=True)

					#~ disableCatalogIds = getDisableCatalogIds(company)
					#~ queryset = queryset.filter(view_permission="public").exclude(Q(id__in=cids) | Q(id__in=disableCatalogIds)).order_by('-sort_order')
					return queryset

			except ObjectDoesNotExist:
				return Catalog.objects.none()
		else:
			return Catalog.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(title__icontains=search)|qs.filter(brand__name__icontains=search)|qs.filter(category__category_name__icontains=search)|qs.filter(created_at__icontains=search)

		title = self.request.GET.get('columns[1][search][value]', None)
		if title:
			title_parts = title.split(' ')
			qs_params = None
			for part in title_parts:
				q = Q(title__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		brand = self.request.GET.get('columns[3][search][value]', None)
		if brand:
			brand_parts = brand.split(' ')
			qs_params = None
			for part in brand_parts:
				q = Q(brand__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		category = self.request.GET.get('columns[4][search][value]', None)
		if category:
			qs = qs.filter(category__category_name__icontains=category)

		name = self.request.GET.get('columns[5][search][value]', None)
		if name:
			qs = qs.filter(company__name__icontains=name)

		time = self.request.GET.get('columns[6][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		trusted_seller = self.request.GET.get('columns[8][search][value]', None)
		if trusted_seller:
			qs = qs.filter(company__trusted_seller=trusted_seller)

		return qs

	def prepare_results(self, qs):
		global company
		#JSON array data
		json_data = []
		for item in qs:

			#pushCatalogObj = Push_Catalog.objects.filter(catalog=item.id).values_list('push', flat=True)
			#pushIds = str(pushCatalogObj).strip('[]')

			#categoryObj = item.category.all().values_list('category_name', flat=True)
			#categories = ', '.join(categoryObj)

			disableproducts = ProductStatus.objects.filter(product__catalog=item, status='Disable').values_list('product', flat=True)

			totalproducts = item.products.exclude(id__in=disableproducts).count()

			# is_invited = Buyer.objects.filter(selling_company=item.company, buying_company=company).exists()
			# is_connected = Buyer.objects.filter(selling_company=item.company, buying_company=company, status="approved").exists()

			is_invited = is_connected = False
			buyerObj = Buyer.objects.filter(selling_company=item.company, buying_company=company).last()
			if buyerObj:
				is_invited = True
				if buyerObj.status == "approved":
					is_connected = True

			is_trusted_seller = "No"
			if item.company.trusted_seller:
				is_trusted_seller = "Yes"

			catalog_type = "public"
			if item.company == company:
				catalog_type = "mycatalog"

			i_am_selling_this = False
			if CatalogSeller.objects.filter(catalog=item, selling_type="Public", selling_company=company).exists():
				i_am_selling_this = True
			if item.view_permission == "push":
				i_am_selling_this = True

			json_data.append([
				item.id,
				item.title,
				item.thumbnail.thumbnail[settings.SMALL_IMAGE].url, #item.thumbnail.url,
				item.brand.name,
				#categories,
				item.category.category_name,
				item.company.name,
				str(item.created_at),
				str(totalproducts),
				is_trusted_seller,
				{"selling_company":item.company.id, "selling_company_chat_user":item.company.chat_admin_user.username, "selling_company_name":item.company.name, "is_invited":is_invited, "is_connected":is_connected, "brand":item.brand.id, "catalog_type":catalog_type, "i_am_selling_this":i_am_selling_this, "sell_full_catalog":item.sell_full_catalog},
				#pushIds
			])
		return json_data

class ReceivedSelectionDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','name', 'products.title'] #Table columns
	order_columns = ['id','name', 'products.title']
	search_columns = ['id','name', 'products.title']

	def get_initial_queryset(self):
		global company

		user = self.request.user
		company = user.companyuser.company

		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		pushUserSelectionId = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj).exclude(selection__isnull=True).order_by('selection').values_list('selection', flat=True).distinct()
		queryset = Selection.objects.filter(id__in=pushUserSelectionId).prefetch_related('products').distinct().order_by('-id')
		return queryset

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(products__title__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			name_parts = name.split(' ')
			qs_params = None
			for part in name_parts:
				q = Q(name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		products = self.request.GET.get('columns[2][search][value]', None)
		if products:
			qs = qs.filter(products__title__icontains=products)

		soldby = self.request.GET.get('columns[4][search][value]', None)
		if soldby:
			selectionids = CompanyProductFlat.objects.filter(buying_company=company, is_disable=False, selling_company__name__icontains=soldby).values_list('selection', flat=True)
			qs = qs.filter(id__in=selectionids)

		status = self.request.GET.get('columns[6][search][value]', None)
		if status:
			if status == "Disable":
				selectionids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(selection__isnull=True).values_list('selection', flat=True)
				qs = qs.filter(id__in=selectionids)
			elif status == "Enable":
				selectionids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(selection__isnull=True).values_list('selection', flat=True)
				qs = qs.exclude(id__in=selectionids)

		return qs

	def prepare_results(self, qs):
		global company
		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
		#JSON array data
		json_data = []
		for item in qs:
			#productObj = item.products.all().values_list('title', flat=True)
			#products = ', '.join(productObj)

			status = "Enable"
			if CatalogSelectionStatus.objects.filter(company=company, selection=item.id, status="Disable").exists():
				status = "Disable"

			#productids = CompanyProductFlat.objects.filter(selection=item, buying_company=company, is_disable=False).values_list('product', flat=True)

			productsArr = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, selection=item.id, is_disable=False).values_list('product__title', flat=True)
			products = ', '.join(productsArr)

			cpfObj = CompanyProductFlat.objects.filter(selection=item, buying_company=company, is_disable=False).select_related('selling_company').last()
			selling_company = None
			selling_company_id = None
			if cpfObj:
				selling_company =  cpfObj.selling_company.name
				selling_company_id = cpfObj.selling_company.id

			json_data.append([
				item.id,
				item.name,
				products,
				str(item.image()),
				#item.products.filter(id__in=productids).count(),
				selling_company,
				len(productsArr),
				status,
				selling_company_id,
				#str(item.image.thumbnail['150x210'].url)
			])
		return json_data

class SelectionDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','name', 'products.title'] #Table columns
	order_columns = ['id','name', 'products.title']
	search_columns = ['id','name', 'products.title']

	def get_initial_queryset(self):
		global company
		user = self.request.user

		company = user.companyuser.company

		return Selection.objects.filter(user=user, deleted=False).prefetch_related('products')

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(products__title__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			name_parts = name.split(' ')
			qs_params = None
			for part in name_parts:
				q = Q(name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		products = self.request.GET.get('columns[2][search][value]', None)
		if products:
			qs = qs.filter(products__title__icontains=products)

		status = self.request.GET.get('columns[5][search][value]', None)
		if status:
			if status == "Disable":
				selectionids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(selection__isnull=True).values_list('selection', flat=True)
				qs = qs.filter(id__in=selectionids)
			elif status == "Enable":
				selectionids = CatalogSelectionStatus.objects.filter(company=company, status="Disable").exclude(selection__isnull=True).values_list('selection', flat=True)
				qs = qs.exclude(id__in=selectionids)

		return qs

	def prepare_results(self, qs):
		global company
		#JSON array data
		json_data = []
		for item in qs:
			productObj = item.products.all().values_list('title', flat=True)
			products = ', '.join(productObj)

			status = "Enable"
			if CatalogSelectionStatus.objects.filter(company=company, selection=item.id, status="Disable").exists():
				status = "Disable"

			json_data.append([
				item.id,
				item.name,
				products,
				str(item.image()),
				item.products.count(),
				status,
				#str(item.image.thumbnail['150x210'].url)
			])
		return json_data


class BrandsCatalogDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','title', 'thumbnail', 'brand', 'category']
	order_columns = ['id','title', 'id', 'brand', 'category']
	search_columns = ['title', 'brand', 'category']

	def get_initial_queryset(self):
		global company
		global brand

		queryset = Catalog.objects.filter(deleted=False, catalog_type = "catalog").select_related('brand', 'category')

		user = self.request.user

		brand = self.request.GET.get('brand', None)

		if user.is_staff:
			company = user.companyuser.company
			queryset = queryset.filter(brand=brand).order_by('-id')
			return queryset

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company

					sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
					catalogsIds = Push_User.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, catalog__brand=brand).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()

					queryset = queryset.filter(Q(view_permission="public", brand=brand) | Q(company=company, brand=brand) | Q(id__in=catalogsIds)).order_by('-id')
					return queryset


			except ObjectDoesNotExist:
				return Catalog.objects.none()
		else:
			return Catalog.objects.none()

	def filter_queryset(self, qs):
		global myDisableCatalogIds

		myDisableCatalogIds = getMyDisableCatalogIds(company)

		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(title__icontains=search)|qs.filter(brand__name__icontains=search)|qs.filter(category__category_name__icontains=search)

		title = self.request.GET.get('columns[1][search][value]', None)
		if title:
			title_parts = title.split(' ')
			qs_params = None
			for part in title_parts:
				q = Q(title__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		brand = self.request.GET.get('columns[3][search][value]', None)
		if brand:
			brand_parts = brand.split(' ')
			qs_params = None
			for part in brand_parts:
				q = Q(brand__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		category = self.request.GET.get('columns[4][search][value]', None)
		if category:
			qs = qs.filter(category__category_name__icontains=category)

		search = self.request.GET.get('columns[5][search][value]', None)
		if search:
			qs = qs.filter(company__name__icontains=search)

		status = self.request.GET.get('columns[6][search][value]', None)
		if status:
			if status == "Disable":
				qs = qs.filter(id__in=myDisableCatalogIds)
			elif status == "Enable":
				qs = qs.exclude(id__in=myDisableCatalogIds)

		return qs

	def prepare_results(self, qs):
		global company
		global myDisableCatalogIds

		#JSON array data
		json_data = []

		for item in qs:
			status = "Enable"
			#if CatalogSelectionStatus.objects.filter(company=company, catalog=item.id, status="Disable").exists():
			if item.id in myDisableCatalogIds:
				status = "Disable"

			catalog_type = ""

			selling_company = None
			total_products = 0
			if item.view_permission == "public" and item.company == company:
				total_products = item.products.count()
				catalog_type = "mycatalog"
			if item.view_permission == "public":
				selling_company = item.company.name
				total_products = item.products.count()
				catalog_type = "public"
			elif item.company == company:
				total_products = item.products.count()
				catalog_type = "mycatalog"
			else:
				cpfObj = CompanyProductFlat.objects.filter(catalog=item, buying_company=company, is_disable=False).select_related('selling_company').last()
				if cpfObj:
					selling_company =  cpfObj.selling_company.name
				total_products = CompanyProductFlat.objects.filter(catalog=item, buying_company=company, is_disable=False).count()
				catalog_type = "received"



			json_data.append([
				item.id,
				item.title,
				item.thumbnail.thumbnail[settings.SMALL_IMAGE].url, #item.thumbnail.url,
				item.brand.name,
				#categories,
				item.category.category_name,
				selling_company,
				total_products,
				status,
				catalog_type,
				#pushIds
			])

		return json_data

class ProductDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'image', 'sku', 'fabric', 'work', 'price', 'public_price', 'catalog.title', 'id', 'sort_order'] #Table columns
	order_columns = ['id', 'id', 'sku', 'fabric', 'work', 'price', 'public_price', 'catalog.title', 'id', 'sort_order']
	search_columns = ['id', 'id', 'sku', 'fabric', 'work', 'price', 'public_price', 'catalog.title', 'id', 'sort_order']

	def get_initial_queryset(self):
		global pid
		global ptype
		global company

		queryset = Product.objects.all().exclude(Q(deleted=True) | Q(catalog__deleted=True)).select_related('catalog')

		user = self.request.user
		company = get_user_company(user)

		pid = self.request.GET.get('id', None)
		ptype = self.request.GET.get('type', None)

		if ptype == "mycatalog":
			if user.is_staff:
				queryset = queryset.filter(catalog=pid).distinct().order_by('-catalog','sort_order','id')
				return queryset
			else:
				if company:
					cssellerids = CatalogSeller.objects.filter(catalog=pid).values_list('selling_company', flat=True)
					cssellerids = list(cssellerids)
					cssellerids.append(company.id)

					queryset = queryset.filter(catalog__company__in=cssellerids, catalog=pid).distinct().order_by('-catalog','sort_order','id')
					return queryset

		if user.is_staff:
			return queryset

		try:
			if company:
				return queryset.filter(catalog__company=company).distinct().order_by('-catalog','sort_order','id')
		except ObjectDoesNotExist:
			return Product.objects.none()

	def filter_queryset(self, qs):
		global company
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(fabric__icontains=search)|qs.filter(work__icontains=search)|qs.filter(sku__icontains=search)|qs.filter(price__icontains=search)|qs.filter(catalog__title__icontains=search)

		sku = self.request.GET.get('columns[2][search][value]', None)
		if sku:
			qs = qs.filter(sku__icontains=sku)

		fabric = self.request.GET.get('columns[3][search][value]', None)
		if fabric:
			#qs = qs.filter(fabric__icontains=fabric)
			'''fabrics = list(fabric.strip().replace(' ','').split(','))
			productsIds = ProductEAVFlat.objects.filter(Q(product__in=qs) & (Q(reduce(lambda x, y: x | y, [Q(fabric_text__icontains=fabric) for fabric in fabrics])) | Q(reduce(lambda x, y: x | y, [Q(fabric__icontains=fabric) for fabric in fabrics])))).values_list('product', flat=True).distinct()
			qs = qs.filter(id__in=productsIds)'''

			#cfqueryset = catalogFabricFilter(fabric, Catalog.objects.filter(id__in=qs.values_list('catalog', flat=True)))
			#qs = qs.filter(catalog__in=cfqueryset)
			catalogids = qs.values_list('catalog', flat=True)
			cefids = catalogFabricFilter(fabric, catalogids)
			qs = qs.filter(catalog__in=cefids)

		work = self.request.GET.get('columns[4][search][value]', None)
		if work:
			#qs = qs.filter(work__icontains=work)
			'''works = list(work.strip().replace(' ','').split(','))
			productsIds = ProductEAVFlat.objects.filter(Q(product__in=qs) & (Q(reduce(lambda x, y: x | y, [Q(work_text__icontains=work) for work in works])) | Q(reduce(lambda x, y: x | y, [Q(work__icontains=work) for work in works])))).values_list('product', flat=True).distinct()
			qs = qs.filter(id__in=productsIds)'''

			#cfqueryset = catalogWorkFilter(work, Catalog.objects.filter(id__in=qs.values_list('catalog', flat=True)))
			#qs = qs.filter(catalog__in=cfqueryset)
			catalogids = qs.values_list('catalog', flat=True)
			cefids = catalogWorkFilter(work, catalogids)
			qs = qs.filter(catalog__in=cefids)


		price = self.request.GET.get('columns[5][search][value]', None)
		if price:
			price = price.split("~")
			if price[0] != "" and price[1] != "":
				qs = qs.filter(price__range=[price[0],price[1]])
			elif price[0] != "":
				qs = qs.filter(price__gte=price[0])
			elif price[1] != "":
				qs = qs.filter(price__lte=price[1])
			#qs = qs.filter(price__icontains=price)

		public_price = self.request.GET.get('columns[6][search][value]', None)
		if public_price:
			price = public_price.split("~")
			if price[0] != "" and price[1] != "":
				qs = qs.filter(public_price__range=[price[0],price[1]])
			elif price[0] != "":
				qs = qs.filter(public_price__gte=price[0])
			elif price[1] != "":
				qs = qs.filter(public_price__lte=price[1])
			#qs = qs.filter(public_price__icontains=public_price)

		catalog = self.request.GET.get('columns[7][search][value]', None)
		if catalog:
			qs = qs.filter(catalog__title__icontains=catalog)

		status = self.request.GET.get('columns[8][search][value]', None)
		if status:
			if status == "Disable":
				productids = ProductStatus.objects.filter(company=company, status="Disable").values_list('product', flat=True)
				qs = qs.filter(id__in=productids)
			elif status == "Enable":
				productids = ProductStatus.objects.filter(company=company, status="Disable").values_list('product', flat=True)
				qs = qs.exclude(id__in=productids)


		return qs

	def prepare_results(self, qs):
		global company
		#JSON array data
		json_data = []

		#user = self.request.user
		#company = user.companyuser.company

		for item in qs:
			#catalogObj = item.catalog.all().values_list('title', flat=True)
			#catalogs = ', '.join(catalogObj)

			status = "Enable"
			if ProductStatus.objects.filter(company=company, product=item.id, status="Disable").exists():
				status = "Disable"

			public_price = ""

			if item.public_price > 0:
				public_price = item.public_price

			catalogeav = getCatalogEAV(item.catalog, "allInJson")
			fabric = work = None
			if "fabric" in catalogeav.keys():
				fabric = ", ".join(catalogeav["fabric"])
			if "work" in catalogeav.keys():
				work = ", ".join(catalogeav["work"])

			json_data.append([
				item.id,
				str(item.image.thumbnail[settings.SMALL_IMAGE].url),
				item.sku,
				#getEAVFabricWork(item, "fabric"), #item.fabric,
				#getEAVFabricWork(item, "work"), #item.work,
				fabric, #getCatalogEAV(item.catalog, "fabricInString"),
				work, #getCatalogEAV(item.catalog, "workInString"),
				item.price,
				public_price,
				#catalogs,
				item.catalog.title,
				status,
				item.sort_order
			])
		return json_data

from django.db.models import Sum, Min, Max
class ProductsDetailDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'image', 'sku', 'fabric', 'work', 'price', 'sort_order', 'sort_order'] #Table columns
	order_columns = ['id', 'id', 'sku', 'fabric', 'work', 'price', 'sort_order', 'sort_order']
	search_columns = ['id', 'sku', 'fabric', 'work', 'price', 'sort_order', 'sort_order']

	def get_initial_queryset(self):
		queryset = Product.objects.all().exclude(deleted=True).select_related('catalog__company')

		user = self.request.user

		global company
		global pid
		global ptype

		pid = self.request.GET.get('id', None)
		ptype = self.request.GET.get('type', None)
		print ptype
		try:
			user_company = (user.companyuser.company is not None)

			if user_company:
				company = user.companyuser.company
				print company
				#if ptype != "mycatalog" or ptype != "myselection":
				if ptype not in ["mycatalog", "myselection", "receivedselection"]:
					catalog = Catalog.objects.get(pk=pid)
					ccvObj, created = CompanyCatalogView.objects.get_or_create(company=company, catalog=catalog, catalog_type=catalog.view_permission)
					if not created:
						ccvObj.created_at=datetime.now()
						ccvObj.clicks += 1
						ccvObj.save()

				if ptype == "mycatalog":
					return queryset.filter(catalog__company=company, catalog=pid).distinct().order_by('-catalog','sort_order','id')

				elif ptype == "myselection":
					products = Selection.objects.filter(user__companyuser__company=company, id=pid).values_list('products', flat=True).distinct()
					return queryset.filter(id__in=products).distinct().order_by('-catalog','sort_order','id')

				elif ptype == "receivedcatalog":
					sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
					productsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, catalog=pid, is_disable=False).values_list('product', flat=True)

					#sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
					#productsIds = Push_User_Product.objects.filter(user=user, selling_company__in=sellingCompanyObj, catalog = pid).order_by('product').values_list('product', flat=True).distinct()

					return queryset.filter(id__in=productsIds).distinct().order_by('-catalog','sort_order','id')

				elif ptype == "receivedselection":
					sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
					productsIds = CompanyProductFlat.objects.filter(buying_company=company, selling_company__in=sellingCompanyObj, selection=pid, is_disable=False).values_list('product', flat=True)

					#productsIds = Push_User_Product.objects.filter(user=user, selling_company__in=sellingCompanyObj, selection = pid).order_by('product').values_list('product', flat=True).distinct()

					return queryset.filter(id__in=productsIds).distinct().order_by('-catalog','sort_order','id')

				elif ptype == "publiccatalog":
					#catalog = Catalog.objects.get(pk=pid)

					#if catalog.view_permission == "public":
					#	ccvObj, created = CompanyCatalogView.objects.get_or_create(company=company, catalog=catalog, catalog_type=catalog.view_permission)

					cobj = Catalog.objects.filter(view_permission='public', id=pid).values_list('id', flat=True)

					disableproducts = ProductStatus.objects.filter(product__catalog__in=cobj, status='Disable').values_list('product', flat=True)

					return queryset.filter(catalog__in=cobj).exclude(id__in=disableproducts).distinct().order_by('-catalog','sort_order','id')

				else:
					return queryset.none()

		except ObjectDoesNotExist as e:
			print e
			return Product.objects.none()

	def filter_queryset(self, qs):
		global company
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(fabric__icontains=search)|qs.filter(work__icontains=search)|qs.filter(sku__icontains=search)|qs.filter(price__icontains=search)|qs.filter(catalog__title__icontains=search)

		sku = self.request.GET.get('columns[2][search][value]', None)
		if sku:
			qs = qs.filter(sku__icontains=sku)

		fabric = self.request.GET.get('columns[3][search][value]', None)
		if fabric:
			#qs = qs.filter(fabric__icontains=fabric)
			#~ fabrics = list(fabric.strip().replace(' ','').split(','))
			#~ productsIds = ProductEAVFlat.objects.filter(Q(product__in=qs) & (Q(reduce(lambda x, y: x | y, [Q(fabric_text__icontains=fabric) for fabric in fabrics])) | Q(reduce(lambda x, y: x | y, [Q(fabric__icontains=fabric) for fabric in fabrics])))).values_list('product', flat=True).distinct()
			#~ qs = qs.filter(id__in=productsIds)

			#~ cfqueryset = catalogFabricFilter(fabric, Catalog.objects.filter(id__in=qs.values_list('catalog', flat=True)))
			#~ qs = qs.filter(catalog__in=cfqueryset)
			catalogids = qs.values_list('catalog', flat=True)
			cefids = catalogFabricFilter(fabric, catalogids)
			qs = qs.filter(catalog__in=cefids)

		work = self.request.GET.get('columns[4][search][value]', None)
		if work:
			#qs = qs.filter(work__icontains=work)
			#~ works = list(work.strip().replace(' ','').split(','))
			#~ productsIds = ProductEAVFlat.objects.filter(Q(product__in=qs) & (Q(reduce(lambda x, y: x | y, [Q(work_text__icontains=work) for work in works])) | Q(reduce(lambda x, y: x | y, [Q(work__icontains=work) for work in works])))).values_list('product', flat=True).distinct()
			#~ qs = qs.filter(id__in=productsIds)

			#~ cfqueryset = catalogWorkFilter(work, Catalog.objects.filter(id__in=qs.values_list('catalog', flat=True)))
			#~ qs = qs.filter(catalog__in=cfqueryset)
			catalogids = qs.values_list('catalog', flat=True)
			cefids = catalogWorkFilter(work, catalogids)
			qs = qs.filter(catalog__in=cefids)

		price = self.request.GET.get('columns[5][search][value]', None)
		if price:
			price = price.split("~")
			if price[0] != "" and price[1] != "":
				qs = qs.filter(price__range=[price[0],price[1]])
			elif price[0] != "":
				qs = qs.filter(price__gte=price[0])
			elif price[1] != "":
				qs = qs.filter(price__lte=price[1])
			#qs = qs.filter(price__icontains=price)

		status = self.request.GET.get('columns[6][search][value]', None)
		if status:
			if status == "Disable":
				productids = ProductStatus.objects.filter(company=company, status="Disable").values_list('product', flat=True)
				qs = qs.filter(id__in=productids)
			elif status == "Enable":
				productids = ProductStatus.objects.filter(company=company, status="Disable").values_list('product', flat=True)
				qs = qs.exclude(id__in=productids)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		global company
		global pid
		global ptype

		json_data = []

		user = self.request.user
		company = user.companyuser.company

		sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()

		for item in qs:
			price = None
			if item.catalog.company==company:
				#print "if"
				price = item.price
			else:
				#print "else"
				if ptype == "receivedcatalog":
					#print "catalog"
					cpfObj = CompanyProductFlat.objects.filter(product=item.id, buying_company=company, selling_company__in=sellingCompanyObj, catalog=pid, is_disable=False).last()
					if cpfObj:
						price = cpfObj.final_price
				elif ptype == "receivedselection":
					#print "selection"
					cpfObj = CompanyProductFlat.objects.filter(product=item.id, buying_company=company, selling_company__in=sellingCompanyObj, selection=pid, is_disable=False).last()
					if cpfObj:
						price = cpfObj.final_price
				elif ptype == "publiccatalog":
					#print "publiccatalog"
					price = item.public_price
				else:
					cpfObj = CompanyProductFlat.objects.filter(product=item.id, buying_company=company, selling_company__in=sellingCompanyObj, is_disable=False).last()
					if cpfObj:
						price = cpfObj.final_price
				#pushUserProductId = Push_User_Product.objects.filter(user=user, product=item.id, selling_company__in=sellingCompanyObj).values('user','product','selling_company').annotate(Max('id')).values('id__max')
				#pushUserProductObj = Push_User_Product.objects.filter(id__in=pushUserProductId).order_by('price').first()
				#price = pushUserProductObj.price

			status = "Enable"
			if ProductStatus.objects.filter(company=company, product=item.id, status="Disable").exists():
				status = "Disable"

			json_data.append([
				item.id,
				str(item.image.thumbnail[settings.SMALL_IMAGE].url),
				item.sku,
				#getEAVFabricWork(item, "fabric"), #item.fabric,
				#getEAVFabricWork(item, "work"), #item.work,
				getCatalogEAV(item.catalog, "fabricInString"),
				getCatalogEAV(item.catalog, "workInString"),
				price,
				status,
				item.sort_order
			])
		return json_data


class BuyerDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'buying_company.name', 'buying_company_name', 'buying_company.state.state_name', 'buying_company.city.city_name', 'buying_company.phone_number', 'group_type.name', 'status', 'buying_company.thumbnail'] #Table columns
	order_columns = ['id', 'buying_company.name', 'buying_company_name', 'buying_company.state.state_name', 'buying_company.city.city_name', 'buying_company.phone_number', 'group_type.name', 'status']
	#search_columns = ['id', 'buying_company.name', 'buying_company.street_address']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Buyer.objects.all().select_related('buying_company__state', 'buying_company__city', 'group_type', 'invitee')

		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return queryset.filter(selling_company=company, buyer_type="Relationship")
		except ObjectDoesNotExist:
			return Buyer.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(buying_company__name__icontains=search)|qs.filter(buying_company__state__state_name__icontains=search)|qs.filter(buying_company__city__city_name__icontains=search)|qs.filter(buying_company__phone_number__icontains=search)|qs.filter(group_type__name__icontains=search)|qs.filter(status__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		company_name = self.request.GET.get('columns[1][search][value]', None)
		if company_name:
			qs = qs.filter(Q(buying_company__name__icontains=company_name) | Q(invitee__invitee_name__icontains=company_name))

		'''street_address = self.request.GET.get('columns[3][search][value]', None)
		if street_address:
			street_address_parts = street_address.split(' ')
			qs_params = None
			for part in street_address_parts:
				q = Q(buying_company__street_address__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)'''

		company_name = self.request.GET.get('columns[2][search][value]', None)
		if company_name:
			qs = qs.filter(Q(buying_company__name__icontains=company_name) | Q(invitee__invitee_name__icontains=company_name))

		state_name = self.request.GET.get('columns[3][search][value]', None)
		if state_name:
			qs = qs.filter(buying_company__state__state_name__icontains=state_name)

		city_name = self.request.GET.get('columns[4][search][value]', None)
		if city_name:
			qs = qs.filter(buying_company__city__city_name__icontains=city_name)

		'''pincode = self.request.GET.get('columns[6][search][value]', None)
		if pincode:
			qs = qs.filter(buying_company__pincode__icontains=pincode)'''


		phone_number = self.request.GET.get('columns[5][search][value]', None)
		if phone_number:
			qs = qs.filter(Q(buying_company__phone_number__icontains=phone_number) | Q(invitee__invitee_number__icontains=phone_number))

		group_type = self.request.GET.get('columns[6][search][value]', None)
		if group_type:
			qs = qs.filter(group_type__name__icontains=group_type)

		status = self.request.GET.get('columns[7][search][value]', None)
		if status:
			qs = qs.filter(status=status)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			if item.group_type:
				group_name = item.group_type.name
			else:
				group_name=None

			if item.buying_company is None:
				json_data.append([item.id,'',item.invitee.invitee_name,'','',item.invitee.invitee_number,group_name,item.get_status_display(),''])
			else:
				#categoryObj = item.buying_company.category.all().values_list('category_name', flat=True)
				#categories = ', '.join(categoryObj)
				'''image = ''
				if item.buying_company.thumbnail:
					image = item.buying_company.thumbnail.url'''

				state = None
				if item.buying_company.state:
					state = item.buying_company.state.state_name
				city = None
				if item.buying_company.city:
					city = item.buying_company.city.city_name

				# ~ inviteename = None
				# ~ if item.invitee:
					# ~ if item.invitee.invitation_type == "Buyer":
						# ~ inviteename = item.invitee.invitee_name

				json_data.append([
					item.id,
					item.buying_company.name,
					item.buying_company_name, #inviteename,
					#item.buying_company.street_address,
					state,
					city,
					#item.buying_company.pincode,
					#categories,
					item.buying_company.phone_number,
					group_name,
					item.get_status_display(),#.replace('_',' '),
					item.buying_company.id,
					#image
				])
		return json_data

class BuyerEnquiryDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'buying_company.name', 'buying_company.state.state_name', 'buying_company.city.city_name', 'buying_company.phone_number', 'group_type.name', 'created_at', 'status', 'buying_company.thumbnail'] #Table columns
	order_columns = ['id', 'buying_company.name', 'buying_company.state.state_name', 'buying_company.city.city_name', 'buying_company.phone_number', 'group_type.name', 'created_at', 'status']
	#search_columns = ['id', 'buying_company.name', 'buying_company.street_address']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Buyer.objects.all().select_related('buying_company__state', 'buying_company__city', 'group_type', 'invitee')

		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				#return queryset.filter(selling_company=company, buyer_type="Enquiry")
				return queryset.filter(selling_company=company, created_type="Enquiry")
		except ObjectDoesNotExist:
			return Buyer.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(buying_company__name__icontains=search)|qs.filter(buying_company__state__state_name__icontains=search)|qs.filter(buying_company__city__city_name__icontains=search)|qs.filter(buying_company__phone_number__icontains=search)|qs.filter(group_type__name__icontains=search)|qs.filter(status__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[0][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		company_name = self.request.GET.get('columns[1][search][value]', None)
		if company_name:
			qs = qs.filter(Q(buying_company__name__icontains=company_name) | Q(invitee__invitee_name__icontains=company_name))

		'''street_address = self.request.GET.get('columns[3][search][value]', None)
		if street_address:
			street_address_parts = street_address.split(' ')
			qs_params = None
			for part in street_address_parts:
				q = Q(buying_company__street_address__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)'''

		state_name = self.request.GET.get('columns[2][search][value]', None)
		if state_name:
			qs = qs.filter(buying_company__state__state_name__icontains=state_name)

		city_name = self.request.GET.get('columns[3][search][value]', None)
		if city_name:
			qs = qs.filter(buying_company__city__city_name__icontains=city_name)

		'''pincode = self.request.GET.get('columns[6][search][value]', None)
		if pincode:
			qs = qs.filter(buying_company__pincode__icontains=pincode)'''


		phone_number = self.request.GET.get('columns[4][search][value]', None)
		if phone_number:
			qs = qs.filter(Q(buying_company__phone_number__icontains=phone_number) | Q(invitee__invitee_number__icontains=phone_number))

		group_type = self.request.GET.get('columns[5][search][value]', None)
		if group_type:
			qs = qs.filter(group_type__name__icontains=group_type)

		time = self.request.GET.get('columns[6][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		status = self.request.GET.get('columns[7][search][value]', None)
		if status:
			qs = qs.filter(status=status)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			if item.group_type:
				group_name = item.group_type.name
			else:
				group_name=None

			if item.buying_company is None:
				json_data.append([item.id,item.invitee.invitee_name,'','',item.invitee.invitee_number,group_name,item.get_status_display(),''])
			else:
				#categoryObj = item.buying_company.category.all().values_list('category_name', flat=True)
				#categories = ', '.join(categoryObj)
				'''image = ''
				if item.buying_company.thumbnail:
					image = item.buying_company.thumbnail.url'''

				state = None
				if item.buying_company.state:
					state = item.buying_company.state.state_name
				city = None
				if item.buying_company.city:
					city = item.buying_company.city.city_name

				image = ''
				title = ''
				catalog_id= None
				if item.enquiry_catalog:
					image = item.enquiry_catalog.thumbnail.thumbnail[settings.SMALL_IMAGE].url
					title = item.enquiry_catalog.title
					catalog_id = item.enquiry_catalog.id

				json_data.append([
					item.id,
					item.buying_company.name,
					#item.buying_company.street_address,
					state,
					city,
					#item.buying_company.pincode,
					#categories,
					item.buying_company.phone_number,
					group_name,
					#str(timezone.localtime(item.created_at).strftime("%Y-%m-%d")),
					str(item.created_at),
					item.get_status_display(),#.replace('_',' '),
					image,
					title,
					{"buying_company":item.buying_company.id, "buying_company_chat_user":item.buying_company.chat_admin_user.username, "buying_company_name":item.buying_company.name, "catalog_id":catalog_id},
				])
		return json_data

class SellerDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'selling_company.name', 'selling_company.state.state_name', 'selling_company.city.city_name', 'selling_company.phone_number', 'group_type.name', 'status', 'selling_company.thumbnail'] #Table columns
	order_columns = ['id', 'selling_company.name', 'selling_company.state.state_name', 'selling_company.city.city_name', 'selling_company.phone_number', 'group_type.name', 'status']
	#search_columns = ['id', 'selling_company.name', 'selling_company.street_address']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Buyer.objects.all().select_related('selling_company__state', 'selling_company__city', 'group_type', 'invitee')

		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return queryset.filter(buying_company=company)
		except ObjectDoesNotExist:
			return Buyer.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(selling_company__name__icontains=search)|qs.filter(selling_company__state__state_name__icontains=search)|qs.filter(selling_company__city__city_name__icontains=search)|qs.filter(selling_company__phone_number__icontains=search)|qs.filter(group_type__name__icontains=search)|qs.filter(status__icontains=search)

		company_name = self.request.GET.get('columns[1][search][value]', None)
		if company_name:
			qs = qs.filter(Q(selling_company__name__icontains=company_name) | Q(invitee__invitee_name__icontains=company_name))

		state_name = self.request.GET.get('columns[2][search][value]', None)
		if state_name:
			qs = qs.filter(selling_company__state__state_name__icontains=state_name)

		city_name = self.request.GET.get('columns[3][search][value]', None)
		if city_name:
			qs = qs.filter(selling_company__city__city_name__icontains=city_name)

		phone_number = self.request.GET.get('columns[4][search][value]', None)
		if phone_number:
			qs = qs.filter(Q(selling_company__phone_number__icontains=phone_number) | Q(invitee__invitee_number__icontains=phone_number))

		group_type = self.request.GET.get('columns[5][search][value]', None)
		if group_type:
			qs = qs.filter(group_type__name__icontains=group_type)

		status = self.request.GET.get('columns[6][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			if item.group_type:
				group_name = item.group_type.name
			else:
				group_name=None

			if item.selling_company is None:
				json_data.append([item.id,item.invitee.invitee_name,'','',item.invitee.invitee_number,group_name,item.get_status_display(),''])#.replace('_',' ')
			else:
				#categoryObj = item.selling_company.category.all().values_list('category_name', flat=True)
				#categories = ', '.join(categoryObj)
				'''image = ''
				if item.selling_company.thumbnail:
					image = item.selling_company.thumbnail.url'''

				suppliername = item.selling_company.name
				if item.invitee:
					if item.invitee.invitation_type == "Supplier":
						suppliername = item.invitee.invitee_name

				json_data.append([
					item.id,
					suppliername, #item.selling_company.name,
					item.selling_company.state.state_name,
					item.selling_company.city.city_name,
					#categories,
					item.selling_company.phone_number,
					group_name,
					item.get_status_display(),#.replace('_',' '),
					item.selling_company.id,
					#image
				])
		return json_data

class SellerEnquiryDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'selling_company.name', 'selling_company.state.state_name', 'selling_company.city.city_name', 'selling_company.phone_number', 'group_type.name', 'created_at', 'status', 'selling_company.thumbnail'] #Table columns
	order_columns = ['id', 'selling_company.name', 'selling_company.state.state_name', 'selling_company.city.city_name', 'selling_company.phone_number', 'group_type.name', 'created_at', 'status']
	#search_columns = ['id', 'selling_company.name', 'selling_company.street_address']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Buyer.objects.all().select_related('selling_company__state', 'selling_company__city', 'group_type', 'invitee')

		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				#return queryset.filter(buying_company=company, buyer_type="Enquiry")
				return queryset.filter(buying_company=company, created_type="Enquiry")
		except ObjectDoesNotExist:
			return Buyer.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(selling_company__name__icontains=search)|qs.filter(selling_company__state__state_name__icontains=search)|qs.filter(selling_company__city__city_name__icontains=search)|qs.filter(selling_company__phone_number__icontains=search)|qs.filter(group_type__name__icontains=search)|qs.filter(status__icontains=search)

		company_name = self.request.GET.get('columns[1][search][value]', None)
		if company_name:
			qs = qs.filter(Q(selling_company__name__icontains=company_name) | Q(invitee__invitee_name__icontains=company_name))

		state_name = self.request.GET.get('columns[2][search][value]', None)
		if state_name:
			qs = qs.filter(selling_company__state__state_name__icontains=state_name)

		city_name = self.request.GET.get('columns[3][search][value]', None)
		if city_name:
			qs = qs.filter(selling_company__city__city_name__icontains=city_name)

		phone_number = self.request.GET.get('columns[4][search][value]', None)
		if phone_number:
			qs = qs.filter(Q(selling_company__phone_number__icontains=phone_number) | Q(invitee__invitee_number__icontains=phone_number))

		group_type = self.request.GET.get('columns[5][search][value]', None)
		if group_type:
			qs = qs.filter(group_type__name__icontains=group_type)

		time = self.request.GET.get('columns[6][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		status = self.request.GET.get('columns[7][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			if item.group_type:
				group_name = item.group_type.name
			else:
				group_name=None

			if item.selling_company is None:
				json_data.append([item.id,item.invitee.invitee_name,'','',item.invitee.invitee_number,group_name,item.get_status_display(),''])#.replace('_',' ')
			else:
				#categoryObj = item.selling_company.category.all().values_list('category_name', flat=True)
				#categories = ', '.join(categoryObj)
				'''image = ''
				if item.selling_company.thumbnail:
					image = item.selling_company.thumbnail.url'''

				image = ''
				title = ''
				catalog_id = None
				if item.enquiry_catalog:
					image = item.enquiry_catalog.thumbnail.thumbnail[settings.SMALL_IMAGE].url
					title = item.enquiry_catalog.title
					catalog_id = item.enquiry_catalog.id

				json_data.append([
					item.id,
					item.selling_company.name,
					item.selling_company.state.state_name,
					item.selling_company.city.city_name,
					#categories,
					item.selling_company.phone_number,
					group_name,
					str(item.created_at),
					item.get_status_display(),#.replace('_',' '),
					image,
					title,
					{"selling_company":item.selling_company.id, "selling_company_chat_user":item.selling_company.chat_admin_user.username, "selling_company_name":item.selling_company.name, "catalog_id":catalog_id},
					#image
				])
		return json_data

class SegmentationDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','segmentation_name', 'group_type', 'city', 'category', 'buyers', 'active_buyers','last_generated','pushes'] #Table columns
	order_columns = ['id','segmentation_name', 'id', 'id', 'id', 'id', 'id', 'last_generated','id']
	search_columns = ['id','segmentation_name', 'group_type', 'city', 'category', 'buyers', 'last_generated']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = BuyerSegmentation.objects.all().distinct()#.prefetch_related('category', 'city', 'group_type')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return queryset.filter(company=company)
		except ObjectDoesNotExist:
			return BuyerSegmentation.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(segmentation_name__icontains=search)|qs.filter(city__city_name__icontains=search)|qs.filter(category__category_name__icontains=search)|qs.filter(last_generated__icontains=search)

		#Column wise filter
		'''ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)'''

		segmentation_name = self.request.GET.get('columns[1][search][value]', None)
		if segmentation_name:
			segmentation_name_parts = segmentation_name.split(' ')
			qs_params = None
			for part in segmentation_name_parts:
				q = Q(segmentation_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		group_type = self.request.GET.get('columns[2][search][value]', None)
		if group_type:
			'''group_type_parts = group_type.split(' ')
			qs_params = None
			for part in group_type_parts:
				q = Q(group_type__name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)'''
			qs = qs.filter(group_type__name__icontains=group_type)

		city = self.request.GET.get('columns[3][search][value]', None)
		if city:
			city_parts = city.split(' ')
			qs_params = None
			for part in city_parts:
				q = Q(city__city_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		category = self.request.GET.get('columns[4][search][value]', None)
		if category:
			category_parts = category.split(' ')
			qs_params = None
			for part in category_parts:
				q = Q(category__category_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)

		buyername = self.request.GET.get('columns[5][search][value]', None)
		if buyername:
			buyerids = qs.filter(buyers__name__icontains=buyername).values_list('id', flat=True)
			qs = qs.filter(id__in=buyerids)

		last_generated = self.request.GET.get('columns[7][search][value]', None)
		if last_generated:
			date=last_generated.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(last_generated__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(last_generated__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(last_generated__lte=date[1])

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			categoryObj = item.category.all().values_list('category_name', flat=True)
			categories = ', '.join(categoryObj)

			cityObj = item.city.all().values_list('city_name', flat=True)
			cities = ', '.join(cityObj)

			groupType = item.group_type.all().values_list('name', flat=True)
			group_type = ', '.join(groupType)

			pushObj = Push.objects.filter(buyer_segmentation=item.id).values_list('id', flat=True).count()
			pushes = str(pushObj).strip('[]')

			if cities == "" and "All " in item.segmentation_name:
				cities = "All Cities"
			if categories == "" and "All " in item.segmentation_name:
				categories = "All Categories"

			buyersObj = item.buyers.all().values_list('name', flat=True)
			buyers = ', '.join(buyersObj)

			json_data.append([
				#'',
				item.id,
				item.segmentation_name,
				group_type,
				cities,#,.lower(),
				categories,
				buyers,
				str(item.active_buyers()),
				str(timezone.localtime(item.last_generated).strftime("%Y-%m-%d : %I:%M%p")),
				pushes
			])
		return json_data


class InviteeDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id','invitee_name', 'invitee_company', 'invitee_number', 'invite_type', 'invite.relationship_type', 'status'] #Table columns
	order_columns = ['id','id','invitee_name', 'invitee_company', 'invitee_number', 'invite_type', 'invite.relationship_type', 'status']
	search_columns = ['id','invitee_name', 'invitee_company', 'invitee_number', 'invite_type', 'invite.relationship_type', 'status']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Invitee.objects.all()

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return queryset.filter(invite__company=company)
		except ObjectDoesNotExist:
			return Invitee.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(invitee_name__icontains=search)|qs.filter(invitee_company__icontains=search)|qs.filter(invitee_number__icontains=search)|qs.filter(invite_type__icontains=search)|qs.filter(invite__relationship_type__icontains=search)|qs.filter(status__icontains=search)

		#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)

		invitee_name = self.request.GET.get('columns[2][search][value]', None)
		if invitee_name:
			qs = qs.filter(invitee_name__icontains=invitee_name)

		invitee_company = self.request.GET.get('columns[3][search][value]', None)
		if invitee_company:
			qs = qs.filter(invitee_company__icontains=invitee_company)

		invitee_number = self.request.GET.get('columns[4][search][value]', None)
		if invitee_number:
			qs = qs.filter(invitee_number__icontains=invitee_number)

		invite_type = self.request.GET.get('columns[5][search][value]', None)
		if invite_type:
			qs = qs.filter(invite_type__icontains=invite_type)

		relationship_type = self.request.GET.get('columns[6][search][value]', None)
		if relationship_type:
			qs = qs.filter(invite__relationship_type__icontains=relationship_type)

		status = self.request.GET.get('columns[7][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			json_data.append([
				'',
				item.id,
				item.invitee_name,
				item.invitee_company,
				item.invitee_number,
				item.invite_type,
				item.invite.relationship_type,
				item.status
			])
		return json_data


class SalesPersonDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'companyuser__company__name', 'username', 'first_name', 'userprofile.phone_number', 'is_active', 'companyuser.deputed_to', 'userprofile.user_approval_status'] #Table columns
	order_columns = ['id', 'companyuser__company__name', 'username', 'first_name', 'userprofile.phone_number', 'is_active', 'companyuser.deputed_to', 'userprofile.user_approval_status']
	search_columns = ['id', 'companyuser__company__name', 'username', 'first_name', 'userprofile.phone_number', 'is_active', 'companyuser.deputed_to', 'userprofile.user_approval_status']

	def get_initial_queryset(self):
		queryset = User.objects.filter(groups__name="salesperson").select_related('userprofile')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		#If User is Administartor
		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					companyUserIds = CompanyUser.objects.filter(Q(company=company) | Q(deputed_to=company)).values_list('user', flat=True).distinct()
					return queryset.filter(id__in=companyUserIds)
					#return User.objects.filter(groups__name="salesperson", id__in=companyUserIds)
			except ObjectDoesNotExist:
				return User.objects.none()
		else:
			return queryset.filter(id=user.id)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(username__icontains=search)|qs.filter(first_name__icontains=search)|qs.filter(last_name__icontains=search)|qs.filter(email__icontains=search)|qs.filter(userprofile__phone_number__icontains=search)|qs.filter(is_active=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(companyuser__company__name__icontains=search)

		username = self.request.GET.get('columns[2][search][value]', None)
		if username:
			qs = qs.filter(username__icontains=username)

		first_name = self.request.GET.get('columns[3][search][value]', None)
		if first_name:
			qs = qs.filter(first_name__icontains=first_name)

		'''last_name = self.request.GET.get('columns[3][search][value]', None)
		if last_name:
			qs = qs.filter(last_name__icontains=last_name)

		email = self.request.GET.get('columns[4][search][value]', None)
		if email:
			qs = qs.filter(email__icontains=email)'''

		phone_number = self.request.GET.get('columns[4][search][value]', None)
		if phone_number:
			qs = qs.filter(userprofile__phone_number__icontains=phone_number)

		is_active = self.request.GET.get('columns[5][search][value]', None)
		if is_active:
			qs = qs.filter(userprofile__user_approval_status=is_active)
			#~ if is_active == "Yes":
				#~ qs = qs.filter(is_active=True)
			#~ elif is_active == "No":
				#~ qs = qs.filter(is_active=False)

		deputed_to = self.request.GET.get('columns[6][search][value]', None)
		if deputed_to:
			qs = qs.filter(companyuser__deputed_to__name__icontains=deputed_to)

		groupname = self.request.GET.get('columns[7][search][value]', None)
		if groupname:
			uids = qs.values_list('id', flat=True)
			uids = AssignGroups.objects.filter(user__in=uids, groups__segmentation_name__icontains=groupname).values_list('user', flat=True)
			qs = qs.filter(id__in=uids)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []

		todayDate = date.today()

		yesterdayDate = todayDate - timedelta(days=1)

		currentWeekStartDate = todayDate - timedelta(days=todayDate.weekday())

		for item in qs:
			#~ if item.is_active:
				#~ status = "Yes"
			#~ else:
				#~ status = "No"

			deputed_to = ""
			if item.companyuser.deputed_to:
				deputed_to = item.companyuser.deputed_to.name

			agNames = AssignGroups.objects.filter(user=item).values_list('groups__segmentation_name', flat=True)
			agNames = ', '.join(agNames)

			todaymeetings = Meeting.objects.filter(user=item, start_datetime__gte=datetime.combine(todayDate, time.min), start_datetime__lte=datetime.combine(todayDate, time.max)).count()
			thisweekmeetings = Meeting.objects.filter(user=item, start_datetime__gte=datetime.combine(currentWeekStartDate, time.min), start_datetime__lte=datetime.combine(todayDate, time.max)).count()

			json_data.append([
				item.id,
				item.companyuser.company.name,
				item.username,
				item.first_name,
				#item.last_name,
				#item.email,
				item.userprofile.phone_number,
				item.userprofile.user_approval_status, #status,
				deputed_to,
				agNames,
				todaymeetings,
				thisweekmeetings
			])
		return json_data


class AdminisratorDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number', 'userprofile.user_approval_status'] #Table columns
	order_columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number', 'userprofile.user_approval_status']
	search_columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number', 'userprofile.user_approval_status']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = User.objects.filter(groups__name="administrator").select_related('userprofile')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		#If User is Administartor
		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					companyUserIds = CompanyUser.objects.filter(company=company).values_list('user', flat=True).distinct()
					return queryset.filter(id__in=companyUserIds)
			except ObjectDoesNotExist:
				return User.objects.none()
		else:
			return queryset.filter(id=user.id)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(username__icontains=search)|qs.filter(first_name__icontains=search)|qs.filter(last_name__icontains=search)|qs.filter(email__icontains=search)|qs.filter(userprofile__phone_number__icontains=search)|qs.filter(userprofile__user_approval_status=search)

		username = self.request.GET.get('columns[1][search][value]', None)
		if username:
			qs = qs.filter(username__icontains=username)

		first_name = self.request.GET.get('columns[2][search][value]', None)
		if first_name:
			qs = qs.filter(first_name__icontains=first_name)

		last_name = self.request.GET.get('columns[3][search][value]', None)
		if last_name:
			qs = qs.filter(last_name__icontains=last_name)

		email = self.request.GET.get('columns[4][search][value]', None)
		if email:
			qs = qs.filter(email__icontains=email)

		phone_number = self.request.GET.get('columns[5][search][value]', None)
		if phone_number:
			qs = qs.filter(userprofile__phone_number__icontains=phone_number)

		is_active = self.request.GET.get('columns[6][search][value]', None)
		if is_active:
			qs = qs.filter(userprofile__user_approval_status=is_active)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			#~ if item.is_active:
				#~ status = "Yes"
			#~ else:
				#~ status = "No"

			json_data.append([
				item.id,
				item.username,
				item.first_name,
				item.last_name,
				item.email,
				item.userprofile.phone_number,
				item.userprofile.user_approval_status
			])
		return json_data

from django.utils import timezone
class PushDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'catalog', 'selection', 'message', 'time', 'status', 'buyer_segmentation.segmentation_name', 'total_users', 'total_viewed'] #Table columns
	order_columns = ['id', 'id', 'id', 'message', 'time', 'status', 'buyer_segmentation.segmentation_name', 'id', 'id']
	search_columns = ['id', 'id', 'id', 'message', 'time', 'status', 'buyer_segmentation.segmentation_name']

	#max_display_length = 10000

	def get_initial_queryset(self):
		global company
		#Initial Queryset
		queryset = Push.objects.all().select_related('buyer_segmentation', 'single_company_push', 'shared_catalog__company')
		queryset = queryset.filter(to_show="yes")

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return queryset.filter(company=company)
		except ObjectDoesNotExist:
			return Push.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(time__icontains=search)|qs.filter(status__icontains=search)|qs.filter(message__icontains=search)|qs.filter(buyer_segmentation__segmentation_name__icontains=search)|qs.filter(single_company_push__name__icontains=search)

		catalog = self.request.GET.get('columns[1][search][value]', None)
		if catalog:
			#pushids = Push_User.all_objects.filter(catalog__title__icontains=str(catalog)).exclude(catalog__isnull=True).values_list('push', flat=True).distinct()
			#qs = qs.filter(id__in=pushids)
			qs = qs.filter(shared_catalog__title__icontains=catalog)

		selection = self.request.GET.get('columns[2][search][value]', None)
		if selection:
			pushids = Push_User.all_objects.filter(selection__name__icontains=str(selection)).exclude(selection__isnull=True).values_list('push', flat=True).distinct()
			qs = qs.filter(id__in=pushids)

		'''message = self.request.GET.get('columns[3][search][value]', None)
		if message:
			message_parts = message.split(' ')
			qs_params = None
			for part in message_parts:
				q = Q(message__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)'''

		segmentation_name = self.request.GET.get('columns[4][search][value]', None)
		if segmentation_name:
			qs = qs.filter(buyer_segmentation__segmentation_name__icontains=segmentation_name)|qs.filter(single_company_push__name__icontains=segmentation_name)

		time = self.request.GET.get('columns[8][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(time__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(time__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(time__lte=date[1])

		'''status = self.request.GET.get('columns[5][search][value]', None)
		if status:
			qs = qs.filter(status=status)'''


		return qs

	def prepare_results(self, qs):
		global company
		#JSON array data
		json_data = []
		for item in qs:
			catalog_selection_type = ""
			catalog_selection_id = None

			#pushUserCatalogId = Push_User.all_objects.filter(push=item.id).exclude(catalog__isnull=True).order_by('catalog').values_list('catalog__title', flat=True).distinct()
			#pushCatalogs = ', '.join(pushUserCatalogId)

			#catalogObj = Push_User.all_objects.filter(push=item.id).exclude(catalog__isnull=True).first()
			catalog_name = ""

			if item.shared_catalog is not None:
				catalogObj = item.shared_catalog
				catalog_name = catalogObj.title
				catalog_selection_id = catalogObj.id
				if catalogObj.company == company:
					catalog_selection_type = "mycatalog"
				elif catalogObj.view_permission == "public":
					catalog_selection_type = "publiccatalog"
				else:
					catalog_selection_type = "receivedcatalog"

			#pushUserSelectionId = Push_User.all_objects.filter(push=item.id).exclude(selection__isnull=True).order_by('selection').values_list('selection__name', flat=True).distinct()
			#pushSelections = ', '.join(pushUserSelectionId)

			# selectionObj = Push_User.all_objects.filter(push=item.id).exclude(selection__isnull=True).first()
			# selection_name = ""
			# if selectionObj is not None and selectionObj.selection is not None:
			# 	selectionObj = selectionObj.selection
			# 	selection_name = selectionObj.name
			# 	catalog_selection_id = selectionObj.id
			# 	if selectionObj.user.companyuser.company == company:
			# 		catalog_selection_type = "myselection"
			# 	else:
			# 		catalog_selection_type = "receivedselection"

			total_products = PushSellerPrice.objects.filter(push=item.id).values_list('product', flat=True).distinct().count()

			segmentation_name = None
			if item.buyer_segmentation:
				segmentation_name = item.buyer_segmentation.segmentation_name
			elif item.single_company_push:
				segmentation_name = item.single_company_push.name

			json_data.append([
				item.id,
				catalog_name,
				"",# selection_name,
				total_products,
				segmentation_name,
				item.total_users(),
				item.total_viewed(),
				item.total_products_viewed(),
				str(timezone.localtime(item.time).strftime("%Y-%m-%d : %I:%M%p")),
				catalog_selection_type,
				catalog_selection_id,
			])
		return json_data

class PushBuyerDetailDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'buying_company__name', 'id', 'id']
	order_columns = ['id', 'buying_company__name', 'id', 'id', 'id']
	search_columns = ['id', 'buying_company__name', 'id', 'id']

	def get_initial_queryset(self):
		global pid
		global pushObj
		#global ptype

		pid = self.request.GET.get('id', None)
		#ptype = self.request.GET.get('type', None)

		user = self.request.user

		pushObj = Push.objects.get(pk=pid)

		puids = Push_User.all_objects.filter(push=pushObj, selling_company=pushObj.company).values_list('buying_company', flat=True)
		queryset = Buyer.objects.filter(selling_company=pushObj.company, status='approved', buying_company__in=puids)

		# queryset =Buyer.objects.raw('SELECT * FROM api_buyer where selling_company=%s and status=`approved` and buying_company in %s', [pushObj.company, puids])
		# print queryset
		return queryset

	def ordering(self, qs):
		global pid
		global pushObj

		order_column = self.request.GET.get('order[0][column]', None)
		order_type = self.request.GET.get('order[0][dir]', None)

		print order_column
		print order_type

		sorting_cols = 0
		if self.pre_camel_case_notation:
			try:
				sorting_cols = int(self._querydict.get('iSortingCols', 0))
			except ValueError:
				sorting_cols = 0
		else:
			sort_key = 'order[{0}][column]'.format(sorting_cols)
			while sort_key in self._querydict:
				sorting_cols += 1
				sort_key = 'order[{0}][column]'.format(sorting_cols)

		order = []
		order_columns = self.get_order_columns()

		for i in range(sorting_cols):
			# sorting column
			sort_dir = 'asc'
			try:
				if self.pre_camel_case_notation:
					sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
					# sorting order
					sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
				else:
					sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
					# sorting order
					sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
			except ValueError:
				sort_col = 0

			sdir = '-' if sort_dir == 'desc' else ''
			sortcol = order_columns[sort_col]

			if isinstance(sortcol, list):
				for sc in sortcol:
					order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
			else:
				order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

		if order_column == "4" and pushObj.shared_catalog is not None:
			print "if order_column == 4"
			buyers = qs.values_list('buying_company', flat=True)
			buyers = list(buyers)

			if order_type == "desc":
				print "in desc"
				viewedcompany = CompanyCatalogView.objects.filter(catalog=pushObj.shared_catalog, company__in=buyers).order_by('-created_at').values_list('company', flat=True)

			elif order_type == "asc":
				print "in asc"
				viewedcompany = CompanyCatalogView.objects.filter(catalog=pushObj.shared_catalog, company__in=buyers).order_by('created_at').values_list('company', flat=True)

			viewedcompany = list(viewedcompany)
			viewedcompany.extend(buyers)

			preserved = Case(*[When(buying_company=pk, then=pos) for pos, pk in enumerate(viewedcompany)])
			qs = qs.filter().order_by(preserved)
		elif order:
			print "elif order:"
			return qs.order_by(*order)

		return qs

	def filter_queryset(self, qs):
		global pid
		global pushObj
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(buying_company__name__icontains=search)|qs.filter(id__icontains=search)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			qs = qs.filter(buying_company__name__icontains=name)

		is_viewed = self.request.GET.get('columns[3][search][value]', None)
		if is_viewed:
			buyers = qs.values_list('buying_company', flat=True)
			viewedcompany = CompanyCatalogView.objects.filter(catalog=pushObj.shared_catalog, company__in=buyers).values_list('company', flat=True)
			if is_viewed == 'Yes':
				qs = qs.filter(buying_company__in=viewedcompany)
			else:
				qs = qs.exclude(buying_company__in=viewedcompany)


		return qs

	def prepare_results(self, qs):
		global pid
		global pushObj

		#JSON array data
		json_data = []
		for item in qs:
			total_products_viewed = 0
			if pushObj.shared_catalog:
				total_products_viewed = CompanyProductView.objects.filter(product__in=pushObj.shared_catalog.products.all(), company=item.buying_company).count()

			is_catalog_viewed = 'No'
			ccvdate = None
			ccvObj = CompanyCatalogView.objects.filter(catalog=pushObj.shared_catalog, company=item.buying_company).first()
			#if CompanyCatalogView.objects.filter(catalog=pushObj.shared_catalog, company=item.buying_company).exists():
			if ccvObj:
				is_catalog_viewed = 'Yes'
				#ccvdate = str(timezone.localtime(ccvObj.created_at).strftime("%Y-%m-%d : %I:%M%p")),
				ccvdate = pretty_date(ccvObj.created_at)

			autoShareSubBuyers = Push_User.all_objects.filter(push=pid, selling_company=item.buying_company).count()

			json_data.append([
				item.id,
				item.buying_company.name,
				total_products_viewed,
				is_catalog_viewed,
				ccvdate,
				autoShareSubBuyers,
				item.buying_company.id,
			])
		return json_data

class PushProductDetailDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'buying_company__name', 'id', 'id']
	order_columns = ['id', 'buying_company__name', 'id', 'id']
	search_columns = ['id', 'buying_company__name', 'id', 'id']

	def get_initial_queryset(self):
		global pid
		global pushObj
		global buyers

		pid = self.request.GET.get('id', None)

		user = self.request.user

		pushObj = Push.objects.get(pk=pid)

		productids = PushSellerPrice.objects.filter(push=pid).values_list('product', flat=True).distinct()

		queryset = Product.objects.filter(id__in=productids)

		buyers = Push_User.all_objects.filter(push=pid).values_list('buying_company', flat=True).distinct()

		return queryset

	def filter_queryset(self, qs):
		global pid
		global pushObj

		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(sku__icontains=search)|qs.filter(id__icontains=search)

		name = self.request.GET.get('columns[2][search][value]', None)
		if name:
			qs = qs.filter(sku__icontains=name)

		return qs

	def prepare_results(self, qs):
		global pid
		global pushObj
		global buyers

		json_data = []

		for item in qs:
			totalproductviewed=CompanyProductView.objects.filter(product=item, company__in=buyers).count()

			json_data.append([
				item.id,
				str(item.image.thumbnail[settings.SMALL_IMAGE].url),
				item.sku,
				totalproductviewed,
			])
		return json_data

class SalesOrderDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'order_number', 'created_at', 'company__name', 'company__phone_number', 'items', 'total_rate', 'id', 'shipping_charges', 'customer_status', 'processing_status', 'tracking_details'] #Table columns
	order_columns = ['id', 'order_number', 'created_at', 'company__name', 'company__phone_number',  'items', 'total_rate', 'id', 'shipping_charges', 'customer_status', 'processing_status', 'tracking_details']
	search_columns = ['order_number', 'created_at', 'company__name', 'company__phone_number', 'items', 'total_rate', 'customer_status', 'processing_status', 'tracking_details']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = SalesOrder.objects.filter(visible_to_supplier=True).exclude(processing_status__in=["Draft","Cart"]).select_related('seller_company','company', 'tranferred_to__seller_company').prefetch_related('items', 'invoice_set')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		#If User is Administartor

		userid = self.request.GET.get('user', None)
		buying_company = self.request.GET.get('buying_company', None)

		if user.groups.filter(name="administrator").exists():
			company = get_user_company(user)
			if company:
				if userid is not None:
					return queryset.filter(user=userid, seller_company=company)
				if buying_company is not None:
					return queryset.filter(company=buying_company)
				return queryset.filter(seller_company=company)
			else:
				return queryset.none()
			# try:
			# 	user_company = (user.companyuser.company is not None)
			# 	if user_company:
			# 		company = user.companyuser.company
			# 		if userid is not None:
			# 			return queryset.filter(user=userid, seller_company=company)
			# 		if buying_company is not None:
			# 			return queryset.filter(company=buying_company)
			# 		return queryset.filter(seller_company=company)#(user__companyuser__company=company)
			# except ObjectDoesNotExist:
			# 	return SalesOrder.objects.none()
		else:
			return queryset.filter(user=user)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(order_number__icontains=search)|qs.filter(created_at__icontains=search)|qs.filter(time__icontains=search)|qs.filter(processing_status__icontains=search)|qs.filter(customer_status__icontains=search)|qs.filter(company__name__icontains=search)|qs.filter(tracking_details__icontains=search)

		'''#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)'''

		order_number = self.request.GET.get('columns[1][search][value]', None)
		if order_number:
			qs = qs.filter(order_number__icontains=order_number)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(company__name__icontains=search)

		search = self.request.GET.get('columns[4][search][value]', None)
		if search:
			qs = qs.filter(company__phone_number__icontains=search)

		order_status = self.request.GET.get('columns[9][search][value]', None)
		if order_status:
			# qs = qs.filter(customer_status=customer_status)
			qs = filterOrderPaymentStatus(qs, order_status)

		processing_status = self.request.GET.get('columns[10][search][value]', None)
		if processing_status:
			qs = qs.filter(processing_status=processing_status)

		tracking_details = self.request.GET.get('columns[11][search][value]', None)
		if tracking_details:
			qs = qs.filter(tracking_details__icontains=tracking_details)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			#salesOrderItemObj = SalesOrderItem.objects.filter(sales_order=item.id).values_list('product__title', flat=True)
			#salesOrderItems = ', '.join(salesOrderItemObj)

			#noOfItemObj = SalesOrderItem.objects.filter(sales_order=item.id).count()

			'''customer_status = item.customer_status
			if item.customer_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if item.customer_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)'''

			payment_status = item.payment_status()
			customer_status = payment_status
			if payment_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if payment_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)

			processing_status = item.processing_status
			if item.processing_status == "Cancelled" and item.supplier_cancel is not None and item.supplier_cancel != "":
				processing_status += "<br> Note: "+str(item.supplier_cancel)
			if (item.processing_status == "Dispatched" or item.processing_status == "Delivered") and item.tracking_details is not None and item.tracking_details != "":
				processing_status += "<br> Note: "+str(item.tracking_details)
			if item.processing_status == "Transferred" and item.tranferred_to is not None:
				processing_status += "<br> To : "+str(item.tranferred_to.seller_company.name)

			# soiQty = SalesOrderItem.objects.filter(sales_order=item).aggregate(Sum('pending_quantity')).get('pending_quantity__sum', 0)
			# if soiQty is None:
			# 	soiQty = 0

			is_invited = Buyer.objects.filter(selling_company=item.seller_company, buying_company=item.company).exists()

			#taxes_sum = Invoice.objects.filter(order=item).aggregate(Sum('taxes')).get('taxes__sum', 0)
			#if taxes_sum is None:
			#	taxes_sum = 0

			# invoices = Invoice.objects.filter(order=item).values_list('id', flat=True)
			taxes_sum = None
			invoices = []
			for invoice in item.invoice_set.all():
				invoices.append(invoice.id)
				if invoice.taxes:
					if taxes_sum is None:
						taxes_sum = 0
					taxes_sum += invoice.taxes

			json_data.append([
				item.id,
				item.order_number,
				str(timezone.localtime(item.created_at).strftime("%Y-%m-%d : %I:%M%p")),
				item.company.name,
				item.company.phone_number,
				item.total_products(),
				item.total_rate(),
				taxes_sum,
				item.shipping_charges,
				customer_status,
				processing_status,
				{"total_pending_quantity":item.total_pending_quantity(), "buying_company_id":item.company.id, "is_invited":is_invited, "invoices":list(invoices)},

				#item.total_pending_quantity(),#soiQty,
				#item.company.id,

				#item.tracking_details,
				#item.supplier_cancel,
				#item.buyer_cancel,
				#item.payment_details,
			])
		return json_data

class SalesOrderInvoiceDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'order__order_number', 'datetime', 'order__company__name', 'total_qty', 'amount', 'taxes', 'total_amount', 'payment_status', 'status']
	order_columns = ['id', 'order__order_number', 'datetime', 'order__company__name', 'total_qty', 'amount', 'taxes', 'total_amount', 'id', 'payment_status', 'status']
	search_columns = ['order__order_number', 'datetime', 'order__company__name', 'total_qty', 'amount', 'taxes', 'total_amount', 'id', 'payment_status', 'status']

	def get_initial_queryset(self):
		queryset = Invoice.objects.all().select_related('order__seller_company', 'order__company').prefetch_related('shipment_set', 'items__tax_class_1', 'items__tax_class_2')

		user = self.request.user

		if user.is_staff:
			queryset = queryset.exclude(order__processing_status="Draft")
			return queryset

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(order__seller_company=company).exclude(order__processing_status="Draft")
			except ObjectDoesNotExist:
				return queryset.none()
		else:
			return queryset.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(order__order_number__icontains=search)|qs.filter(datetime__icontains=search)|qs.filter(order__company__name__icontains=search)|qs.filter(total_qty__icontains=search)|qs.filter(amount__icontains=search)|qs.filter(paid_amount__icontains=search)|qs.filter(pending_amount__icontains=search)|qs.filter(payment_status__icontains=search)

		'''#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)'''

		order_number = self.request.GET.get('columns[1][search][value]', None)
		if order_number:
			qs = qs.filter(order__order_number__icontains=order_number)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(datetime__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(datetime__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(datetime__lte=date[1])

		name = self.request.GET.get('columns[3][search][value]', None)
		if name:
			qs = qs.filter(order__company__name__icontains=name)

		total_qty = self.request.GET.get('columns[4][search][value]', None)
		if total_qty:
			qs = qs.filter(total_qty__icontains=total_qty)

		amount = self.request.GET.get('columns[5][search][value]', None)
		if amount:
			qs = qs.filter(amount__icontains=amount)

		taxes = self.request.GET.get('columns[6][search][value]', None)
		if taxes:
			qs = qs.filter(taxes__icontains=taxes)

		total_amount = self.request.GET.get('columns[7][search][value]', None)
		if total_amount:
			qs = qs.filter(total_amount__icontains=total_amount)

		payment_status = self.request.GET.get('columns[8][search][value]', None)
		if payment_status:
			qs = qs.filter(payment_status=payment_status)

		status = self.request.GET.get('columns[9][search][value]', None)
		if status:
			qs = qs.filter(status=status)

		'''customer_status = self.request.GET.get('columns[10][search][value]', None)
		if customer_status:
			qs = qs.filter(order__customer_status=customer_status)

		processing_status = self.request.GET.get('columns[11][search][value]', None)
		if processing_status:
			qs = qs.filter(order__processing_status=processing_status)'''

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			status = ""
			#if Shipment.objects.filter(invoice=item).exists():
			if item.shipment_set.count() > 0:
				status = "Dispatched"

			tax = ""
			if item.tax_class_1():
				tax += str(item.tax_class_1())+"-"+str(item.total_tax_value_1())
			if item.tax_class_2():
				tax += "<br>"+str(item.tax_class_2())+"-"+str(item.total_tax_value_2())

			json_data.append([
				item.id,
				item.order.order_number,
				str(timezone.localtime(item.datetime).strftime("%Y-%m-%d : %I:%M%p")),
				#item.datetime,
				item.order.company.name,
				item.total_qty,
				item.amount,
				#item.paid_amount,
				#item.pending_amount,
				tax,
				item.total_amount,
				item.payment_status,
				#item.order.customer_status,
				#item.order.processing_status,
				item.status,
				status,
				{"selling_company_id":item.order.seller_company.id, "buying_company_id":item.order.company.id},
			])
		return json_data

class PurchaseOrderInvoiceDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'order__order_number', 'datetime', 'order__seller_company__name', 'total_qty', 'amount', 'taxes', 'total_amount', 'payment_status', 'status']
	order_columns = ['id', 'order__order_number', 'datetime', 'order__seller_company__name', 'total_qty', 'amount', 'taxes', 'total_amount', 'id', 'payment_status', 'status']
	search_columns = ['order__order_number', 'datetime', 'order__seller_company__name', 'total_qty', 'amount', 'taxes', 'total_amount', 'id', 'payment_status', 'status']

	def get_initial_queryset(self):
		queryset = Invoice.objects.all().select_related('order__seller_company').prefetch_related('shipment_set', 'items__tax_class_1', 'items__tax_class_2')

		user = self.request.user

		if user.is_staff:
			queryset = queryset.exclude(order__processing_status="Draft")
			return queryset

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(order__company=company).exclude(order__processing_status="Draft")
			except ObjectDoesNotExist:
				return queryset.none()
		else:
			return queryset.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(order__order_number__icontains=search)|qs.filter(datetime__icontains=search)|qs.filter(order__company__name__icontains=search)|qs.filter(total_qty__icontains=search)|qs.filter(amount__icontains=search)|qs.filter(paid_amount__icontains=search)|qs.filter(pending_amount__icontains=search)|qs.filter(payment_status__icontains=search)

		'''#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)'''

		order_number = self.request.GET.get('columns[1][search][value]', None)
		if order_number:
			qs = qs.filter(order__order_number__icontains=order_number)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(datetime__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(datetime__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(datetime__lte=date[1])

		name = self.request.GET.get('columns[3][search][value]', None)
		if name:
			qs = qs.filter(order__seller_company__name__icontains=name)

		total_qty = self.request.GET.get('columns[4][search][value]', None)
		if total_qty:
			qs = qs.filter(total_qty__icontains=total_qty)

		amount = self.request.GET.get('columns[5][search][value]', None)
		if amount:
			qs = qs.filter(amount__icontains=amount)

		taxes = self.request.GET.get('columns[6][search][value]', None)
		if taxes:
			qs = qs.filter(taxes__icontains=taxes)

		total_amount = self.request.GET.get('columns[7][search][value]', None)
		if total_amount:
			qs = qs.filter(total_amount__icontains=total_amount)

		payment_status = self.request.GET.get('columns[8][search][value]', None)
		if payment_status:
			qs = qs.filter(payment_status=payment_status)

		status = self.request.GET.get('columns[9][search][value]', None)
		if status:
			qs = qs.filter(status=status)

		'''customer_status = self.request.GET.get('columns[10][search][value]', None)
		if customer_status:
			qs = qs.filter(order__customer_status=customer_status)

		processing_status = self.request.GET.get('columns[11][search][value]', None)
		if processing_status:
			qs = qs.filter(order__processing_status=processing_status)'''

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			status = ""
			#if Shipment.objects.filter(invoice=item).exists():
			if item.shipment_set.count() > 0:
				status = "Dispatched"

			tax = ""
			if item.tax_class_1():
				tax += str(item.tax_class_1())+"-"+str(item.total_tax_value_1())
			if item.tax_class_2():
				tax += "<br>"+str(item.tax_class_2())+"-"+str(item.total_tax_value_2())

			json_data.append([
				item.id,
				item.order.order_number,
				str(timezone.localtime(item.datetime).strftime("%Y-%m-%d : %I:%M%p")),
				#item.datetime,
				item.order.seller_company.name,
				item.total_qty,
				item.amount,
				#item.paid_amount,
				#item.pending_amount,
				tax,
				item.total_amount,
				item.payment_status,
				#item.order.customer_status,
				#item.order.processing_status,
				item.status,
				status,
				{"order_id":item.order.id}

			])
		return json_data

class OrderDetailDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'image', 'product__sku', 'product__catalog__title', 'product__catalog__brand__name', 'quantity', 'dispatched_qty', 'rate', 'id'] #Table columns
	order_columns = ['id', 'id', 'product__sku', 'product__catalog__title', 'product__catalog__brand__name', 'quantity', 'dispatched_qty', 'rate', 'id']
	search_columns = ['id', 'product__sku', 'product__catalog__title', 'product__catalog__brand__name', 'quantity', 'dispatched_qty', 'rate', 'id']

	def get_initial_queryset(self):
		global pid
		global ptype
		global company

		pid = self.request.GET.get('id', None)
		ptype = self.request.GET.get('type', None)

		user = self.request.user

		queryset = SalesOrderItem.objects.filter(sales_order=pid).select_related('product__catalog__brand')

		try:
			if user.is_staff:
				company = SalesOrder.objects.get(pk=pid).seller_company
				return queryset.filter(sales_order=pid).distinct()

			if user.companyuser is not None:
				company = user.companyuser.company

				if ptype == "salesorders":
					return queryset.filter(sales_order__seller_company=company, sales_order=pid).distinct()

				elif ptype == "purchaseorders":
					return queryset.filter(sales_order__company=company, sales_order=pid).distinct()

				else:
					return queryset.none()

		except ObjectDoesNotExist:
			return queryset.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(product__catalog__title__icontains=search)|qs.filter(product__sku__icontains=search)|qs.filter(rate__icontains=search)|qs.filter(quantity__icontains=search)|qs.filter(product__catalog__brand__name__icontains=search)

		sku = self.request.GET.get('columns[2][search][value]', None)
		if sku:
			qs = qs.filter(product__sku__icontains=sku)

		title = self.request.GET.get('columns[3][search][value]', None)
		if title:
			qs = qs.filter(product__catalog__title__icontains=title)

		title = self.request.GET.get('columns[4][search][value]', None)
		if title:
			qs = qs.filter(product__catalog__brand__name__icontains=title)

		quantity = self.request.GET.get('columns[5][search][value]', None)
		if quantity:
			qs = qs.filter(quantity__icontains=quantity)

		dispatched_qty = self.request.GET.get('columns[6][search][value]', None)
		if dispatched_qty:
			qs = qs.filter(dispatched_qty__icontains=dispatched_qty)

		pending_quantity = self.request.GET.get('columns[7][search][value]', None)
		if pending_quantity:
			qs = qs.filter(pending_quantity__icontains=pending_quantity)

		price = self.request.GET.get('columns[8][search][value]', None)
		if price:
			qs = qs.filter(rate__icontains=price)

		packing_type = self.request.GET.get('columns[9][search][value]', None)
		if packing_type:
			qs = qs.filter(packing_type=packing_type)

		note = self.request.GET.get('columns[10][search][value]', None)
		if note:
			qs = qs.filter(note__icontains=note)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		global pid
		global company

		json_data = []

		#soObj = SalesOrder.objects.get(pk=pid)

		for item in qs:
			catalog_type = ""
			catalog = item.product.catalog
			if catalog.view_permission == "public" and catalog.company == company:
				catalog_type = "mycatalog"
			if catalog.view_permission == "public":
				catalog_type = "public"
			elif catalog.company == company:
				catalog_type = "mycatalog"
			else:
				catalog_type = "received"

			json_data.append([
				item.id,
				str(item.product.image.thumbnail[settings.SMALL_IMAGE].url),
				item.product.sku,
				#item.product.title,
				item.product.catalog.title,
				item.product.catalog.brand.name,
				item.quantity,
				item.dispatched_qty,
				item.pending_quantity,
				item.rate,
				item.packing_type,
				item.note,
				#item.id,
				{"catalog":item.product.catalog.id, "brand":item.product.catalog.brand.id, "catalog_type":catalog_type},
				#soObj.processing_status,
			])
		return json_data

class PurchaseDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'order_number', 'created_at', 'seller_company__name', 'items', 'total_rate', 'shipping_charges', 'customer_status', 'processing_status', 'tracking_details'] #Table columns
	order_columns = ['id', 'order_number', 'created_at', 'seller_company__name', 'items', 'total_rate', 'shipping_charges', 'customer_status', 'processing_status', 'tracking_details']
	search_columns = ['order_number', 'created_at', 'seller_company__name', 'items', 'total_rate', 'customer_status', 'processing_status', 'tracking_details']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = SalesOrder.objects.filter(visible_to_buyer=True).exclude(processing_status__in=["Cart"]).select_related('seller_company').prefetch_related('items', 'invoice_set')

		#If User is Staff User
		user = self.request.user
		#if user.is_staff:
		#	return queryset

		#If User is Administartor
		selling_company = self.request.GET.get('selling_company', None)

		if user.groups.filter(name="administrator").exists():
			try:
				if selling_company is not None:
					queryset = queryset.filter(seller_company=selling_company)
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(company=company)#(user__companyuser__company=company)
			except ObjectDoesNotExist:
				return SalesOrder.objects.none()
		else:
			return queryset.filter(user=user)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(order_number__icontains=search)|qs.filter(created_at__icontains=search)|qs.filter(time__icontains=search)|qs.filter(processing_status__icontains=search)|qs.filter(customer_status__icontains=search)|qs.filter(seller_company__name__icontains=search)|qs.filter(tracking_details__icontains=search)

		'''#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)'''

		order_number = self.request.GET.get('columns[1][search][value]', None)
		if order_number:
			qs = qs.filter(order_number__icontains=order_number)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(seller_company__name__icontains=search)

		order_status = self.request.GET.get('columns[8][search][value]', None)
		if order_status:
			# qs = qs.filter(customer_status=customer_status)
			qs = filterOrderPaymentStatus(qs, order_status)

		processing_status = self.request.GET.get('columns[9][search][value]', None)
		if processing_status:
			qs = qs.filter(processing_status=processing_status)

		tracking_details = self.request.GET.get('columns[10][search][value]', None)
		if tracking_details:
			qs = qs.filter(tracking_details__icontains=tracking_details)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			#salesOrderItemObj = SalesOrderItem.objects.filter(sales_order=item.id).values_list('product__title', flat=True)
			#salesOrderItems = ', '.join(salesOrderItemObj)

			#noOfItemObj = SalesOrderItem.objects.filter(sales_order=item.id).count()

			'''customer_status = item.customer_status
			if item.customer_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if item.customer_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)'''

			payment_status = item.payment_status()
			customer_status = payment_status
			if payment_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if payment_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)

			processing_status = item.processing_status
			if item.processing_status == "Cancelled" and item.supplier_cancel is not None and item.supplier_cancel != "":
				processing_status += "<br> Note: "+str(item.supplier_cancel)
			if (item.processing_status == "Dispatched" or item.processing_status == "Delivered") and item.tracking_details is not None and item.tracking_details != "":
				processing_status += "<br> Note: "+str(item.tracking_details)

			# taxes_sum = Invoice.objects.filter(order=item).aggregate(Sum('taxes')).get('taxes__sum', 0)
			# invoices = item.invoice_set.all().values_list('id', flat=True) #Invoice.objects.filter(order=item).values_list('id', flat=True)

			taxes_sum = None
			invoices = []
			for invoice in item.invoice_set.all():
				invoices.append(invoice.id)
				if invoice.taxes:
					if taxes_sum is None:
						taxes_sum = 0
					taxes_sum += invoice.taxes

			json_data.append([
				item.id,
				item.order_number,
				str(timezone.localtime(item.created_at).strftime("%Y-%m-%d : %I:%M%p")),
				item.seller_company.name,
				item.total_item(),
				item.total_rate(),
				taxes_sum,
				item.shipping_charges,
				customer_status,
				processing_status,
				#item.seller_company.id
				{"selling_company_id":item.seller_company.id, "invoices":list(invoices)},
			])
		return json_data


class BrokerageOrderDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'order_number', 'created_at', 'seller_company__name', 'company__name', 'items', 'total_rate', 'id', 'shipping_charges', 'customer_status', 'processing_status', 'tracking_details'] #Table columns
	order_columns = ['id', 'order_number', 'created_at', 'seller_company__name', 'company__name', 'items', 'total_rate', 'id', 'shipping_charges', 'customer_status', 'processing_status', 'tracking_details']
	search_columns = ['order_number', 'created_at', 'seller_company__name', 'company__name', 'items', 'total_rate', 'customer_status', 'processing_status', 'tracking_details']

	def get_initial_queryset(self):
		queryset = SalesOrder.objects.all().select_related('company__chat_admin_user','seller_company__chat_admin_user').prefetch_related('items', 'invoice_set')

		user = self.request.user

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(broker_company=company)
			except ObjectDoesNotExist:
				return queryset.none()
		return queryset.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(order_number__icontains=search)|qs.filter(created_at__icontains=search)|qs.filter(time__icontains=search)|qs.filter(processing_status__icontains=search)|qs.filter(customer_status__icontains=search)|qs.filter(seller_company__name__icontains=search)|qs.filter(company__name__icontains=search)|qs.filter(tracking_details__icontains=search)

		'''#Column wise filter
		ids = self.request.GET.get('columns[1][search][value]', None)
		if ids:
			qs = qs.filter(id=ids)'''

		order_number = self.request.GET.get('columns[1][search][value]', None)
		if order_number:
			qs = qs.filter(order_number__icontains=order_number)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(seller_company__name__icontains=search)

		search = self.request.GET.get('columns[4][search][value]', None)
		if search:
			qs = qs.filter(company__name__icontains=search)

		order_status = self.request.GET.get('columns[10][search][value]', None)
		if order_status:
			# qs = qs.filter(customer_status=customer_status)
			qs = filterOrderPaymentStatus(qs, order_status)

		processing_status = self.request.GET.get('columns[11][search][value]', None)
		if processing_status:
			qs = qs.filter(processing_status=processing_status)

		tracking_details = self.request.GET.get('columns[12][search][value]', None)
		if tracking_details:
			qs = qs.filter(tracking_details__icontains=tracking_details)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			#salesOrderItemObj = item.items.filter(sales_order=item.id).values_list('product__title', flat=True)
			#salesOrderItems = ', '.join(salesOrderItemObj)

			#noOfItemObj = item.items.filter(sales_order=item.id).count()

			'''customer_status = item.customer_status
			if item.customer_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if item.customer_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)'''

			payment_status = item.payment_status()
			customer_status = payment_status
			if payment_status == "Paid" and item.payment_details is not None and item.payment_details != "":
				customer_status += "<br> Note: "+str(item.payment_details)
			if payment_status == "Cancelled" and item.buyer_cancel is not None and item.buyer_cancel != "":
				customer_status += "<br> Note: "+str(item.buyer_cancel)

			processing_status = item.processing_status
			if item.processing_status == "Cancelled" and item.supplier_cancel is not None and item.supplier_cancel != "":
				processing_status += "<br> Note: "+str(item.supplier_cancel)
			if (item.processing_status == "Dispatched" or item.processing_status == "Delivered") and item.tracking_details is not None and item.tracking_details != "":
				processing_status += "<br> Note: "+str(item.tracking_details)

			# taxes_sum = item.invoice_set.filter(order=item).aggregate(Sum('taxes')).get('taxes__sum', 0)
			# invoices = item.invoice_set.all().values_list('id', flat=True) #Invoice.objects.filter(order=item).values_list('id', flat=True)

			taxes_sum = None
			invoices = []
			for invoice in item.invoice_set.all():
				invoices.append(invoice.id)
				if invoice.taxes:
					if taxes_sum is None:
						taxes_sum = 0
					taxes_sum += invoice.taxes

			json_data.append([
				item.id,
				item.order_number,
				str(timezone.localtime(item.created_at).strftime("%Y-%m-%d : %I:%M%p")),
				item.seller_company.name,
				item.company.name,
				item.total_item(),
				item.total_rate(),
				taxes_sum,
				item.shipping_charges,
				(item.total_rate() * item.brokerage_fees / 100),
				customer_status,
				processing_status,
				{"selling_company_id":item.seller_company.id, "selling_company_chat_user":item.seller_company.chat_admin_user.username, "selling_company_name":item.seller_company.name, "invoices":list(invoices),
				"buying_company_id":item.company.id, "buying_company_chat_user":item.company.chat_admin_user.username, "buying_company_name":item.company.name},

			])
		return json_data

class CompanyPhoneAliasDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'alias_number', 'status'] #Table columns
	order_columns = ['id', 'alias_number', 'status']
	search_columns = ['id', 'alias_number', 'status']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = CompanyPhoneAlias.objects.all().select_related('country')

		#If User is Staff User
		user = self.request.user

		#If User is Administartor
		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(company=company)
			except ObjectDoesNotExist:
				return CompanyPhoneAlias.objects.none()
		else:
			return CompanyPhoneAlias.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(country__phone_code__icontains=search)|qs.filter(alias_number__icontains=search)|qs.filter(status__icontains=search)

		'''country = self.request.GET.get('columns[1][search][value]', None)
		if country:
			qs = qs.filter(country__name__icontains=country)'''

		alias = self.request.GET.get('columns[1][search][value]', None)
		if alias:
			qs = qs.filter(Q(alias_number__icontains=alias)|Q(country__phone_code__icontains=alias))

		status = self.request.GET.get('columns[2][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			json_data.append([
				item.id,
				item.country.phone_code+item.alias_number,
				item.status,
			])
		return json_data

class CompanyBuyerGroupDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'buyer_type', 'price_list', 'payment_duration', 'discount', 'cash_discount'] #Table columns
	order_columns = ['id', 'buyer_type', 'price_list', 'payment_duration', 'discount', 'cash_discount']
	search_columns = ['id', 'buyer_type', 'price_list', 'payment_duration', 'discount', 'cash_discount']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = CompanyBuyerGroup.objects.all().select_related('price_list')

		#If User is Staff User
		user = self.request.user
		user_agent = self.request.META.get('HTTP_USER_AGENT', None)
		user_agent = user_agent.lower()
		logger.info("useragent = %s"% (str(user_agent)))
		#If User is Administartor
		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(company=company)
			except ObjectDoesNotExist:
				return CompanyBuyerGroup.objects.none()
		else:
			return CompanyBuyerGroup.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(buyer_type__name__icontains=search)|qs.filter(price_list__number_pricelists__icontains=search)|qs.filter(payment_duration__icontains=search)|qs.filter(discount__icontains=search)|qs.filter(cash_discount__icontains=search)

		buyer_type = self.request.GET.get('columns[1][search][value]', None)
		if buyer_type:
			qs = qs.filter(buyer_type__name__icontains=buyer_type)

		price_list = self.request.GET.get('columns[2][search][value]', None)
		if price_list:
			qs = qs.filter(price_list__number_pricelists__icontains=price_list)

		payment_duration = self.request.GET.get('columns[3][search][value]', None)
		if payment_duration:
			qs = qs.filter(payment_duration__icontains=payment_duration)

		discount = self.request.GET.get('columns[4][search][value]', None)
		if discount:
			qs = qs.filter(discount__icontains=discount)

		cash_discount = self.request.GET.get('columns[5][search][value]', None)
		if cash_discount:
			qs = qs.filter(cash_discount__icontains=cash_discount)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			if item.price_list is not None:
				json_data.append([
					item.id,
					item.buyer_type,
					item.price_list.number_pricelists,
					item.payment_duration,
					item.discount,
					item.cash_discount,
				])
			else:
				json_data.append([
					item.id,
					item.buyer_type,
					'',
					item.payment_duration,
					item.discount,
					item.cash_discount,
				])
		return json_data



class InventoryDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'warehouse', 'product__catalog', 'product__catalog__brand', 'product', 'in_stock', 'available', 'blocked', 'open_sale', 'open_purchase']
	order_columns = ['id', 'warehouse', 'product__catalog', 'product__catalog__brand', 'product', 'in_stock', 'available', 'blocked', 'open_sale', 'open_purchase']
	search_columns = ['id', 'warehouse', 'product__catalog', 'product__catalog__brand', 'product', 'in_stock', 'available', 'blocked', 'open_sale', 'open_purchase']

	def get_initial_queryset(self):
		#Initial Queryset
		user = self.request.user
		company = user.companyuser.company

		queryset = Stock.objects.filter(company=company).select_related('warehouse', 'product__catalog__brand')

		return queryset

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(product__catalog__brand__name__icontains=search)|qs.filter(product__catalog__title__icontains=search)|qs.filter(warehouse__name__icontains=search)|qs.filter(product__title__icontains=search)|qs.filter(in_stock__icontains=search)|qs.filter(blocked__icontains=search)|qs.filter(open_sale__icontains=search)|qs.filter(open_purchase__icontains=search)|qs.filter(available__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(warehouse__name__icontains=search)

		search = self.request.GET.get('columns[2][search][value]', None)
		if search:
			qs = qs.filter(product__catalog__brand__name__icontains=search)

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(product__catalog__title__icontains=search)

		search = self.request.GET.get('columns[4][search][value]', None)
		if search:
			qs = qs.filter(product__title__icontains=search)

		search = self.request.GET.get('columns[5][search][value]', None)
		if search:
			qs = qs.filter(in_stock__icontains=search)

		search = self.request.GET.get('columns[6][search][value]', None)
		if search:
			qs = qs.filter(available__icontains=search)

		search = self.request.GET.get('columns[7][search][value]', None)
		if search:
			qs = qs.filter(blocked__icontains=search)

		search = self.request.GET.get('columns[8][search][value]', None)
		if search:
			qs = qs.filter(open_sale__icontains=search)

		search = self.request.GET.get('columns[9][search][value]', None)
		if search:
			qs = qs.filter(open_purchase__icontains=search)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			warehouse = None
			if item.warehouse:
				warehouse = item.warehouse.name

			json_data.append([
				item.id,
				warehouse,
				item.product.catalog.brand.name,
				item.product.catalog.title,
				item.product.title,
				item.in_stock,
				item.available,
				item.blocked,
				item.open_sale,
				item.open_purchase,
			])
		return json_data

class SKUMapDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'product__title', 'external_sku', 'catalog__title', 'external_catalog']
	order_columns = ['id', 'product__title', 'external_sku', 'catalog__title', 'external_catalog']
	search_columns = ['id', 'product__title', 'external_sku', 'catalog__title', 'external_catalog']

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			appInstanceObj = AppInstance.objects.filter(company=company)

			queryset = SKUMap.objects.filter(app_instance__in=appInstanceObj).select_related('product__catalog', 'catalog')
			return queryset
		except ObjectDoesNotExist:
			return SKUMap.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(product__sku__icontains=search)|qs.filter(external_sku__icontains=search)

		sku = self.request.GET.get('columns[1][search][value]', None)
		if sku:
			qs = qs.filter(product__sku__icontains=sku)

		sku = self.request.GET.get('columns[2][search][value]', None)
		if sku:
			qs = qs.filter(external_sku__icontains=sku)

		title = self.request.GET.get('columns[3][search][value]', None)
		if title:
			qs = qs.filter(Q(catalog__title__icontains=title) | Q(product__catalog__title__icontains=title))

		external_catalog = self.request.GET.get('columns[4][search][value]', None)
		if external_catalog:
			qs = qs.filter(external_catalog__icontains=external_catalog)

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			sku = ""
			catalog_title = ""

			if item.product:
				sku = item.product.sku
				catalog_title = item.product.catalog.title

			if item.catalog:
				catalog_title = item.catalog.title

			json_data.append([
				item.id,
				sku,
				item.external_sku,
				catalog_title,
				item.external_catalog,
			])
		return json_data


class StockDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'warehouse', 'product', 'in_stock', 'blocked', 'open_sale', 'open_purchase']
	order_columns = ['id', 'warehouse', 'product', 'in_stock', 'blocked', 'open_sale', 'open_purchase']
	search_columns = ['id', 'warehouse', 'product', 'in_stock', 'blocked', 'open_sale', 'open_purchase']

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = Stock.objects.filter(company=company).select_related('warehouse','product')

			return queryset
		except ObjectDoesNotExist:
			return Stock.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(warehouse__name__icontains=search)|qs.filter(product__sku__icontains=search)|qs.filter(in_stock__icontains=search)|qs.filter(blocked__icontains=search)|qs.filter(open_sale__icontains=search)|qs.filter(open_purchase__icontains=search)

		value = self.request.GET.get('columns[0][search][value]', None)
		if value:
			qs = qs.filter(id__icontains=value)

		value = self.request.GET.get('columns[1][search][value]', None)
		if value:
			qs = qs.filter(warehouse__name__icontains=value)

		value = self.request.GET.get('columns[2][search][value]', None)
		if value:
			qs = qs.filter(product__sku__icontains=value)

		value = self.request.GET.get('columns[3][search][value]', None)
		if value:
			qs = qs.filter(in_stock__icontains=value)

		value = self.request.GET.get('columns[4][search][value]', None)
		if value:
			qs = qs.filter(blocked__icontains=value)

		value = self.request.GET.get('columns[5][search][value]', None)
		if value:
			qs = qs.filter(open_sale__icontains=value)

		value = self.request.GET.get('columns[6][search][value]', None)
		if value:
			qs = qs.filter(open_purchase__icontains=value)

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			warehouse = None
			if item.warehouse:
				warehouse = item.warehouse.name
			json_data.append([
				item.id,
				warehouse,
				item.product.sku,
				item.in_stock,
				item.blocked,
				item.open_sale,
				item.open_purchase,
			])
		return json_data


class MeetingDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'buying_company_ref', 'start_datetime', 'duration', 'note']
	order_columns = ['id', 'buying_company_ref', 'start_datetime', 'duration', 'note']
	search_columns = ['id', 'buying_company_ref', 'start_datetime', 'duration', 'note']

	def get_initial_queryset(self):
		global company
		queryset = Meeting.objects.all().select_related('buying_company_ref').order_by('-id')

		user = self.request.user

		#pid = self.request.GET.get('id', None)
		userid = self.request.GET.get('user', None)


		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					companyUserIds = CompanyUser.objects.filter((Q(company=company) | Q(deputed_to=company)) & Q(user=userid)).values_list('user', flat=True).distinct()

					return queryset.filter(user__in=companyUserIds)
					#return queryset.filter(user=userid)

			except ObjectDoesNotExist:
				return User.objects.none()
		else:
			return queryset.filter(user=user)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(buying_company_ref__name__icontains=search)|qs.filter(duration__icontains=search)|qs.filter(start_datetime__icontains=search)|qs.filter(note__icontains=search)|qs.filter(buyer_name_text__icontains=search)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			qs = qs.filter(Q(buying_company_ref__name__icontains=name) | Q(buyer_name_text__icontains=name))

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(start_datetime__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(start_datetime__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(start_datetime__lte=date[1])

		duration = self.request.GET.get('columns[3][search][value]', None)
		if duration:
			qs = qs.filter(duration__icontains=duration)

		note = self.request.GET.get('columns[4][search][value]', None)
		if note:
			qs = qs.filter(note__icontains=note)

		return qs

	def prepare_results(self, qs):
		global company
		#JSON array data
		json_data = []

		#start = self.request.GET.get('start', 0)
		#i = int(start)

		for item in qs:
			#i = i+1
			name = None;
			buying_company_id = None;
			#buyer_table_id = None
			if item.buying_company_ref:
				name = item.buying_company_ref.name
				buying_company_id = item.buying_company_ref.id
				#~ buyerObj = Buyer.objects.filter(selling_company=company, buying_company=item.buying_company_ref).last()
				#~ if buyerObj:
					#~ buyer_table_id = buyerObj.id
			elif item.buyer_name_text != "":
				name = item.buyer_name_text
			#else:
			#	name = item.note

			json_data.append([
				item.id,
				name,
				str(timezone.localtime(item.start_datetime).strftime("%Y-%m-%d : %I:%M%p")),
				str(item.duration).split(".")[0],
				#item.salesorder.count(),
				item.note,
				{"start_lat":item.start_lat, "start_long":item.start_long, "end_lat":item.end_lat, "end_long":item.end_long, "buying_company_id":buying_company_id},
				#i
			])
		return json_data

class AttendanceDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'company', 'date_time', 'action', 'no']
	order_columns = ['id', 'company', 'date_time', 'action', 'no']
	search_columns = ['id', 'company', 'date_time', 'action', 'no']

	def get_initial_queryset(self):
		queryset = Attendance.objects.all().order_by('-id')

		user = self.request.user

		userid = self.request.GET.get('user', None)

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					companyUserIds = CompanyUser.objects.filter((Q(company=company) | Q(deputed_to=company)) & Q(user=userid)).values_list('user', flat=True).distinct()

					return queryset.filter(user__in=companyUserIds)

			except ObjectDoesNotExist:
				return User.objects.none()
		else:
			return queryset.filter(user=user)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(date_time__icontains=search)|qs.filter(action__icontains=search)|qs.filter(company__name__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(company__name__icontains=search)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(date_time__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(date_time__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(date_time__lte=date[1])

		action = self.request.GET.get('columns[3][search][value]', None)
		if action:
			qs = qs.filter(action__icontains=action)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []

		start = self.request.GET.get('start', 0)
		i = int(start)

		for item in qs:
			i = i+1
			json_data.append([
				item.id,
				item.company.name,
				str(timezone.localtime(item.date_time).strftime("%Y-%m-%d : %I:%M%p")),
				item.action,
				i,
				{"att_lat":item.att_lat, "att_long":item.att_long},
			])
		return json_data

class CompanyAccountDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'buyer_company', 'mapped_accout_ref']
	order_columns = ['id', 'buyer_company', 'mapped_accout_ref']
	search_columns = ['id', 'buyer_company', 'mapped_accout_ref']

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = CompanyAccount.objects.filter(company=company).select_related('buyer_company')
			return queryset
		except ObjectDoesNotExist:
			return CompanyAccount.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(buyer_company__name__icontains=search)|qs.filter(mapped_accout_ref__icontains=search)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			qs = qs.filter(buyer_company__name__icontains=name)

		mapped_accout = self.request.GET.get('columns[2][search][value]', None)
		if mapped_accout:
			qs = qs.filter(mapped_accout_ref__icontains=mapped_accout)

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			json_data.append([
				item.id,
				item.buyer_company.name,
				item.mapped_accout_ref,
			])
		return json_data

class JobsDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['created_at', 'job_type', 'upload_file', 'error_file', 'status', 'total_rows', 'completed_rows',]
	order_columns = ['created_at', 'job_type', 'upload_file', 'error_file', 'status', 'total_rows', 'completed_rows',]
	search_columns = ['created_at', 'job_type', 'upload_file', 'error_file', 'status', 'total_rows', 'completed_rows',]

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = Jobs.objects.filter(company=company)
			return queryset
		except ObjectDoesNotExist:
			return Jobs.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(created_at__icontains=search)|qs.filter(job_type__icontains=search)|qs.filter(status__icontains=search)|qs.filter(total_rows__icontains=search)|qs.filter(completed_rows__icontains=search)

		time = self.request.GET.get('columns[0][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created_at__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created_at__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created_at__lte=date[1])

		job_type = self.request.GET.get('columns[1][search][value]', None)
		if job_type:
			qs = qs.filter(job_type__icontains=job_type)

		status = self.request.GET.get('columns[4][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)

		total_rows = self.request.GET.get('columns[5][search][value]', None)
		if total_rows:
			qs = qs.filter(total_rows__icontains=total_rows)

		completed_rows = self.request.GET.get('columns[6][search][value]', None)
		if completed_rows:
			qs = qs.filter(completed_rows__icontains=completed_rows)

		error_details = self.request.GET.get('columns[7][search][value]', None)
		if error_details:
			qs = qs.filter(error_details__icontains=error_details)

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			upload_file = None
			error_file = None
			if item.upload_file:
				upload_file = item.upload_file.url
			if item.error_file:
				error_file = item.error_file.url

			json_data.append([
				#item.id,
				str(timezone.localtime(item.created_at).strftime("%Y-%m-%d : %I:%M%p")),
				item.job_type,
				upload_file,
				error_file,
				item.status,
				item.total_rows,
				item.completed_rows,
				item.error_details,
			])
		return json_data


class SalesmanLocationDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'salesman', 'state', 'city', ]
	order_columns = ['id', 'salesman', 'state', 'city', ]
	search_columns = ['id', 'salesman', 'state', 'city', ]

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = SalesmanLocation.objects.filter(salesman__companyuser__company=company)
			return queryset
		except ObjectDoesNotExist:
			return SalesmanLocation.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(salesman__username__icontains=search)|qs.filter(state__state_name__icontains=search)|qs.filter(city__city_name__icontains=search)

		search = self.request.GET.get('columns[0][search][value]', None)
		if search:
			qs = qs.filter(id__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(salesman__username__icontains=search)

		search = self.request.GET.get('columns[2][search][value]', None)
		if search:
			qs = qs.filter(Q(state__state_name__icontains=search) | Q(city__city_name__icontains=search))
			print qs

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			'''citynames = item.city.all().values_list('city_name', flat=True)
			cities = ', '.join(citynames)

			statenames = item.state.all().values_list('state_name', flat=True)
			states = ', '.join(statenames)

			if cities == "":
				cities = "All Cities"

			if states == "":
				states = "All States"'''
			statecity = ""
			states = item.state.all()

			for state in states:
				statecity += state.state_name + " - "
				cities = item.city.filter(state=state)
				if len(cities) == 0:
					statecity += "All Cities, "
				else:
					for city in cities:
						statecity += city.city_name + ", "

			cities = item.city.exclude(state__in=states)
			for city in cities:
				statecity += city.city_name + ", "

			json_data.append([
				item.id,
				item.salesman.username,
				statecity,
			])
		return json_data


class BuyerSalesmenDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'salesman', 'buyer', ]
	order_columns = ['id', 'salesman', 'buyer', ]
	search_columns = ['id', 'salesman', 'buyer', ]

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = BuyerSalesmen.objects.filter(salesman__companyuser__company=company)
			return queryset
		except ObjectDoesNotExist:
			return BuyerSalesmen.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(salesman__username__icontains=search)|qs.filter(buyer__name__icontains=search)

		search = self.request.GET.get('columns[0][search][value]', None)
		if search:
			qs = qs.filter(id__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(salesman__username__icontains=search)

		search = self.request.GET.get('columns[2][search][value]', None)
		if search:
			qs = qs.filter(buyer__name__icontains=search)
			print qs

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			buyers = item.buyers.all().values_list('name', flat=True)
			buyers = list(buyers)
			buyers = ", ".join(buyers)
			json_data.append([
				item.id,
				item.salesman.username,
				buyers,
			])
		return json_data


class BrandOwnSaleDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'name', 'image', 'company', ]
	order_columns = ['id', 'name', 'id', 'company', ]
	search_columns = ['id', 'name', 'company', ]

	def get_initial_queryset(self):
		global company
		try:
			user = self.request.user
			company = user.companyuser.company

			brand_distributor = BrandDistributor.objects.filter(company=company).order_by('brand').values_list('brand', flat=True).distinct()

			queryset = Brand.objects.filter(Q(company=company) | Q(manufacturer_company=company) | Q(id__in=brand_distributor)).select_related('company')
			return queryset
		except ObjectDoesNotExist:
			return Brand.objects.none()

	def filter_queryset(self, qs):
		global company
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(company__icontains=search)

		search = self.request.GET.get('columns[0][search][value]', None)
		if search:
			qs = qs.filter(id__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(name__icontains=search)

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			if search == "Brand I Own":
				qs = qs.filter(company=company)
			if search == "Brand I Sell":
				qs = qs.exclude(company=company)
			print qs

		return qs

	def prepare_results(self, qs):
		global company
		json_data = []
		for item in qs:
			brand_type = "Brand I Sell"
			if company == item.company:
				brand_type = "Brand I Own"

			json_data.append([
				item.id,
				item.name,
				item.image.thumbnail[settings.SMALL_SQR_IMAGE].url,
				brand_type,
			])
		return json_data


class WarehouseDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'company__name', 'name', 'supplier__name', 'salesmen', ]
	order_columns = ['id', 'company__name', 'name', 'supplier__name', 'salesmen', ]
	search_columns = ['id', 'company__name', 'name', 'supplier__name', 'salesmen',  ]

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = Warehouse.objects.filter(company=company).select_related('company').prefetch_related('supplier', 'salesmen')
			return queryset
		except ObjectDoesNotExist:
			return Brand.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(supplier__name__icontains=search)|qs.filter(salesmen__username__icontains=search)

		search = self.request.GET.get('columns[0][search][value]', None)
		if search:
			qs = qs.filter(id__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(company__name__icontains=search)

		search = self.request.GET.get('columns[2][search][value]', None)
		if search:
			qs = qs.filter(name__icontains=search)

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(supplier__name__icontains=search)

		search = self.request.GET.get('columns[4][search][value]', None)
		if search:
			qs = qs.filter(salesmen__username__icontains=search)

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			# suppliers = item.supplier.all().values_list('name', flat=True)
			# suppliers = list(suppliers)
			# suppliers = ", ".join(suppliers)
			suppliers = []
			for supplier in item.supplier.all():
				suppliers.append(supplier.name)
			suppliers = ", ".join(suppliers)

			# users = item.salesmen.all().values_list('username', flat=True)
			# users = list(users)
			# users = ", ".join(users)
			users = []
			for salesmen in item.salesmen.all():
				users.append(salesmen.username)
			users = ", ".join(users)


			json_data.append([
				item.id,
				item.company.name,
				item.name,
				suppliers,
				users,
			])
		return json_data

class OpeningStockDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'warehouse', 'date', 'user', 'remark', 'upload_file', ]
	order_columns = ['id', 'warehouse', 'date', 'user', 'remark', ]
	search_columns = ['id', 'warehouse', 'date', 'user',  'remark', ]

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = OpeningStock.objects.filter(company=company).order_by('-id')
			return queryset
		except ObjectDoesNotExist:
			return OpeningStock.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(warehouse__name__icontains=search)|qs.filter(supplier__name__icontains=search)|qs.filter(salesmen__username__icontains=search)

		search = self.request.GET.get('columns[0][search][value]', None)
		if search:
			qs = qs.filter(id__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(warehouse__name__icontains=search)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(date__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(date__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(date__lte=date[1])

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(user__username__icontains=search)

		search = self.request.GET.get('columns[4][search][value]', None)
		if search:
			qs = qs.filter(remark__icontains=search)

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			upload_file = None
			if item.upload_file:
				upload_file = item.upload_file.url
			username = None
			if item.user:
				username = item.user.username
			warehouse = None
			if item.warehouse:
				warehouse = item.warehouse.name
			json_data.append([
				item.id,
				warehouse,
				str(item.date),
				username,
				item.remark,
				upload_file,
			])
		return json_data


class InventoryAdjustmentDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'warehouse', 'date', 'user', 'remark', 'upload_file', ]
	order_columns = ['id', 'warehouse', 'date', 'user', 'remark', ]
	search_columns = ['id', 'warehouse', 'date', 'user',  'remark', ]

	def get_initial_queryset(self):
		try:
			user = self.request.user
			company = user.companyuser.company

			queryset = InventoryAdjustment.objects.filter(company=company).select_related('user', 'warehouse').order_by('-id')
			return queryset
		except ObjectDoesNotExist:
			return InventoryAdjustment.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(warehouse__name__icontains=search)|qs.filter(supplier__name__icontains=search)|qs.filter(salesmen__username__icontains=search)

		search = self.request.GET.get('columns[0][search][value]', None)
		if search:
			qs = qs.filter(id__icontains=search)

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(warehouse__name__icontains=search)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(date__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(date__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(date__lte=date[1])

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(user__username__icontains=search)

		search = self.request.GET.get('columns[4][search][value]', None)
		if search:
			qs = qs.filter(remark__icontains=search)

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			upload_file = None
			if item.upload_file:
				upload_file = item.upload_file.url
			username = None
			if item.user:
				username = item.user.username
			warehouse = None
			if item.warehouse:
				warehouse = item.warehouse.name
			json_data.append([
				item.id,
				warehouse,
				str(item.date),
				username,
				item.remark,
				upload_file,
			])
		return json_data

class BuyerMeetingDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'user__username', 'start_datetime', 'duration', 'id', 'note']
	order_columns = ['id', 'user__username', 'start_datetime', 'duration', 'id', 'note']
	search_columns = ['id', 'user__username', 'start_datetime', 'duration', 'id', 'note']

	def get_initial_queryset(self):
		queryset = Meeting.objects.all().select_related('buying_company_ref').order_by('-id')

		user = self.request.user

		buying_company_id = self.request.GET.get('buying_company', None)

		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company

					return queryset.filter(company=company, buying_company_ref=buying_company_id)
			except ObjectDoesNotExist:
				return queryset.none()
		return queryset.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(user__username__icontains=search)|qs.filter(duration__icontains=search)|qs.filter(start_datetime__icontains=search)|qs.filter(note__icontains=search)

		name = self.request.GET.get('columns[1][search][value]', None)
		if name:
			qs = qs.filter(user__username__icontains=name)

		time = self.request.GET.get('columns[2][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(start_datetime__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(start_datetime__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(start_datetime__lte=date[1])

		duration = self.request.GET.get('columns[3][search][value]', None)
		if duration:
			qs = qs.filter(duration__icontains=duration)

		note = self.request.GET.get('columns[5][search][value]', None)
		if note:
			qs = qs.filter(note__icontains=note)

		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []

		#start = self.request.GET.get('start', 0)
		#i = int(start)

		for item in qs:
			#i = i+1
			json_data.append([
				item.id,
				item.user.username,
				str(timezone.localtime(item.start_datetime).strftime("%Y-%m-%d : %I:%M%p")),
				str(item.duration).split(".")[0],
				item.salesorder.count(),
				item.note,
				{"start_lat":item.start_lat, "start_long":item.start_long, "end_lat":item.end_lat, "end_long":item.end_long},
			])
		return json_data

class SellerStatisticDatatables(BaseDatatableView, APIView):

	permission_classes = (permissions.IsAdminUser,)

	columns = ['id', 'name', 'wishbook_salesman', 'company_type', 'city', 'phone_number', 'last_login', 'catalogs_uploaded', 'total_catalog_seller', 'total_enabled_catalog', 'last_catalog_upload_date', 'last_catalog_seller_date', 'last_catalog_or_seller_name', 'total_enquiry_received', 'total_enquiry_converted', 'total_enquiry_pending', 'total_enquiry_values', 'handling_time', 'total_order_values', 'total_pending_order_values', 'total_prepaid_order_values', 'total_prepaid_cancelled_order_values', 'avg_dispatch_time', 'enquiry_not_handled', 'total_pending_order', 'prepaid_order_cancellation_rate']
	order_columns = ['id', 'name', 'wishbook_salesman', 'company_type', 'city', 'phone_number', 'last_login', 'catalogs_uploaded', 'total_catalog_seller', 'total_enabled_catalog', 'last_catalog_upload_date', 'last_catalog_seller_date', 'last_catalog_or_seller_name', 'total_enquiry_received', 'total_enquiry_converted', 'total_enquiry_pending', 'total_enquiry_values', 'handling_time', 'total_order_values', 'total_pending_order_values', 'total_prepaid_order_values', 'total_prepaid_cancelled_order_values', 'avg_dispatch_time', 'enquiry_not_handled', 'total_pending_order', 'prepaid_order_cancellation_rate']
	search_columns = ['id', 'name', 'wishbook_salesman', 'company_type', 'city', 'phone_number', 'last_login', 'catalogs_uploaded', 'total_catalog_seller', 'total_enabled_catalog', 'last_catalog_upload_date', 'last_catalog_seller_date', 'last_catalog_or_seller_name', 'total_enquiry_received', 'total_enquiry_converted', 'total_enquiry_pending', 'total_enquiry_values', 'handling_time', 'total_order_values', 'total_pending_order_values', 'total_prepaid_order_values', 'total_prepaid_cancelled_order_values', 'avg_dispatch_time', 'enquiry_not_handled', 'total_pending_order', 'prepaid_order_cancellation_rate']

	def get_initial_queryset(self):
		print "///////// seller statisticz"
		return SellerStatistic.objects.all()#.select_related('company')

	def filter_queryset(self, qs):

		search = self.request.GET.get('columns[1][search][value]', None)
		if search:
			qs = qs.filter(name__icontains=search)

		search = self.request.GET.get('columns[2][search][value]', None)
		if search:
			qs = qs.filter(wishbook_salesman__icontains=search)

		search = self.request.GET.get('columns[3][search][value]', None)
		if search:
			qs = qs.filter(company_type__icontains=search)

		search = self.request.GET.get('columns[4][search][value]', None)
		if search:
			qs = qs.filter(city__icontains=search)

		search = self.request.GET.get('columns[5][search][value]', None)
		if search:
			qs = qs.filter(phone_number__icontains=search)

		time = self.request.GET.get('columns[6][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(last_login__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(last_login__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(last_login__lte=date[1])

		search = self.request.GET.get('columns[7][search][value]', None)
		if search:
			qs = qs.filter(catalogs_uploaded__icontains=search)

		search = self.request.GET.get('columns[8][search][value]', None)
		if search:
			qs = qs.filter(total_catalog_seller__icontains=search)

		search = self.request.GET.get('columns[9][search][value]', None)
		if search:
			qs = qs.filter(total_enabled_catalog__icontains=search)

		time = self.request.GET.get('columns[10][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(last_catalog_upload_date__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(last_catalog_upload_date__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(last_catalog_upload_date__lte=date[1])

		time = self.request.GET.get('columns[11][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(last_catalog_seller_date__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(last_catalog_seller_date__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(last_catalog_seller_date__lte=date[1])

		search = self.request.GET.get('columns[12][search][value]', None)
		if search:
			qs = qs.filter(last_catalog_or_seller_name__icontains=search)

		search = self.request.GET.get('columns[13][search][value]', None)
		if search:
			qs = qs.filter(total_enquiry_received__icontains=search)

		search = self.request.GET.get('columns[14][search][value]', None)
		if search:
			qs = qs.filter(total_enquiry_converted__icontains=search)

		search = self.request.GET.get('columns[15][search][value]', None)
		if search:
			qs = qs.filter(total_enquiry_pending__icontains=search)

		search = self.request.GET.get('columns[16][search][value]', None)
		if search:
			qs = qs.filter(total_enquiry_values__icontains=search)

		search = self.request.GET.get('columns[17][search][value]', None)
		if search:
			qs = qs.filter(handling_time__icontains=search)

		search = self.request.GET.get('columns[18][search][value]', None)
		if search:
			qs = qs.filter(total_order_values__icontains=search)

		search = self.request.GET.get('columns[19][search][value]', None)
		if search:
			qs = qs.filter(total_pending_order_values__icontains=search)

		search = self.request.GET.get('columns[20][search][value]', None)
		if search:
			qs = qs.filter(total_prepaid_order_values__icontains=search)

		search = self.request.GET.get('columns[21][search][value]', None)
		if search:
			qs = qs.filter(total_prepaid_cancelled_order_values__icontains=search)

		search = self.request.GET.get('columns[22][search][value]', None)
		if search:
			qs = qs.filter(avg_dispatch_time__icontains=search)

		search = self.request.GET.get('columns[23][search][value]', None)
		if search:
			qs = qs.filter(enquiry_not_handled__icontains=search)

		search = self.request.GET.get('columns[24][search][value]', None)
		if search:
			qs = qs.filter(total_pending_order__icontains=search)

		search = self.request.GET.get('columns[25][search][value]', None)
		if search:
			qs = qs.filter(prepaid_order_cancellation_rate__icontains=search)


		return qs


	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:

			last_login = item.last_login
			if last_login:
				last_login = str(timezone.localtime(item.last_login).strftime("%Y-%m-%d : %I:%M%p"))

			json_data.append([
				item.id,
				item.name,
				item.wishbook_salesman,
				item.company_type,
				item.city,
				item.phone_number,
				last_login,

				item.catalogs_uploaded,
				item.total_catalog_seller,
				item.total_enabled_catalog,
				item.last_catalog_upload_date,
				item.last_catalog_seller_date,
				item.last_catalog_or_seller_name,

				item.total_enquiry_received,
				item.total_enquiry_converted,
				item.total_enquiry_pending,
				item.total_enquiry_values,
				item.handling_time,

				item.total_order_values,
				item.total_pending_order_values,
				item.total_prepaid_order_values,
				item.total_prepaid_cancelled_order_values,
				item.avg_dispatch_time,

				item.enquiry_not_handled,
				item.total_pending_order,
				item.prepaid_order_cancellation_rate,

				{"company":item.company_id}


			])
		return json_data

class MyEnquiryDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'id', 'catalog__title', 'selling_company__name', 'selling_company__state__state_name', 'selling_company__city__city_name', 'selling_company__phone_number', 'text', 'created', 'item_type', 'item_quantity', 'status']
	order_columns = ['id', 'id', 'catalog__title', 'selling_company__name', 'selling_company__state__state_name', 'selling_company__city__city_name', 'selling_company__phone_number', 'text', 'created', 'item_type', 'item_quantity', 'status']
	search_columns = ['id', 'id', 'catalog__title', 'selling_company__name', 'selling_company__state__state_name', 'selling_company__city__city_name', 'selling_company__phone_number', 'text', 'created', 'item_type', 'item_quantity', 'status']

	def get_initial_queryset(self):
		queryset = CatalogEnquiry.objects.all().select_related('catalog', 'selling_company__address__state', 'selling_company__address__city').order_by('-id')

		user = self.request.user
		company = get_user_company(user)

		if company:
			return queryset.filter(buying_company=company)
		return queryset.none()

	def filter_queryset(self, qs):
		#Main filter

		title = self.request.GET.get('columns[2][search][value]', None)
		if title:
			qs = qs.filter(catalog__title__icontains=title)

		name = self.request.GET.get('columns[3][search][value]', None)
		if name:
			qs = qs.filter(selling_company__name__icontains=name)

		name = self.request.GET.get('columns[4][search][value]', None)
		if name:
			qs = qs.filter(selling_company__state__state_name__icontains=name)

		name = self.request.GET.get('columns[5][search][value]', None)
		if name:
			qs = qs.filter(selling_company__city__city_name__icontains=name)

		name = self.request.GET.get('columns[6][search][value]', None)
		if name:
			qs = qs.filter(selling_company__phone_number__icontains=name)

		text = self.request.GET.get('columns[7][search][value]', None)
		if text:
			qs = qs.filter(text__icontains=text)

		time = self.request.GET.get('columns[8][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created__lte=date[1])

		item_type = self.request.GET.get('columns[9][search][value]', None)
		if item_type:
			qs = qs.filter(item_type__icontains=item_type)

		item_quantity = self.request.GET.get('columns[10][search][value]', None)
		if item_quantity:
			qs = qs.filter(item_quantitye__icontains=item_quantity)


		status = self.request.GET.get('columns[11][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)

		return qs

	def prepare_results(self, qs):
		json_data = []

		for item in qs:
			json_data.append([
				item.id,
				{"applogic_conversation_id":item.applogic_conversation_id, "selling_company_chat_user":item.selling_company.chat_admin_user.username, "catalog_id":item.catalog.id, "selling_company_id":item.selling_company.id, "selling_company_name":item.selling_company.name },
				item.catalog.title,
				item.selling_company.name,
				item.selling_company.address.state.state_name,
				item.selling_company.address.city.city_name,
				item.selling_company.phone_number,
				item.text,
				str(timezone.localtime(item.created).strftime("%Y-%m-%d : %I:%M%p")),
				item.item_type,
				item.item_quantity,
				item.status,
			])
		return json_data

class MyLeadDatatables(BaseDatatableView, APIView):

	permission_classes = (IsCompanyAdministratorOrAdmin,)

	columns = ['id', 'id', 'catalog__title', 'buying_company__name', 'buying_company__state__state_name', 'buying_company__city__city_name', 'buying_company__phone_number', 'text', 'created', 'item_type', 'item_quantity', 'status']
	order_columns = ['id', 'id', 'catalog__title', 'buying_company__name', 'buying_company__state__state_name', 'buying_company__city__city_name', 'buying_company__phone_number', 'text', 'created', 'item_type', 'item_quantity', 'status']
	search_columns = ['id', 'id', 'catalog__title', 'buying_company__name', 'buying_company__state__state_name', 'buying_company__city__city_name', 'buying_company__phone_number', 'text', 'created', 'item_type', 'item_quantity', 'status']

	def get_initial_queryset(self):
		queryset = CatalogEnquiry.objects.all().select_related('catalog', 'buying_company__address__city', 'buying_company__address__state').order_by('-id')

		user = self.request.user
		company = get_user_company(user)

		if company:
			return queryset.filter(selling_company=company)
		return queryset.none()

	def filter_queryset(self, qs):
		#Main filter

		title = self.request.GET.get('columns[2][search][value]', None)
		if title:
			qs = qs.filter(catalog__title__icontains=title)

		name = self.request.GET.get('columns[3][search][value]', None)
		if name:
			qs = qs.filter(buying_company__name__icontains=name)

		name = self.request.GET.get('columns[4][search][value]', None)
		if name:
			qs = qs.filter(buying_company__state__state_name__icontains=name)

		name = self.request.GET.get('columns[5][search][value]', None)
		if name:
			qs = qs.filter(buying_company__city__city_name__icontains=name)

		name = self.request.GET.get('columns[6][search][value]', None)
		if name:
			qs = qs.filter(buying_company__phone_number__icontains=name)

		text = self.request.GET.get('columns[7][search][value]', None)
		if text:
			qs = qs.filter(text__icontains=text)

		time = self.request.GET.get('columns[8][search][value]', None)
		if time:
			date=time.split("~")
			if date[1] != "":
				date[1] = datetime.strptime(date[1], '%Y-%m-%d')
				date[1] = datetime.combine(date[1], datetime.max.time())

			if date[0] != "" and date[1] != "":
				qs = qs.filter(created__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(created__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(created__lte=date[1])

		item_type = self.request.GET.get('columns[9][search][value]', None)
		if item_type:
			qs = qs.filter(item_type__icontains=item_type)

		item_quantity = self.request.GET.get('columns[10][search][value]', None)
		if item_quantity:
			qs = qs.filter(item_quantitye__icontains=item_quantity)


		status = self.request.GET.get('columns[11][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)

		return qs

	def prepare_results(self, qs):
		json_data = []

		for item in qs:
			json_data.append([
				item.id,
				{"applogic_conversation_id":item.applogic_conversation_id, "buying_company_chat_user":item.buying_company.chat_admin_user.username, "catalog_id":item.catalog.id, "buying_company_id":item.buying_company.id, "buying_company_name":item.buying_company.name },
				item.catalog.title,
				item.buying_company.name,
				item.buying_company.address.state.state_name,
				item.buying_company.address.city.city_name,
				item.buying_company.phone_number,
				item.text,
				str(timezone.localtime(item.created).strftime("%Y-%m-%d : %I:%M%p")),
				item.item_type,
				item.item_quantity,
				item.status,
			])
		return json_data
