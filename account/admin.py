from django.contrib import admin

from .models import Merchant, Customer, Shop, Trade, Order

admin.site.register(Shop)
admin.site.register(Trade)
admin.site.register(Order)
admin.site.register(Merchant)
admin.site.register(Customer)