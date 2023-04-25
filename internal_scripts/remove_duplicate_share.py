from api.models import *
#import IPython
from django.db.models import Sum, Min, Max

###for delete duplicate catalog
print " =====catalog===== "
max_catalog_push_user_ids = Push_User.objects.filter(catalog__isnull=False).values('user','selling_company', 'buying_company','catalog').annotate(id__max=Max('id')).values_list('id__max', flat=True)
print "max push_user unique"
print len(max_catalog_push_user_ids)

catalog_push_user_ids = []
catalog_push_user_product_ids = []

for row in Push_User.objects.filter(catalog__isnull=False).exclude(id__in=list(max_catalog_push_user_ids)).order_by('id'):
    pupids = Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, catalog=row.catalog).values_list('id', flat=True)
    catalog_push_user_ids.append(row.id)
    catalog_push_user_product_ids.extend(pupids)
	
print "delete push_user id"
print len(catalog_push_user_ids)
print "delete push_user_product id"
print len(catalog_push_user_product_ids)

##use only want to delete
#Push_User.objects.filter(id__in=catalog_push_user_ids).delete()
#Push_User_Product.objects.filter(id__in=catalog_push_user_product_ids).delete()


###for delete duplicate selection
print " =====selection===== "
max_selection_push_user_ids = Push_User.objects.filter(selection__isnull=False).values('user','selling_company','buying_company','selection').annotate(id__max=Max('id')).values_list('id__max', flat=True)
print "max push_user unique"
print len(max_selection_push_user_ids)

selection_push_user_ids = []
selection_push_user_product_ids = []

for row in Push_User.objects.filter(selection__isnull=False).exclude(id__in=list(max_selection_push_user_ids)).order_by('id'):
    pupids = Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, selection=row.selection).values_list('id', flat=True)
    selection_push_user_ids.append(row.id)
    selection_push_user_product_ids.extend(pupids)
	
print "delete push_user id"
print len(selection_push_user_ids)
print "delete push_user_product id"
print len(selection_push_user_product_ids)

##use only want to delete
#Push_User.objects.filter(id__in=selection_push_user_ids).delete()
#Push_User_Product.objects.filter(id__in=selection_push_user_product_ids).delete()


##remove unnecessary push
print " =====push===== "
pushids = Push_User.objects.all().values_list('push', flat=True).distinct()
pids=Push.objects.all().exclude(id__in=pushids).values_list('id', flat=True)
print "delete push id"
print len(pids)
#Push.objects.filter(id__in=pids).delete()
