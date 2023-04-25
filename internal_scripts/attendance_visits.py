from api.models import *
from django.contrib.auth.models import User, Group


meetings = Meeting.objects.filter(company__isnull=True).order_by('id')

for meeting in meetings:
	print meeting.id
	try:
		meeting.company=meeting.user.companyuser.company
		meeting.save()
	except Exception:
		pass
	
attendances = Attendance.objects.filter(company__isnull=True).order_by('id')

for attendance in attendances:
	print attendance.id
	try:
		attendance.company=attendance.user.companyuser.company
		attendance.save()
	except Exception:
		pass
	
