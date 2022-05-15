from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from app import models
from app.serializers import LotSerializer


class LotApiView(ListCreateAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()


class LotDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LotSerializer
    queryset = models.Lot.objects.all()

