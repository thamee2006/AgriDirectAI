from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Crop, Order


# =========================
# HOME
# =========================

def home(request):
    return render(
        request,
        'marketplace/home.html'
    )


# =========================
# FARMER DASHBOARD
# =========================

@login_required(login_url='/login/')
def farmer(request):

    if request.session.get('role') != 'farmer':
        return redirect('/buyer/')

    crops = Crop.objects.filter(
        farmer=request.user
    ).order_by('-created_at')

    return render(
        request,
        'marketplace/farmer.html',
        {
            'crops': crops
        }
    )


# =========================
# ADD CROP
# =========================

@login_required(login_url='/login/')
def add_crop(request):

    if request.session.get('role') != 'farmer':
        return redirect('/buyer/')

    if request.method == "POST":

        farmer_name = request.POST.get("farmer_name")
        crop_name = request.POST.get("crop_name")
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")
        location = request.POST.get("location")
        description = request.POST.get("description")

        Crop.objects.create(

            farmer=request.user,

            farmer_name=farmer_name,

            crop_name=crop_name,

            quantity=quantity,

            price=price,

            location=location,

            description=description
        )

        return render(
            request,
            'marketplace/add_crop.html',
            {
                'success': 'Crop added successfully!'
            }
        )

    return render(
        request,
        'marketplace/add_crop.html'
    )


# =========================
# BUYER MARKETPLACE
# =========================

@login_required(login_url='/login/')
def buyer(request):

    if request.session.get('role') != 'buyer':
        return redirect('/farmer/')

    crops = Crop.objects.all().order_by('-created_at')

    return render(
        request,
        'marketplace/buyer.html',
        {
            'crops': crops
        }
    )


# =========================
# BUY CROP
# =========================

@login_required(login_url='/login/')
def buy_crop(request, crop_id):

    if request.session.get('role') != 'buyer':
        return redirect('/farmer/')

    crop = get_object_or_404(
        Crop,
        id=crop_id
    )

    if request.method == "POST":

        buyer_name = request.POST.get(
            "buyer_name"
        )

        quantity_text = request.POST.get(
            "quantity"
        )

        try:
            quantity = float(quantity_text)
        except (TypeError, ValueError):

            return render(
                request,
                'marketplace/buy.html',
                {
                    'crop': crop,
                    'error': 'Please enter a valid quantity.'
                }
            )

        # Check available quantity

        if quantity <= 0:

            return render(
                request,
                'marketplace/buy.html',
                {
                    'crop': crop,
                    'error': 'Quantity must be greater than 0.'
                }
            )

        if quantity > crop.quantity:

            return render(
                request,
                'marketplace/buy.html',
                {
                    'crop': crop,
                    'error': 'Requested quantity is not available.'
                }
            )

        # Calculate total price

        total_price = quantity * crop.price

        # Create order

        order = Order.objects.create(
            crop=crop,
            buyer=request.user,
            buyer_name=buyer_name,
            quantity=quantity,
            total_price=total_price,
            status='Pending'
        )

        return redirect(f'/payment/{order.id}/')

    return render(
            request,
            'marketplace/buy.html',
            {
                'crop': crop,
                'success': 'Order placed successfully!'
            }
        )

    return render(
        request,
        'marketplace/buy.html',
        {
            'crop': crop
        }
    )


# =========================
# PAYMENT
# =========================

@login_required(login_url='/login/')
def payment(request, order_id):

    if request.session.get('role') != 'buyer':
        return redirect('/farmer/')

    order = get_object_or_404(
        Order,
        id=order_id,
        buyer=request.user
    )

    if request.method == "POST":
        order.status = "Confirmed"
        order.save()
        return redirect('/orders/')

    return render(
        request,
        'marketplace/payment.html',
        {
            'order': order
        }
    )


# =========================
# MY ORDERS
# =========================

@login_required(login_url='/login/')
def my_orders(request):

    role = request.session.get('role')

    # Buyer orders

    if role == 'buyer':

        orders = Order.objects.filter(
            buyer=request.user
        ).select_related(
            'crop'
        ).order_by(
            '-created_at'
        )

    # Farmer orders

    elif role == 'farmer':

        orders = Order.objects.filter(
            crop__farmer=request.user
        ).select_related(
            'crop',
            'buyer'
        ).order_by(
            '-created_at'
        )

    else:

        orders = Order.objects.none()

    return render(
        request,
        'marketplace/orders.html',
        {
            'orders': orders
        }
    )


# =========================
# UPDATE ORDER STATUS
# =========================

@login_required(login_url='/login/')
def update_order_status(
    request,
    order_id
):

    if request.session.get('role') != 'farmer':

        return redirect('/orders/')

    order = get_object_or_404(

        Order,

        id=order_id,

        crop__farmer=request.user
    )

    if request.method == "POST":

        new_status = request.POST.get(
            "status"
        )

        allowed_status = [
            'Pending',
            'Confirmed',
            'Shipped',
            'Delivered'
        ]

        if new_status in allowed_status:

            order.status = new_status

            order.save()

    return redirect('/orders/')


# =========================
# AI FAIR PRICE
# =========================

@login_required(login_url='/login/')
def fair_price(request):

    crops = Crop.objects.all()

    for crop in crops:

        if crop.quantity >= 1000:

            recommended_price = (
                crop.price * 1.10
            )

        elif crop.quantity >= 500:

            recommended_price = (
                crop.price * 1.05
            )

        else:

            recommended_price = crop.price

        crop.recommended_price = round(
            recommended_price,
            2
        )

    return render(
        request,
        'marketplace/fair_price.html',
        {
            'crops': crops
        }
    )


# =========================
# AI DEMAND FORECAST
# =========================

@login_required(login_url='/login/')
def demand_forecast(request):

    crops = Crop.objects.all()

    for crop in crops:

        if crop.quantity >= 1000:

            demand = "High"

            forecast = (
                "Demand is expected to increase"
            )

        elif crop.quantity >= 500:

            demand = "Medium"

            forecast = (
                "Demand is expected to remain stable"
            )

        else:

            demand = "Low"

            forecast = (
                "Demand may increase with better marketing"
            )

        crop.demand_level = demand

        crop.forecast_message = forecast

    return render(
        request,
        'marketplace/demand_forecast.html',
        {
            'crops': crops
        }
    )


# =========================
# SMART MATCHING
# =========================

@login_required(login_url='/login/')
def smart_matching(request):

    search_crop = request.GET.get(
        'crop',
        ''
    ).strip()

    if search_crop:

        crops = Crop.objects.filter(

            crop_name__icontains=search_crop

        ).order_by(
            '-created_at'
        )

    else:

        crops = Crop.objects.all().order_by(
            '-created_at'
        )

    for crop in crops:

        score = 70

        if crop.quantity >= 100:

            score += 10

        if crop.price <= 50:

            score += 10

        if (
            search_crop
            and
            search_crop.lower()
            ==
            crop.crop_name.lower()
        ):

            score += 10

        crop.match_score = min(
            score,
            100
        )

    return render(
        request,
        'marketplace/smart_matching.html',
        {
            'crops': crops,
            'search_crop': search_crop
        }
    )


# =========================
# SMART LOGISTICS
# =========================

@login_required(login_url='/login/')
def logistics(request):

    role = request.session.get('role')

    if role == 'farmer':

        orders = Order.objects.filter(

            crop__farmer=request.user

        ).select_related(
            'crop',
            'buyer'
        ).order_by(
            '-created_at'
        )

    elif role == 'buyer':

        orders = Order.objects.filter(

            buyer=request.user

        ).select_related(
            'crop'
        ).order_by(
            '-created_at'
        )

    else:

        orders = Order.objects.none()

    for order in orders:

        distance = 50

        delivery_time = "1-2 Days"

        if (
            order.crop.location.lower()
            ==
            "tiruvannamalai"
        ):

            distance = 20

            delivery_time = (
                "Same Day / 1 Day"
            )

        order.distance = distance

        order.delivery_time = delivery_time

    return render(
        request,
        'marketplace/logistics.html',
        {
            'orders': orders
        }
    )


# =========================
# REGISTER
# =========================

def register_user(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        role = request.POST.get(
            "role"
        )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'marketplace/register.html',
                {
                    'error':
                    'Username already exists!'
                }
            )

        user = User.objects.create_user(

            username=username,

            password=password
        )

        login(
            request,
            user
        )

        request.session['role'] = role

        if role == "farmer":

            return redirect('/farmer/')

        return redirect('/buyer/')

    return render(
        request,
        'marketplace/register.html'
    )


# =========================
# LOGIN
# =========================

def login_user(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        role = request.POST.get(
            "role"
        )

        user = authenticate(

            request,

            username=username,

            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            request.session['role'] = role

            if role == "farmer":

                return redirect('/farmer/')

            return redirect('/buyer/')

        return render(
            request,
            'marketplace/login.html',
            {
                'error':
                'Invalid username or password!'
            }
        )

    return render(
        request,
        'marketplace/login.html'
    )


# =========================
# LOGOUT
# =========================

def logout_user(request):

    logout(request)

    return redirect('/')