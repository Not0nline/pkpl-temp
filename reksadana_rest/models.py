import datetime
import math
import uuid
from django.db import models
from random import randint, uniform
from django.utils import timezone

#TODO: Semua class ini belum ada validasi

class Reksadana(models.Model):
    TINGKAT_RESIKO_CHOICE = [
        ("Konservatif", "Konservatif"),
        ("Moderat", "Moderat"),
        ("Agresif", "Agresif"),
    ]
    id_reksadana = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(
        max_length=255,
        unique=True
    )
    category = models.ForeignKey(to="CategoryReksadana", on_delete=models.CASCADE)
    kustodian = models.ForeignKey(to="Bank", 
                                  on_delete=models.CASCADE,
                                  related_name="kustodian_reksadana"
                                  )
    penampung = models.ForeignKey(to="Bank", 
                                  on_delete=models.CASCADE,
                                  related_name="penampung_reksadana"
                                  )

    nav = models.IntegerField()
    aum = models.IntegerField()
    tingkat_resiko = models.CharField(
        max_length=20,  # Adjust based on longest value
        choices=TINGKAT_RESIKO_CHOICE,
        default="Konservatif",
    )

    def generate_made_up_history_per_hour(self):
        history = HistoryReksadana.objects.filter(id_reksadana=self.id_reksadana).order_by('-date')
        print("aaaa", history)
        if not history.exists():
            # If no history, create the first entry
            new_nav = randint(50, 150)
            new_aum = randint(500, 1500)

            HistoryReksadana.objects.create(
                id_reksadana=self,
                date=datetime.datetime.now(),
                nav=new_nav,
                aum=new_aum
            )

            print('ppp',datetime.datetime.now())
            return

        # Get the latest history entry
        last_entry = history.first()
        print('uwu',last_entry)
        last_nav = last_entry.nav
        last_aum = last_entry.aum
        last_date = last_entry.date
        
        if timezone.is_naive(last_date):
            last_date = timezone.make_aware(last_date, timezone.get_current_timezone())
        # Get current datetime
        current_time = datetime.datetime.now()
        if timezone.is_naive(current_time):
            current_time = timezone.make_aware(current_time, timezone.get_current_timezone())
        
        # Calculate how many hours have passed
        hours_passed = int((current_time - last_date).total_seconds() // 3600)

        if hours_passed <= 0:
            return  # No new data needed

        # Generate missing history entries for each passed hour
        for i in range(1, hours_passed + 1):
            new_time = last_date + datetime.timedelta(hours=i)

            # Introduce randomness in changes
            base_change_nav = uniform(-5, 5)  # Base price movement
            base_change_aum = uniform(-50, 50)

            # Add oscillations for zigzag effect
            oscillation_nav = math.sin(i * uniform(0.5, 2.0)) * uniform(2, 5)
            oscillation_aum = math.sin(i * uniform(0.5, 2.0)) * uniform(10, 30)

            # Compute new values
            new_nav = last_nav + base_change_nav + oscillation_nav
            new_aum = last_aum + base_change_aum + oscillation_aum

            # Ensure values stay within reasonable bounds
            new_nav = max(1, round(new_nav, 2))  # NAV shouldn't go negative
            new_aum = max(100, round(new_aum, 2))  # AUM shouldn't go negative

            # Save new history entry
            HistoryReksadana.objects.create(
                id_reksadana=self,
                date=new_time,
                nav=new_nav,
                aum=new_aum
            )

            # Update last_nav and last_aum for next iteration
            last_nav = new_nav
            last_aum = new_aum

class Bank(models.Model):
    name = models.CharField(max_length=255)

class CategoryReksadana(models.Model):
    name = models.CharField(max_length=255)

class HistoryReksadana(models.Model):
    id_reksadana = models.ForeignKey(to="Reksadana", 
                                     on_delete=models.CASCADE, 
                                     to_field="id_reksadana"  )
    date = models.DateTimeField(null=False, blank=False)
    nav = models.IntegerField()
    aum = models.IntegerField()


class UnitDibeli(models.Model):
    user_id = models.UUIDField()
    id_reksadana = models.ForeignKey(to="Reksadana", 
                                     on_delete=models.CASCADE,
                                     to_field="id_reksadana")
    nominal = models.IntegerField()
    waktu_pembelian = models.DateTimeField()

    def clean(self):
        super().clean()
        if self.nominal<0:
            raise ValueError("Ini apaan uang <0 :V")
        
class Payment(models.Model):
    #TODO: BELUM DI HASH
    user_id = models.UUIDField()
    id_reksadana = models.ForeignKey(to="Reksadana", 
                                     on_delete=models.CASCADE,
                                     to_field="id_reksadana"  
                                     )
    nominal = models.IntegerField()
    waktu_pembelian = models.DateTimeField()

    def clean(self):
        super().clean()
        if self.nominal<0:
            raise ValueError("Ini apaan uang <0 :V")