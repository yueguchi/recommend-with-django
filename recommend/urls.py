from django.conf.urls import patterns, include, url
from . import views
# https://docs.djangoproject.com/en/1.11/topics/http/urls/

urlpatterns = patterns('recommend.views',
    url(r'^$', views.index, name='item-list'),
    url(r'^purchase/$', views.purchase, name='item-purchase'),
    url(r'^purchase/cancel/$', views.cancel, name='item-purchase-cancel'),
    url(r'^jaccard/$', views.jaccard, name='jaccard'),
)
