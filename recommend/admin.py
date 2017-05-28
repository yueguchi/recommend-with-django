from django.contrib import admin
from recommend.models import Users, Categories, Items, Purchases

admin.site.register(Users)
admin.site.register(Categories)
admin.site.register(Items)
admin.site.register(Purchases)