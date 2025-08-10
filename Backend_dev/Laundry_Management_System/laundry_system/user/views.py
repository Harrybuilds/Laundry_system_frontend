from django.shortcuts import render
from .models import User, CustomerProfile, StaffProfile
from order.models import Order, OrderItem, Invoice
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .utils.createuser import create_user
from .auth.auth_jwt import generate_token, generate_otp, send_otp_email, verify_otp, get_client_ip
from .auth.decorators import auth_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.cache import cache


# Create your views here.
@csrf_exempt
def create_user_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return create_user(**data)
        except Exception as e:
            return JsonResponse({type(e).__name__: str(e)}, status=400)
    else:
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


@csrf_exempt
@auth_required(['staff'])
def manage_user_data(request, pk):
    if request.method == 'POST':
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)

    user = User.objects.filter(id=pk).first()

    if not user:
        return JsonResponse({'error': 'user not found'}, status=404)

    if request.method == 'GET':    
        return JsonResponse({'user': {'email': user.email, 'user_type': user.user_type}}, status=200)

    elif request.method == 'PUT':
        try:
            # get new data
            data = json.loads(request.body)

            # validate new data
            if data.get('email'):
                raise ValidationError('Email can not be changed')

            USER_TYPE = ['customer', 'staff']
            if data.get('user_type') not in USER_TYPE:
                raise ValidationError(f'user_type must be one of these options {USER_TYPE}')

            # update old data
            user.user_type = data.get('user_type', user.user_type)

            if user.user_type != 'customer':
                user.is_staff = True
            else: user.is_staff = False
            
            # save user
            user.save()
            return JsonResponse({'success': 'user data updated successfully',
            'user': {'user_type': user.user_type, 'is_staff': user.is_staff}}, status=200)
        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({type(e).__name__: str(e)}, status=400)

    elif request.method == 'DELETE':
        user.delete()
        return JsonResponse({'user has been deleted from the system'}, status=200)

@csrf_exempt
@auth_required(['staff'])          
def get_all_users(request):
    if request.method == 'GET':
        users_qs = User.objects.all()
        users = [
            {
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'is_staff': user.is_staff,
                'phone': user.phone
            } for user in users_qs
        ]
        return JsonResponse({'users': users}, status=200)
    else: return JsonResponse({'error': f'{request.method} method not allowed here'}, status=405)


"""def search_for_user(request):
    if request.method == 'GET':
        pass
    else: return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)"""


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        ip_address = get_client_ip(request)
        print(f'ip_address: {ip_address}')

        login_attempt = f'login_attempts:{ip_address}'
        attempts = cache.get(login_attempt, 0)

        if attempts >= 5:
            return JsonResponse({'error': 'Too many attempts, try again later.'}, status=429)

        try:
            data = json.loads(request.body)

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'email and password are required'}, status=400)

            user = authenticate(request, email=email, password=password)

            if not user:
                cache.set(login_attempt, attempts + 1, timeout=600)
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
                
            token = generate_token(user)
            user.last_login = timezone.now()
            user.save()
            return JsonResponse({'token': token}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)


"""def logout_view(request):
    if request.method == 'POST':
        user = request.user
        request.user = AnonymousUser
    return JsonResponse({'success': f'{user} logged out successfully'}, status=200)"""


@csrf_exempt
@auth_required(['customer','staff'])
def profile_view(request):
    """
    Return these:
    Basic personal info:  name, email, phone, gender, date_of_birth
    contact info:     address, city, state/region, zip_code/postal_code
    account info:      date_joined, last_login, is_active, is_verified, profile_picture
    preference and settings:  preferred pickup time, notification preference, preferred services  
    role/access control:   role, permissions
    layalty/tracking:     layalty points, total_orders, total_spent
    """
    if request.method not in ['GET', 'PUT']:
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)
    
    # get the user
    user = request.user

    user_info = {
        'email': user.email,
        'phone': user.phone,
        'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S'),
        'is_active': user.is_active,
        'role': user.user_type
    }

    if request.method == 'GET':
        if user.user_type == 'customer':
            customer = CustomerProfile.objects.get(user=user)
            user_info['address'] = customer.address
            return JsonResponse({'profile': user_info}, status=200)
        elif user.user_type == 'staff':
            staff = StaffProfile.objects.get(user=user)
            user_info['address'] = customer.address
            return JsonResponse({'profile': user_info}, status=200)
    
    elif request.method == 'PUT':
        try:
            # get new data
            data = json.loads(request.body)

            # validate new data
            if data.get('email'):
                raise ValidationError('Email can not be changed')

            if data.get('user_type'):
                raise ValidationError(f'user_type can not be changed')

            # update old data
            if data.get('phone'):
                user.phone = data.get('phone')
            
            user_info['phone'] = data.get('phone')

            # update the user in the database
            user.save()
            return JsonResponse({'success': 'user data updated successfully',
            'updated_profile': user_info}, status=200)
        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({type(e).__name__: str(e)}, status=400)


@csrf_exempt
#@auth_required(['customer'])
def otp_password_reset_view(request):
    """
    For non_logged-in users
    steps
    generate 6 digits numbers
    save the 6 digits number in a cache and add a specific valid timeframe
    forward number to user phone number
    when user provide the forwarded number, validate if number provided is correct and the timeframe is not yet met
    if yes, allow user to change password by setting to new provided password to be the current password else do nothing
    """
    if request.method != 'POST':
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)

    try:
        data = json.loads(request.body)
        phone = data.get('phone')

        if not phone:
            return JsonResponse({'error': 'phone number is required'})
        try:
            user = User.objects.filter(phone=phone).first()
            otp = generate_otp(6)
            timeout=300
            cache.set(f'otp_{user.email}', otp, timeout=timeout)

            send_otp_email(otp, user.email, timeout)
            return JsonResponse({"success": f"otp has been sent to {user.email}"})
        except User.DoesNotExist:
            return JsonResponse({'error': 'user not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)


@csrf_exempt
def password_reset_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': f'{request.method} method is not allowed here'}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        password = data.get('newpassword')

        valid_otp = verify_otp(otp, cache.get(f'otp_{email}', 0))
        if valid_otp:
            try:
                user = User.objects.filter(email=email).first()
                user.set_password(password)
                user.save()
                return JsonResponse({'success': 'password reset successfully'}, status=200)
            except User.DoesNotExist:
                return JsonResponse({'error': 'user not valid'}, status=404)
        else:
            return JsonResponse({'error': 'invalid otp'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)



@csrf_exempt
@auth_required(['customer'])
def dashboard_view(request):
    # user
    """
    orders        --->       history of orders
    order and order status      --->   recent orders with their status if any
    amount spent      --->   Monthly break down on laundry (optional)
    discount/coupon   --->   loyalty points, referral rewards or discount code
    pickup delivery schedule   -->  Upcoming schedule pickups or drop-offs
    notification      --->   updates on order status, promos or messages from staff
    order summary     --->   number of cloths washed this month, type of service used
    download invoice  --->   option to view/download invoice or receipt
    profile summary   --->   quick view of customer info
    """

    user = request.user
    orders = Order.objects.filter(customer=user)
    history = [ 
        {
            'order status': order.order_status,
            'order date': order.created_at,
            'items': order_items.all(),
            'total_cost': order.total_cost
        } for order in orders ]

    return JsonResponse({'histrory': history}, status=200)
    # staff
    """
    order breakdown        --->      how many are "pending", "processing", "completed", and "delived"
    customer served today  --->      count of today's customer order
    pickup/delivery schedule ->      list of todays scheduled deliveries or pickup
    sort orders            --->      sort orders based on certain criteria(date, order status, etc)
    overdue orders         --->      orders that have passed the delivery time
    daily/weekly/monthlu revenue ->  total money made today or this week or this month
    branch performance     --->      if multi-branch, orders andrevenue per location
    active users/customers  -->      number of registered/returning user
    tasks for staff        --->      laundry stask assigned (e.g, items to iron, sort) 
    system notification    --->      alerts on customer complaints, system issues, low stock etc
    chart/summary stat     --->      pictorial representation of orders
    profile summary        --->      quick view of staff info
    """