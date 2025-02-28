import json

import stripe 

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from django.db.models import Prefetch
from django.conf import settings

from .models import Item, Order

stripe.log = 'info'

class ItemDetailView(DetailView):
    """Представление для item ('/item/{id}')"""
    template_name = 'item.html'
    model = Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item = self.get_object()
        currency = item.currency.lower()

        if currency == 'usd':
            public_key = settings.STRIPE_API_PUBLIC_KEY_USD
        elif currency == 'eur':
            public_key = settings.STRIPE_API_PUBLIC_KEY_EUR
        else:
            public_key = None

        # Передаем публичный ключ в контекст шаблона
        context['public_key'] = public_key

        return context
    

class BuyItemView(View):
    """Предаставление для получения session.id. Чтобы понять какой заказ пришел (одиночный или корзина), используется параметр 'order' """
    def get(self, request, pk):
        is_order = request.GET.get("order") == 'True' #Проверяем является ли запрос Order
        if is_order:
            order = get_object_or_404(Order.objects.prefetch_related(Prefetch('items')), id=pk)
            return self.create_checkout_session(request, order.items.all(), 'order', order.id, order.discount, order.tax)
        else:
            item = get_object_or_404(Item, id=pk)
            return self.create_checkout_session(request, [item], 'item', item.id)

    def create_checkout_session(self, request, items, obj_type, obj_id, discount=None, tax=None):
        """Запрос в stripe"""
        try:

            currencies = {item.currency for item in items} # Получаем все валюты в заказе
            if len(currencies) != 1:
                return JsonResponse({'error': 'All items must have the same currency'}, status=400)

            currency = currencies.pop() # Выясняем валюту заказа

            if currency == 'usd':
                stripe.api_key = settings.STRIPE_API_KEY_USD
            elif currency == 'eur':
                stripe.api_key = settings.STRIPE_API_KEY_EUR
            else:
                return JsonResponse({'error': 'Unsupported currency'}, status=400)

            line_items = [{
                    'price_data': {
                        'currency': item.currency,
                        'product_data': {
                            'name': item.name,
                        },
                        'unit_amount': int(item.price * 100),
                    },
                    'quantity': 1,
                    'tax_rates': [tax.stripe_tax_rate_id] if tax else [] # Применяем налог
                } for item in items]

            data = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': f'{settings.MAIN_URL}/{obj_type}/{obj_id}/',
                'cancel_url': f'{settings.MAIN_URL}/{obj_type}/{obj_id}/',
            }

            if discount and discount.stripe_coupon_id:
                data['discounts'] = [{'coupon': discount.stripe_coupon_id}] # Применяем скидку 

            session = stripe.checkout.Session.create(
                **data
            )
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    

class OrderDetailView(DetailView):
    """Представление для Order ('/order/{id}')"""
    template_name = 'order.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.get_object()

        currencies = {item.currency for item in order.items.all()}
        if len(currencies) != 1:
            context['public_key'] = None
            context['error'] = 'All items in the order must have the same currency.'
            return context

        currency = currencies.pop()

        if currency == 'usd':
            public_key = settings.STRIPE_API_PUBLIC_KEY_USD
        elif currency == 'eur':
            public_key = settings.STRIPE_API_PUBLIC_KEY_EUR
        else:
            public_key = None

        context['public_key'] = public_key

        return context


class CreatePaymentIntentView(View):
    """Представление для создания Stripe Payment Intent"""
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        if 'item_id' in data: # Проверка является ли заказ одиночным
            item_id = data['item_id']
            item = get_object_or_404(Item, id=item_id)
            currency = item.currency.lower()
            amount = int(item.price * 100) # Сумма заказа
        elif 'order_id' in data:
            order_id = data['order_id']
            order = get_object_or_404(Order, id=order_id)
            items = order.items.all()

            currencies = {item.currency for item in items}
            if len(currencies) != 1:
                return JsonResponse({'error': 'All items must have the same currency'}, status=400)

            currency = currencies.pop()
            amount = sum(int(item.price * 100) for item in items) # Сумма заказа
        else:
            return JsonResponse({'error': 'Invalid data. Must provide item_id or order_id.'}, status=400)

        if currency == 'usd':
            stripe.api_key = settings.STRIPE_API_KEY_USD
        elif currency == 'eur':
            stripe.api_key = settings.STRIPE_API_KEY_EUR
        else:
            return JsonResponse({'error': 'Unsupported currency'}, status=400)

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=['card'],
            )
            return JsonResponse({'clientSecret': intent.client_secret})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)