from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PurchaseRequest(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    color1 = models.CharField(max_length=50)  # First color choice
    color2 = models.CharField(max_length=50)  # Second color choice
    created_at = models.DateTimeField(auto_now_add=True)

class ProductToMake(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    color1 = models.CharField(max_length=50)
    color2 = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
    ], default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)