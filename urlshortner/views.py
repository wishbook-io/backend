from django.shortcuts import render

from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.views.generic.base import RedirectView
from django.conf import settings
from .models import Link
from django.shortcuts import redirect

# Create your views here.
class LinkCreate(CreateView):
	model = Link
	fields = ["url"]

	def form_valid(self, form):
		prev = Link.objects.filter(url=form.instance.url)
		if prev:
			return redirect("link_show", pk=prev[0].pk)
		return super(LinkCreate, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(LinkCreate, self).get_context_data(**kwargs)
		# Passing link_list to display original and short_url in link_form.html
		context['link_list'] = Link.objects.all().order_by('-id')[:10]
		# Passing site_url to display domain base
		context['site_url'] = settings.SITE_URL
		return context

class LinkShow(DetailView):
	model = Link
	def get_context_data(self, **kwargs):
		context = super(LinkShow, self).get_context_data(**kwargs)
		context['site_url'] = settings.SITE_URL
		return context


class RedirectToLongURL(RedirectView):

	permanent = False

	def get_redirect_url(self, *args, **kwargs):
		short_url = kwargs["short_url"]
		short_url = short_url.rstrip(",./")
		return Link.expand(short_url)
# Create your views here.
