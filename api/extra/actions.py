from django.http import HttpResponse
from django.views.generic import View
from django.core import serializers
from django.shortcuts import render
from django.http import JsonResponse
from api.models import Company, Company_User, Brand, Catalog
from django.contrib.auth.models import User

class ABC(View):
	def get(self, request):
		username = 'admin'
		request.session['username']= username
		com_user = Company_User.objects.get(user__username=username)
		if(com_user.relationship_type == 'admin'):
			comp = com_user.company
			bran = Brand.objects.filter(owning_company = comp)
			catalog = Catalog.objects.filter(brand__in = bran)
			request.session['owning_session'] = [b.id for b in bran]
			data = serializers.serialize("json", catalog, fields=('id', 'title'))
			return HttpResponse(data)
		return HttpResponse('You are not an Admin user')