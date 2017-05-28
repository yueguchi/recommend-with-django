from django.conf.urls import patterns, include, url

urlpatterns = patterns('recommend.views',
    url(r'^$', 'index', name='item-list'),
    url(r'^purchase/$', 'purchase', name='item-purchase'),
)