from django.shortcuts import render
from .models import LaundryService, ServiceType, Garment, ServicePricing
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import json
from user.auth.decorators import auth_required
from datetime import timedelta

# Create your views here.
#@auth_required(roles=['customer', 'staff'])
@csrf_exempt
def create_laundry_service_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description')

            if not name:
                raise ValidationError('a service without a name cannot be created')
            
            name = name.title()

            if name and description:
                service = LaundryService.objects.create(name=name, description=description)
            elif not description:
                service = LaundryService.objects.create(name=name)

            return JsonResponse({'success_msg': f'{service.name} service created sucessfully'}, status=201)
        except Exception as e: return JsonResponse({type(e).__name__: str(e)}, status=400)

    else: return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


#@auth_required(roles=['staff', 'customer'])
def manage_laundryservice_view(request, name):
    if request.method == 'POST':
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)

    service = LaundryService.objects.filter(name=name).first()

    if not service:
        return JsonResponse({'error':'service does not exist'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'service_detail': {
                'name': service.name,
                'description': service.description
            }
        }, status=200)
    elif request.method == 'PUT':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else: data = request.PUT

        if not data.get('name'):
            return JsonResponse({'error': 'name is required to update a service'})

        service.name = data.get('name')
        service.description = data.get('description')

        service.save()

        return JsonResponse({
            'message': 'service has been updated',
            'service_data': {
                'service_new_name': service.name,
                'service_new_description': service.description
            }
        }, status=200)

    elif request.method == 'DELETE':
        service.delete()
        return JsonResponse({'success_msg': 'service successfully deleted from the system'}, status=200)
    

#@auth_required(roles=['staff', 'customer'])
def all_laundry_services_view(request):
    if request.method == 'GET':
        all_services = LaundryService.objects.all()
        return JsonResponse({'all_services': [{
                'service_name':service.name, 
                'service_desc': service.description
                }
                for service in all_services
                ]}, status=200)
    else: return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


@csrf_exempt
#@auth_required(roles=['staff'])
def create_service_type_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description')

            if not name:
                raise ValidationError('a service_type without a name cannot be created')
            
            name = name.title()

            SERVICETYPES = ['Standard', 'Express', 'Premium']

            if name not in SERVICETYPES:
                return JsonResponse({
                    'error': f'{name} can not be created as a service_type. Valid service_types are {SERVICETYPES}'},
                     status=400)

            if name and description:
                service_type = ServiceType.objects.create(name=name, description=description)
            elif not description:
                service_type = ServiceType.objects.create(name=name)

            return JsonResponse({'success_msg': f'{service_type.name} service_type created sucessfully'}, status=201)
        except Exception as e: return JsonResponse({type(e).__name__: str(e)}, status=400)

    else: return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


@csrf_exempt
#@auth_required(roles=['staff'])
def manage_services_type_view(request, name):
    if request.method == 'POST':
        return JsonResponse({'error': f'{request.method} method not allowed here'}, status=405)

    name = name.title()

    service_type = ServiceType.objects.filter(name=name).first()

    if not service_type:
        return JsonResponse({'error': f"we don't render this service_type '{name}' yet"}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'servicetype_name': service_type.name,
            'servicetype_desc': service_type.description
            }, status=200)
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)

            name = data.get('name')
            description = data.get('description', '')

            if not data:
                return JsonResponse({'error': 'name field is required'}, status=400)

            service_type.name = name
            service_type.description = description

            service_type.save()

            return JsonResponse({
                'msg': f'The service_type {name} has be updated',
                'updated_service_type' : {
                    'name': service_type.name,
                    'description': service_type.description
                } 
                }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON'
            }, status=400)

        pass
    elif request.method == 'DELETE':
        service_type.delete()
        return JsonResponse({'msg': f'{service_type.name} has been deleted'}, status=200)

    return JsonResponse({'manage_service_types': []})


#@auth_required(roles=['staff', 'customer'])
def all_services_type_view(request):
    all_service_types_qset = ServiceType.objects.all()
    all_service_types = [
        {
            'name': service_type.name,
            'description': service_type.description
        } 
        for service_type in all_service_types_qset
    ]
    return JsonResponse({'all_service_types': all_service_types})

@csrf_exempt
#@auth_required(roles=['staff'])
def create_garment_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description')

            if not name:
                raise ValidationError('a service without a name cannot be created')
            
            name = name.lower()

            if name and description:
                item = Garment.objects.create(name=name, description=description)
            elif not description:
                item = Garment.objects.create(name=name)

            return JsonResponse({'success_msg': f'The item {item.name} has been created sucessfully'}, status=201)
        except Exception as e: return JsonResponse({type(e).__name__: str(e)}, status=400)

    else: return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


#@auth_required(roles=['customer', 'staff'])
def manage_garment_view(request, name):
    if request.method == 'POST':
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)

    garment = Garment.objects.filter(name=name).first()

    if not garment:
        return JsonResponse({'error': f'{name} is not yet in the database'}, status=404)

    name = name.title()

    if request.method == 'GET':
        return JsonResponse({'garment': {
            'name': garment.name,
            'description': garment.description
        }}, status=200)
    elif request.method == 'PUT':
        data = json.loads(request.body)

        newname = data.get('name')
        description = data.get('description', '')

        if not newname:
            return JsonResponse({'error': 'name field required to update this garment'}, status=400)
        
        garment.name = newname
        garment.description = description

        garment.save()

        return JsonResponse({'message': f'{name} successfully updated to {newname}'}, status=200)
    elif request.method == 'DELETE':
        garment.delete()
        return JsonResponse({'message': f'{garment.name} has been successfully deleted from this system'}, status=200)


#@auth_required(roles=['staff'])
def all_garment_view(request):
    all_garments = Garment.objects.all()
    garments = [
        {
            'name': garment.name,
            'description': garment.description
        } 
        for garment in all_garments
    ]
    return JsonResponse({'garments': garments})


@csrf_exempt
#@auth_required(roles=['staff'])
def create_service_pricing_view(request):
    if request.method == 'POST':
        try:
            # parse data from json or form
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else: data = request.POST
            
            service_name = data.get('service_name')
            print('service_name:', service_name)
            service_type_name = data.get('service_type')
            print('service_type_name:', service_type_name)
            item_name = data.get('item_name')
            print('item_name:', item_name)
            price = data.get('price')
            print('price:', price)
            delivery_hours = data.get('delivery_hours')
            print('delivery_hour:', delivery_hours)
            is_active = data.get("is_active", True)
            print('is_active:', is_active)

            # Validate required fields
            if not all([service_name, service_type_name, item_name, price, delivery_hours]):
                return JsonResponse(
                    {"error": "Missing required fields (service_name,service_type_name,item_name, delivery_hour and price)"},
                    status=400
                    )


            """
            ensure ServicePricing instance properties to be created is already mentioned in Service, ServiceType and Garment table
            """
            laundry_service, created = LaundryService.objects.get_or_create(name=service_name)
            """if not laundry_service:
                    return JsonResponse(
                    {'error': f"{service_name} is a service that's not in the service table. please add to LaundryService table first"},
                    status=404
                    )"""
            
            service_type, created = ServiceType.objects.get_or_create(name=service_type_name)
            """if not service_type:
                return JsonResponse(
                    {'error': f"{service_type_name} is a service_type that's not in the service_type table. please add to ServiceType table first"},
                    status=404
                    )"""

            garment, created = Garment.objects.get_or_create(name=item_name)
            """if not garment:
                return JsonResponse(
                    {'error': f"{item_name} is an item that's not yet in the garment table, please add to the Garment table first"},
                    status=404
                    )"""

            # check uniqueness manually to avoid data duplicate/repeat data in Servicepricing table
            if ServicePricing.objects.filter(
                service_name=laundry_service,
                service_type=service_type,
                service_item=garment
            ).exists():
                return JsonResponse(
                    {'error': f'This {laundry_service.name} + {service_type.name} + {garment.name} already exist'},
                    status=400
                    )

            # Convert delivery time to timedelta
            try:
                delivery_time = timedelta(hours=int(delivery_hours))
                print(delivery_time)
            except (TypeError, ValueError):
                return JsonResponse({"error": "Invalid delivery_time format. Must be integer hours."}, status=400)

            # create ServicePricing
            service = ServicePricing(
                service_name=laundry_service,
                service_type=service_type, 
                service_item=garment, 
                price=price, 
                duration=delivery_time, #int(delivery_time.total_seconds() // 3600),
                is_active=is_active
                )
            print(service.duration)
            service.save()

            return JsonResponse(
                {
                    'message': "ServicePricing created successfully",
                    "id": service.id,
                    "service": service.service_name.name,
                    "type": service.service_type.name,
                    "item": service.service_item.name,
                    "price": str(service.price),
                    "delivery_hours": int(service.duration.time.total_seconds() // 3600),
                },
                status=201
                )
            
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Invalid service, type, or garment name"}, status=404)

        except (ValueError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': f"Unexpected server error: {str(e)}"}, status=500)

    else: return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


#@auth_required(roles=['staff'])
def manage_services_pricing_view(request, name):
    if request.method == 'POST':
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)

    servicepricing = ServicePricing.objects.filter(name=name).first()

    if not servicepricing:
        return JsonResponse({'error': f'{name} is not yet in the servicepricing table'}, status=404)

    name = name.title()

    if request.method == 'GET':
        return JsonResponse({'garment': {
            'name': servicepricing.name,
            'description': servicepricing.description
        }}, status=200)
    elif request.method == 'PUT':
        data = json.loads(request.body)

        newname = data.get('name')
        description = data.get('description', '')

        if not newname:
            return JsonResponse({'error': 'name field required to update this garment'}, status=400)
        
        servicepricing.name = newname
        servicepricing.description = description

        servicepricing.save()

        return JsonResponse({'message': f'{name} successfully updated to {newname}'}, status=200)
    elif request.method == 'DELETE':
        servicepricing.delete()
        return JsonResponse({'message': f'{servicepricing.name} has been successfully deleted from this system'}, status=200)


#@auth_required(roles=['staff', 'customer'])
def all_servicepricing_view(request):
    servicepricing = ServicePricing.objects.all()
    try:
        return JsonResponse({'all_servicepricing': [{
            'service_type': service.service_type.name,
            'service': service.service_name.name,
            'garment': service.service_item.name,
            'price': service.price,
            'delivery_time': int(service.duration.total_seconds()),
            'is_active': service.is_active
        } for service in servicepricing
        ]}, status=200)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f"Unexpected server error: {str(e)}"}, status=500)