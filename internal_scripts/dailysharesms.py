from datetime import date, datetime, timedelta
from api.models import *
from django.db.models.functions import Concat
import random

logger.info("in dailyShareSMS")
#todayDate = date.today()
oldChObj = CronHistory.objects.filter(cron_type="dailyShareSMS").order_by('-time').first()
if oldChObj:
    lastDate = oldChObj.time + timedelta(hours = 5.5)
else:
    lastDate = datetime.now() - timedelta(days=1)
logger.info(str(lastDate))

todayDate = datetime.now()
#chObj = CronHistory.objects.create(cron_type="dailyShareSMS", time=todayDate)
logger.info(str(todayDate))
count = 0
buying_companies = Push_User.objects.filter(push__time__lte=todayDate, push__time__gte=lastDate, catalog__isnull=False).values_list('buying_company', flat=True).distinct().order_by('buying_company')
#print (Push_User.objects.filter(push__time__lte=todayDate, push__time__gte=lastDate, catalog__isnull=False))
print (buying_companies.count())
unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()

for buying_company in buying_companies:
    logger.info("buying_company id == == %s"% (str(buying_company)))
    totalcatalogs = Push_User.objects.filter(push__time__lte=todayDate, push__time__gte=lastDate, buying_company=buying_company, catalog__isnull=False).values_list('catalog', flat=True).distinct().count()

    if totalcatalogs <= 1:
        logger.info("totalcatalogs <= 1: continue --")
        continue
    print (Push_User.objects.filter(push__time__lte=todayDate, push__time__gte=lastDate, buying_company=buying_company, catalog__isnull=False))
    print (buying_company)
    users = CompanyUser.objects.filter(company=buying_company).values_list('user', flat=True).distinct()
    users = User.objects.filter(id__in=users, groups__name="administrator")
    count =  count + 1
    print (users)

print ("total users: ")
print (count)
