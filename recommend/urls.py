from django.conf.urls import patterns, include, url
from . import views
# https://docs.djangoproject.com/en/1.11/topics/http/urls/

urlpatterns = patterns('recommend.views',
    url(r'^$', views.index),
    url(r'^purchase/$', views.purchase),
    url(r'^purchase/cancel/$', views.cancel),
    url(r'^jaccard/$', views.jaccard),
)