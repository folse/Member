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
		responese['msg'] = 'login faild'
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
            name=request.GET['name'],
            phone=request.GET['phone'],
            address=request.GET['address'],
            description=request.GET['description']
            )
		shop.save()
		responese['resp'] = '0000'
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'add shop faild'
	return HttpResponse(json.dumps(responese))

@login_required
def shop(request):
	responese = {}
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
			members.append(member)
		data['members'] = members
		responese['resp'] = '0000'
		responese['data'] = data
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'get membership faild'
	return HttpResponse(json.dumps(responese))

@login_required
def shop_promotion(request):
	responese = {}
	if True:
		data = {}
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		shop.promotion = request.GET['promotion']
		shop.save()
		responese['resp'] = '0000'
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'update promotion faild'
	return HttpResponse(json.dumps(responese))

@login_required
def membership_new(request):
	responese = {}
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
	            phone=request.GET['phone']
	            )
			customer.save()

		memberships = Membership.objects.filter(shop = shop, customer = customer)
		if memberships.exists():
			responese['resp'] = '0003'
			responese['msg'] = 'This customer already exist'
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
-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "Valkommen till '+ shop.name +' kundklubb. Du nu del av butikens erbjudanden och kan direkt till din mobil.Grattis, du har nu laddat upp med ' + request.GET['quantity'] + 'poäng.", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'

			message = os.popen(sms_cmd).readline()

			print message

			responese['msg'] = message
			responese['resp'] = '0000'
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'add membership faild'
	return HttpResponse(json.dumps(responese))

@login_required
def membership(request):
	responese = {}
	data = {}
	shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
	customer = Customer.objects.filter(username=request.GET['customer_username'])[0]
	memberships = Membership.objects.filter(shop = shop, customer = customer)
	if memberships.exists():
		membership = memberships[0]
		data['vaild_quantity'] = membership.vaild_quantity
		data['used_quantity'] = membership.used_quantity
		data['punched_quantity'] = membership.punched_quantity
		responese['resp'] = '0000'
		responese['data'] = data
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(responese))

@login_required
def trade_add(request):
	responese = {}
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
-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "You just traded at '+ shop.name +' ", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'

				message = os.popen(sms_cmd).readline()
				print message

				responese['msg'] = message
				responese['resp'] = '0000'
			else:
				responese['resp'] = '0005'
				responese['msg'] = 'Fel, ckligt' #There is no enough quantity
		else:
			responese['resp'] = '0004'
			responese['msg'] = 'This user has no membership with this shop'
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(responese))

@login_required
def punch_add(request):
	responese = {}
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
			responese['punched_quantity'] = membership.punched_quantity

			sms_cmd = 'curl -H "Authorization: Token f1205211a7f4f97331eca4f78ced18cf2304298bca79f782a03f051132576b91" \
-H "Content-Type: application/json" \
-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "Välkommen till '+ shop.name +'. Du har nu samlat ' + request.GET['quantity'] + ' poäng, samla ihop lite fler så får du del av våra specialerbjudanden. För mer info så kan du kontakta '+ shop.name +'.", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'

			message = os.popen(sms_cmd).readline()

			print message

			responese['resp'] = '0000'
		else:
			responese['resp'] = '0004'
			responese['msg'] = 'This user has no membership with this shop'
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(responese))

@login_required
def punch_reset(request):
	responese = {}
	if True:
		shop = Shop.objects.filter(id=request.GET['shop_id'])[0]
		customers = Customer.objects.filter(username=request.GET['customer_username'])
		if customers.exists():
			# add a new membership record
			customer = customers[0]
			membership = Membership.objects.filter(customer = customer)[0]
			membership.punched_quantity = 0
			membership.save()

			responese['resp'] = '0000'
		else:
			responese['resp'] = '0004'
			responese['msg'] = 'no this customer'
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	return HttpResponse(json.dumps(responese))

@login_required
def order_add(request):
	responese = {}
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
-X POST -d \'{"to": "46' + request.GET['customer_username'][1:] +'", "message": "Tack för att du handlar hos '+ shop.name +'. Du har nu ' + request.GET['quantity'] + ' poäng kvar påditt konto hos oss, ladda upp med fler poäng sådu inte missar ut pånågot bra erbjudande. För mer information såkan du kontakta '+ shop.name +'.", "from": "Kundsystem", "encoding": "UTF-8", "receive_dlr": 0}\' \
"https://api.beepsend.com/2/send/"'

			message = os.popen(sms_cmd).readline()

			print message

			responese['resp'] = '0000'
		else:
			responese['resp'] = '0006'
			responese['msg'] = 'Fel, Denna medlem har inte registrerats innan' #This membership does not exist
	else:
		responese['resp'] = '0001'
		responese['msg'] = 'add order faild'
	return HttpResponse(json.dumps(responese))

