from api.models import *

Company.objects.all().update(phone_number_verified='yes')
