from django_datatables_view.base_datatable_view import BaseDatatableView
from django.core import serializers
from django.shortcuts import render
from django.http import JsonResponse
# from datetime import datetime
from django.http import HttpResponse
from api.models import *
from django.contrib.auth.models import User

class UserDatatable(BaseDatatableView):		#UserDatatable-view for handling of sorting, filtering and creating JSON output

	model = User
	columns = ['user_id','name','email']
	order_columns = ['user_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(user_id_icontains=part)|Q(name_icontains=part)|Q(email_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class User_NumberDatatable(BaseDatatableView):	#User_NumberDatatable-view for handling of sorting, filtering and creating JSON output

	model = User_Number
	columns = ['user_id.user_id','phone_number']
	order_columns = ['user_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(user_id_icontains=part)|Q(phone_number_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class CompanyDatatable(BaseDatatableView):	#CompanyDatatable-view for handling of sorting, filtering and creating JSON output

	model = Company
	columns = ['name', 'street_address', 'city', 'state', 'pincode', 'push_downstream','admin_user_id.user_id']
	order_columns = ['name',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(name_icontains=part)|Q(street_address_icontains=part)|Q(city_icontains=part)|Q(state_icontains=part)|Q(pincode_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Company_UserDatatable(BaseDatatableView):	#Company_UserDatatable-view for handling of sorting, filtering and creating JSON output

	model = Company_User
	columns = ['user_id.user_id','company_id.id','relationship_type']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(user_id_icontains=part)|Q(company_id_icontains=part)|Q(relationship_type_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class ChoiceDatatable(BaseDatatableView):	#ChoiceListDatatable-view for handling of sorting, filtering and creating JSON output

	model = Choice
	columns = ['name',]
	order_columns = ['name',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(name_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

# class ChoiceList_UserDatatable(BaseDatatableView): #ChoiceList_UserDatatable-view for handling of sorting, filtering and creating JSON output

# 	model = ChoiceList_User
# 	columns = ['list_id.id','user_id.user_id']
# 	order_columns = ['list_id',","]
# 	max_display_length = 5

# 	def filter_queryset(self, qs):

# 		search = self.request.GET.get(u'search[value]', None)
# 		if search:
# 			search_part = filter_search.split(' ')
# 			qs_params = None
# 			for part in search_part:
# 				q =Q(list_id_icontains=part)|Q(user_id_icontains=part)
# 				qs_params = qs_params | q if qs_params else q
# 			qs = qs.filter(qs_params)
# 		return qs

class BuyerDatatable(BaseDatatableView):	#Buyer-view for handling of sorting, filtering and creating JSON output

	model = Buyer
	columns = ['selling_company_id.id','buying_company_id.id']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(selling_company_id_icontains=part)|Q(buying_company_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class BrandDatatable(BaseDatatableView):	#BrandDatatable-view for handling of sorting, filtering and creating JSON output

	model = Brand
	columns = ['name','owning_company_id.id']
	order_columns = ['name',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(name_icontains=part)|Q(owning_company_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class CatalogDatatable(BaseDatatableView):	#CatalogDatatable-view for handling of sorting, filtering and creating JSON output

	model = Catalog
	columns = ['title','brand_id.id']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(brand_id_icontains=part)|Q(title_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Sales_OrderDatatable(BaseDatatableView):	#Sales_OrderDatatable-view for handling of sorting, filtering and creating JSON output

	model = Sales_Order
	columns = ['order_number','company_id.id','total_rate', 'date', 'time', 'status']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(company_id_icontains=part)|Q(date_icontains=part)|Q(status_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class ProductDatatable(BaseDatatableView):	#ProductDatatable-view for handling of sorting, filtering and creating JSON output

	model = Product
	columns = ['catalog_id.id', 'sku', 'work', 'fabric', 'title','brand_id.id']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(catalog_id_icontains=part)|Q(total_rate_icontains=part)|Q(sku_icontains=part)|Q(title_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Sales_Order_ItemDatatable(BaseDatatableView):	#Sales_Order_ItemDatatable-view for handling of sorting, filtering and creating JSON output

	model = Sales_Order_Item
	columns = ['order_id.id','product_id.id','name', 'qty', 'rate']
	order_columns = ['order_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(order_id_icontains=part)|Q(product_id_icontains=part)|Q(name_rate_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class SelectionDatatable(BaseDatatableView):	#SelectionDatatable-view for handling of sorting, filtering and creating JSON output

	model = Selection
	columns = ['user_id.user_id', 'selection_name']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(selection_name_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

# class Selection_ProductDatatable(BaseDatatableView):	#Selection_ProductDatatable-view for handling of sorting, filtering and creating JSON output

# 	model = Selection_Product
# 	columns = ['selection_id.id','id']
# 	order_columns = ['id',","]
# 	max_display_length = 5

# 	def filter_queryset(self, qs):

# 		search = self.request.GET.get(u'search[value]', None)
# 		if search:
# 			search_part = filter_search.split(' ')
# 			qs_params = None
# 			for part in search_part:
# 				q =Q(selection_id_icontains=part)|Q(product_id_icontains=part)
# 				qs_params = qs_params | q if qs_params else q
# 			qs = qs.filter(qs_params)
# 		return qs

class Channel_TypeDatatable(BaseDatatableView):		#Channel_TypeDatatable-view for handling of sorting, filtering and creating JSON output

	model = Channel_Type
	columns = ['name', 'credential_format', 'file_format']
	order_columns = ['name',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(name_icontains=part)|Q(file_format_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class ChannelDatatable(BaseDatatableView):	#ChannelDatatable-view for handling of sorting, filtering and creating JSON output

	model = Channel
	columns = ['Channel_Type_id.id', 'name']
	order_columns = ['name',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(name_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class PushDatatable(BaseDatatableView):	#PushDatatable-view for handling of sorting, filtering and creating JSON output

	model = Push
	columns = ['date', 'time', 'typ', 'target_type', 'target_state_id', 'target_city_id']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(date_id_icontains=part)|Q(typ_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Push_UserDatatable(BaseDatatableView):	#Push_UserDatatable-view for handling of sorting, filtering and creating JSON output

	model = Push_User
	columns = ['push_id.id','user_id.user_id']
	order_columns = ['push_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(push_id_icontains=part)|Q(user_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Push_ResultDatatable(BaseDatatableView):	#Push_ResultDatatable-view for handling of sorting, filtering and creating JSON output

	model = Push_Result
	columns = ['push_id.id','num_people_targeted', 'num_app_users', 'num_product_views']
	order_columns = ['push_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(push_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Push_CatalogDatatable(BaseDatatableView):	  #Push_CatalogDatatable-view for handling of sorting, filtering and creating JSON output

	model = Push_Catalog
	columns = ['push_id.id','catalog_id.id']
	order_columns = ['push_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(push_id_icontains=part)|Q(catalog_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs


class Push_ProductDatatable(BaseDatatableView):	#Push_ProductDatatable-view for handling of sorting, filtering and creating JSON output

	model = Push_Product
	columns = ['push_id.id','product_id.id']
	order_columns = ['push_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(push_id_icontains=part)|Q(product_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class ExportDatatable(BaseDatatableView):	#ExportDatatable-view for handling of sorting, filtering and creating JSON output

	model = Export
	columns = ['channel_id.id','date', 'time']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(date_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Export_ResultDatatable(BaseDatatableView):	#Export_ResultDatatable-view for handling of sorting, filtering and creating JSON output

	model = Export_Result
	columns = ['export_id.id','file_path']
	order_columns = ['export_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(export_id_icontains=part)|Q(filepath_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Export_CatalogDatatable(BaseDatatableView):	#Export_CatalogDatatable-view for handling of sorting, filtering and creating JSON output

	model = Export_Catalog
	columns = ['export_id.id','catalog_id.id']
	order_columns = ['export_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(export_id_icontains=part)|Q(catalog_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class Export_ProductDatatable(BaseDatatableView):	#Export_ProductDatatable-view for handling of sorting, filtering and creating JSON output

	model = Export_Product
	columns = ['export_id.id','product_id.id']
	order_columns = ['export_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(export_id_icontains=part)|Q(product_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class InviteDatatable(BaseDatatableView):	#InviteDatatable-view for handling of sorting, filtering and creating JSON output

	model = Invite
	columns = ['company_id.id', 'relationship_type', 'date', 'time', 'user_id.user_id']
	order_columns = ['id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(company_id_icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

class InviteeDatatable(BaseDatatableView):	#InviteeDatatable-view for handling of sorting, filtering and creating JSON output

	model = Invitee
	columns = ['invite_id.id','invitee_number', 'invitee_company.id', 'invitee_name', 'is_converted']
	order_columns = ['export_id',","]
	max_display_length = 5

	def filter_queryset(self, qs):

		search = self.request.GET.get(u'search[value]', None)
		if search:
			search_part = filter_search.split(' ')
			qs_params = None
			for part in search_part:
				q =Q(invite_id_icontains=part)|Q(invitee_number__icontains=part)|Q(invitee_company__icontains=part)|Q(invitee_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		return qs

