import uuid
from django.db import models

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

class Bank(models.Model):
    name = models.CharField(max_length=255)

class CategoryReksadana(models.Model):
    name = models.CharField(max_length=255)

class HistoryReksadana(models.Model):
    id_reksadana = models.ForeignKey(to="Reksadana", 
                                     on_delete=models.CASCADE, 
                                     to_field="id_reksadana"  )
    date = models.DateField()
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