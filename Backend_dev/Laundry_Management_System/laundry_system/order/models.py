from django.db import models
from django.conf import settings
from laundryservice.models import LaundryService, ServiceType, ServicePricing, Garment
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.
class Order(models.Model):
    STATUS_ORDER = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered')
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    pickup_time = models.DateTimeField(blank=True)
    address = models.TextField(default='')
    order_status = models.CharField(max_length=15, choices=STATUS_ORDER, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total_cost(self):
        """
        Calculate and update the total price of the order
        by summing the total prices of all associated order items.

        Each order item’s total price = quantity * unit price.
        """
        
        total = sum(item.total_cost for item in self.order_items.all())
        self.total_cost = total

        self.save()
        return self.total_cost

    def __str__(self):
        return f'{self.customer.email} {self.pickup_time} {self.order_status} {self.total_cost}'

    """def save(self, *args, **kwargs):
        super().save(*args, **kwargs)"""


class OrderItem(models.Model):
    ORDER_ITEM_STATUS = {
        'pending': 'Pending',
        'processing': 'Processing',
        'completed': 'Completed',
        'delivered': 'Delivered'
    }
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    service = models.ForeignKey(LaundryService, on_delete=models.PROTECT)
    item_name = models.ForeignKey(Garment, on_delete=models.PROTECT)
    item_status = models.CharField(max_length=15, default=ORDER_ITEM_STATUS.get('pending'))
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2) # snapshot of price at order time
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(help_text='Delivery time in hours')
    
    
    @property
    def delivery_time(self):
        return self.created_at + self.duration


    @property
    def time_remaining(self):
        return self.delivery_time - timezone.now()
    
    def __str__(self):
        return f'{self.order.customer} {self.service.name} {self.item_name.name} {self.quantity} ({self.service_type.name})'

    @property
    def total_cost(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        pricing = ServicePricing.objects.filter(
            service_name=self.service,
            service_type=self.service_type,
            service_item=self.item_name
        ).first()

        price = pricing.price if pricing else 0.00 
        #delivery_time = pricing.duration if pricing else timedelta(days=3)
       
        self.price = price
        self.total_price = self.total_cost
        #self.delivery_time = self.delivery_time

        super().save(*args, **kwargs)
    

class Invoice(models.Model):
    order = models.OneToOneField(Order, related_name='invoice_items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)