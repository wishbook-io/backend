from api.models import *
from api.v0.serializers import *
from django.contrib.auth.models import User, Group

from datetime import datetime, date, time, timedelta

todayDate = date.today()

currentMonthStartDate = todayDate.replace(day=1)

lastMonthEndDate = currentMonthStartDate - timedelta(days=1)
lastMonthStartDate = lastMonthEndDate.replace(day=1)

pushes = Push.objects.filter(date__gte=lastMonthStartDate).order_by('id')#.values_list('id', flat=True)

for push in pushes:
	print push.id
	Push_User_Product.objects.filter(push=push, is_viewed='yes').update(viewed_date=push.date)



