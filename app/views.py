import django_filters
import jwt

from rest_framework import status, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from app import models
from app.pagination import SmallPagesPagination
from app.serializers import LotSerializer, PaymentSerializer, LotCreationSerializer
from app.services import CryptoService


class LotApiView(ListCreateAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()
    pagination_class = SmallPagesPagination
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['$price', '$lot_type', '$payment__bank_name']
    filterset_fields = ['lot_type', 'price', 'payment__bank_name', 'payment__payment_type']

    def post(self, request, *args, **kwargs):
        self.serializer_class = LotCreationSerializer
        encoded_jwt = jwt.decode(request.data['access_token'], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', 'HS256')
        user_id = encoded_jwt.get('user_id')
        crypto = CryptoService(user_id)
        currency = request.data['currency']
        wallet_data = crypto.get_p2p_wallet() if currency is 'eth' else crypto.get_p2p_wallet_erc20()
        resp = models.Lot.objects.filter(seller_id=user_id, lot_type=request.data['lot_type']).first()
        if resp:
            return Response({
                'success': 'false',
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': 'You already have an existing lot'
            }, status=status.HTTP_400_BAD_REQUEST)
        if int(request.data['supply']) > wallet_data['balance']:
            return Response({
                'success': 'false',
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': 'You do not have enough supply count in your p2p wallet'
            }, status=status.HTTP_400_BAD_REQUEST)
        request.data['seller_id'] = user_id
        serializer = LotCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class LotDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()

    def get(self, request):
        try:
            encoded_jwt = jwt.decode(request.data['access_token'], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', 'HS256')
            user_id = encoded_jwt.get('user_id')
            lot = models.Lot.objects.get(seller_id=user_id)
            crypto = CryptoService(user_id)
            status_code = status.HTTP_200_OK
            serializer = self.serializer_class(lot)
            wallet_data = crypto.get_p2p_wallet()
            response = {
                'success': 'true',
                'status code': status_code,
                'message': 'Lot fetched successfully',
                'data': {
                    'lot': serializer.data,
                    'wallet': wallet_data,
                }
            }
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                'success': 'false',
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': 'Lot does not exists',
                'error': str(e)
            }
        return Response(response, status=status_code)

    def put(self, request, format=None):
        encoded_jwt = jwt.decode(request.data['access_token'], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', 'HS256')
        user_id = encoded_jwt.get('user_id')
        lot = models.Lot.objects.get(seller_id=user_id)
        serializer = LotSerializer(lot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        encoded_jwt = jwt.decode(request.data['access_token'], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', 'HS256')
        user_id = encoded_jwt.get('user_id')
        lot = models.Lot.objects.get(seller_id=user_id)
        lot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentApiView(ListCreateAPIView):
    serializer_class = PaymentSerializer
    queryset = models.Payment.objects.all()

    def post(self, request, *args, **kwargs):
        encoded_jwt = jwt.decode(request.data['access_token'], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', 'HS256')
        user_id = encoded_jwt.get('user_id')
        request.data['seller_id'] = user_id
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class PaymentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = models.Payment.objects.all()

    def get(self, request):
        try:
            encoded_jwt = jwt.decode(request.data['access_token'], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', 'HS256')
            user_id = encoded_jwt.get('user_id')
            payments = models.Payment.objects.filter(seller_id=user_id).all()
            data = []
            for payment in payments:
                serializer = self.serializer_class(payment)
                data.append(serializer.data)
            status_code = status.HTTP_200_OK
            response = {
                'success': 'true',
                'status code': status_code,
                'message': 'Payment requisites fetched successfully',
                'data': {
                    'payment': data,
                }
            }
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                'success': 'false',
                'status code': status.HTTP_400_BAD_REQUEST,
                'message': 'Payment requisites does not exists',
                'error': str(e)
            }
        return Response(response, status=status_code)

    def delete(self, request, format=None):
        encoded_jwt = jwt.decode(request.data['access_token'], 'X]E&`I"mCdS1Y3uD+}_*lU?0~@|S6c', 'HS256')
        user_id = encoded_jwt.get('user_id')
        payments = models.Payment.objects.filter(seller_id=user_id).all()
        for payment in payments:
            payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
