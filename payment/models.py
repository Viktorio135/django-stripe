from django.db import models


class Item(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=30)
    description = models.CharField(verbose_name='Описание', max_length=300)
    price = models.IntegerField(verbose_name='Цена')
    currency = models.CharField(max_length=10, choices=[('usd', 'USD'), ('eur', 'EUR')], default='usd')


    def __str__(self):
        return f'{self.name}: {self.price}{self.currency}'
    

    class Meta:
        verbose_name = 'Элемент'
        verbose_name_plural = 'Элементы'


class Discount(models.Model):
    name = models.CharField(max_length=100)
    stripe_coupon_id = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.name}"


    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'
    

class Tax(models.Model):
    name = models.CharField(max_length=100)
    stripe_tax_rate_id = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.name}"


    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"Order {self.id}"


    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

