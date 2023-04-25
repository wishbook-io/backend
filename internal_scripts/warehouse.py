from api.models import *

stocks = Stock.objects.filter(company__isnull=True).order_by('id')
for stock in stocks:
	print "Stock id =", stock
	try:
		stock.company = stock.warehouse.company
		stock.save()
	except Exception as e:
		logger.info("Stock in Exception error")
		logger.info(str(e))


stocks = OpeningStock.objects.filter(company__isnull=True).order_by('id')
for stock in stocks:
	print "OpeningStock id =", stock
	try:
		stock.company = stock.warehouse.company
		stock.save()
	except Exception as e:
		logger.info("OpeningStock in Exception error")
		logger.info(str(e))

stocks = InventoryAdjustment.objects.filter(company__isnull=True).order_by('id')
for stock in stocks:
	print "InventoryAdjustment id =", stock
	try:
		stock.company = stock.warehouse.company
		stock.save()
	except Exception as e:
		logger.info("InventoryAdjustment in Exception error")
		logger.info(str(e))
	
