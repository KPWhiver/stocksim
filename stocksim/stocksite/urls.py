from django.conf.urls.defaults import patterns, include, url
from stocksite import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'stocksite.views.home', name='home'),
    # url(r'^stocksite/', include('stocksite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'stocksite.views.home'),
    url(r'^settings/$', 'stocksite.views.settings'),
    url(r'^companies/$', 'stocksite.views.companies'),
    url(r'^companies/([A-Z]+)/$', 'stocksite.views.company'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url': '/accounts/login/'}),
)
