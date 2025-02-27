from django.urls import path

from .views import ItemDetailView, BuyItemView, OrderDetailView, CreatePaymentIntentView

urlpatterns = [
    path("item/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("buy/<int:pk>/", BuyItemView.as_view(), name="buy_item"),
    path("order/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("create-payment-intent/", CreatePaymentIntentView.as_view(), name="create_payment_intent")
]