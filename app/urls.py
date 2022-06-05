from django.urls import path

from app import views

urlpatterns = [
    path("lot/", views.LotApiView.as_view(), name="lot"),
    path("payment/", views.PaymentApiView.as_view(), name="payment"),
    path("lot/detail/<int:pk>", views.LotDetailView.as_view(), name="lot_detail"),
    path("payment/detail/<int:pk>", views.PaymentDetailView.as_view(), name="payment_detail"),
]
