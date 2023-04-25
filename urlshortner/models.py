from django.db import models

from django.core.urlresolvers import reverse
from hashids import Hashids
hashids = Hashids()

from django.conf import settings

# Create your models here.
class Link(models.Model):
	# Using this field is actually a Charfield but with a URL validator. AWESOME!
	url = models.URLField()

	def get_absolute_url(self):
		return reverse("link_show", kwargs={"pk": self.pk})

	# Encodes Url to a short url
	@staticmethod
	def shorten(link):
		l, _ = Link.objects.get_or_create(url=link.url)
		# using library to encrypt id
		return str(hashids.encrypt(l.pk))

	# Decodes short url to original url
	@staticmethod
	def expand(slug):
		# Decrypting slug and getting '(12,)'
		dirty_str = str(hashids.decrypt(slug))
		# stripping out '(,)'
		clean_id = dirty_str.strip("(,)")
		# now converting '12' into 12
		#if clean_id is None or clean_id == "":
		#	return settings.GLOBAL_SITE_URL
		try:
			link_id = int(clean_id)
			l = Link.objects.get(pk=link_id)
		except Exception as e:
			return settings.GLOBAL_SITE_URL.rstrip('/')
		return l.url

	def short_url(self):
		return reverse("redirect_short_url",
                   kwargs={"short_url": Link.shorten(self)})# Create your models here.
