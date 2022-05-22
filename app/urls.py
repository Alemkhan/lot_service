from django.urls import path, include

from app import views

urlpatterns = [
    path('lot/', views.LotApiView.as_view(), name="lot"),
    path('payment/', views.PaymentApiView.as_view(), name="payment"),
    path('lot/detail', views.LotDetailView.as_view(), name="lot_detail"),
    path('payment/detail', views.PaymentDetailView.as_view(), name="payment_detail")
    # path('user-detail/<int:pk>/', views.userDetail, name="user-detail"),
    # path('user-update/<int:pk>/', views.userUpdate, name="user-update"),
    # path('user-delete/<int:pk>/', views.userDelete, name="user-delete"),
    # path('user-create/', views.userCreate, name="user-create"),
    ]
