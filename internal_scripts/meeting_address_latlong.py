from api.models import *


meetings = Meeting.objects.filter(buying_company_ref__isnull=False).order_by('id')
for meeting in meetings:
	print "meeting id =",meeting.id
	if meeting.buying_company_ref.address:
		if meeting.buying_company_ref.address.latitude is None:
			print "address id =",meeting.buying_company_ref.address.id
			meeting.buying_company_ref.address.latitude = meeting.start_lat
			meeting.buying_company_ref.address.longitude = meeting.start_long
			meeting.buying_company_ref.address.save()



