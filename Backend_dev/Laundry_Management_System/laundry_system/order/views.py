from django.shortcuts import render
from .models import Order, OrderItem
from laundryservice.models import LaundryService, ServiceType, Garment, ServicePricing
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from user.auth.decorators import auth_required
import json
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from laundry_system.utils import paginate, paginate_queryset



# Create your views here.
@csrf_exempt
@auth_required(roles=['customer'])
def place_order_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)

    try:
        data = json.loads(request.body) # a dict with 1 item as key and list of items ({'items':{[{},{},...]}}) as value
        items = data.get('items', {'order': [{},{}]})

        if not items:
            return JsonResponse({'error': 'No items provided'}, status=400)

        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                pickup_time = timezone.now() + timedelta(days=3),
                total_cost = 0.00
                ) # create and save the order in the database

            order_items = []
            warning = []

            response_data = {
                'msg': 'Order created successfully', 
                'order_id': order.id
            }

            for item in items:
                service_type = ServiceType.objects.filter(name=item.get('service_type')).first()
                service = LaundryService.objects.filter(name=item.get('service')).first()
                garment = Garment.objects.filter(name=item.get('item_name')).first()

                # validate service_type, service, item_name
                if not service_type:
                    return JsonResponse({'error': f"We currently do not provide this service_type: {item.get('service_type')}"}, status=400)

                if not service:
                    return JsonResponse({'error': f"We currently do not provide this service: {item.get('service')}"}, status=400)
                
                if not garment:
                    return JsonResponse({'error': f"we currently do not handle item such as: {item.get('name')}"}, status=400)
                
                # Lookup pricing
                pricing = ServicePricing.objects.filter(
                    service_name=service,
                    service_type=service_type,
                    service_item=garment,
                ).first()

                if not pricing:
                    warning.append(item)
                    continue

                price = pricing.price if pricing else 0.00
                duration = pricing.duration if pricing else timedelta(days=3)
                
                # Prepare the OrderItem (not yet saved)
                order_item = OrderItem(
                order=order,
                service_type=service_type,
                service=service,
                item_name=garment,
                quantity=item.get('quantity', 1),
                price=price,
                duration=duration
                )

                order_item.save()
                order_items.append(order_item)


        order.calculate_total_cost()
        if warning:
            response_data['warning'] = [
            {
                'service_type': item.get('service_type'),
                'service': item.get('service'),
                'garment': item.get('item_name'),
                'quantity': str(item.get('quantity')),
                'price': str(item.get('price', 0.00)),
            }
            for item in warning
        ]
    
        response_data['order_items'] = [
            {
                'service_type': item.service_type.name,
                'service': item.service.name,
                'garment': item.item_name.name,
                'quantity': str(item.quantity),
                'price': str(item.price),
                'total_cost': str(item.total_cost),
                'duration': str(item.duration),
                'time_remaining': str(item.time_remaining)
            }
            for item in order_items
        ]

        order_total_cost = order.calculate_total_cost()
        response_data['order_total_cost'] = order_total_cost

        return JsonResponse(response_data, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def create_order(request):
    """
    for just 1 orderitem

    handle the http method
    parse request body to get the order and orderitem data
    verify that orderitem can be created, if no, return an error msg, if yes, proceed
    create an order
    create the orderitem associating it with the order, then calc the total cost for the orderitem
    recalculate the cost of the order
    return a success message


    orderitem can only be created if:
        it's service is valid
        it's servicetype is valid

    """
    pass


@csrf_exempt
def manage_order_view(request, pk):
    if request.method == 'POST':
        return JsonResponse({'error': f'{request.method} method not allowed here'}, status=405)

    page = int(request.GET.get('page')) if request.GET.get('page') else 1
    per_page = int(request.GET.get('per_page')) if request.GET.get('per_page') else 5

    order = Order.objects.filter(id=pk).first()

    if not order:
        return JsonResponse({'error': 'No such order'}, status=404)

    if request.method == 'GET':
        orderitems = [
            {
                'service_type': item.service_type.name,
                ' service': item.service.name,
                'item_name': item.item_name.name,
                'quantity': item.quantity,
                'price': item.price,
                'total_price': item.total_price,
                'delivery_time': item.delivery_time
            }
            for item in order.order_items.all()
        ]
        
        order_info = {
            'customer': order.customer.email,
            'address': order.address,
            'order_status': order.order_status,
            'placement_date': order.created_at,
            'pickup_time':order.pickup_time,
            'orderitems': orderitems,
            'total_cost': order.calculate_total_cost()
        }
        return JsonResponse({'order_info': paginate(request, data=order_info, page=page, per_page=per_page)}, status=200)
    elif request.method == 'PUT':
        pass
    elif request.method == 'DELETE':
        order.delete()
        return JsonResponse({'message': f'order has been deleted successfully'}, status=200)


@auth_required(roles=['customer', 'staff'])
def order_history(request):
    page = int(request.GET.get('page')) if request.GET.get('page') else 1
    per_page = int(request.GET.get('per_page')) if request.GET.get('per_page') else 5
    
    user = request.user

    if user.user_type == 'staff':
        orders_qset = Order.objects.all()
    else:
        orders_qset = Order.objects.filter(customer=user)

    orders = [ {
        'order_id': order.pk,
        'customer_id': order.customer.id,
        'pickup_time': order.pickup_time,
        'address': order.address,
        'order_status': order.order_status,
        'placement_date': order.created_at,
        'total_cost': order.calculate_total_cost()
    } for order in orders_qset ]

    return JsonResponse({'orders': paginate(request, data=orders, page=page, per_page=per_page)}, status=200)
    pass


@auth_required(roles=['customer', 'staff'])
def search_for_laundry_order(request):
    from django.db.models import ForeignKey

    page = int(request.GET.get('page')) if request.GET.get('page') else 1
    per_page = int(request.GET.get('per_page')) if request.GET.get('per_page') else 5

    user = request.user

    if user.user_type == 'staff':
        pass

    keys = [ 
            'id', 'customer', 'customer_id', 'created_at', 'order_items',
            'order_status', 'pickup_time', 'address', 'total_cost', 'invoice'
        ]
    
    fk_search_field = 'email'

    filter = {}

    for key in keys:
        value = request.GET.get(key)
        if not value:
            continue

        try:
            field = Order._meta.get_field(key)
        except Exception:
            # Possibly not a real field or invalid
            continue

        # If it's a ForeignKey, search on a field of the related model
        if isinstance(field, ForeignKey):
            related_model = field.related_model
            if fk_search_field in [f.name for f in related_model._meta.fields]:
                filter[f"{key}__{fk_search_field}__icontains"] = value

        else:
            filter[f"{key}__icontains"] = value

    print(f'filter: {filter}')

    queryset = Order.objects.filter(**filter)
    result = list(queryset.values())

    return JsonResponse({
        'count': len(result),
        'result': paginate(request, data=result, page=page, per_page=per_page)
    }, status=200)
    


def all_orders_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': f'{request.method} method not allowed here'}, status=405)

    page = int(request.GET.get('page')) if request.GET.get('page') else 1
    per_page = int(request.GET.get('per_page')) if request.GET.get('per_page') else 5

    orders_qset = Order.objects.all()
    orders = [
        {
            'order_id': order.id,
            'customer': order.customer.email,
            'order_status': order.order_status,
            'address': order.address,
            'placement_time': order.created_at,
            'pickup_time': order.pickup_time,
            'total_cost': order.total_cost
        }
        for order in orders_qset
    ]

    return JsonResponse({'orders': paginate(request, data=orders, page=page, per_page=per_page)}, status=200)


def orderitem_search(request):
    pass