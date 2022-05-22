from django.db import models


class Currency(models.TextChoices):
    ETH = 'eth'
    KZT = 'kzt'


class LotType(models.TextChoices):
    BUY = 'buy'
    SELL = 'sell'


class PaymentType(models.TextChoices):
    PHONE = 'phone'
    BANK_NUM = 'bank_number'


class Lot(models.Model):
    seller_id = models.CharField(null=False, blank=False, max_length=200)
    price = models.FloatField(null=False, blank=False)
    supply = models.FloatField(null=False, blank=False)
    min_limit = models.FloatField(null=False, blank=False)
    max_limit = models.FloatField(null=False, blank=False)
    lot_type = models.CharField(choices=LotType.choices, max_length=200, default=LotType.SELL)
    currency = models.CharField(choices=Currency.choices, max_length=200, default=Currency.KZT)
    payment = models.ManyToManyField('Payment')


class Payment(models.Model):
    seller_id = models.CharField(null=False, blank=False, max_length=200)
    bank_name = models.CharField(null=False, blank=False, max_length=200)
    requisite_number = models.CharField(null=False, blank=False, max_length=200)
    payment_type = models.CharField(choices=PaymentType.choices, max_length=200, default=PaymentType.PHONE)
