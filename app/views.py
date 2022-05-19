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
        validated_data = self.get_serializer(request.data)



class LotDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()

    def get(self, request):
        try:
            lot = models.Lot.objects.get(seller_id=request.data['user_id'])
            crypto = CryptoService(request.data['email'])
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

