from api.models import Company,UserProfile,CatalogEnquiry
from django.contrib.auth.models import User
from django.db.models import Q
from api.v1.sugar_crm import update_user_to_crm,update_company_to_crm,update_enquiry_to_crm

def crm_company_script():
    companies = Company.objects.filter(Q(sugar_crm_account_id__isnull=True) | Q(sugar_crm_account_id__exact='')).order_by('id')
    for company in companies:
        print(company.id)
        update_company_to_crm(company.id,True)

def crm_user_script():
    userprofiles = UserProfile.objects.filter(Q(sugar_crm_user_id__isnull=True) | Q(sugar_crm_user_id__exact='')).order_by('user_id')
    for userprofile in userprofiles:
        print(userprofile.user_id)
        update_user_to_crm(userprofile.user_id,True)
def enquiry_crm_script():
    # enquiries = CatalogEnquiry.objects.filter(Q(sugar_crm_lead_id__isnull=True) | Q(sugar_crm_lead_id__exact='')).exclude(selling_company__sugar_crm_account_id__isnull=True).exclude(selling_company__sugar_crm_account_id__exact='').order_by('id')
    enquiries = CatalogEnquiry.objects.filter(Q(sugar_crm_lead_id__isnull=True) | Q(sugar_crm_lead_id__exact='')).order_by('id')
    for enquiry in enquiries:
        print enquiry.id,enquiry.selling_company.id
        update_enquiry_to_crm(enquiry.id,True)