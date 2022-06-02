from typing import Any

from rest_framework import serializers

from app.models import Lot, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class PaymentCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ("user_email",)


class LotSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(many=True)

    class Meta:
        model = Lot
        fields = "__all__"


class LotCreationSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        exclude = ("is_active", "initiator_wallet", "lot_initiator_email")


class LotCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = "__all__"

    def validate(self, data) -> dict[str, Any]:
        """
        Check that the start is before the stop.
        """
        if data["min_limit"] >= data["max_limit"]:
            raise serializers.ValidationError("min_limit must be smaller than max_limit")

        return data


class ChangeLotSupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = ("supply",)
