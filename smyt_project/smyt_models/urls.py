from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('smyt_models.views',
    url(r'^edit_cell/$', 'edit_cell'),
    url(r'^add/$', 'add_object'),
    url(r'^table/$', 'get_table'),
    url(r'^$', 'index', name='index'),
)