import os
from decimal import ROUND_DOWN, Decimal
from typing import Any, Type

import jwt
from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from jwt import DecodeError
from rest_framework import status
from rest_framework.pagination import BasePagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app import models
from app.exceptions import (AuthenticationRequiredException,
                            LotAlreadyExistsException,
                            NotEnoughBalanceException, NotFoundException,
                            PermissionDeniedException)
from app.pagination import SmallPagesPagination
from app.serializers import (ChangeLotSupplySerializer, LotCreationSerializer,
                             LotCreationSwaggerSerializer, LotLiteSerializer,
                             LotSerializer, PaymentCreationSerializer,
                             PaymentSerializer)
from app.services import CryptoService, get_current_user_data


class GenericAPIView(APIView):
    pagination_class: Type[BasePagination]

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class LotApiView(GenericAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()
    pagination_class = SmallPagesPagination

    @swagger_auto_schema(request_body=LotCreationSwaggerSerializer())
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        encoded_jwt = get_current_user_data(request)

        user_email = encoded_jwt.get(
            "user_id",
        )

        crypto_service = CryptoService(user_email)
        currency = request.data["crypto_currency"]

        wallet_data = crypto_service.get_p2p_wallet(currency)

        resp = models.Lot.objects.filter(
            lot_initiator_email=user_email,
            lot_type=request.data["lot_type"],
            is_active=True,
        ).first()

        if resp:
            raise LotAlreadyExistsException

        if Decimal(request.data["supply"]).quantize(Decimal(".0001"), rounding=ROUND_DOWN) > Decimal(
            wallet_data["balance"]
        ).quantize(Decimal(".0001"), rounding=ROUND_DOWN):
            raise NotEnoughBalanceException

        request.data["lot_initiator_email"] = user_email

        body = {
            **request.data,
            "initiator_wallet": wallet_data["address"],
        }

        serializer = LotCreationSerializer(data=body)

        if serializer.is_valid():
            serializer.save()
            crypto_service.increase_seller_wallet_balance(
                float(request.data["supply"]),
                wallet_data["id"],
                request.data["crypto_currency"],
                request.data["lot_type"],
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors)

    crypto_type = openapi.Parameter(
        "crypto_type", openapi.IN_QUERY, description="Crypto type: ETH, ERC20", type=openapi.TYPE_STRING
    )
    sell_type = openapi.Parameter(
        "sell_type", openapi.IN_QUERY, description="Sell type: Sell, Buy", type=openapi.TYPE_STRING
    )
    email = openapi.Parameter("email", openapi.IN_QUERY, description="Trader's email", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[crypto_type, sell_type, email])
    def get(self, request: Request) -> Response:
        serializer = LotLiteSerializer
        lookup = Q()

        if crypto_type := request.GET.get("crypto_type"):
            lookup &= Q(crypto_currency=crypto_type)

        if trader_email := request.GET.get("email"):
            lookup &= Q(lot_initiator_email=trader_email)

        if sell_type := request.GET.get("sell_type"):
            lookup &= Q(lot_type=sell_type)

        existing_lots: list[models.Lot] = self.queryset.filter(lookup)
        page = self.paginate_queryset(existing_lots)
        if page:
            serializer = self.get_paginated_response(serializer(page, many=True).data)
        else:
            serializer = serializer(existing_lots, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LotDetailView(APIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()

    def get_object(self, pk):
        try:
            return models.Lot.objects.get(pk=pk)
        except models.Lot.DoesNotExist:
            raise NotFoundException(detail="Lot not found")

    def get(self, request: Request, pk: int) -> Response:
        existing_lot: models.Lot = self.get_object(pk=pk)

        serializer = self.serializer_class(existing_lot)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, pk: int) -> Response:
        encoded_jwt = get_current_user_data(request)
        user_email = encoded_jwt.get(
            "user_id",
        )
        user_role = encoded_jwt.get("role")

        existing_lot: models.Lot = self.get_object(pk=pk)

        if existing_lot.lot_initiator_email != user_email and user_role not in [
            "A",
            "SU",
        ]:
            raise PermissionDeniedException

        serializer = LotSerializer(existing_lot, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @swagger_auto_schema(request_body=ChangeLotSupplySerializer())
    def patch(self, request: Request, pk: int) -> Response:
        existing_lot: models.Lot = self.get_object(pk=pk)

        serializer = ChangeLotSupplySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Wrong parameters!")

        serialized_data = serializer.data

        new_supply = existing_lot.supply - serialized_data["supply"]

        if new_supply < 0:
            raise NotEnoughBalanceException

        if new_supply == 0:
            new_supply = {"supply": new_supply, "is_active": False}
        else:
            new_supply = {"supply": new_supply}

        serializer = LotSerializer(existing_lot, data=new_supply, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST, data="Wrong parameters!")

    @transaction.atomic
    def delete(self, request, pk: int) -> Response:
        encoded_jwt = get_current_user_data(request)
        user_email = encoded_jwt.get(
            "user_id",
        )
        user_role = encoded_jwt.get("role")

        existing_lot: models.Lot = self.get_object(pk=pk)

        if existing_lot.lot_initiator_email != user_email and user_role not in [
            "A",
            "SU",
        ]:
            raise PermissionDeniedException

        existing_lot.delete()

        return Response(status=status.HTTP_200_OK)


class PaymentApiView(APIView):
    serializer_class = PaymentSerializer
    queryset = models.Payment.objects.all()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        encoded_jwt = get_current_user_data(request)
        user_email = encoded_jwt.get(
            "user_id",
        )
        user_role = encoded_jwt.get("role")

        if user_role in ["A", "SU"]:
            payments: list[models.Payment] = self.queryset.all()
        else:
            payments: list[models.Payment] = self.queryset.filter(user_email=user_email)

        serializer = self.serializer_class(payments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PaymentCreationSerializer())
    def post(self, request, *args, **kwargs):
        encoded_jwt = get_current_user_data(request)

        user_email = encoded_jwt.get(
            "user_id",
        )

        body = {**request.data, "user_email": user_email}

        serializer = PaymentSerializer(data=body)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors)


class PaymentDetailView(APIView):
    serializer_class = PaymentSerializer

    def get_object(self, pk):
        try:
            return models.Payment.objects.get(pk=pk)
        except models.Payment.DoesNotExist:
            raise NotFoundException(detail="Lot not found")

    def get(self, request: Request, pk: int):
        encoded_jwt = get_current_user_data(request)
        user_email = encoded_jwt.get(
            "user_id",
        )
        user_role = encoded_jwt.get("role")

        existing_payment: models.Payment = self.get_object(pk=pk)

        if existing_payment.user_email != user_email and user_role not in [
            "A",
            "SU",
        ]:
            raise PermissionDeniedException

        serializer = self.serializer_class(existing_payment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, format=None, **kwargs):
        try:
            encoded_jwt = jwt.decode(request.COOKIES.get("access-jwt"), os.environ.get("SECRET_KEY"), "HS256")
        except DecodeError:
            raise AuthenticationRequiredException

        user_id = encoded_jwt.get(
            "user_id",
        )
        payments = models.Payment.objects.filter(seller_id=user_id).all()
        for payment in payments:
            payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
