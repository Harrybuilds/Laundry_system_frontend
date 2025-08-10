from django.core.management.base import BaseCommand
from yourapp.models import LaundryService, ServiceOption

class Command(BaseCommand):
    help = 'Seed LaundryService and ServiceVariant data'

    def handle(self, *args, **options):
        wash_fold, created = LaundryService.objects.get_or_create(
            name='Wash & Fold', defaults={'description': 'Basic wash and fold laundry service'}
        )
        dry_clean, created = LaundryService.objects.get_or_create(
            name='Dry Cleaning', defaults={'description': 'Dry cleaning for delicate clothes'}
        )
        ironing, created = LaundryService.objects.get_or_create(
            name='Ironing', defaults={'description': 'Ironing service for clothes'}
        )

        variants = [
            (wash_fold, 'standard', 300, 72),
            (wash_fold, 'express', 500, 48),
            (wash_fold, 'premium', 1000, 24),
            (dry_clean, 'standard', 700, 96),
            (dry_clean, 'express', 1200, 48),
            (dry_clean, 'premium', 2000, 24),
            (ironing, 'standard', 200, 72),
            (ironing, 'express', 350, 48),
            (ironing, 'premium', 600, 24),
        ]

        for laundry_service, service_type, price, delivery_time in variants:
            ServiceVariant.objects.get_or_create(
                laundry_service=laundry_service,
                service_type=service_type,
                defaults={'price': price, 'delivery_time': delivery_time}
            )

        self.stdout.write(self.style.SUCCESS('Laundry services and options seeded successfully.'))
