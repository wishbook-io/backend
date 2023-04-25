from models import *
from rest_framework.serializers import *
from django import forms
#from allauth.account.forms import SignupForm
from django.contrib.auth.models import User, Group
#from .models import UserProfile
from django.core.validators import RegexValidator, MinValueValidator

from django.core.exceptions import ObjectDoesNotExist

from django.forms import ModelForm
from django.core.exceptions import NON_FIELD_ERRORS

from push_notifications.models import APNSDevice, GCMDevice

import logging
logger = logging.getLogger(__name__)

#phone_regex = RegexValidator(regex=r'^\+\d{10,15}$', message="Phone number must be entered in the format. Eg: '+915432112345'.")

from api.models import *
from api.common_functions import *

class SignupForm(forms.Form):
    #company_name = forms.CharField(max_length=30, label='CompanyName', required=True)
    country = forms.CharField(max_length=30, label='Country', required=False)
    state = forms.CharField(max_length=30, label='State', required=False)
    city = forms.CharField(max_length=30, label='City', required=False)
    phone_number = forms.CharField(max_length=30, label='PhoneNumber')#, validators=[phone_regex]
    #invite_id = forms.CharField(label='InviteId', required=True)
    company_name = forms.CharField(max_length=100, label='Name', required=False)
    registration_id = forms.CharField(max_length=500, label='RegistrationId', required=False)
    
    discovery_ok = forms.CharField(max_length=30, label='Discovery Ok', required=False)
    connections_preapproved = forms.CharField(max_length=30, label='Connections Preapproved', required=False)
    
    usertype = forms.CharField(max_length=30, label='User Type', required=False)
    company = forms.CharField(max_length=100, label='Company', required=False)
    
    number_verified = forms.CharField(max_length=30, label='Number Verified', required=False)
    
    def signup(self, request, user):
        logger.info("New Registration")
        
        company_name = None
        phone_number = self.cleaned_data['phone_number'][-10:]
        
        if self.cleaned_data['company_name'] != "":
            company_name = self.cleaned_data['company_name']
        
        logger.info(company_name)
        
        discovery_ok = True
        if self.cleaned_data['discovery_ok'] != "":
            discovery_ok = self.cleaned_data['discovery_ok']
        
        connections_preapproved = True
        if self.cleaned_data['connections_preapproved'] != "":
            connections_preapproved = self.cleaned_data['connections_preapproved']
        
        country = Country.objects.get(pk=1)
        if self.cleaned_data['country'] != "":
            country = Country.objects.get(pk=self.cleaned_data['country'])
        
        state = State.objects.filter(state_name="gujarat").first()
        if self.cleaned_data['state'] != "":
            state = State.objects.get(pk=self.cleaned_data['state'])
        
        city = City.objects.filter(city_name="surat").first()
        if self.cleaned_data['city'] != "":
            city = City.objects.get(pk=self.cleaned_data['city'])
        
        phone_number_verified = "yes"
        if self.cleaned_data['number_verified'] != "":
            phone_number_verified = "no"
        
        UserProfile.objects.filter(user=user).update(phone_number=phone_number, country=country, phone_number_verified=phone_number_verified) #company_name=self.cleaned_data['company_name'], 
        #user_number = UserNumber(user=user, phone_number=self.cleaned_data['phone_number'])
        #user_number.save()
        inviteeObj = Invitee.objects.filter(invitee_number=phone_number, country=country).update(status="registered", registered_user=user)
        '''if inviteeObj is not None:
            for obj in inviteeObj:
                obj.status = "registered"
                obj.registered_user = user
                obj.save()'''
        
        if "@wishbooks.io" in user.email:
            newemail = str(country.phone_code).replace("+", "")+user.email
            if not User.objects.filter(email=newemail).exists():
                user.email = newemail
        
        
        registration_id = self.cleaned_data['registration_id']
        if registration_id != "":
            logger.info(str(registration_id))
            gcmDeviceDelete = GCMDevice.objects.filter(registration_id=registration_id).delete()
            gcmDevice = GCMDevice.objects.create(registration_id=registration_id, active=True, user=user)
        
        if self.cleaned_data['usertype'] != "" and self.cleaned_data['company'] != "":
            logger.info(str(self.cleaned_data['usertype']))
            groupObj = Group.objects.get(name=self.cleaned_data['usertype'])
            user.groups.add(groupObj)
            user.first_name=company_name
            
            user.is_active = False
            user.save()
            
            companyUser = CompanyUser.objects.create(user=user, company=Company.objects.get(pk=int(self.cleaned_data['company'])))
        
        else:
            logger.info(str("New company created"))
            groupObj = Group.objects.get(name="administrator")
            user.groups.add(groupObj)
            user.first_name=company_name
            user.save()
            
            ##start making company, branch and companyuser
            if company_name == None:
                company_name = user.username #phone_number
            company = Company.objects.create(name=company_name, phone_number=phone_number, city=city, state=state, country=country, discovery_ok=discovery_ok, connections_preapproved=connections_preapproved, email=user.email)
            category = Category.objects.all().values_list('id', flat=True)
            company.category.add(*category)
            company.save()
            
            companyType = CompanyType.objects.create(company=company)
            
            branch = Branch.objects.get_or_create(company = company, name="Main Branch - "+company.name, street_address=company.street_address, city=company.city, state=company.state, phone_number=company.phone_number, country=country)# ,
            
            companyUser = CompanyUser.objects.create(user=user, company=company)
            
            ##end making company, branch and companyuser
            
            logger.info("start default segmentation")
            ##start default segmentation
            city = City.objects.all().values_list('id', flat=True).distinct()
            category = Category.objects.all().values_list('id', flat=True).distinct()
            group_type = GroupType.objects.all().values_list('id', flat=True).distinct()
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="Send All",company=company)#city=city,category=category,
            buyerSegmentation.city = city #.add(city)
            buyerSegmentation.category = category #.add(category)
            buyerSegmentation.group_type = group_type
            
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Distributor",company=company)
            buyerSegmentation.city = city
            buyerSegmentation.category = category
            buyerSegmentation.group_type = GroupType.objects.filter(id=1).values_list('id', flat=True).distinct()
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Wholesaler",company=company)
            buyerSegmentation.city = city
            buyerSegmentation.category = category
            buyerSegmentation.group_type = GroupType.objects.filter(id=2).values_list('id', flat=True).distinct()
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Semi-Wholesaler",company=company)
            buyerSegmentation.city = city
            buyerSegmentation.category = category
            buyerSegmentation.group_type = GroupType.objects.filter(id=3).values_list('id', flat=True).distinct()
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Retailer",company=company)
            buyerSegmentation.city = city
            buyerSegmentation.category = category
            buyerSegmentation.group_type = GroupType.objects.filter(id=4).values_list('id', flat=True).distinct()
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Online-Retailer",company=company)
            buyerSegmentation.city = city
            buyerSegmentation.category = category
            buyerSegmentation.group_type = GroupType.objects.filter(id=5).values_list('id', flat=True).distinct()
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Resellers",company=company)
            buyerSegmentation.city = city
            buyerSegmentation.category = category
            buyerSegmentation.group_type = GroupType.objects.filter(id=8).values_list('id', flat=True).distinct()
            
            buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Broker",company=company)
            buyerSegmentation.city = city
            buyerSegmentation.category = category
            buyerSegmentation.group_type = GroupType.objects.filter(id=9).values_list('id', flat=True).distinct()
            ##end default segmentation
            
            logger.info("start make default buyer/supplier")
            ##start make default buyer/supplier
            inviteeIds = Invitee.objects.filter(invitee_number=company.phone_number, invite__isnull=False, country=country)
            if inviteeIds:
                for invitee in inviteeIds:
                    try:
                        if invitee.invite.relationship_type == "buyer":
                            logger.info("buyer")
                            if Buyer.objects.filter(invitee=invitee).exists():
                                buyerObj = Buyer.objects.filter(invitee=invitee).last()
                                buyerObj.buying_company = company
                                #buyerObj.status="buyer_pending"
                                buyerObj.status="approved"
                                buyerObj.save()
                                #requestNotification(buyerObj.selling_company, data['invitee_number'], "buyer", buyerObj, buyerObj.buying_company)
                                pushOnApproves(buyerObj.selling_company, buyerObj.buying_company)
                            else:
                                #buyerObj = Buyer.objects.get_or_create(selling_company = invitee.invite.company, buying_company = company, status="buyer_pending")
                                buyerObj = Buyer.objects.get_or_create(selling_company = invitee.invite.company, buying_company = company, status="approved", group_type=GroupType.objects.get(pk=2))
                                #requestNotification(buyerObj.selling_company, data['invitee_number'], "buyer", buyerObj, buyerObj.buying_company)
                                pushOnApproves(buyerObj.selling_company, buyerObj.buying_company)
                        elif invitee.invite.relationship_type == "supplier":
                            logger.info("supplier")
                            if Buyer.objects.filter(invitee=invitee).exists():
                                buyerObj = Buyer.objects.filter(invitee=invitee).last()
                                buyerObj.selling_company = company
                                #buyerObj.status="supplier_pending"
                                buyerObj.status="approved"
                                buyerObj.save()
                                #requestNotification(buyerObj.buying_company, data['invitee_number'], "supplier", buyerObj, buyerObj.selling_company)
                                pushOnApproves(buyerObj.selling_company, buyerObj.buying_company)
                            else:
                                #buyerObj = Buyer.objects.get_or_create(selling_company = company, buying_company = invitee.invite.company, status="supplier_pending")
                                buyerObj = Buyer.objects.get_or_create(selling_company = company, buying_company = invitee.invite.company, status="supplier_pending", group_type=GroupType.objects.get(pk=2))
                                #requestNotification(buyerObj.buying_company, data['invitee_number'], "supplier", buyerObj, buyerObj.selling_company)
                                pushOnApproves(buyerObj.selling_company, buyerObj.buying_company)
                    except Exception as e:
                        logger.info("registration error")
                        logger.info(str(e))
                        pass
            ##end make default buyer/supplier
            
            ##start make default warehouse
            warehouse = Warehouse.objects.create(company=company, name=company.name+" warehouse")
            ##end make default warehouse
        
        if phone_number_verified == "no":
            otp = random.randrange(100000, 999999, 1)
            otpstatus = sendOTP(str(country.phone_code)+str(phone_number), str(otp))
            registrationOtp = RegistrationOTP.objects.create(phone_number=phone_number, otp=otp, country=country)
            logger.info(str(otpstatus))
            
            
            
