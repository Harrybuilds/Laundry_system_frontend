from django.db import models
from datetime import timedelta

# Create your models here.
class LaundryService(models.Model):
    """
    This is the base service. It represents each service your laundry business offers,
    for example “Wash & Fold,” “Dry Cleaning,” “Ironing,” etc.

    args:
        name: Unique service name.

        description: Optional details about the service.
        """
    name = models.CharField(max_length=100, unique=True)
    description =models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} {self.description[:10]}'


class Garment(models.Model):  # e.g., shirt, jean
    """
    This represent the different clothing items for laundry services
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return f'{self.name}'


class ServiceType(models.Model): # standard, express, premium
    """
    This is the model that represent the diffent service_type a certain service can have.
    e.g
        Express: A LaundryService can be an express service 
        Standard: A LaundryService can be a standard service

    args:
        name:
        description
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)


class ServicePricing(models.Model):
    """
    Pricing information for a specific combination of LaundryService,
    ServiceType, and Garment.
    """
    service_name = models.ForeignKey(LaundryService, related_name='services', on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, related_name='servicetypes', on_delete=models.CASCADE)
    service_item = models.ForeignKey(Garment, related_name='garments', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    duration = models.DurationField(help_text='Estimated delivery time in hours', default=timedelta(days=3))
    is_active = models.BooleanField(default=True)

    class Meta:
        """
        Goal: prevent duplication of specific combinations of fields so as to prevents conflicting or duplicate data.
        This means that I cannot insert duplicate rows where the three fields have the same values

        e.g: Let's say I have a LaundryService called "Wash & Fold". and I defining different options for it.

            I can do this:
            | LaundryService | ServiceType | serviceItem  | Price | Duration |
            | -------------- | ----------- | -----------  | ----- | -------- |
            | Wash & Fold    | standard    |    shirt     |  300  |  3 days  |
            | Wash & Fold    | standard    |    jean      |  500  |  3 days  |
            | Wash & Fold    | express     |    shirt     |  500  |  2 days  |
            | Wash & Fold    | express     |    jean      |  800  |  2 days  |
            | Wash & Fold    | premium     |    shirt     | 1000  |  1 day   |
            | Wash & Fold    | premium     |    jean      | 2000  |  1 day   |

            if I try to create another "Wash & Fold" + "express" + "shirt" again, say

            | LaundryService | ServiceType | serviceItem  | Price | Duration |
            | -------------- | ----------- | -----------  | ----- | -------- |
            | Wash & Fold    | standard    |    shirt     |  .... |  ......  |
                        
            it will raise an IntergrityError because all 3 fields (laundry_services, service_type, service_item)
            should be unique as per my current definition
        """ 
        unique_together = ('service_name', 'service_type', 'service_item')

    def __str__(self):
        return f'{self.laundry_service.name} {self.service_type.name}  - {self.service_item.name} | Price: {self.price} | Delivery: {self.delivery_time}h'
    