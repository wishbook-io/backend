import logging

from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Min, Max, Count
from datetime import datetime, date, time, timedelta
from django.db.models import Case, When

logger = logging.getLogger(__name__)

def setPublicCatalogCache(cacheKey):
    from api.models import Catalog, CatalogSeller
    from django.core.cache import cache

    logger.info("in setPublicCatalogCache cacheKey = %s"% (cacheKey))

    queryset = Catalog.objects.filter(deleted=False, catalog_type='catalog').select_related('brand', 'category', 'company')

    logger.info("in setPublicCatalogCache catalog queryset = %s"% (queryset))

    dtnow = datetime.now()
    cscatalogids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow).values_list('catalog', flat=True).distinct()
    # ~ productcatalogs = Product.objects.filter(catalog__view_permission="public", catalog__in=cscatalogids).values_list('catalog', flat=True).distinct()
    # ~ queryset = queryset.filter(id__in=productcatalogs).order_by('-sort_order', '-id')
    queryset = queryset.filter(id__in=cscatalogids, view_permission="public", total_products_uploaded__gt=0).order_by('-sort_order', '-id')

    logger.info("in setPublicCatalogCache final queryset = %s"% (queryset))

    cache.set(cacheKey, queryset, settings.CACHE_EXPIRE_TIME)

def setPublicCatalogTrustedSellerCache(cacheKey):
    from api.models import CatalogSeller
    from django.core.cache import cache

    queryset = getCache("public")

    cscatalogids = CatalogSeller.objects.filter(catalog__in=queryset, selling_company__trusted_seller=True, selling_type="Public", status="Enable").values_list('catalog', flat=True)
    queryset = queryset.filter(id__in=list(cscatalogids)).order_by('-trusted_sort_order').distinct()

    cache.set(cacheKey, queryset, settings.CACHE_EXPIRE_TIME)

def setPublicCatalogMostViewedCache(cacheKey):
    from api.models import CompanyCatalogView
    from django.core.cache import cache

    queryset = getCache("public")

    todayDate = datetime.now()
    lastDate = todayDate - timedelta(days=7)
    ccvCatalogIds = CompanyCatalogView.objects.filter(catalog__in=queryset, created_at__gte=lastDate).values('catalog').annotate(catalog_count=Count('catalog')).order_by('-catalog_count').values_list('catalog', flat=True).distinct()
    ccvCatalogIds = list(ccvCatalogIds)[:10]
    #print "most_viewed ccvCatalogIds", ccvCatalogIds
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ccvCatalogIds)])
    queryset = queryset.filter(id__in=ccvCatalogIds).order_by(preserved)
    # print "most_viewed=",queryset

    cache.set(cacheKey, queryset, settings.CACHE_EXPIRE_TIME)

def setPublicCatalogMostOrderedCache(cacheKey):
    from api.models import SalesOrderItem
    from django.core.cache import cache

    queryset = getCache("public")

    todayDate = datetime.now()
    lastDate = todayDate - timedelta(days=30)
    soiCatalogIds = SalesOrderItem.objects.filter(sales_order__created_at__gte=lastDate, product__catalog__in=queryset).values('product__catalog').annotate(catalog_count=Count('product__catalog')).order_by('-catalog_count').values_list('product__catalog', flat=True).distinct()
    soiCatalogIds = list(soiCatalogIds)[:10]
    #print "most_ordered soiCatalogIds", soiCatalogIds
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(soiCatalogIds)])
    queryset = queryset.filter(id__in=soiCatalogIds).order_by(preserved)

    cache.set(cacheKey, queryset, settings.CACHE_EXPIRE_TIME)

def getCache(cacheKey):
    from django.core.cache import cache

    result = None
    if cacheKey:
        result = cache.get(cacheKey)
        # print "getCache -", cacheKey, "- result = ",result
        if not result:
            if "public" == cacheKey:
                logger.info("in getCache public cacheKey = %s"% (cacheKey))
                setPublicCatalogCache(cacheKey)
            elif "trusted_seller" == cacheKey:
                setPublicCatalogTrustedSellerCache(cacheKey)
            elif "most_viewed" == cacheKey:
                setPublicCatalogMostViewedCache(cacheKey)
            elif "most_ordered" == cacheKey:
                setPublicCatalogMostOrderedCache(cacheKey)

            result = cache.get(cacheKey)
            # print "getCache -", cacheKey, "- if not result = ",result

    return result

def deleteCache(cacheKey):
    from django.core.cache import cache
    
    logger.info("deleteCache = %s"% (cacheKey))
    cache.delete(cacheKey)
    if cacheKey == "public":
        cache.delete("trusted_seller")
