from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login', views.login_merchant),
    url(r'^register', views.register_merchant),
    url(r'^membership_new', views.membership_new),
    url(r'^membership_customer', views.membership_customer),
    url(r'^membership', views.membership),
    url(r'^trade_add', views.trade_add),
    url(r'^order_add', views.order_add),
    url(r'^punch_add', views.punch_add),
    url(r'^punch_reset', views.punch_reset),
    url(r'^shop_add', views.shop_add),
    url(r'^shop_promotion', views.shop_promotion),
    url(r'^shop', views.shop),
    # url(r'^logout', views.logout),
]
