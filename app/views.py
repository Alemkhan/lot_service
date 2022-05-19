import jwt
import requests
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from app import models
from app.serializers import LotSerializer
from app.services import CryptoService


class LotApiView(ListCreateAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()

    def post(self, request, *args, **kwargs):
        encoded_jwt = jwt.decode(request.data['access_token'], 'qwe', 'HS256')
        user_id = encoded_jwt.get('user_id')
        request.data['seller_id'] = user_id
        serializer = LotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class LotDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()

    def get(self, request):
        try:
            encoded_jwt = jwt.decode(request.data['access_token'], 'qwe', 'HS256')
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
        encoded_jwt = jwt.decode(request.data['access_token'], 'qwe', 'HS256')
        user_id = encoded_jwt.get('user_id')
        lot = models.Lot.objects.get(seller_id=user_id)
        serializer = LotSerializer(lot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        encoded_jwt = jwt.decode(request.data['access_token'], 'qwe', 'HS256')
        user_id = encoded_jwt.get('user_id')
        lot = models.Lot.objects.get(seller_id=user_id)
        lot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

