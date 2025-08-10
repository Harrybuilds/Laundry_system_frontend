from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    
    USER_TYPE = (
        ('staff', 'STAFF'),
        ('customer', 'CUSTOMER')
    )
    user_type = models.CharField(max_length=8, default='customer')
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(unique=True, blank=False)
    created_at = models.DateField(auto_now_add=True)
    phone = models.CharField(max_length=12, unique=True)
    password = models.CharField(max_length=81)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.email} {self.user_type} {self.is_staff}'


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(default='')


class StaffProfile(models.Model):
    ROLES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='staff')
    is_available = models.BooleanField(default=True)
