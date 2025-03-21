from django.core.management.base import BaseCommand
from reksadana_rest.models import Bank, CategoryReksadana

class Command(BaseCommand):
    help = "Seed the database with initial data"

    def handle(self, *args, **kwargs):
        banks = [
            "BCA",
            "Mandiri",
            "BNI",
            "Permata",
            "CIMB Niaga"
        ]

        for bank in banks:
            obj, created = Bank.objects.get_or_create(name=bank)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created bank: {bank}"))
            else:
                self.stdout.write(self.style.WARNING(f"Bank already exists: {bank}"))
        
        categories = [
            "Reksadana Pasar Uang",
            "Reksadana Pendapatan Tetap",
            "Reksadana Campuran",
            "Reksadana Saham",
        ]

        for category in categories:
            obj, created = CategoryReksadana.objects.get_or_create(name=category)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category}"))
            else:
                self.stdout.write(self.style.WARNING(f"Category already exists: {category}"))