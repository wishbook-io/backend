import csv
from django.utils.encoding import smart_str
from django.http import HttpResponse
from api.models import *

#from rest_framework.decorators import api_view, permission_classes
#from rest_framework.permissions import IsAuthenticated

# TODO: extrememly redundant. make a generic function to club this whle file into one function

def createCsvUser(request):			#function to export 'User' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="User.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Username', 'EmailAddress', 'FirstName', 'LastName'])
	queryset = User.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.username), str(obj.email), str(obj.first_name), str(obj.last_name),])
	return response

def createCsvChoice(request):			#function to export 'User' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Choice.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'User', 'Name', 'UserList'])
	queryset = Choice.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.user), str(obj.name), str(obj.userlist),])
	return response

def createCsvCompany(request):			#function to export 'Company' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Company.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Name', 'PushDownstream', 'Admin', 'StreetAddress', 'City', 'State', 'PhoneNumber'])
	queryset = Company.objects.all()
	for obj in queryset:
		adminNames = ""
		for adminTitle in obj.admin.all():
			adminNames+=adminTitle.username+", "
		adminNames = adminNames[:-1]
		writer.writerow([str(obj.pk), str(obj.name), str(obj.push_downstream), str(adminNames), str(obj.street_address),  str(obj.city), str(obj.state), str(obj.phone_number),])
	return response

def createCsvBranch(request):			#function to export 'Branch' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Branch.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Company', 'Name', 'StreetAddress', 'City', 'State', 'Pincode', 'PhoneNumber'])
	queryset = Branch.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.company), str(obj.name), str(obj.street_address),  str(obj.city), str(obj.state), str(obj.pincode), str(obj.phone_number),])
	return response

def createCsvCompanyUser(request):			#function to export 'CompanyUser' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="CompanyUser.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Company', 'User', 'RelationshipType'])
	queryset = CompanyUser.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.company), str(obj.user), str(obj.relationship_type),])
	return response	

def createCsvBrand(request):			#function to export 'Brand' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Brand.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'name', 'company'])
	queryset = Brand.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.name), str(obj.company),])
	return response

def createCsvCatalog(request):			#function to export 'Catalog' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Catalog.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Title', 'Brand'])
	queryset = Catalog.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.title), str(obj.brand),])
	return response

def createCsvProduct(request):			#function to export 'Product' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Product.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Title', 'Catalog', 'SKU', 'Fabric', 'Work', 'Price'])
	queryset = Product.objects.all()
	for obj in queryset:
		catalogTitles = ""
		for catalogTitle in obj.catalog.all():
			catalogTitles+=catalogTitle.title+", "
		catalogTitles = catalogTitles[:-1]#.rstrip(',')
		writer.writerow([str(obj.pk), str(obj.title), str(catalogTitles), str(obj.sku), str(obj.fabric), str(obj.work), str(obj.price),])
	return response

def createCsvBuyer(request):			#function to export 'Buyer' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Buyer.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'SelingCompany', 'BuyingCompany'])
	queryset = Buyer.objects.all()
	loginUser = request.user
	try:
		user_company = (loginUser.companyuser.company is not None)
		if user_company:
			company = loginUser.companyuser.company
			queryset = queryset.filter(selling_company=company)
	except ObjectDoesNotExist:
		queryset = Buyer.objects.none()
	
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.selling_company), str(obj.buying_company),])
	return response

def createCsvSalesOrder(request):			#function to export 'SalesOrder' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="SalesOrder.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'User', 'OrderNumber', 'Company', 'TotalRate', 'Time', 'Processing Status', 'Customer Status'])
	queryset = SalesOrder.objects.all()
	for obj in queryset:
		total_rate = obj.total_rate()
		writer.writerow([str(obj.pk), str(obj.user), str(obj.order_number), str(obj.company), str(total_rate), str(obj.time), str(obj.processing_status), str(obj.customer_status),])
	return response

def createCsvSalesOrderItem(request):			#function to export 'SalesOrderItem' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="SalesOrderItem.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Order', 'Product', 'Quantity', 'Rate'])
	queryset = SalesOrderItem.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.sales_order), str(obj.product), str(obj.quantity), str(obj.rate),])
	return response

def createCsvSelection(request):			#function to export 'Selection' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Selection.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'User', 'Name', 'Products'])
	queryset = Selection.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.user), str(obj.name), str(obj.products),])
	return response

def createCsvChannelType(request):			#function to export 'ChannelType' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="ChannelType.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Name', 'CredentialFormat', 'FileFormat'])
	queryset = ChannelType.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.name), str(obj.credential_format), str(obj.file_format),])
	return response

def createCsvChannel(request):			#function to export 'Channel' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Channel.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'ChannelType','Name'])
	queryset = Channel.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.channel_type), str(obj.name),])
	return response

def createCsvPush(request):			#function to export 'Push' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Push.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Time', 'PushType', 'TargetType', 'TargetCity', 'TargetState', 'PushDownstream', 'Status'])
	queryset = Push.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.time), str(obj.push_type), str(obj.target_city), str(obj.target_state), str(obj.push_downstream), str(obj.status),])
	return response

def createCsvExport(request):			#function to export 'Export' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Export.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Channel', 'time'])
	queryset = Export.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.channel), str(obj.time),])
	return response

def createCsvInvite(request):			#function to export 'Invite' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="Invite.csv"'
	writer = csv.writer(response)
	writer.writerow(['id', 'Company', 'RelationshipType', 'Date', 'Time', 'User'])
	queryset = Invite.objects.all()
	for obj in queryset:
		writer.writerow([str(obj.pk), str(obj.company), str(obj.relationship_type), str(obj.date), str(obj.time), str(obj.user),])
	return response

def createCsvSalesPerson(request):			#function to export 'Product' in 'CSV' format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="SalesPerson.csv"'
	writer = csv.writer(response)
	writer.writerow(['Username', 'First name', 'Last name', 'Email address', 'Alternate email', 'Company name', 'Phone number'])
	queryset = User.objects.filter(groups__name="salesperson")
	user = request.user
	try:
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			companyUserIds = CompanyUser.objects.filter(company=company).values_list('user', flat=True).distinct()
			queryset = queryset.filter(id__in=companyUserIds)
	except ObjectDoesNotExist:
		queryset = User.objects.none()
		
	for obj in queryset:
		writer.writerow([str(obj.username), str(obj.first_name), str(obj.last_name), str(obj.email), str(obj.userprofile.alternate_email), str(obj.userprofile.company_name), str(obj.userprofile.phone_number),])
	return response
