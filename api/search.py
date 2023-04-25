from api.models import *
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Integer, Completion
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch


#connections.create_connection()
connections.create_connection(hosts=[settings.ELASTICSEARCH_HOST])

class CatalogIndex(DocType):
	title = Text()
	brand = Text()
	category = Text()
	work = Text()
	fabric = Text()

	company = Text()
	stitching_type = Text()
	min_price = Integer()
	max_price = Integer()
	sellers = Text()
	catalog_suggest = Completion()
	class Meta:
		index = 'catalog-index'

#for old models indexing
'''
def bulk_indexing():
	from api.models import Catalog
	CatalogIndex.init()
	es = Elasticsearch(settings.ELASTICSEARCH_HOST)
	bulk(client=es, actions=(b.indexing() for b in Catalog.objects.filter(view_permission="public").iterator()))
'''

def bulk_indexing():
	from api.models import Catalog
	from api.models import CatalogSeller
	CatalogIndex.init()
	es = Elasticsearch(settings.ELASTICSEARCH_HOST)
	catalogids = CatalogSeller.objects.filter(selling_type="Public", status="Enable").values_list('catalog', flat=True).distinct().order_by('catalog')
	#print list(catalogids)

	bulk(client=es, actions=(b.indexing() for b in Catalog.objects.filter(id__in=catalogids).iterator()))

	for catalog in list(catalogids):
		seller_names = CatalogSeller.objects.filter(catalog=catalog, selling_type="Public", status="Enable").values_list('selling_company__name', flat=True)
		if len(seller_names) > 1:
			obj = CatalogIndex.get(id=catalog, ignore=404)
			print "CatalogIndex =",obj
			if obj:
				print "seller_names =", seller_names
				obj.update(sellers=list(seller_names))

	print "total catalogs=",len(catalogids)
