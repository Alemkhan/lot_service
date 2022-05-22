from rest_framework import serializers

from app.models import Lot, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class LotSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(many=True)

    class Meta:
        model = Lot
        fields = '__all__'


class LotCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = '__all__'

