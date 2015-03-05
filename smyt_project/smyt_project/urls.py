from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^edit_cell/$', 'smyt_models.views.edit_cell'),
    url(r'^$', 'smyt_models.views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),
)
