from api.models import *

print "catalog"
for puo in Push_User.objects.filter(catalog__isnull=False, id__gt=40000, id__lte=50000).values_list('id', flat=True).order_by('id'):
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

print "selection"
for puo in Push_User.objects.filter(selection__isnull=False, id__gt=40000, id__lte=50000).values_list('id', flat=True).order_by('id'):
	print puo
	row = Push_User.objects.filter(pk=puo).select_related('push','selling_company','buying_company','selection').first()
	buyer = Buyer.objects.filter(selling_company=row.selling_company, buying_company=row.buying_company).last()
	if buyer:
		pushUserProductObj = Push_User_Product.objects.filter(push=row.push, selling_company=row.selling_company, buying_company=row.buying_company, selection=row.selection).select_related('product')
		for pupObj in pushUserProductObj:
			if CompanyProductFlat.objects.filter(product=pupObj.product, selection=row.selection, buying_company=row.buying_company).exists():
				cpfObj = CompanyProductFlat.objects.filter(product=pupObj.product, selection=row.selection, buying_company=row.buying_company).select_related('selling_company').last()
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
				CompanyProductFlat.objects.create(product=pupObj.product, selection=row.selection, buying_company=row.buying_company, final_price=pupObj.price, selling_price=sellPrice, selling_company=row.selling_company, push_reference=row.push)
