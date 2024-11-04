from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import string
import random
# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(default='pass@gmail.com', unique=True)
    password = models.CharField(max_length=20, default='')
    phone_number = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    is_distributor = models.BooleanField(default=False)
    coupon_code = models.CharField(max_length=6)
    applied_coupon = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.first_name} | {self.last_name} | {self.pk}"


class MenPerfume(models.Model):
    name = models.CharField(max_length=30)
    pic_name = models.TextField()
    picurl = models.ImageField(upload_to='perfumes/')
    description = models.CharField(max_length=30)
    date = models.DateField(auto_now_add=True)
    price = models.IntegerField(default=0)
    scent = models.CharField(max_length=20)
    is_for_men = models.BooleanField(default=True)
    product_type = 'men'

    def __str__(self):
        return f"{self.name} | {self.pk} | {self.is_for_men}"


class WomenPerfume(models.Model):
    name = models.CharField(max_length=30)
    pic_name = models.TextField()
    picurl = models.ImageField(upload_to='perfumes/')
    description = models.CharField(max_length=30)
    date = models.DateField(auto_now_add=True)
    price = models.IntegerField(default=0)
    scent = models.CharField(max_length=20)
    is_for_women = models.BooleanField(default=True)
    product_type = 'women'

    def __str__(self):
        return f"{self.name} | {self.pk} | {self.is_for_women}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    billing_name = models.CharField(max_length=30)
    billing_address = models.CharField(max_length=60)
    billing_city = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30)
    status = models.CharField(max_length=10, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    confirmed_order_code = models.CharField(max_length=7, blank=True, null=True)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.billing_name}'s order going to : {self.billing_address}"

    def generate_confirmation_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    def confirm_order(self):
        self.status = 'confirmed'
        self.confirmed_order_code = self.generate_confirmation_code()
        self.save()


class Review(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.first_name}"


class WishlistItem(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)

    # ContentType and object_id define the GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user}'s wishlist item: {self.product} (x{self.quantity})"


class ConfirmedOrders(models.Model):
    pass


class Articles(models.Model):
    title = models.CharField(max_length=30)
    summary = models.CharField(max_length=45)
    content = models.TextField()
    publish_date = models.DateField(auto_now_add=True)


class ContactUS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    message = models.TextField(default='')
    date_sent = models.DateField(auto_now_add=True)

    def full_name(self):
        return f"{self.user.first_name} | {self.user.last_name}"
