import json

from .models import *

# create cart for guest user
def cookie_cart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart:', cart)

    orderitems = []

    # the html will be expecting a variable called order
    # initialize a dictionary with the expected keys
    # which will be viewed as an object
    # with attributes corresponding to the keys
    order = {'total_quantity': 0, 'total_price': 0, 'shipping': False}
    total_quantity = order['total_quantity']

    for i in cart:
        try:
            current_quantity = cart[i]['quantity']
            print(current_quantity)
            total_quantity += current_quantity
            print(total_quantity)

            product = Product.objects.get(id=i)
            total_price = (product.price * current_quantity)

            order['total_price'] += total_price

            orderitem = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': current_quantity,
                'total': total_price
            }
            orderitems.append(orderitem)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass

    print(total_quantity)

    order['total_quantity'] = total_quantity

    return {
        'total_quantity': total_quantity,
        'order': order,
        'orderitems': orderitems
    }

# handle user or guest actions
# return appropriate cart data
def cart_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
        total_quantity = order.total_quantity
    else:
        cookie_data = cookie_cart(request)
        total_quantity = cookie_data['total_quantity']
        order = cookie_data['order']
        orderitems = cookie_data['orderitems']

    return {
        'total_quantity': total_quantity,
        'order': order,
        'orderitems': orderitems
    }

def guest_order(request, data):
    print('User is not logged in.')

    print('COOKIES: ', request.COOKIES)

    name = data['form']['name']
    email = data['form']['email']

    data = cookie_cart(request)
    orderitems = data['orderitems']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order, created = Order.objects.get_or_create(
        customer=customer,
        complete=False,
    )

    for orderitem in orderitems:
        product = Product.objects.get(id=orderitem['product']['id'])

        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=orderitem['quantity']
        )

    return customer, order