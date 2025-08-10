from django.db import models
from uuid import uuid4 as uuid
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal


# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid())
    email = models.CharField(max_length=60, unique=True)
    phone_number = models.CharField(max_length=13, unique=True)

    USERNAME_FIELD =  'email'
    REQUIRED_FIELDS = ['username']


class Room(models.Model):
    ROOM_TYPE = (
        ('standard', 'STANDARD'),
        ('deluxe', 'DELUXE'),
        ('suite', 'SUITE')
    )

    DEFAULT_PRICE = {
        'standard': Decimal(100.00),
        'deluxe': Decimal(200.00),
        'suite': Decimal(300)
    }

    id = models.AutoField(primary_key=True)
    room_no = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(default='', blank=True)
    category = models.CharField(max_length=15, choices=ROOM_TYPE, default='standard')
    available = models.BooleanField(default=True)


    """def clean(self):
        if self.is_available_from and self.is_available_to:
            if self.is_available_from > self.is_available_to:
                raise ValidationError('available_from must be before available_to')
            
        
    def is_available_for(self, check_in, check_out):
        if not self.available:
            return False
        return self.is_available_from <= check_in and self.is_available_to >= check_out"""


    def save(self, *args, **kwargs):
        if not self.room_no:
            last_room = Room.objects.order_by('-id'). first()
            next_number = 1 if not last_room else last_room.id + 1
            self.room_no = f'RM {str(next_number).zfill(3)}'
        if not self.price:
            self.price = self.DEFAULT_PRICE.get(self.category, Decimal('0.00'))
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f''' room_number: {self.room_no}
        category: {self.category}
        cost: {self.price}
        availability: {self.available}'''



class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='booking')
    guest_name = models.CharField(max_length=100)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'''{self.room}, checkin: {self.check_in}, checkout: {self.check_out}'''