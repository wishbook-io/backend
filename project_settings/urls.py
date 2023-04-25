from django.conf.urls import include, url, patterns
from django.contrib import admin

from django.views.generic import TemplateView, RedirectView
from allauth.account.views import confirm_email

from urlshortner.views import RedirectToLongURL

#from django.contrib.auth import views
###from allauth.account.views import ConfirmEmailView
###from rest_auth.registration.views import VerifyEmailView



urlpatterns = [

    url(r'^api/', include('api.v0.urls')),
    url(r'^api/v1/', include('api.v1.urls')),

    #url(r'^s/(?P<short_url>\w+)$', RedirectToLongURL.as_view(), name='redirect_short_url'),
    url(r'^s/(?P<short_url>.+)$', RedirectToLongURL.as_view(), name='redirect_short_url'),

    url(r'^api/docs/', include('rest_framework_docs.urls')),

    url(r'^api/admin/', include(admin.site.urls)),
    url(r'^api/admin/user/', include('impersonate.urls')),#impersonate
    url(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')), #for enable login at api

    url(r'^api/rest-auth/', include('rest_auth.urls')),
    url(r'^api/rest-auth/registration/', include('rest_auth.registration.urls')),

    url(r'^api/v1/auth/', include('rest_auth.urls')),
    url(r'^api/v1/auth/registration/', include('rest_auth.registration.urls')),



    url(r'^account/', include('allauth.urls')),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=True), name='profile-redirect'),

    url(r'^index.html#/verifyemail/(?P<key>\w+)/$', confirm_email,
        name="account_confirm_email"),

    url(r'^#/auth/passwordreset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name='password_reset_confirm'),

    #url(r'^index.html#/passwordresetconfirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #   TemplateView.as_view(template_name="password_reset_confirm.html"),
    #   name='password_reset_confirm'),

    #url(r'^api/rest-auth/verify-email/$', VerifyEmailView.as_view(), name='rest_verify_email'),
    #url(r'^api/rest-auth/registration/account-confirm-email/(?P<key>\w+)/$', ConfirmEmailView.as_view(template_name="../api/email/password_reset_email.html"), name='confirm_email'),

]

from django.conf import settings
from django.conf.urls.static import static
'''if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )'''
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
