import os
from decimal import ROUND_DOWN, Decimal
from typing import Any

import django_filters
import jwt
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from jwt import DecodeError
from rest_framework import filters, status
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView)
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
                             LotCreationSwaggerSerializer, LotSerializer,
                             PaymentCreationSerializer, PaymentSerializer)
from app.services import CryptoService, get_current_user_data


class LotApiView(APIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()
    pagination_class = SmallPagesPagination
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    search_fields = ["$price", "$lot_type", "$payment__bank_name"]
    filterset_fields = [
        "lot_type",
        "price",
        "payment__bank_name",
        "payment__payment_type",
    ]

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
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors)


class LotDetailView(APIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()

    def get_object(self, pk):
        try:
            return models.Lot.objects.get(pk=pk)
        except models.Lot.DoesNotExist:
            raise NotFoundException(detail="Lot not found")

    def get(self, request: Request, pk: int) -> Response:
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

        serializer = ChangeLotSupplySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Wrong parameters!")

        serialized_data = serializer.data

        new_supply = existing_lot.supply - serialized_data["supply"]

        if new_supply < 0:
            raise NotEnoughBalanceException

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


class PaymentApiView(ListCreateAPIView):
    serializer_class = PaymentSerializer
    queryset = models.Payment.objects.all()

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


class PaymentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = models.Payment.objects.all()

    def get(self, request, **kwargs):
        try:
            encoded_jwt = jwt.decode(request.COOKIES.get("access-jwt"), os.environ.get("SECRET_KEY"), "HS256")
        except DecodeError:
            raise AuthenticationRequiredException

        try:
            encoded_jwt = jwt.decode(request.data["access_token"], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', "HS256")
            user_id = encoded_jwt.get(
                "user_id",
            )
            payments = models.Payment.objects.filter(seller_id=user_id).all()
            data = []
            for payment in payments:
                serializer = self.serializer_class(payment)
                data.append(serializer.data)
            status_code = status.HTTP_200_OK
            response = {
                "success": "true",
                "status code": status_code,
                "message": "Payment requisites fetched successfully",
                "data": {
                    "payment": data,
                },
            }
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "success": "false",
                "status code": status.HTTP_400_BAD_REQUEST,
                "message": "Payment requisites does not exists",
                "error": str(e),
            }
        return Response(response, status=status_code)

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
