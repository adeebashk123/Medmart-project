from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.contrib.auth.models import AbstractUser

class meduser1(AbstractUser):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    email1 = models.CharField(max_length=50)
    phoneno1 = models.CharField(max_length=14)
    address1 = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username

class MedManager(models.Manager):
    def search(self, query):
        if query:
            return self.get_queryset().filter(models.Q(name__exact=query) | models.Q(breed__exact=query))



class Medicine(models.Model):
    name = models.CharField(max_length=200, validators=[RegexValidator(regex=r'^[a-zA-Z\s]+$', message="Name can contain only alphabets and spaces", code="invalid_name")])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(100, message="The minimum priced medicine should be 100 rupees.")])
    company_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to='medicine_images/', blank=True, null=True)
    user = models.ForeignKey(meduser1, null=True, blank = True, on_delete=models.CASCADE)
    objects = MedManager()

    class Meta:
        permissions = [
            ('can_add_medicine', 'Can add a medicine'), 
            ('can_update_medicine', 'Can update a medicine')
        ]
        
class health_Product(models.Model):
    product_name = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^[a-zA-Z\s]+$', message="Product Name can contain only alphabets and spaces", code="invalid_product_name")])
    category = models.CharField(max_length=15)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(500, message="The minimum priced health product should be 500 rupees.")])
    quantity_in_stock = models.IntegerField()
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='product_images/')
    user = models.ForeignKey(meduser1, null=True, blank = True, on_delete=models.CASCADE)

from django.db import models
from .models import meduser1, Medicine

class Order(models.Model):
    user = models.ForeignKey(meduser1, null=True, blank=True, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING'
    )
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True) 
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)  # ✅ Allow NULL
    product = models.ForeignKey(health_Product, on_delete=models.SET_NULL, null=True, blank=True)    # ✅ Allow NULL
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.quantity} x {self.medicine.name} in Order {self.order.id}"



class Payments(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=15)
    amout = models.DecimalField(max_digits=10, decimal_places=2)
    
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

from django.utils.timezone import now 

class Cart(models.Model):
    user = models.ForeignKey(meduser1, on_delete=models.CASCADE)  # Check the actual field name
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(health_Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meduser.username}'s Cart Item"

