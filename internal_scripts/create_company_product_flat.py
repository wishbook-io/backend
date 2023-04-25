from api.models import *

print "catalog"

start_range = raw_input("Some input please: ") 
start_range = int(start_range)
end_range = start_range + 10000

for puo in Push_User.objects.filter(catalog__isnull=False, id__gte=start_range, id__lte=end_range).values_list('id', flat=True).order_by('id'):
	print puo
	row = Push_User.objects.filter(pk=puo).select_related('push','selling_company','buying_company','catalog').first()
	buyer = Buyer.objects.filter(selling_company=row.selling_company, buying_company=row.buying_company).last()
	if buyer:
		pushUserProductObj = Push_User_Product.objects.filter(push=row.push, selling_company=row.selling_company, buying_company=row.buying_company, catalog=row.catalog).select_related('product')
		for pupObj in pushUserProductObj:
			if CompanyProductFlat.objects.filter(product=pupObj.product, catalog=row.catalog, buying_company=row.buying_company).exists():
				cpfObj = CompanyProductFlat.objects.filter(product=pupObj.product, catalog=row.catalog, buying_company=row.buying_company).select_related('selling_company').last()
				if cpfObj.final_price > pupObj.price or cpfObj.selling_company == row.selling_company:
					#print "update"
					sellPrice = (pupObj.price+buyer.fix_amount) + ((pupObj.price*buyer.percentage_amount)/100)
					cpfObj.final_price = pupObj.price
					cpfObj.selling_price = sellPrice
					cpfObj.selling_company = row.selling_company
					cpfObj.push_reference = row.push
					cpfObj.save()
			else:
				#print "create"
				sellPrice = (pupObj.price+buyer.fix_amount) + ((pupObj.price*buyer.percentage_amount)/100)
				CompanyProductFlat.objects.create(product=pupObj.product, catalog=row.catalog, buying_company=row.buying_company, final_price=pupObj.price, selling_price=sellPrice, selling_company=row.selling_company, push_reference=row.push)
