from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login', views.login_merchant),
    url(r'^register', views.register_merchant),
    url(r'^membership_new', views.membership_new),
    url(r'^membership', views.membership),
    url(r'^trade_add', views.trade_add),
    url(r'^order_add', views.order_add),
    url(r'^shop_add', views.shop_add),
    # url(r'^logout', views.logout),
]
