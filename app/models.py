from django.db import models


class Lot(models.Model):
    seller_name = models.CharField(null=False, max_length=200)
    seller_id = models.CharField(null=False, blank=False, unique=True, max_length=200)
    price = models.FloatField(null=False, blank=False)
    buyer_id = models.CharField(null=True, default=None, blank=True, max_length=200)
