from api.models import *
#from api.serializers import *
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q

from rest_framework import permissions
from rest_framework.views import APIView

from api.permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin, IsCompanyOrAdmin, IsCompanyAdministratorOrAdmin, IsOwner, HasGroupOrPermission

from django.db.models import Sum
import datetime

from django.core.exceptions import ObjectDoesNotExist

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
		return Brand.objects.all()

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
	
	columns = ['id','name', 'thumbnail_url', 'brand', 'phone_number', 'website', 'invoice_credit', 'status'] #Table columns
	order_columns = ['id','name', 'id', 'brand', 'phone_number', 'website', 'id', 'status']
	search_columns = ['id','name', 'phone_number', 'website', 'status']

	def get_initial_queryset(self):
		#Initial Queryset
		return Company.objects.all()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(name__icontains=search)|qs.filter(phone_number__icontains=search)|qs.filter(website__icontains=search)|qs.filter(status__icontains=search)
			
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
			
		phone_number = self.request.GET.get('columns[5][search][value]', None)
		if phone_number:
			phone_number_parts = phone_number.split(' ')
			qs_params = None
			for part in phone_number_parts:
				q = Q(phone_number__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
			
		website = self.request.GET.get('columns[6][search][value]', None)
		if website:
			website_parts = website.split(' ')
			qs_params = None
			for part in website_parts:
				q = Q(website__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
			
		status = self.request.GET.get('columns[7][search][value]', None)
		if status:
			qs = qs.filter(status__contains=status)
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			brandObj = Brand.objects.filter(company=item.id).values_list('name', flat=True)
			brands = ', '.join(brandObj)
			
			invoice_credit = InvoiceCredit.objects.filter(company=item.id, expire_date__gte=datetime.date.today()).aggregate(Sum('credit_amount')).get('credit_amount__sum', 0)
			if invoice_credit is None:
				invoice_credit = 0
			
			json_data.append([
				'',
				item.id,
				item.name,
				str(item.thumbnail_url()),
				brands,
				item.phone_number,
				item.website,
				invoice_credit,
				item.status
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

class CatalogDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id','title', 'thumbnail', 'brand', 'category'] #Table columns
	order_columns = ['id','title', 'id', 'brand', 'id']
	search_columns = ['title', 'brand', 'category']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Catalog.objects.all()
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(company=company)
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
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			
			pushCatalogObj = Push_Catalog.objects.filter(catalog=item.id).values_list('push', flat=True)
			pushIds = str(pushCatalogObj).strip('[]')
			
			categoryObj = item.category.all().values_list('category_name', flat=True)
			categories = ', '.join(categoryObj)
			
			json_data.append([
				item.id,
				item.title,
				item.thumbnail.thumbnail['150x210'].url, #item.thumbnail.url,
				item.brand.name,
				categories,
				pushIds
			])
		return json_data


class ReceivedCatalogDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id','title', 'thumbnail', 'brand', 'category'] #Table columns
	order_columns = ['id','title', 'id', 'brand', 'category']
	search_columns = ['title', 'brand', 'category']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Catalog.objects.all()
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					
					sellingCompanyObj = Buyer.objects.filter(buying_company=company, status="approved").values_list('selling_company', flat=True).distinct()
					#if sellingCompanyObj:
					pushUserCatalogId = Push_User.objects.filter(user=user, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('catalog').values_list('catalog', flat=True).distinct()
					print pushUserCatalogId
					return queryset.filter(id__in=pushUserCatalogId).order_by('-id')
					
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
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			
			pushCatalogObj = Push_Catalog.objects.filter(catalog=item.id).values_list('push', flat=True)
			pushIds = str(pushCatalogObj).strip('[]')
			
			categoryObj = item.category.all().values_list('category_name', flat=True)
			categories = ', '.join(categoryObj)
			
			json_data.append([
				item.id,
				item.title,
				item.thumbnail.thumbnail['150x210'].url, #item.thumbnail.url,
				item.brand.name,
				categories,
				pushIds
			])
		return json_data


class SelectionDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id','name', 'products.title'] #Table columns
	order_columns = ['id','name', 'products.title']
	search_columns = ['id','name', 'products.title']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Selection.objects.all()
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
		return queryset.filter(user=user)

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
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			productObj = item.products.all().values_list('title', flat=True)
			products = ', '.join(productObj)
			
			json_data.append([
				item.id,
				item.name,
				products,
				str(item.image())
				#str(item.image.thumbnail['150x210'].url)
			])
		return json_data


class ProductDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id', 'image', 'sku', 'title', 'price', 'catalog.title'] #Table columns
	order_columns = ['id', 'id', 'sku', 'title', 'price', 'catalog.title']
	search_columns = ['id', 'sku', 'title', 'price', 'catalog.title']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Product.objects.all()
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
		try:
			user_company = (user.companyuser.company is not None)
			
			if user_company:
				company = user.companyuser.company
				return queryset.filter(catalog__company=company).distinct()
		except ObjectDoesNotExist:
			return Product.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(title__icontains=search)|qs.filter(sku__icontains=search)|qs.filter(price__icontains=search)|qs.filter(catalog__title__icontains=search)
		
		sku = self.request.GET.get('columns[2][search][value]', None)
		if sku:
			qs = qs.filter(sku__icontains=sku)
			
		title = self.request.GET.get('columns[3][search][value]', None)
		if title:
			title_parts = title.split(' ')
			qs_params = None
			for part in title_parts:
				q = Q(title__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
			
		price = self.request.GET.get('columns[4][search][value]', None)
		if price:
			qs = qs.filter(price__icontains=price)
		
		catalog = self.request.GET.get('columns[5][search][value]', None)
		if catalog:
			qs = qs.filter(catalog__title__icontains=catalog)
			
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			catalogObj = item.catalog.all().values_list('title', flat=True)
			catalogs = ', '.join(catalogObj)
			
			json_data.append([
				item.id,
				str(item.image.thumbnail['150x210'].url),
				item.sku,
				item.title,
				item.price,				
				catalogs,
				
			])
		return json_data


class BuyerDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id', 'buying_company.name', 'buying_company.state.state_name', 'buying_company.city.city_name', 'buying_company.category.category_name',  'buying_company.phone_number', 'group_type.name', 'status', 'buying_company.thumbnail'] #Table columns
	order_columns = ['id', 'buying_company.name', 'buying_company.state.state_name', 'buying_company.city.city_name', 'buying_company.category.category_name', 'buying_company.phone_number', 'group_type.name', 'status']
	#search_columns = ['id', 'buying_company.name', 'buying_company.street_address']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Buyer.objects.all()
		
		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return Buyer.objects.filter(selling_company=company)
		except ObjectDoesNotExist:
			return Buyer.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(buying_company__name__icontains=search)|qs.filter(buying_company__state__state_name__icontains=search)|qs.filter(buying_company__city__city_name__icontains=search)|qs.filter(buying_company__phone_number__icontains=search)|qs.filter(group_type__name__icontains=search)|qs.filter(status__icontains=search)|qs.filter(buying_company__category__category_name__icontains=search)
			
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
			
		categories = self.request.GET.get('columns[4][search][value]', None)
		if categories:
			categories_parts = categories.split(' ')
			qs_params = None
			for part in categories_parts:
				q = Q(buying_company__category__category_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
			
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
			if item.buying_company is None:
				json_data.append([item.id,item.invitee.invitee_name,'','','',item.invitee.invitee_number,item.group_type.name,item.status.replace('_',' '),''])
			else:
				categoryObj = item.buying_company.category.all().values_list('category_name', flat=True)
				categories = ', '.join(categoryObj)
				image = ''
				if item.buying_company.thumbnail:
					image = item.buying_company.thumbnail.url
				
				json_data.append([
					item.id,
					item.buying_company.name,
					#item.buying_company.street_address,
					item.buying_company.state.state_name,
					item.buying_company.city.city_name,
					#item.buying_company.pincode,
					categories,
					item.buying_company.phone_number,
					item.group_type.name,
					item.status.replace('_',' '),
					image
				])
		return json_data

class SellerDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id', 'selling_company.name', 'selling_company.state.state_name', 'selling_company.city.city_name', 'selling_company.category.category_name', 'selling_company.phone_number', 'group_type.name', 'status', 'selling_company.thumbnail'] #Table columns
	order_columns = ['id', 'selling_company.name', 'selling_company.state.state_name', 'selling_company.city.city_name', 'selling_company.category.category_name', 'selling_company.phone_number', 'group_type.name', 'status']
	#search_columns = ['id', 'selling_company.name', 'selling_company.street_address']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Buyer.objects.all()
		
		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return Buyer.objects.filter(buying_company=company)
		except ObjectDoesNotExist:
			return Buyer.objects.none()

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(selling_company__name__icontains=search)|qs.filter(selling_company__state__state_name__icontains=search)|qs.filter(selling_company__city__city_name__icontains=search)|qs.filter(selling_company__phone_number__icontains=search)|qs.filter(group_type__name__icontains=search)|qs.filter(status__icontains=search)|qs.filter(selling_company__category__category_name__icontains=search)
		
		company_name = self.request.GET.get('columns[1][search][value]', None)
		if company_name:
			qs = qs.filter(Q(selling_company__name__icontains=company_name) | Q(invitee__invitee_name__icontains=company_name))
		
		state_name = self.request.GET.get('columns[2][search][value]', None)
		if state_name:
			qs = qs.filter(selling_company__state__state_name__icontains=state_name)
		
		city_name = self.request.GET.get('columns[3][search][value]', None)
		if city_name:
			qs = qs.filter(selling_company__city__city_name__icontains=city_name)
			
		categories = self.request.GET.get('columns[4][search][value]', None)
		if categories:
			categories_parts = categories.split(' ')
			qs_params = None
			for part in categories_parts:
				q = Q(selling_company__category__category_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
			
		phone_number = self.request.GET.get('columns[5][search][value]', None)
		if phone_number:
			qs = qs.filter(Q(selling_company__phone_number__icontains=phone_number) | Q(invitee__invitee_number__icontains=phone_number))
			
		group_type = self.request.GET.get('columns[6][search][value]', None)
		if group_type:
			qs = qs.filter(group_type__name__icontains=group_type)
			
		status = self.request.GET.get('columns[7][search][value]', None)
		if status:
			qs = qs.filter(status__icontains=status)
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			if item.selling_company is None:
				json_data.append([item.id,item.invitee.invitee_name,'','','',item.invitee.invitee_number,item.group_type.name,item.status.replace('_',' '),''])
			else:
				categoryObj = item.selling_company.category.all().values_list('category_name', flat=True)
				categories = ', '.join(categoryObj)
				image = ''
				if item.selling_company.thumbnail:
					image = item.selling_company.thumbnail.url
					
				json_data.append([
					item.id,
					item.selling_company.name,
					item.selling_company.state.state_name,
					item.selling_company.city.city_name,
					categories,
					item.selling_company.phone_number,
					item.group_type.name,
					item.status.replace('_',' '),
					image
				])
		return json_data

class SegmentationDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id','segmentation_name', 'group_type', 'city', 'category', 'active_buyers','last_generated','pushes'] #Table columns
	order_columns = ['id','segmentation_name', 'id', 'id', 'id', 'id', 'last_generated','id']
	search_columns = ['id','segmentation_name', 'group_type', 'city', 'category', 'last_generated']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = BuyerSegmentation.objects.all()
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
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
			qs = qs.filter(group_type__name=group_type)
			
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
		
		last_generated = self.request.GET.get('columns[6][search][value]', None)
		if last_generated:
			date=last_generated.split("~")
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
			
			json_data.append([
				#'',
				item.id,
				item.segmentation_name,
				group_type,
				cities,#,.lower(),
				categories,
				str(item.active_buyers()),
				item.last_generated,
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
		if user.is_staff:
			return queryset
		
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
	
	columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number'] #Table columns
	order_columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number']
	search_columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number']

	def get_initial_queryset(self):
		user = self.request.user
		
		#Initial Queryset
		queryset = User.objects.all()#filter(groups__name="salesperson", id=user.id)
		
		#If User is Administartor
		if user.groups.filter(name="administrator").exists():		
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					companyUserIds = CompanyUser.objects.filter(company=company).values_list('user', flat=True).distinct()
					return User.objects.filter(groups__name="salesperson", id__in=companyUserIds)
			except ObjectDoesNotExist:
				return User.objects.none()
		else:
			return queryset.filter(id=user.id)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(username__icontains=search)|qs.filter(first_name__icontains=search)|qs.filter(last_name__icontains=search)|qs.filter(email__icontains=search)|qs.filter(userprofile__phone_number__icontains=search)
		
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
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			
			json_data.append([
				item.id,
				item.username,
				item.first_name,
				item.last_name,
				item.email,
				item.userprofile.phone_number,
				item.is_active
			])
		return json_data


class AdminisratorDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number'] #Table columns
	order_columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number']
	search_columns = ['id', 'username', 'first_name', 'last_name', 'email', 'userprofile.phone_number']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = User.objects.filter(groups__name="administrator")
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
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
			qs = qs.filter(id__icontains=search)|qs.filter(username__icontains=search)|qs.filter(first_name__icontains=search)|qs.filter(last_name__icontains=search)|qs.filter(email__icontains=search)|qs.filter(userprofile__phone_number__icontains=search)
		
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
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			
			json_data.append([
				item.id,
				item.username,
				item.first_name,
				item.last_name,
				item.email,
				item.userprofile.phone_number,
				item.is_active
			])
		return json_data


class PushDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id', 'catalog', 'selection', 'message', 'time', 'status', 'buyer_segmentation.segmentation_name', 'total_users', 'total_viewed'] #Table columns
	order_columns = ['id', 'id', 'id', 'message', 'time', 'status', 'buyer_segmentation.segmentation_name', 'id', 'id']
	search_columns = ['id', 'message', 'time', 'status', 'buyer_segmentation.segmentation_name']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = Push.objects.all()
		queryset = queryset.filter(to_show="yes")
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
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
			qs = qs.filter(id__icontains=search)|qs.filter(time__icontains=search)|qs.filter(status__icontains=search)|qs.filter(message__icontains=search)|qs.filter(buyer_segmentation__segmentation_name__icontains=search)
		
		message = self.request.GET.get('columns[3][search][value]', None)
		if message:
			message_parts = message.split(' ')
			qs_params = None
			for part in message_parts:
				q = Q(message__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
			
		time = self.request.GET.get('columns[4][search][value]', None)
		if time:
			date=time.split("~")
			if date[0] != "" and date[1] != "":
				qs = qs.filter(time__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(time__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(time__lte=date[1])
			
		status = self.request.GET.get('columns[5][search][value]', None)
		if status:
			qs = qs.filter(status=status)
						
		segmentation_name = self.request.GET.get('columns[6][search][value]', None)
		if segmentation_name:
			segmentation_name_parts = segmentation_name.split(' ')
			qs_params = None
			for part in segmentation_name_parts:
				q = Q(buyer_segmentation__segmentation_name__icontains=part)
				qs_params = qs_params | q if qs_params else q
			qs = qs.filter(qs_params)
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
						
			'''pushCatalogObj = Push_Catalog.objects.filter(push=item.id).values_list('catalog__title', flat=True)
			pushCatalogs = ', '.join(pushCatalogObj)#str(pushCatalogObj).strip('[]')'''
			
			pushUserCatalogId = Push_User.objects.filter(push=item.id).exclude(catalog__isnull=True).order_by('catalog').values_list('catalog__title', flat=True).distinct()
			print pushUserCatalogId
			pushCatalogs = ', '.join(pushUserCatalogId)
					
			
			'''pushSelectionObj = Push_Selection.objects.filter(push=item.id).values_list('selection__name', flat=True)
			pushSelections = ', '.join(pushSelectionObj)#str(pushSelectionObj).strip('[]')'''
			
			pushUserSelectionId = Push_User.objects.filter(push=item.id).exclude(selection__isnull=True).order_by('selection').values_list('selection__name', flat=True).distinct()
			print pushUserSelectionId
			pushSelections = ', '.join(pushUserSelectionId)
			
			json_data.append([
				item.id,
				pushCatalogs,
				pushSelections,
				item.message,
				item.time,
				item.status,
				item.buyer_segmentation.segmentation_name,
				#item.push_type,
				item.total_users(),
				item.total_viewed(),
			])
		return json_data


class SalesOrderDatatables(BaseDatatableView, APIView):
	
	permission_classes = (IsCompanyAdministratorOrAdmin,)
	
	columns = ['id', 'order_number', 'time', 'user', 'items', 'total_rate', 'customer_status', 'processing_status'] #Table columns
	order_columns = ['id', 'order_number', 'time', 'user', 'items', 'items', 'customer_status', 'processing_status']
	search_columns = ['order_number', 'time', 'user', 'items', 'total_rate', 'customer_status', 'processing_status']

	def get_initial_queryset(self):
		#Initial Queryset
		queryset = SalesOrder.objects.all()
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
		#If User is Administartor
		if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(seller_company=company)#(user__companyuser__company=company)
			except ObjectDoesNotExist:
				return SalesOrder.objects.none()
		else:
			return queryset.filter(user=user)

	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(id__icontains=search)|qs.filter(order_number__icontains=search)|qs.filter(date__icontains=search)|qs.filter(time__icontains=search)|qs.filter(processing_status__icontains=search)|qs.filter(customer_status__icontains=search)|qs.filter(user__username__icontains=search)
			
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
			if date[0] != "" and date[1] != "":
				qs = qs.filter(time__range=[date[0],date[1]])
			elif date[0] != "":
				qs = qs.filter(time__gte=date[0])
			elif date[1] != "":
				qs = qs.filter(time__lte=date[1])
		
		user = self.request.GET.get('columns[3][search][value]', None)
		if user:
			qs = qs.filter(user__username__icontains=user)
						
		customer_status = self.request.GET.get('columns[6][search][value]', None)
		if customer_status:
			qs = qs.filter(customer_status=customer_status)
		
		processing_status = self.request.GET.get('columns[7][search][value]', None)
		if processing_status:
			qs = qs.filter(processing_status=processing_status)
		
		return qs

	def prepare_results(self, qs):
		#JSON array data
		json_data = []
		for item in qs:
			
			salesOrderItemObj = SalesOrderItem.objects.filter(sales_order=item.id).values_list('product__title', flat=True)
			salesOrderItems = ', '.join(salesOrderItemObj)
			
			noOfItemObj = SalesOrderItem.objects.filter(sales_order=item.id).count()
			
			json_data.append([
				item.id,
				item.order_number,
				item.time,
				item.user.username,
				item.total_item(),
				item.total_rate(),
				item.customer_status,
				item.processing_status,
			])
		return json_data
