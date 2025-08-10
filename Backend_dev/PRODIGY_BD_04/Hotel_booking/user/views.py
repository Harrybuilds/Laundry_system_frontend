from decimal import Decimal
from django.http import JsonResponse
from .models import Room, Booking
from django.core.exceptions import ValidationError
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

# Create your views here.

def display(request):
    return JsonResponse({'msg': 'display view function called'}, status=200)


@csrf_exempt
def new_room(request):
    if request.method == 'POST':
        try:
            # handles json data 
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                price = data.get('price')
                description = data.get('description', '')
                category = data.get('category')
            else:
                # handles form data                
                price = request.POST.get('price')
                description = request.POST.get('description', '')
                category = request.POST.get('category')

            if price and category and description:
                room = Room.objects.create(price=price, description=description, category=category)

            elif price and category:
                room = Room.objects.create(price=price, category=category)

            elif price and description:
                room = Room.objects.create(price=price, description=description)

            else:
                room = Room.objects.create()


            room = Room.objects.create()
            
            return JsonResponse({'message': f'room created successfully {room}'}, status=201)

        except Exception as e:
            return JsonResponse({type(e).__name__: str(e)}, status=400)
    
    return JsonResponse({'error': f'{request.method} method not allowed here'}, status=405)


@csrf_exempt
def get_all_rooms(request):
    if request.method == 'GET':
        all_rooms = Room.objects.all()
        rooms = [ {
            "room_no": room.room_no,
            "price": str(room.price),
            "category": room.category,
            "available": 'yes' if room.available else 'no',
            } for room in all_rooms ]
        return JsonResponse({'all_rooms': rooms}, status=200)
    return JsonResponse({'error': f'{request.method} method not allowed here'}, status=405)


@csrf_exempt
def access_room_by_room_no(request, room_no):
    room = Room.objects.filter(room_no=room_no).first()
    if room:
        if request.method == 'GET':
            room_data = {
                "room_no": room.room_no,
                "price": str(room.price),
                "category": room.category,
                "available": 'yes' if room.available else 'no',
            }
            return JsonResponse({'Room Details': room_data}, status=200)
            
        elif request.method == 'PUT':
            try:
                # handles json data
                if request.content_type == 'application/json':
                    room_data = json.loads(request.body)
                    room.description = room_data.get('description', room.description)
                    room.category = room_data.get('category', room.category)
                    available = room_data.get('available', room.available)
                    room.price = room_data.get('price', room.DEFAULT_PRICE.get(room.category))
                
                if room.category not in room.DEFAULT_PRICE:
                    raise ValidationError('specified room category must be in the original categories list') 

                room.save()
                return JsonResponse({'message': 'room updated successfully',
                'new_roon_info': {'room_no': room_no, 'description': room.description,
                'category':room.category, 'available': 'yes' if room.available else 'no', 'price': room.price
                }
                }, status=200)
                    
            except Exception as e:
                return JsonResponse({type(e).__name__: str(e)}, status=500)

        elif request.method == 'DELETE':
            room.delete()
            return JsonResponse({'message': f'{room.room_no} has been successfully deleted'})
        else:
            return JsonResponse({'error': f'{request.method} method not allowed here'}, status=405) 
    else:
        return JsonResponse({'error': 'Room does not exist'}, status=404)


def search_available_rooms(request):
    if request.method == 'GET':
        unavailable = request.GET.get('unavailable')
        if unavailable is True:
            stat = True
        else:
            stat = False
        rooms_qs = Room.objects.filter(available=stat)
        rooms = [
                {
                'room_number': room.room_no,
                'price': Decimal(room.price),
                'category': room.category,
                'description': room.description
                }
                for room in rooms_qs
            ]

        available_rooms = {'available_rooms': rooms}
        unavailable_rooms = {'unavailable_rooms': rooms}

        if stat:
            return JsonResponse(available_rooms, status=200)
        else:
            return JsonResponse(unavailable_rooms, status=200)
    return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


def check_room_availability_within_timeframe(request):
    if request.method == 'GET':
            # handles query parameter data
            room_no = request.GET.get('room_no')
            check_in = request.GET.get('check_in')
            check_out = request.GET.get('check_out')

            if not check_in or not check_out:
                return JsonResponse({'error': 'Either check_in or check_out date is misssing'}, status=400)
            try:
                check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out, "%Y-%m-%d").date()

                # continue working from here
                room = Room.objects.filter(room_no=room_no).first()

                if room:
                    room_bk = Booking.objects.filter(room=room,
                    check_in__lte=check_in,
                    check_out__gte=check_out
                    )
                    if room_bk:
                        return JsonResponse({'error': 'room would not be available by then'})
                    else:
                        return JsonResponse({'Free Room': 'room would be available by then'})
                else:
                    return JsonResponse({'error': 'room does not exist'}, status=404)

                """rooms = Room.objects.filter(
                    available=True,
                    room_bk_qs.check_in__lte=check_in,
                    room_bk_qs.check_out__gte=check_out
                )"""

            except Exception as e:
                return JsonResponse({type(e).__name__: str(e)}, status=400)
    
    return JsonResponse({'error': f'{request.method} method is not allowed'}, status=405)


@csrf_exempt
def changeroomavailability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            room_no = data.get('room_no')
            availability = data.get('availability')

            room = Room.objects.filter(room_no=room_no).first()
            if room:
                room.available = availability
                room.save()
                return JsonResponse({'message': f"{room.room_no} has be updated"})
        except Exception as e:
            return JsonResponse({type(e).__name__: str(e)}, status=400)
    else:
        return JsonResponse({'error': f'{request.method} method is not allowed'}, status=405)

def bookaroom(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        room_no = data.get('room_no')
        check_in = data.get("check_in")
        check_out = data.get("check_out")

        """ check room availability by confirming the room.available is True,
        check the booking record if the room is free for
        the period of the checkin and checkout timeframe
        book or reject request based on the outcome of the check """
