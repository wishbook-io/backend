from api.models import *
from django.contrib.auth.models import User, Group
from datetime import datetime, date, time, timedelta


push = Push_User_Product.objects.filter(is_viewed='yes').exclude(push__isnull=True).values_list('push', flat=True).distinct()
print "push"
print push

catalog = Push_User_Product.objects.filter(is_viewed='yes').exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
print "catalog"
print catalog

product = Push_User_Product.objects.filter(is_viewed='yes').exclude(product__isnull=True).values_list('product', flat=True).distinct()
print "product"
print product

buying_company = Push_User_Product.objects.filter(is_viewed='yes').exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct()
print "buying_company"
print buying_company




cpf = CompanyProductFlat.objects.filter(push_reference__in=push, catalog__in=catalog, product__in=product, buying_company__in=buying_company).values_list('id', flat=True)

print "cpf"
print cpf

'''
updatecpf = CompanyProductFlat.objects.filter(id__in=list(cpf)).update(is_viewed='yes')
print "updatecpf"
print updatecpf
'''
