import csv
from django.contrib.auth.models import User, Group
from api.models import *
from api.serializers import *
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.http import HttpResponse
from django.template import loader
from exporthelpers import *


import os
import webbrowser
#import time
#from datetime import date, datetime, timedelta
from datetime import datetime, date, time, timedelta
import httplib2
import gdata
from gdata.photos.service import PhotosService
import gdata.media
import gdata.geo
import gdata.gauth
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

#create, update and delete to authenticated user
#from rest_framework import permissions
from api.permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsOwnerOrAdmin, IsCompanyOrAdmin, IsCompanyAdministratorOrAdmin, IsOwner, HasGroupOrPermission, IsCompanyAdministratorOrAdminOrReadOnly #owner update or delete


#from rest_framework.response import Response
import re
from django.db.models import Q

from django.core.exceptions import ObjectDoesNotExist

import json

from django_datatables_view.base_datatable_view import BaseDatatableView

from django.http import HttpResponseBadRequest

#import random

#from registration.backends.default.views import RegistrationView


@permission_classes((IsCompanyAdministratorOrAdmin,))
def OAuth2Login(email):
    scope='https://picasaweb.google.com/data/'
    user_agent='djangoserver'
    
    configdir = os.path.expanduser('picasa_secrets/')
    client_secrets = os.path.join(configdir, 'client_secret.json')
    credential_store = os.path.join(configdir, 'credentials.dat')  

    storage = Storage(credential_store)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(client_secrets, scope=scope, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        uri = flow.step1_get_authorize_url()
        webbrowser.open(uri)
        code = raw_input('Enter the authentication code: ').strip()
        credentials = flow.step2_exchange(code)

    if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
        http = httplib2.Http()
        http = credentials.authorize(http)
        credentials.refresh(http)

    storage.put(credentials)

    gd_client = gdata.photos.service.PhotosService(source=user_agent,
                                                   email=email,
                                                   additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})

    return gd_client


@permission_classes((IsCompanyAdministratorOrAdmin,))
def picasaImport(request):  
	configdir = os.path.expanduser('~/b2b/picasa_secrets/')
	client_secrets = os.path.join(configdir, 'client_secret.json')
	credential_store = os.path.join(configdir, 'credentials.dat')   
	
	gd_client =	OAuth2Login('tech@trivenisarees.com')
	
	username = 'tech@trivenisarees.com'
    #albums = gd_client.GetUserFeed(user=username)
	photos = gd_client.SearchUserPhotos('picasa',user=username, limit='10')
	
	for photo in photos.entry:
		print 'Community photo title:', photo.title.text,photo.GetHtmlLink().href
	#for album in albums.entry:
		#print 'title: %s, %s, number of photos: %s, id: %s' % (album.GetHtmlLink().href,album.title.text,album.numphotos.text, album.gphoto_id.text)
	return HttpResponse('Done')

def findOrCreateAlbum(gd_client, title):
    delay = 1
    while True:
        try:
            album = findAlbum(gd_client, title)
            if not album:
                album = createAlbum(gd_client, title,'private')
            return album
        except gdata.photos.service.GooglePhotosException as e:
            print("caught exception " + str(e))
            print("sleeping for " + str(delay) + " seconds")
            time.sleep(delay)
            delay = delay * 2

def findAlbum(gd_client, title):
    albums = gd_client.GetUserFeed()
    for album in albums.entry:
        if album.title.text == title:
            return album
    return None
    
def createAlbum(gd_client, title, accessSpecifier):
    print("Creating album " + title)
    # public, private, protected. private == "anyone with link"
    album = gd_client.InsertAlbum(title=title, summary='', access=accessSpecifier)
    return album
               
def postPhoto(gd_client, album, filename, photoname):
    album_url = '/data/feed/api/user/%s/albumid/%s' % (gd_client.email, album.gphoto_id.text)
    photo = gd_client.InsertPhotoSimple(album_url, photoname,
            photoname, filename, content_type='image/jpeg')
    return photo

def postPhotoToAlbum(gd_client, albumtitle, filename, photoname):
    album = findOrCreateAlbum(gd_client, albumtitle)
    photo = postPhoto(gd_client, album, filename, photoname)
    return photo

@api_view(['POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVProduct(request):
	f = request.FILES['ProductCSV']
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	try:
		flag = True
		for line in f:
			if(flag==True):
				flag = False
				continue
			line =  line[:-1].split(',')
			#print line
			fields = {}
			for k,v in columns.iteritems():
				fields[k] = line[v]
			
			del fields['catalog']
			
			catalogs = line[columns['catalog']].split('.')
			
			catalogCompany = Catalog.objects.filter(id__in=catalogs).order_by('company').values_list('company', flat=True).distinct()
			
			loginUser = request.user
			user_company = (loginUser.companyuser.company is not None)
			if user_company:
				company = loginUser.companyuser.company
				
				if len(catalogCompany) == 1 and catalogCompany[0] == company.id:
					product = Product.objects.create(**fields)
					product.catalog.add(*catalogs)
				else:
					return Response("Wrong Catalog")
				
					
	except Exception as e:
		return HttpResponse(e)
	f.close()
	return HttpResponse('Succesfully Added into Product')

@api_view(['POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVCatalog(request):
	f = request.FILES['CatalogCSV']
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	flag = True
	try:
		for line in f:
			if (flag==True):
				flag = False
				continue
			line =  line[:-1].split(',')
			fields = {}
			for k,v in columns.iteritems():
				fields[k] = line[v]
			fields['brand'] = Brand.objects.get(pk=line[columns['brand']])
			#fields['category'] = Category.objects.get(pk=line[columns['category']])
			del fields['category']
			print "in catelog import"
			categories = line[columns['category']].split('.')
			categoryObj = Category.objects.filter(id__in=categories).order_by('id').values_list('id', flat=True).distinct()
			
			loginUser = request.user
			user_company = (loginUser.companyuser.company is not None)
			if user_company:
				company = loginUser.companyuser.company
				fields['company'] = company
				Catalog.objects.create(**fields)
				print Catalog
				Catalog.category = categoryObj
	except Exception as e:
		return HttpResponse('Check CSV File')
	f.close()
	return HttpResponse('Succesfully Added into Catalog')


def importCSVCompany(request):
	f = request.FILES['CompanyCSV']
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	try:
		flag = True
		for line in f:
			if(flag==True):
				flag = False
				continue
			line =  line[:-1].split(',')
			#print line
			fields = {}
			for k,v in columns.iteritems():
				fields[k] = line[v]
			
			del fields['category']
			
			fields['city'] = City.objects.get(pk=line[columns['city']])
			fields['state'] = State.objects.get(pk=line[columns['state']])
			company = Company.objects.create(**fields)
				
			categorys = line[columns['category']].split('.')
			for category in categorys:
				CategoryObj = Category.objects.get(pk=category)
				company.category.add(CategoryObj)
				
			
	except Exception as e:
		return HttpResponse(e)
	f.close()
	return HttpResponse('Succesfully Added into Company')

@api_view(['POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVBuyer(request):
	f = request.FILES['BuyerCSV']
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	flag = True
	try:
		for line in f:
			if (flag==True):
				flag = False
				continue
			line = line[:-1].split(',')
			fields = {}
			for k,v in columns.iteritems():
				fields[k] = line[v]
			#fields['user'] = User.objects.get(pk=line[columns['user']])
			loginUser = request.user
			user_company = (loginUser.companyuser.company is not None)
			if user_company:
				selling_company = loginUser.companyuser.company
				fields['selling_company'] = selling_company#Company.objects.get(pk=line[columns['selling_company']])
				fields['buying_company'] = Company.objects.get(pk=line[columns['buying_company']])
				Buyer.objects.create(**fields)
	except Exception as e:
		return HttpResponse('Check CSV File')
	f.close()
	return HttpResponse('Succesfully Added into Buyer')

@api_view(['POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVInvite(request):
	f = request.FILES['InviteCSV']
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	flag = True
	try:
		for line in f:
			if (flag==True):
				flag = False
				continue
			line = line[:-1].split(',')
			fields = {}
			for k,v in columns.iteritems():
				fields[k] = line[v]
			fields['company'] = Company.objects.get(pk=line[columns['company']])
			fields['user'] = User.objects.get(pk=line[columns['user']])
			Invite.objects.create(**fields)
	except Exception as e:
		return HttpResponse('Check CSV File')
	f.close()
	return HttpResponse('Succesfully Added into Invite')

@api_view(['POST'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def importCSVSalesPerson(request):
	f = request.FILES['SalesPersonCSV']
	first_line = f.readline()[:-1].split(',')
	columns = {}
	i = 0
	for model in first_line:
		columns[model] = i
		i = i+1
	try:
		flag = True
		for line in f:
			if(flag==True):
				flag = False
				continue
			line =  line[:-1].split(',')
			fields = {}
			for k,v in columns.iteritems():
				fields[k] = line[v]
			
			del fields['password']
			del fields['alternate_email']
			del fields['phone_number']
			
			user = User.objects.create(**fields)
			
			groupObj = Group.objects.get(name="salesperson")#3=salesperson
			user.groups.add(groupObj)
				
			user.set_password(line[columns['password']])
			user.save()
			
			UserProfile.objects.filter(user=user).update(alternate_email=line[columns['alternate_email']], phone_number=line[columns['phone_number']])
			
			loginUser = request.user
			user_company = (loginUser.companyuser.company is not None)
			if user_company:
				company = loginUser.companyuser.company
				CompanyUser.objects.get_or_create(company=company, user=user)
			
	except Exception as e:
		return HttpResponse(e)
	f.close()
	return HttpResponse('Succesfully Added into Sales Person')

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVUser(request):
	output = createCsvUser(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVChoice(request):
	output = createCsvChoice(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVCompany(request):
	output = createCsvCompany(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVBranch(request):
	output = createCsvBranch(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVCompanyUser(request):
	output = createCsvCompanyUser(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVBrand(request):
	output = createCsvBrand(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVCatalog(request):
	output = createCsvCatalog(request)
	return output

@api_view(['GET'])
@permission_classes((IsCompanyAdministratorOrAdmin,))
def exportCSVProduct(request):
	output = createCsvProduct(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVBuyer(request):
	output = createCsvBuyer(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVSalesOrder(request):
	output = createCsvSalesOrder(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVSalesOrderItem(request):
	output = createCsvSalesOrderItem(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVSelection(request):
	output = createCsvSelection(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVChannelType(request):
	output = createCsvChannelType(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVChannel(request):
	output = createCsvChannel(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVPush(request):
	output = createCsvPush(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVExport(request):
	output = createCsvExport(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVInvite(request):
	output = createCsvInvite(request)
	return output

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def exportCSVSalesPerson(request):
	output = createCsvSalesPerson(request)
	return output

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def resendInvite(request):
	json_data = request.read()
	data = json.loads(json_data)
	invitee = Invitee.objects.get(pk=data['invitee_id'])#84
	
	output = sendInvite(str(invitee.invitee_number), str(request.user.username))
	return Response({"status":output.status_code==200})
	
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def makeBuyerOnInviteRegistration(request):
	json_data = request.read()
	data = json.loads(json_data)
	inviteeIds = Invitee.objects.filter(invitee_number=data['invitee_number'], invite__isnull=False)
	if inviteeIds:
		for invitee in inviteeIds:
			if invitee.invite.relationship_type == "buyer":
				loginUser = request.user
				company = loginUser.companyuser.company
				buyerObj = Buyer.objects.get_or_create(selling_company = invitee.invite.company, buying_company = company)
	return Response({"status":True})

@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def makeDefaultSegmentation(request):
	loginUser = request.user
	company = loginUser.companyuser.company
	
	city = City.objects.all().values_list('id', flat=True).distinct()
	category = Category.objects.all().values_list('id', flat=True).distinct()
	print company
	print city
	print category
	buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="default segmentation",company=company)#city=city,category=category,
	buyerSegmentation.city = city #.add(city)
	buyerSegmentation.category = category #.add(category)
	print buyerSegmentation
	return Response({"status":True})
	
@api_view(['GET','POST'])
@permission_classes((permissions.IsAuthenticated,))
def appTable(request):
	user = request.user
	company = user.companyuser.company
	
	dateList = []
	
	todayDate = date.today()
        
	yesterdayDate = todayDate - timedelta(days=1)
	
	currentWeekStartDate = todayDate - timedelta(days=todayDate.weekday())
	
	lastWeekEndDate = currentWeekStartDate - timedelta(days=1)
	lastWeekStartDate = lastWeekEndDate - timedelta(days=lastWeekEndDate.weekday())
	
	currentMonthStartDate = todayDate.replace(day=1)
	
	lastMonthEndDate = currentMonthStartDate - timedelta(days=1)
	lastMonthStartDate = lastMonthEndDate.replace(day=1)
	
	#quarterStartDate = quaterStartDate(todayDate)#(lastMonthStartDate - timedelta(days=1)).replace(day=1)
	
	#currentYearStartDate = todayDate.replace(day=1,month=4)
	
	dateList.append(["today",todayDate,todayDate]);
	dateList.append(["yesterday",yesterdayDate,yesterdayDate]);
	dateList.append(["current_week",currentWeekStartDate,todayDate]);
	dateList.append(["last_week",lastWeekStartDate,lastWeekEndDate]);
	dateList.append(["current_month",currentMonthStartDate,todayDate]);
	dateList.append(["last_month",lastMonthStartDate,lastMonthEndDate]);
	#dateList.append(["current_quarter",quarterStartDate,todayDate]);
	#dateList.append(["current_year",currentYearStartDate,todayDate]);
	
	jsonArr = []
	
	for dates in dateList:
		salesOrderIds = Meeting.objects.filter(user=user, start_datetime__gte=datetime.combine(dates[1], time.min), start_datetime__lte=datetime.combine(dates[2], time.max)).values_list('salesorder', flat=True).distinct()
		TotalItem = SalesOrderItem.objects.filter(sales_order__in=salesOrderIds).aggregate(Sum('quantity')).get('quantity__sum', 0)
		TotalDuration = Meeting.objects.filter(user=user, start_datetime__gte=datetime.combine(dates[1], time.min), start_datetime__lte=datetime.combine(dates[2], time.max)).aggregate(Sum('duration')).get('duration__sum', 0)
		if TotalItem is None:
			TotalItem = 0
		if TotalDuration is None:
			TotalDuration = 0
		jsonArr.append({"day":dates[0],"total_items":str(TotalItem),"total_duration":str(TotalDuration)})
	
	jsonData = json.dumps(jsonArr)
	
	return Response(jsonData)

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))	
def checkUserExist(request):
	json_data = request.read()
	data = json.loads(json_data)
	'''result = User.objects.filter(Q(username=data['username']) | Q(email=data['email'])).exists()
	print result
	return Response({"status":True,"is_exist":result})'''
	#error = {}
	if User.objects.filter(username=data['username']).exists():
		#error["username"] = "Username is already exist. Please choose another username"
		return HttpResponseBadRequest("Username is already exist. Please choose another username")
	if User.objects.filter(email=data['email']).exists():
		#error["email"] = "Email is already registered"
		return HttpResponseBadRequest("Email is already registered")
	#print error
	return Response({"status":True})

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))	
def checkOTPandMobile(request):
	json_data = request.read()
	data = json.loads(json_data)
	
	registrationOtp = RegistrationOTP.objects.filter(phone_number=data['phone_number']).order_by('-created_date')

	if registrationOtp.exists() and str(registrationOtp[0].otp) == data['otp']:
		return Response({"status":True})

	return HttpResponseBadRequest("Please enter valid OTP")

# def set_session(request):
# 	if 'company_id' not in request.session:
# 		company = Company_User.objects.get(user__username=request.user).company
# 		request.session['company_id'] = company.id
# 		brands = Brand.objects.filter(owning_company = company)
# 		request.session['brand_ids'] = [b.id for b in brands]
# 		catalogs = Catalog.objects.filter(brand__in = brands)
# 		request.session['catalog_ids'] = [c.id for c in catalogs]
# def destroy_session():
# 	pass

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	#permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
	def get_queryset(self):
		queryset = User.objects.all()
		
		'''userName = self.request.query_params.get('isexist_username', None)
		email = self.request.query_params.get('isexist_email', None)
		if userName is not None or email is not None:
			result = queryset.filter(Q(username=userName) | Q(email=email)).exists()
			print result
			return Response({"result":result})'''
			
		
		groupsName = self.request.query_params.get('groups', None)
		if groupsName is not None:
			groupsName = groupsName.split(",")
			queryset = queryset.filter(groups__name__in=groupsName)
		
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
			
		#return queryset
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		if user.is_staff:#==False:#staff user will add company			
			serializer.save()
		else:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				userInstance = serializer.save()
				CompanyUser.objects.get_or_create(company=company, user=userInstance)#, relationship_type="salesperson"

class UserProfileViewSet(viewsets.ModelViewSet):
	queryset = UserProfile.objects.all()
	serializer_class = UserProfileSerializer
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = UserProfileSerializer
		if self.request.method == 'GET':
				serializer_class = GetUserProfileSerializer
		return serializer_class
	def get_queryset(self):
		queryset = UserProfile.objects.all()
		user = self.request.query_params.get('user', None)
		if user is not None:
			queryset = queryset.filter(user=user)
			
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
			
		queryset = queryset.filter(user=user)
		
		return queryset
				
class GroupViewSet(viewsets.ModelViewSet):
	queryset = Group.objects.all()
	serializer_class = GroupSerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = Group.objects.all()
		name = self.request.query_params.get('name', None)
		if name is not None:
			queryset = queryset.filter(name=name)
		return queryset
		
class UserNumberViewSet(viewsets.ModelViewSet):
	queryset = UserNumber.objects.all()
	serializer_class = UserNumberSerializer
	def get_queryset(self):
		queryset = UserNumber.objects.all()
		user = self.request.query_params.get('user', None)
		if user is not None:
			queryset = queryset.filter(user=user)
		return queryset
	
'''	
class MyRegistrationView(RegistrationView):

    form_class= MyCustomRegistrationForm

    def register(self, request, **cleaned_data):
        new_user= super(MyRegistrationView, self).register(request, **cleaned_data)
        # here create your new UserProfile object
        print "register"
        return new_user'''

class ChoiceViewSet(viewsets.ModelViewSet):
	queryset = Choice.objects.all()
	serializer_class = ChoiceSerializer

class CompanyViewSet(viewsets.ModelViewSet):
	queryset = Company.objects.all()
	serializer_class = CompanySerializer
	#permission_classes = (IsCompanyOrAdmin, )
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = CompanySerializer
		if self.request.method == 'GET':
				serializer_class = GetCompanySerializer
		return serializer_class
	def get_queryset(self):
		queryset = Company.objects.all()
		company_type = self.request.query_params.get('company_type', None)
		if company_type is not None:
			queryset = queryset.filter(company_type=company_type)
		return queryset

class BranchViewSet(viewsets.ModelViewSet):
	# queryset = Branch.objects.all()
	serializer_class = BranchSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = BranchSerializer
		if self.request.method == 'GET':
				serializer_class = GetBranchSerializer
		return serializer_class
	def get_queryset(self):
		queryset = Branch.objects.all()
		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(company=company)
		return queryset

class CompanyUserViewSet(viewsets.ModelViewSet):
	queryset = CompanyUser.objects.all()
	serializer_class = CompanyUserSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_queryset(self):
		queryset = CompanyUser.objects.all()
		userId = self.request.query_params.get('user', None)
		if userId is not None:
			queryset = queryset.filter(user=userId)
		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(company=company)
		return queryset

class BrandViewSet(viewsets.ModelViewSet):
	queryset = Brand.objects.all()
	serializer_class = BrandSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	#permission_classes = (IsCompanyOrAdmin, IsCompanyAdministratorOrAdmin, )
	####permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_queryset(self):
		queryset = Brand.objects.all()
		
		device = self.request.query_params.get('device', None)
		showAll = self.request.query_params.get('showall', None)
		
		#If User is Staff User
		user = self.request.user
		
		mycompany = self.request.query_params.get('mycompany', None)
		if mycompany is not None and mycompany=="true":
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(company=company)
			except ObjectDoesNotExist:
				return Brand.objects.none()
		
		if user.is_staff or showAll is not None:
			return queryset
			
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				selling_company = Buyer.objects.filter(buying_company=company).order_by('selling_company').values_list('selling_company', flat=True).distinct()
				brand_distributor = BrandDistributor.objects.filter(company=company).order_by('brand').values_list('brand', flat=True).distinct()
				if device is not None and device=="app":
					return queryset.filter(Q(company=company) | Q(company__in=selling_company) | Q(id__in=brand_distributor))
				else:
					return queryset.filter(Q(company=company) | Q(id__in=brand_distributor))
		except ObjectDoesNotExist:
			return Brand.objects.none()
			
	# def get_queryset(self):
	# 	company = Company_User.objects.get(user__username=self.request.user).company
	# 	return Brand.objects.filter(owning_company = company)
	
class BrandAppViewSet(viewsets.ModelViewSet):
	queryset = Brand.objects.all()
	serializer_class = BrandSerializer
	
	#permission_classes = (IsCompanyOrAdmin, IsCompanyAdministratorOrAdmin, )
	####permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsCompanyAdministratorOrAdminOrReadOnly, )
	#permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_queryset(self):
		queryset = Brand.objects.all()
		
		#If User is Staff User
		user = self.request.user
			
		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				selling_company = Buyer.objects.filter(buying_company=company).order_by('selling_company').values_list('selling_company', flat=True).distinct()
				brand_distributor = BrandDistributor.objects.filter(company=company).order_by('brand').values_list('brand', flat=True).distinct()
				brandPublicIds = Catalog.objects.filter(view_permission__icontains='public').order_by('brand').values_list('brand', flat=True).distinct()
				brandIds = list(set(brand_distributor)|set(brandPublicIds))
				return queryset.filter(Q(company=company) | Q(company__in=selling_company) | Q(id__in=brandIds))#Q(id__in=brand_distributor)
			else:
				brandPublicIds = Catalog.objects.filter(view_permission__icontains='public').order_by('brand').values_list('brand', flat=True).distinct()
				return queryset.filter(id__in=brandPublicIds)
				
		except ObjectDoesNotExist:
			return Brand.objects.none()
			
class BrandDistributorViewSet(viewsets.ModelViewSet):
	queryset = BrandDistributor.objects.all()
	serializer_class = BrandDistributorSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_queryset(self):
		queryset = BrandDistributor.objects.all()
		
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
			return BrandDistributor.objects.none()
		
		
	
class CatalogViewSet(viewsets.ModelViewSet):
	queryset = Catalog.objects.all()
	serializer_class = CatalogSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = CatalogSerializer
		if self.request.method == 'GET':
				serializer_class = GetCatalogSerializer
		return serializer_class
	def get_queryset(self):
		queryset = Catalog.objects.all()
		brand = self.request.query_params.get('brand', None)
		if brand is not None:
			queryset = queryset.filter(brand=brand)
		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(company=company)
		category = self.request.query_params.get('category', None)
		if category is not None:
			catalogArray = []
			catalogArray.append(int(category))
			
			catalogParent1 = Category.objects.filter(parent_category=category).order_by('id').values_list('id', flat=True).distinct()
			catalogArray += catalogParent1
			
			catalogParent2 = Category.objects.filter(parent_category__in=catalogParent1).order_by('id').values_list('id', flat=True).distinct()
			catalogArray += catalogParent2
			
			queryset = queryset.filter(category__in=catalogArray)
		
		device = self.request.query_params.get('device', None)
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
		'''if user.groups.filter(name="administrator").exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(company=company)
			except ObjectDoesNotExist:
				return Catalog.objects.none()
		elif user.groups.filter(name="salesperson").exists():'''
		if user.groups.filter(name__in=("administrator","salesperson")).exists():
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					
					userPushIds = Push_User.objects.filter(user=user).order_by('push').values_list('push', flat=True).distinct()
					pushCatalogIds = Push_Catalog.objects.filter(push__in=userPushIds).order_by('catalog').values_list('catalog', flat=True).distinct()
					
					if device is not None and device=="app":
						return queryset.filter(Q(company=company) | Q(view_permission__icontains='public') | Q(id__in=pushCatalogIds))#| Q(id__in=pushCatalogIds)
					else:
						#return queryset.filter(Q(company=company) | Q(view_permission__icontains='public') | Q(id__in=pushCatalogIds))#| Q(id__in=pushCatalogIds)
						return queryset.filter(company=company)
			except ObjectDoesNotExist:
				return Catalog.objects.none()
		else:
			return queryset.filter(view_permission__icontains='public')
	
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		
		gd_client =	OAuth2Login('tech@trivenisarees.com')
		title = self.request.POST.get("title")
		accessSpecifier = 'private'
		album = createAlbum(gd_client, title, accessSpecifier)
		picasa_url = album.GetHtmlLink().href
		picasa_id = album.gphoto_id.text
		
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company, picasa_url=picasa_url, picasa_id=picasa_id)
			
	def perform_destroy(self, instance):#delete photo from picasa
		title = instance.title
		print title
		gd_client =	OAuth2Login('tech@trivenisarees.com')
		albums = gd_client.GetUserFeed(user='tech@trivenisarees.com')
		for album in albums.entry:
			if album.title.text == title:
				gd_client.Delete(album)
		instance.delete()	
	# def get_queryset(self):
	# 	company = Company_User.objects.get(user__username=self.request.user).company
	# 	brands = Brand.objects.filter(owning_company = company)
	# 	return Catalog.objects.filter(brand__in = brands)

class CatalogAppViewSet(viewsets.ModelViewSet):
	queryset = Catalog.objects.all()
	serializer_class = CatalogSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = CatalogSerializer
		if self.request.method == 'GET':
				serializer_class = GetCatalogSerializer
		return serializer_class
	def get_queryset(self):
		queryset = Catalog.objects.all()
		brand = self.request.query_params.get('brand', None)
		if brand is not None:
			queryset = queryset.filter(brand=brand)
		company = self.request.query_params.get('company', None)
		if company is not None:
			return queryset.filter(company=company)
		category = self.request.query_params.get('category', None)
		if category is not None:
			catalogArray = []
			catalogArray.append(int(category))
			
			catalogParent1 = Category.objects.filter(parent_category=category).order_by('id').values_list('id', flat=True).distinct()
			catalogArray += catalogParent1
			
			catalogParent2 = Category.objects.filter(parent_category__in=catalogParent1).order_by('id').values_list('id', flat=True).distinct()
			catalogArray += catalogParent2
			
			queryset = queryset.filter(category__in=catalogArray)
		
		
		user = self.request.user
		
		try:
			if user.is_authenticated() and (user.companyuser.company is not None):
				company = user.companyuser.company
				if company.company_type == "manufacture":
					return queryset.filter(company=company)
				else:
					userPushIds = Push_User.objects.filter(user=user).order_by('push').values_list('push', flat=True).distinct()
					pushCatalogIds = Push_Catalog.objects.filter(push__in=userPushIds).order_by('catalog').values_list('catalog', flat=True).distinct()
					return queryset.filter(Q(company=company) | Q(view_permission__icontains='public') | Q(id__in=pushCatalogIds))
			else:
				return queryset.filter(view_permission__icontains='public')
				
		except ObjectDoesNotExist:
			return Catalog.objects.none()
	
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)
		
			
class ProductViewSet(viewsets.ModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):#'PUT',
				serializer_class = ProductSerializer	#UpdateProductSerializer
		if self.request.method == 'GET':
				serializer_class = GetProductSerializer
		return serializer_class
	def get_queryset(self):
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
			
	def perform_create(self, serializer):#add photo to picasa
		name = self.request.FILES['image_small']
		photoname = self.request.POST.get("sku")
		catalogs = self.request.POST.getlist("catalog")
		gd_client =	OAuth2Login('tech@trivenisarees.com')
		for catalog in catalogs:
			#cat_obj = Catalog.objects.filter(id = catalog).values()[0]
			cat_obj = Catalog.objects.get(pk=catalog)
			photo = postPhotoToAlbum(gd_client, cat_obj.title, name, photoname)
		serializer.save()
		
	def perform_destroy(self, instance):#delete photo from picasa
		name = instance.sku
		gd_client =	OAuth2Login('tech@trivenisarees.com')
		photos = gd_client.SearchUserPhotos(name,user='tech@trivenisarees.com', limit='1')
		for photo in photos.entry:
			gd_client.Delete(photo)
		instance.delete()
		
	def perform_update(self, serializer):#edit photo to picasa
		print 'update'
		if self.request.method == 'PUT':
			name = self.request.FILES['image_small']
			instance = serializer.save()
			photoname = instance.sku
			catalogs = instance.catalog.all()
			gd_client =	OAuth2Login('tech@trivenisarees.com')
			photos = gd_client.SearchUserPhotos(photoname,user='tech@trivenisarees.com', limit='1')
			for photo in photos.entry:
				gd_client.Delete(photo)
			for catalog in catalogs:
				cat_obj = Catalog.objects.filter(id = catalog.id).values()[0]
				photo = postPhotoToAlbum(gd_client, cat_obj['title'], name, photoname)
		else:
			serializer.save()
			
		#~ for catalog in catalogs:
			#~ cat_obj = Catalog.objects.filter(id = catalog).values()[0]
			#~ print cat_obj['title']
			#~ photo = postPhotoToAlbum(gd_client, cat_obj['title'], name, photoname)
				
	# def get_queryset(self):
	# 	company = Company_User.objects.get(user__username=self.request.user).company
	# 	brands = Brand.objects.filter(company = company)
	# 	return Product.objects.filter(catalog__brand__in = brands)

class BuyerViewSet(viewsets.ModelViewSet):
	queryset = Buyer.objects.all()
	serializer_class = BuyerSerializer
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = BuyerSerializer
		if self.request.method == 'GET':
				serializer_class = GetBuyerSerializer
		return serializer_class
	def get_queryset(self):
		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return Buyer.objects.filter(selling_company=company)
		except ObjectDoesNotExist:
			return Buyer.objects.none()
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(selling_company=company)
			
class SellerViewSet(viewsets.ModelViewSet):
	queryset = Buyer.objects.all()
	serializer_class = SellerSerializer
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = SellerSerializer
		if self.request.method == 'GET':
				serializer_class = GetSellerSerializer
		return serializer_class
	def get_queryset(self):
		user = self.request.user
		try:
			user_company = (user.companyuser.company is not None)
			if user_company:
				company = user.companyuser.company
				return Buyer.objects.filter(buying_company=company)
		except ObjectDoesNotExist:
			return Buyer.objects.none()
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(buying_company=company)

class SalesOrderViewSet(viewsets.ModelViewSet):
	# queryset = SalesOrder.objects.all()
	serializer_class = SalesOrderSerializer

	def get_queryset(self):
		queryset = SalesOrder.objects.all()
		company = self.request.query_params.get('company', None)
		if company is not None:
			queryset = queryset.filter(company=company)
			
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
		
	def perform_create(self, serializer):#add user on create
		serializer.save(user=self.request.user)

class PurchaseOrderViewSet(viewsets.ModelViewSet):
	queryset = SalesOrder.objects.all()
	serializer_class = SalesOrderSerializer

	def get_queryset(self):
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
					return queryset.filter(company=company)
			except ObjectDoesNotExist:
				return SalesOrder.objects.none()
		else:
			return SalesOrder.objects.none()
		
	def perform_create(self, serializer):#add user on create
		serializer.save(user=self.request.user)
		
class SalesOrderItemViewSet(viewsets.ModelViewSet):
	# queryset = SalesOrderItem.objects.all()
	serializer_class = SalesOrderItemSerializer
	def get_queryset(self):
		queryset = SalesOrderItem.objects.all()
		salesorder = self.request.query_params.get('salesorder', None)
		if salesorder is not None:
			queryset = queryset.filter(sales_order=salesorder)
		return queryset

class SelectionViewSet(viewsets.ModelViewSet):
	queryset = Selection.objects.all()
	serializer_class = SelectionSerializer
	permission_classes = (IsOwnerOrAdmin, )#(permissions.IsAdminUser, IsOwner,  )#create, update and delete to authenticated user #owner update or delete	permissions.IsAdminUser, 
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = SelectionSerializer
		if self.request.method == 'GET':
				serializer_class = GetSelectionSerializer
		return serializer_class
	def perform_create(self, serializer):#add user on create
		serializer.save(user=self.request.user)
	def get_queryset(self):
		queryset = Selection.objects.all()
		selectionType = self.request.query_params.get('type', None)
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		
		userPushIds = Push_User.objects.filter(user=user).order_by('push').values_list('push', flat=True).distinct()
		pushSelectionIds = Push_Selection.objects.filter(push__in=userPushIds).order_by('selection').values_list('selection', flat=True).distinct()
		
		if selectionType is not None:
			if selectionType == "push":		
				return queryset.filter(id__in=pushSelectionIds)
			elif selectionType == "my":
				return queryset.filter(user=user)
				
		return queryset.filter(Q(id__in=pushSelectionIds) | Q(user=user))

class ChannelTypeViewSet(viewsets.ModelViewSet):
	queryset = ChannelType.objects.all()
	serializer_class = ChannelTypeSerializer

class ChannelViewSet(viewsets.ModelViewSet):
	queryset = Channel.objects.all()
	serializer_class = ChannelSerializer

class PushViewSet(viewsets.ModelViewSet):
	queryset = Push.objects.all()
	serializer_class = PushSerializer
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH','POST','OPTIONS'):
				serializer_class = PushSerializer
		if self.request.method == 'GET':
				serializer_class = GetPushSerializer
		return serializer_class
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(user=user, company=company)
	def get_queryset(self):
		queryset = Push.objects.all()
		
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

class PushUserViewSet(viewsets.ModelViewSet):
	queryset = Push_User.objects.all()
	serializer_class = PushUserSerializer
	def get_queryset(self):
		queryset = Push_User.objects.all()
		pushId = self.request.query_params.get('push', None)
		if pushId is not None:
			queryset = queryset.filter(push=pushId)
		userId = self.request.query_params.get('user', None)
		if userId is not None:
			queryset = queryset.filter(user=userId)
		isViewed = self.request.query_params.get('is_viewed', None)
		if isViewed is not None:
			queryset = queryset.filter(is_viewed=isViewed)
			
		
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset

		#If User is Administartor	####Buyer App Bug - push user count not work - because Buyer is Administrator
		'''if user.groups.filter(name="administrator").exists():		
			try:
				user_company = (user.companyuser.company is not None)
				if user_company:
					company = user.companyuser.company
					return queryset.filter(user__companyuser__company=company)
			except ObjectDoesNotExist:
				return Push_User.objects.none()
		else:'''
		return queryset.filter(user=user)

'''
class PushResultViewSet(viewsets.ModelViewSet):
	queryset = Push_Result.objects.all()
	serializer_class = PushResultSerializer
'''
class PushCatalogViewSet(viewsets.ModelViewSet):
	queryset = Push_Catalog.objects.all()
	serializer_class = PushCatalogSerializer

class PushProductViewSet(viewsets.ModelViewSet):
	queryset = Push_Product.objects.all()
	serializer_class = PushProductSerializer
	
class PushSelectionViewSet(viewsets.ModelViewSet):
	queryset = Push_Selection.objects.all()
	serializer_class = PushSelectionSerializer

class ExportViewSet(viewsets.ModelViewSet):
	queryset = Export.objects.all()
	serializer_class = ExportSerializer

class ExportResultViewSet(viewsets.ModelViewSet):
	queryset = Export_Result.objects.all()
	serializer_class = ExportResultSerializer

class ExportCatalogViewSet(viewsets.ModelViewSet):
	queryset = Export_Catalog.objects.all()
	serializer_class = ExportCatalogSerializer

class ExportProductViewSet(viewsets.ModelViewSet):
	queryset = Export_Product.objects.all()
	serializer_class = ExportProductSerializer

class InviteViewSet(viewsets.ModelViewSet):
	queryset = Invite.objects.all()
	serializer_class = InviteSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(user=user,company=company)
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = InviteSerializer
		if self.request.method == 'GET':
				serializer_class = GetInviteSerializer
		return serializer_class

class InviteeViewSet(viewsets.ModelViewSet):
	queryset = Invitee.objects.all()
	serializer_class = InviteeSerializer
	def get_queryset(self):
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

class MessageViewSet(viewsets.ModelViewSet):
	# permission_classes = (permissions.IsAdminUser,)
	queryset = Message.objects.all()
	serializer_class = MessageSerializer

class ReceivedMessageList(generics.ListAPIView):
	serializer_class = ReceivedMessageSerializer
	def get_queryset(self):
		return Message.objects.filter(receiver_user__username = self.request.user, message_folder_set__folder = 'inbox')

class ReceivedMessageDetail(generics.RetrieveDestroyAPIView):
	serializer_class = ReceivedMessageSerializer
	def get_queryset(self):
		return Message.objects.filter(receiver_user__username = self.request.user, message_folder_set__folder = 'inbox')
	def perform_destroy(self, instance):
		message_folder_instances = MessageFolder.objects.filter(message = instance)
		for m in message_folder_instances:
			if m.folder == 'inbox':
				m.folder = 'trash'
				m.save()
				break

class SentMessageList(generics.ListCreateAPIView):
	serializer_class = SentMessageSerializer
	def get_queryset(self):
		return Message.objects.filter(sender_user__username = self.request.user, message_folder_set__folder = 'sent')

class SentMessageDetail(generics.RetrieveAPIView):
	serializer_class = SentMessageSerializer
	def get_queryset(self):
		return Message.objects.filter(sender_user__username = self.request.user, message_folder_set__folder = 'sent')

class MessageFolderViewSet(viewsets.ModelViewSet):
	queryset = MessageFolder.objects.all()
	serializer_class = MessageFolderSerializer

class MeetingViewSet(viewsets.ModelViewSet):
	queryset = Meeting.objects.all()
	serializer_class = MeetingSerializer
	def perform_create(self, serializer):#add user on create
		serializer.save(user=self.request.user)
	def get_queryset(self):
		queryset = Meeting.objects.all()
		userId = self.request.query_params.get('user', None)
		if userId is not None:
			queryset = queryset.filter(user=userId)
		status = self.request.query_params.get('status', None)
		if status is not None:
			queryset = queryset.filter(status=status)

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
					return queryset.filter(user__companyuser__company=company)
			except ObjectDoesNotExist:
				return Meeting.objects.none()
		else:
			return queryset.filter(user=user)
		
		#return queryset

class BuyerSegmentationViewSet(viewsets.ModelViewSet):
	queryset = BuyerSegmentation.objects.all()
	serializer_class = BuyerSegmentationSerializer
	permission_classes = (IsCompanyAdministratorOrAdminOrReadOnly, )
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = BuyerSegmentationSerializer
		if self.request.method == 'GET':
				serializer_class = GetBuyerSegmentationSerializer
		return serializer_class
	def perform_create(self, serializer):#add user on create
		user = self.request.user
		user_company = (user.companyuser.company is not None)
		if user_company:
			company = user.companyuser.company
			serializer.save(company=company)
	def get_queryset(self):
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
		
	'''@detail_route(methods=['get'])
	def activebuyers(self, request, *args, **kwargs):
		buyersegment = self.get_object()
		serializer = BuyerSegmentationSerializer(buyersegment)
		city = serializer.data['city']
		category = serializer.data['category']

		#totalpeople = Branch.objects.filter(Q(city__in=city)).count()##
		companyIds = Branch.objects.filter(Q(city__in=city)).values_list('company', flat=True)
		print companyIds
		#get Admin IDS from company with category
		companyCategoryIds = Company.objects.filter(id__in=companyIds, category__in=category).values_list('id', flat=True).count()
		#print companyCategoryIds
		#totalBranch = Branch.objects.filter(Q(company__in=companyCategoryIds)).values_list('id', flat=True).count()

		#statencity = re.sub("[^\w]", " ",  "surat, ahmedabad, gujarat").split()#buyersegment.condition
		#totalpeople = Company.objects.filter(Q(city__in=statencity) | Q(state__in=statencity)).count()
		#totalpeople = Company.objects.filter(Q(city__iregex=r'(' + '|'.join(statencity) + ')') | Q(state__iregex=r'(' + '|'.join(statencity) + ')')).count()
		
		content = {'active_buyers': companyCategoryIds}
		return Response(content)'''

class StateViewSet(viewsets.ModelViewSet):
	permission_classes = (IsAdminOrReadOnly, )
	queryset = State.objects.all()
	serializer_class = StateSerializer
	
class CityViewSet(viewsets.ModelViewSet):
	queryset = City.objects.all()
	serializer_class = CitySerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = City.objects.all()
		stateId = self.request.query_params.get('state', None)
		if stateId is not None:
			queryset = queryset.filter(state=stateId)
		return queryset

class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = Category.objects.all()
		parentId = self.request.query_params.get('parent', None)
		if parentId=="null":
			queryset = queryset.filter(parent_category__isnull=True)
		elif parentId is not None:
			queryset = queryset.filter(parent_category=parentId)
		return queryset
'''	
class MainCategoryViewSet(viewsets.ModelViewSet):
	queryset = MainCategory.objects.all()
	serializer_class = MainCategorySerializer
	
class SubCategoryViewSet(viewsets.ModelViewSet):
	queryset = SubCategory.objects.all()
	serializer_class = SubCategorySerializer
'''
class InvoiceViewSet(viewsets.ModelViewSet):
	queryset = Invoice.objects.all()
	serializer_class = InvoiceSerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = Invoice.objects.all()
		companyId = self.request.query_params.get('company', None)
		if companyId is not None:
			queryset = queryset.filter(company=companyId)
		
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
			return Invoice.objects.none()
			
		#return queryset
		
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = InvoiceSerializer
		if self.request.method == 'GET':
				serializer_class = GetInvoiceSerializer
		return serializer_class

class InvoiceCreditViewSet(viewsets.ModelViewSet):
	queryset = InvoiceCredit.objects.all()
	serializer_class = InvoiceCreditSerializer
	permission_classes = (IsAdminOrReadOnly, )
	def get_queryset(self):
		queryset = InvoiceCredit.objects.all()
		
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
			return InvoiceCredit.objects.none()

class RegistrationOTPViewSet(viewsets.ModelViewSet):
	queryset = RegistrationOTP.objects.all()
	serializer_class = RegistrationOTPSerializer
	permission_classes = (permissions.AllowAny, )
	
	def get_serializer_class(self):
		serializer_class = self.serializer_class
		if self.request.method in ('PUT','PATCH'):
				serializer_class = RegistrationOTPSerializer
		if self.request.method == 'GET':
				serializer_class = GetRegistrationOTPSerializer
		return serializer_class
	def get_queryset(self):
		queryset = RegistrationOTP.objects.all()
		phoneNumber = self.request.query_params.get('phone_number', None)
		
		if phoneNumber is not None:
			queryset = queryset.filter(phone_number=phoneNumber).order_by('-created_date')
				
		#If User is Staff User
		user = self.request.user
		if user.is_staff:
			return queryset
		else:
			RegistrationOTP.objects.none()
		
	'''def perform_create(self, serializer):
		
		phoneNumber = self.request.POST.get("phone_number")
		
		#UserProfile.objects.filter(phone_number=phoneNumber).exists():
		#	raise serializers.ValidationError("User is registered with this number")
		
		otp = random.randrange(100000, 999999, 1)
		sendInvite(str(phoneNumber), str(otp))
		serializer.save(otp=otp)'''

'''
class CityDatatables(BaseDatatableView):
	
	columns = ['id','state', 'city_name'] #Table columns
	order_columns = ['id','state', 'city_name']
	search_columns = ['id','state', 'city_name']

	def get_initial_queryset(self):
		#Initial Queryset
		return City.objects.all()


	def filter_queryset(self, qs):
		#Main filter
		search = self.request.GET.get('search[value]', None)
		if search:
			qs = qs.filter(state__state_name__icontains=search)|qs.filter(city_name__icontains=search)
			
		#Row wise filter
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
'''
