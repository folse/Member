from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from account.models import Merchant, Customer, Shop, Trade, Order, Membership

import json

def register_merchant(request):
	responese = {}
	responese['resp'] = '0000'
	email = request.GET['email']
	username = request.GET['email']
	password = request.GET['password']
	if Merchant.objects.create_user(username,email,password) is not None:
		responese['resp'] = '0000'
	else :
		responese['resp'] = '0001'
	return HttpResponse(json.dumps(responese), content_type="application/json")

def login_merchant(request):
	responese = {}
	username = request.GET['username']
	password = request.GET['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		shop = Shop.objects.filter(merchant=user)[0]
		responese['resp'] = '0000'
		responese['shop_id'] = '%s' % shop.id
	else:
		responese['resp'] = '0001'
	return HttpResponse(json.dumps(responese))

# def logout(request):
# 	responese = {}
# 	responese['resp'] = '0000'
# 	return HttpResponse(json.dumps(responese), content_type="application/json") 

@login_required
def shop_add(request):
	responese = {}
	if True:
		print request.body
		shop = Shop(
            merchant=request.user,
            name=request.REQUEST.get('name'),
            phone=request.REQUEST.get('phone'),
            address=request.REQUEST.get('address'),
            description=request.REQUEST.get('description')
            )
		shop.save()
		responese['resp'] = '0000'
	else:
		responese['resp'] = '0001'
	return HttpResponse(json.dumps(responese))

@login_required
def membership_new(request):
	responese = {}
	if True:
		shop = Shop.objects.filter(id=request.REQUEST.get('shop_id'))[0]
		customers = Customer.objects.filter(username=request.REQUEST.get('customer_username'))
		if len(customers) == 0:
			# create new customer
			customer = Customer(
	            username=request.REQUEST.get('customer_username'),
	            email=request.REQUEST.get('email'),
	            phone=request.REQUEST.get('phone')
	            )
			customer.save()

			# create new membership
			membership = Membership(
            shop=shop,
            customer=customer,
            customer_username = request.REQUEST.get('customer_username'),
            vaild_quantity = 0,
            used_quantity = 0,
            trade_type = request.REQUEST.get('trade_type')
            )
			membership.save()

			responese['resp'] = '0000'
		else :
			responese['resp'] = '0003'
			responese['msg'] = 'This user info already exist'
	else:
		responese['resp'] = '0001'
	return HttpResponse(json.dumps(responese))

@login_required
def membership(request):
	responese = {}
	if True:
		data = {}
		shop = Shop.objects.filter(id=request.REQUEST.get('shop_id'))[0]
		customer = Customer.objects.filter(username=request.REQUEST.get('customer_username'))[0]
		membership = Membership.objects.filter(shop = shop, customer = customer, trade_type=request.REQUEST.get('trade_type'))[0]
		data['vaild_quantity'] = membership.vaild_quantity
		data['used_quantity'] = membership.used_quantity
		responese['resp'] = '0000'
		responese['data'] = data
	else:
		responese['resp'] = '0001'
	return HttpResponse(json.dumps(responese))

@login_required
def trade_add(request):
	responese = {}
	if True:
		shop = Shop.objects.filter(id=request.REQUEST.get('shop_id'))[0]
		customer = Customer.objects.filter(username=request.REQUEST.get('customer_username'))[0]
		quantity = request.REQUEST.get('quantity')
		membership_records = Membership.objects.filter(shop=shop, customer=customer,trade_type=request.REQUEST.get('trade_type'))
		if len(membership_records) > 0:
			# update membership info
			membership = membership_records[0]
			if membership.vaild_quantity - quantity >= 0:
				membership.vaild_quantity -= quantity
				membership.used_quantity += quantity
				membership.save()

				# add a new trade record
				trade = Trade(
	            shop=shop,
	            customer=customer,
	            customer_username=request.REQUEST.get('customer_username'),
	            trade_type=request.REQUEST.get('trade_type')
	            )
				trade.save()
				responese['resp'] = '0000'
			else:
				responese['resp'] = '0005'
				responese['msg'] = 'There is no enough quantity'
		else:
			responese['resp'] = '0004'
			responese['msg'] = 'This user has no membership with this shop'
	else:
		responese['resp'] = '0001'
	return HttpResponse(json.dumps(responese))

@login_required
def order_add(request):
	responese = {}
	if True:
		shop = Shop.objects.filter(id=request.REQUEST.get('shop_id'))[0]
		customer = Customer.objects.filter(username=request.REQUEST.get('customer_username'))[0]
		order = Order(
            shop = shop,
            customer = customer,
            quantity = request.REQUEST.get('quantity'),
            trade_type = request.REQUEST.get('trade_type')
            )
		order.save()

		membership_records = Membership.objects.filter(customer = customer,trade_type=request.REQUEST.get('trade_type'))
		if len(membership_records) > 0:
			# add a new membership record
			membership = membership_records[0]
			membership.vaild_quantity += int(request.REQUEST.get('quantity'))

			responese['resp'] = '0000'

		else:

			responese['resp'] = '0006'
			responese['msg'] = 'No membership record'
	else:
		responese['resp'] = '0001'
	return HttpResponse(json.dumps(responese))

