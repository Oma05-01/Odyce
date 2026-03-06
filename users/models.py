from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import string
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Customer(models.Model):
    # User handles first_name, last_name, email, and password automatically.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    is_distributor = models.BooleanField(default=False)
    coupon_code = models.CharField(max_length=6, blank=True, null=True)
    applied_coupon = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} | {self.pk}"


class MenPerfume(models.Model):
    name = models.CharField(max_length=100)  # Increased length
    pic_name = models.CharField(max_length=100)  # Changed from TextField
    picurl = models.ImageField(upload_to='perfumes/')
    description = models.TextField()  # Changed from CharField(30) for longer text
    date = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Matched Order total type
    scent = models.CharField(max_length=50)
    is_for_men = models.BooleanField(default=True)

    @property
    def reviews(self):
        from django.contrib.contenttypes.models import ContentType
        from .models import Review
        ct = ContentType.objects.get_for_model(self.__class__)
        return Review.objects.filter(content_type=ct, object_id=self.id)

    @property
    def product_type(self):
        return 'men'

    def __str__(self):
        return f"{self.name} | {self.pk}"


class WomenPerfume(models.Model):
    name = models.CharField(max_length=100)
    pic_name = models.CharField(max_length=100)
    picurl = models.ImageField(upload_to='perfumes/')
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    scent = models.CharField(max_length=50)
    is_for_women = models.BooleanField(default=True)

    @property
    def reviews(self):
        from django.contrib.contenttypes.models import ContentType
        from .models import Review
        ct = ContentType.objects.get_for_model(self.__class__)
        return Review.objects.filter(content_type=ct, object_id=self.id)

    @property
    def product_type(self):
        return 'women'

    def __str__(self):
        return f"{self.name} | {self.pk}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    billing_name = models.CharField(max_length=100)
    billing_address = models.CharField(max_length=255)
    billing_city = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=30)
    status = models.CharField(max_length=20, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    confirmed_order_code = models.CharField(max_length=7, blank=True, null=True)
    quantity = models.IntegerField(default=1)  # Note: Consider OrderItem model for multi-product carts later

    def __str__(self):
        return f"{self.billing_name}'s order going to: {self.billing_address}"

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
    rating = models.IntegerField(default=5)  # 1 to 5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.user.first_name}"


class WishlistItem(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.user.first_name}'s wishlist item: {self.product.name} (x{self.quantity})"


class Articles(models.Model):
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=255)
    content = models.TextField()
    publish_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class ContactUS(models.Model):
    # Made user nullable in case non-logged-in users want to contact you
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()  # Changed to EmailField for validation
    message = models.TextField(default='')
    date_sent = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        # This only runs when a NEW user is saved
        Customer.objects.get_or_create(user=instance)