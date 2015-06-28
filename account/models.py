from django.db import models
from django.contrib.auth.models import User, BaseUserManager
from django.contrib.auth.models import AbstractBaseUser

class MerchantManager(BaseUserManager):
 
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
  
        user = self.model(
            email = MerchantManager.normalize_email(email),
            username = username,
        )
        user.is_admin = False
        user.is_staff = False
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
     
        user = self.create_user(
            username,email,password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True


class Merchant(AbstractBaseUser):
	username = models.CharField(max_length=64, unique=True, null=False, default='')
	email = models.CharField(max_length=64, null=False, default='')
	phone = models.CharField(max_length=64, null=True, default='')
	real_name = models.CharField(max_length=256, null=False, default='')
	created_at = models.DateTimeField(auto_now_add=True)
	is_admin = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)

	USERNAME_FIELD = 'username'
	objects = MerchantManager()

	def __unicode__(self):
		return self.username

	def get_full_name(self):
		return self.email

	def get_short_name(self):
		return self.username

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	def __str__(self):

		return self.username


class Customer(models.Model):
	username = models.CharField(max_length=64, unique=True, null=False, default='')
	email = models.CharField(max_length=64, null=False, default='')
	phone = models.CharField(max_length=64, null=False, default='')
	real_name = models.CharField(max_length=256, null=False, default='')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):

		return self.username

	def save(self, force_insert=False, force_update=False):
		super(Customer, self).save(force_insert, force_update)


class Shop(models.Model):
	merchant = models.ForeignKey(Merchant)
	name = models.CharField(max_length=64, null=False)
	phone = models.CharField(max_length=64, null=False, default='')
	address = models.CharField(max_length=256, null=False, default='')
	promotion = models.CharField(max_length=256, null=False, default='')
	description = models.CharField(max_length=512, null=False, default='')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):

		return self.name

	def save(self, force_insert=False, force_update=False):
		super(Shop, self).save(force_insert, force_update)


class Trade(models.Model):
	shop = models.ForeignKey(Shop)
	customer = models.ForeignKey(Customer)
	customer_username = models.CharField(max_length=64, null=False, default='')
	trade_type = models.IntegerField(default = 0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):

		return self.customer.username

	def save(self, force_insert=False, force_update=False):
		super(Trade, self).save(force_insert, force_update)


class Order(models.Model):
	shop = models.ForeignKey(Shop)
	customer = models.ForeignKey(Customer)
	customer_username = models.CharField(max_length=64, null=False, default='')
	trade_type = models.IntegerField(default = 0)
	quantity = models.IntegerField(default = 0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):

		return self.customer.username

	def save(self, force_insert=False, force_update=False):
		super(Order, self).save(force_insert, force_update)

class Membership(models.Model):
	shop = models.ForeignKey(Shop)
	customer = models.ForeignKey(Customer)
	customer_username = models.CharField(max_length=64, null=False, default='')
	trade_type = models.IntegerField(default = 0)
	vaild_quantity = models.IntegerField(default = 0)
	used_quantity = models.IntegerField(default = 0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):

		return self.customer.username

	def save(self, force_insert=False, force_update=False):
		super(Membership, self).save(force_insert, force_update)

