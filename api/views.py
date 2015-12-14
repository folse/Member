# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from account.models import Merchant, Customer, Shop, Trade, Order, Membership

import os,sys,json

reload(sys)
sys.setdefaultencoding('utf-8')

def register_merchant(request):
	response = {}
	response['resp'] = '0000'
	email = request.GET['email']
	username = request.GET['email']
	password = request.GET['password']
	if Merchant.objects.create_user(username,email,password) is not None:
		response['resp'] = '0000'
	else :
		response['resp'] = '0001'
	return HttpResponse(json.dumps(response))

def login_merchant(request):
	response = {}
	username = request.GET['username']
	password = request.GET['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		shop = Shop.objects.filter(merchant=user)[0]
		response['resp'] = '0000'
		response['shop_id'] = '%s' % shop.id
		response['shop_name'] = '%s' % shop.name
	else:
		response['resp'] = '0001'
		response['msg'] = 'login faild'
	return HttpResponse(json.dumps(response))

# def logout(request):
# 	response = {}
# 	response['resp'] = '0000'
# 	return HttpResponse(json.dumps(response)) 

@login_required
def shop_add(request):
	response = {}
	if True:
		print request.body
		shop = Shop(
            merchant=request.user,
            name=request.GET['name'],
            phone=request.GET['phone'],
            address=request.GET['address'],
            description=request.GET['description']
            )
		shop.save()
		response['resp'] = '0000'
	else:
		response['resp'] = '0001'
		response['msg'] = 'add shop faild'
	return HttpResponse(json.dumps(response))

@login_required
def shop(request):
	response = {}
	if True:
		data = {}
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		memberships = Membership.objects.filter(shop = shop)
		data['name'] = shop.name
		data['promotion'] = shop.promotion
		members = []
		for membership in memberships :
			member = {}
			member['username'] = membership.customer_username
			member['vaild_quantity'] = membership.vaild_quantity
			member['punched_quantity'] = membership.punched_quantity
			members.append(member)
		data['members'] = members
		response['resp'] = '0000'
		response['data'] = data
	else:
		response['resp'] = '0001'
		response['msg'] = 'get membership faild'
	return HttpResponse(json.dumps(response))

@login_required
def shop_promotion(request):
	response = {}
	if True:
		data = {}
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		shop.promotion = request.GET['promotion']
		shop.save()
		response['resp'] = '0000'
	else:
		response['resp'] = '0001'
		response['msg'] = 'update promotion faild'
	return HttpResponse(json.dumps(response))

@login_required
def membership_new(request):
	response = {}
	if True:
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		customers = Customer.objects.filter(username=request.GET['customer_username'])
		if customers.exists():
			customer = customers[0]
		else:
			# create new customer
			customer = Customer(
	            username=request.GET['customer_username'],
	            email=request.GET['email'],
	            phone=request.GET['phone'],
	            real_name=request.GET['real_name']
	            )
			customer.save()

		memberships = Membership.objects.filter(shop = shop, customer = customer)
		if memberships.exists():
			response['resp'] = '0003'
			response['msg'] = 'This customer already exist'
		else :
			# create new membership
			membership = Membership(
	        	shop=shop,
	            customer=customer,
	            customer_username = request.GET['customer_username'],
	            vaild_quantity = request.GET['quantity'],
	            used_quantity = 0
	        )
			membership.save()

			sms_cmd = 'curl -H "Authorization: Token f1205211a7f4f97331eca4f78ced18cf2304298bca79f782a03f051132576b91" \
-H "Content-Type: application/json" \
-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "Valkommen till '+ shop.name +' kundklubb. Grattis, du har nu laddat upp med ' + request.GET['quantity'] + 'poäng.hos oss. Du får nu del av butikens erbjudanden och kan även fåerbjudanden direkt till din mobil.", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'

			message = os.popen(sms_cmd).readline()

			print message

			response['msg'] = message
			response['resp'] = '0000'
	else:
		response['resp'] = '0001'
		response['msg'] = 'add membership faild'
	return HttpResponse(json.dumps(response))

def membership_customer(request):
	response = {}
	data = {}
	memberships = []
	customer = Customer.objects.filter(username=request.GET['customer_username'])[0]
	memberships_data = Membership.objects.filter(customer = customer)
	for membership_data in memberships_data :
		membership = {}
		shop = Shop.objects.filter(id=membership_data.shop_id)[0]
		membership['shop_name'] = shop.name
		membership['vaild_quantity'] = membership_data.vaild_quantity
		membership['punched_quantity'] = membership_data.punched_quantity
		memberships.append(membership)
	data['memberships'] = memberships
	response['resp'] = '0000'
	response['data'] = data
	return HttpResponse(json.dumps(response))

@login_required
def membership(request):
	response = {}
	data = {}
	shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
	customer = Customer.objects.filter(username=request.GET['customer_username'])[0]
	memberships = Membership.objects.filter(shop = shop, customer = customer)
	if memberships.exists():
		membership = memberships[0]
		data['real_name'] = customer.real_name
		data['used_quantity'] = membership.used_quantity
		data['vaild_quantity'] = membership.vaild_quantity
		data['punched_quantity'] = membership.punched_quantity
		response['resp'] = '0000'
		response['data'] = data
	else:
		response['resp'] = '0001'
		response['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(response))

@login_required
def trade_add(request):
	response = {}
	if True:
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		quantity = int(request.GET['quantity'])
		customers = Customer.objects.filter(username=request.GET['customer_username'])
		if customers.exists():
			# add a new membership record
			customer = customers[0]
			membership = Membership.objects.filter(customer = customer)[0]
			if (membership.vaild_quantity - quantity) >= 0:
				membership.vaild_quantity -= quantity
				membership.used_quantity += quantity
				membership.save()

				# add a new trade record
				trade = Trade(
	            	shop=shop,
	            	customer=customer,
	            	customer_username=request.GET['customer_username'],
	            	trade_type=request.GET['trade_type']
	            )
				trade.save()
				
				sms_cmd = 'curl -H "Authorization: Token f1205211a7f4f97331eca4f78ced18cf2304298bca79f782a03f051132576b91" \
-H "Content-Type: application/json" \
-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "Tack för att du handlar hos '+ shop.name +'. Du har nu ' + str(membership.vaild_quantity) + ' poäng kvar på ditt konto hos oss, ladda på ditt konto för fler erbjudanden.", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'

				message = os.popen(sms_cmd).readline()
				print message

				response['msg'] = message
				response['resp'] = '0000'
			else:
				response['resp'] = '0005'
				response['msg'] = 'Fel, ckligt' #There is no enough quantity
		else:
			response['resp'] = '0004'
			response['msg'] = 'This user has no membership with this shop'
	else:
		response['resp'] = '0001'
		response['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(response))

@login_required
def punch_add(request):
	response = {}
	if True:
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		customers = Customer.objects.filter(username=request.GET['customer_username'])
		if customers.exists():
			# add a new membership record
			customer = customers[0]
			membership = Membership.objects.filter(customer = customer)[0]
			membership.punched_quantity += 1
			membership.save()

			# add a new trade record
			trade = Trade(
            	shop=shop,
            	customer=customer,
            	customer_username=request.GET['customer_username'],
            	trade_type=request.GET['trade_type']
            )
			trade.save()

			if request.GET['need_send_punch_notification'] == 'True':

				sms_cmd = 'curl -H "Authorization: Token f1205211a7f4f97331eca4f78ced18cf2304298bca79f782a03f051132576b91" \
					-H "Content-Type: application/json" \
					-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "Välkommen till '+ shop.name +'. Du har nu samlat ihop 1 poäng, samla ihop mer för en trevlig belöning", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
					"https://api.beepsend.com/2/send/"'

				message = os.popen(sms_cmd).readline()

				print message

			response['resp'] = '0000'
		else:
			response['resp'] = '0004'
			response['msg'] = 'This user has no membership with this shop'
	else:
		response['resp'] = '0001'
		response['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(response))

@login_required
def punch_reset(request):
	response = {}
	if True:
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		customers = Customer.objects.filter(username=request.GET['customer_username'])
		if customers.exists():
			# add a new membership record
			customer = customers[0]
			membership = Membership.objects.filter(customer = customer)[0]
			membership.punched_quantity = 0
			membership.save()

			response['resp'] = '0000'
		else:
			response['resp'] = '0004'
			response['msg'] = 'no this customer'
	else:
		response['resp'] = '0001'
		response['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(response))

@login_required
def order_add(request):
	data = {}
	response = {}
	if True:
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		customers = Customer.objects.filter(username=request.GET['customer_username'])
		if customers.exists():
			# add a new membership record
			customer = customers[0]
			membership = Membership.objects.filter(customer = customer)[0]
			membership.vaild_quantity += int(request.GET['quantity'])
			membership.save()
			
			order = Order(
            	shop = shop,
            	customer = customer,
            	customer_username = customer.username,
            	quantity = request.GET['quantity'],
            	trade_type = request.GET['trade_type']
            )
			order.save()

			sms_cmd = 'curl -H "Authorization: Token f1205211a7f4f97331eca4f78ced18cf2304298bca79f782a03f051132576b91" \
-H "Content-Type: application/json" \
-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "Grattis, du har nu laddat på med ' + request.GET['quantity'] + ' poäng, och ' + str(membership.vaild_quantity) + ' poäng kvar påditt konto hos '+ shop.name +'", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'

			message = os.popen(sms_cmd).readline()

			print message

			data['vaild_quantity'] = membership.vaild_quantity
			response['data'] = data
			response['resp'] = '0000'
			
		else:
			response['resp'] = '0006'
			response['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	else:
		response['resp'] = '0001'
		response['msg'] = 'add order faild'
	return HttpResponse(json.dumps(response))

@login_required
def send_sms(request):
	data = {}
	response = {}
	memberships = Membership.objects.filter(shop_id=request.GET['shop_id'])
	for membership in memberships :
		sms_cmd = 'curl -H "Authorization: Token f1205211a7f4f97331eca4f78ced18cf2304298bca79f782a03f051132576b91" \
-H "Content-Type: application/json" \
-X POST -d \'{"to": "46' + membership.customer_username +'", "message": "'+ request.GET['content'] +'", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'
		message = os.popen(sms_cmd).readline()
		print message
		
	response['data'] = data
	response['resp'] = '0000'
	return HttpResponse(json.dumps(response))
