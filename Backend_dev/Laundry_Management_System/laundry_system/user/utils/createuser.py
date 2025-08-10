from user.models import User, CustomerProfile, StaffProfile
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import re

def create_user(**kwargs):
    """
    Goal - create a user and the appropraite profile for the user  
    """

    username = kwargs.get('username')
    email = kwargs.get('email')
    user_type = kwargs.get('user_type')
    phone = kwargs.get('phone')
    password = kwargs.get('password')
    confirm_password = kwargs.get('confirm_password')

    # data validation
    if not email or not username or not password or not confirm_password or not phone:
        raise ValidationError('email, username, password, confirm_password and phone fields are required')

    # email validation
    EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"

    if not re.match(EMAIL_REGEX, email):
        return JsonResponse({'error': 'Invalid email address'}, status=400)

    # user_type validation
    if user_type:
        USER_TYPE = ['staff', 'customer']
        if user_type not in USER_TYPE:
            raise ValidationError(f'user_type must be in {USER_TYPE}')
    
    # password validation
    if password != confirm_password:
        raise ValidationError('passwords must match, please try again')

    if user_type:
        user = User(email=email, username=username, user_type=user_type, phone=phone)
        user.set_password(password)
    else:
        user = User(email=email, username=username, phone=phone)
        user.set_password(password)

    if user.user_type != 'customer':
        user.is_staff = True
            
    user.save()

    if user_type == 'customer':

        if kwargs.get('address'):
            customer = CustomerProfile(user=user, address=kwargs.get('address'))
        else:
            customer = CustomerProfile(user=user)

        customer.save()
    else:
        if kwargs.get('role'):
            staff = StaffProfile(user=user, role=kwargs.get('role'))
        else:
            staff = StaffProfile(user=user)

        staff.save()
    return JsonResponse({'success': 'User created successfully', 'user': {
                'email':user.email,
                'user_type': user.user_type
                }}, status=201)

