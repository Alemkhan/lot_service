from django.db import models


class CryptoCurrency(models.TextChoices):
    ETH = "eth"
    ERC20 = "erc20"


class FiatCurrency(models.TextChoices):
    KZT = "kzt"
    USD = "usd"


class LotType(models.TextChoices):
    BUY = "buy"
    SELL = "sell"


class PaymentType(models.TextChoices):
    PHONE = "phone"
    BANK_NUM = "bank_number"


class Lot(models.Model):
    lot_initiator_email = models.CharField(null=False, blank=False, max_length=64)
    initiator_wallet = models.CharField(null=False, blank=False, max_length=128)
    price = models.FloatField(null=False, blank=False)  # in fiat
    supply = models.FloatField(null=False, blank=False)  # amount of crypto
    min_limit = models.FloatField(null=False, blank=False)  # min amount of crypto to buy
    max_limit = models.FloatField(null=False, blank=False)  # max amount of crypto to buy
    lot_type = models.CharField(choices=LotType.choices, max_length=8, default=LotType.SELL)

    fiat_currency = models.CharField(choices=FiatCurrency.choices, max_length=8, default=FiatCurrency.KZT)
    crypto_currency = models.CharField(choices=CryptoCurrency.choices, max_length=8, default=CryptoCurrency.ETH)

    is_active = models.BooleanField(default=True, null=False, blank=True)

    payment = models.ManyToManyField("Payment")


class Payment(models.Model):
    user_email = models.CharField(null=False, blank=False, max_length=200)
    bank_name = models.CharField(null=False, blank=False, max_length=200)
    requisite_number = models.CharField(null=False, blank=False, max_length=200)
    payment_type = models.CharField(choices=PaymentType.choices, max_length=200, default=PaymentType.PHONE)
