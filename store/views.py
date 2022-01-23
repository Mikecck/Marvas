from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from django.core.paginator import Paginator

from django.conf import settings

from django.views.generic import DetailView

import json

import datetime

from .models import *

from .filters import *

from .utils import *

from django.contrib.auth import authenticate, login

def sign_in(request):
    userName = request.POST.get('username')
    passWord = request.POST.get('password')

    user = authenticate(username=userName, password=passWord)

    if user is not None:
        if user.is_active:
            if user.is_superuser:
                login(request, user)

                request.session['usertype'] = 'admin'
                
                return JsonResponse({'ret' : 0})
            else:
                return JsonResponse({'ret' : 1, 'msg': 'Use the admin account to login'})
        else:
            return JsonResponse({'ret' : 0, 'msg': 'User has benn banned/deleted'})
    else:
        return JsonResponse({'ret' : 1, 'msg': 'Wrong user name or password'})


def listCustomers(request):
    qs = Customer.objects.values()

    # ph = request.Get.get('id', None)

    # if ph:
    #     qs = qs.filter(id=ph)

    retStr = ''
    for customer in qs:
        for name, value in customer.items():
            retStr += f'{name} : {value}'
        retStr += '<br>'
    return HttpResponse(retStr)

def store(request):
    context = {}

    data = cart_data(request)

    products = Product.objects.all().order_by('name')

    product_filter = ProductFilter(request.GET, queryset=products)
    # context['athlete_list'] = athlete_list
    context['product_filter'] = product_filter

    paginated_product_filter = Paginator(product_filter.qs, 4)
    page_number = request.GET.get('page')
    product_page_obj = paginated_product_filter.get_page(page_number)

    # context['products'] = products
    context['product_page_obj'] = product_page_obj
    context['total_quantity'] = data['total_quantity'] 

    return render(request, 'store/store.html', context=context)

# data_list = {
#         'context' : context,
#         'data' : data,
#         'product_filter' : product_filter,
#         'page_number' : page_number
#     }
#     return JsonResponse(data_list, safe=False)

def cart(request):
    context = cart_data(request)

    return render(request, 'store/cart.html', context=context)

    # data_list = {
    #     'context' : context,
    # }
    # return JsonResponse(data_list, safe=False)

def checkout(request):
    context = cart_data(request)

    context['barikoi_autocomplete_api_key'] = settings.BARIKOI_AUTOCOMPLETE_API_KEY
    
    return render(request, 'store/checkout.html', context=context)

    # data_list = {
    #     'context' : context,
    # }
    # return JsonResponse(data_list, safe=False)

def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    print('action: ', action)
    print('product_id: ', product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderitem.quantity += 1
    elif action == 'remove':
        orderitem.quantity -= 1

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()

    return JsonResponse('Item was added.', safe=False)

def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guest_order(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    # validate against actual price from the Order model
    # also check if cart is empty
    if (total == order.total_price) and (len(order.orderitem_set.all()) > 0):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            zipcode=data['shipping']['zipcode'],
        )

    print('total: ', total)
    print('order.total_price: ', order.total_price)
    print('total == order.total_price: ', total == order.total_price)

    return JsonResponse('Payment complete.', safe=False)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'

    def get(self, request, pk) :
        context = {}
        product = Product.objects.get(id=pk)
        data = cart_data(request)
        context['total_quantity'] = data['total_quantity']
        context['product'] = product
        return render(request, self.template_name, context)

        # data_total = {
        #         'product' : product,
        #         'data' : 'data',
        #         'total_quantity' : 'total_quantity',
        # }
        # return JsonResponse(data_total, safe=False)