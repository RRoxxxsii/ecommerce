import stripe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from basket.basket import Basket


@login_required
def basket_view(request):
    basket = Basket(request)
    total = str(basket.get_total_price())
    total = int(total.replace('.', ''))

    stripe.api_key = 'sk_test_51Mrj3vKLxVOJXXushmb6LJnaB6Ir3cVbOk4PDJt5nCUUp9aBAsqdfsQbLkuFHpTUR14aYZc9A71Earu6FqK1CXww00bTya9G1z'
    intent = stripe.PaymentIntent.create(
        amount=total,
        currency='gbp',
        metadata={'userid': request.user.id}
    )

    return render(request, 'payment/home.html', {'client_secret': intent.client_secret})

