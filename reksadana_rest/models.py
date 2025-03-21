from django.db import models

# Create your models here.

class Reksadana(models.Model):
    TINGKAT_RESIKO_CHOICE = [
        ("Konservatif", "Konservatif"),
        ("Moderat", "Moderat"),
        ("Agresif", "Agresif"),
    ]
    id_reksadana = models.UUIDField(
        unique=True
        )
    name = models.CharField(
        max_length=255,
        unique=True
    )
    category = models.ForeignKey(to="CategoryReksadana", on_delete=models.CASCADE)
    kustodian = models.ForeignKey(to="Bank", on_delete=models.CASCADE)
    penampung = models.ForeignKey(to="Bank", on_delete=models.CASCADE)

    nav = models.IntegerField()
    aum = models.IntegerField()
    tingkat_resiko = models.CharField(
        max_length=10,  # Adjust based on longest value
        choices=TINGKAT_RESIKO_CHOICE,
        default="Konservatif",
    )

class Bank(models.Model):
    id = models.IntegerField(unique=True)
    name = models.CharField()

class CategoryReksadana(models.Model):
    id = models.IntegerField(unique=True)
    name = models.CharField()

class HistoryReksadana(models.Model):
    id_reksadana = models.ForeignKey(to="Reksadana")
    date = models.DateField()
    nav = models.IntegerField()
    aum = models.IntegerField()

class Payment(models.Model):
    user_id = models.UUIDField()
    id_reksadana = models.ForeignKey(to="Reksadana")

class UnitDibeli(models.Model):
    user_id = models.UUIDField()
    id_reksadana = models.ForeignKey(to="Reksadana")
    nominal = models.IntegerField()
    waktu_pembelian = models.DateTimeField()

    def clean(self):
        super().clean()
        if self.nominal<0:
            raise ValueError("Ini apaan uang <0 :V")
        
class Payment(models.Model):
    user_id = models.UUIDField()
    id_reksadana = models.ForeignKey(to="Reksadana")
    nominal = models.IntegerField()
    waktu_pembelian = models.DateTimeField()

    def clean(self):
        super().clean()
        if self.nominal<0:
            raise ValueError("Ini apaan uang <0 :V")