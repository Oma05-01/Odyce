from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from . models import *
from django.core.files.storage import FileSystemStorage
import random
import string
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from .forms import ReviewForm

# Create your views here.
def kini(request):

    return render(request, 'index.html')


def landing(request):
    # Grab the 2 most recent from each category using the auto-added 'date' field
    recent_men = MenPerfume.objects.order_by('-date')[:2]
    recent_women = WomenPerfume.objects.order_by('-date')[:2]

    # Combine them into a single list
    recent_perfumes = list(recent_men) + list(recent_women)

    context = {
        'recent_perfumes': recent_perfumes
    }
    return render(request, 'landing.html', context)


def register(request):
    if request.method == "POST":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get form data
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            password1 = request.POST.get('password')
            password2 = request.POST.get('confirm-password')

            # Generate a 6-character coupon code
            coupon = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            # Validate form data
            if not all([first_name, last_name, email, phone_number, password1, password2]):
                return JsonResponse({'status': 'error', 'msg': 'All fields are required'})

            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'msg': 'This email is already registered'})

            if len(password1) < 8:
                return JsonResponse({'status': 'error', 'msg': 'Your password is too short'})

            if password1 != password2:
                return JsonResponse({'status': 'error', 'msg': "Your passwords didn't match"})

            # Create User
            user = User.objects.create_user(username=email, email=email, password=password1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Create Customer record linked to User
            Customer.objects.create(
                user=user,  # Assuming Customer has a ForeignKey to User
                coupon_code=coupon,
                phone_number=phone_number,
            )

            # Send success response as JSON
            messages.success(request, "Account created successfully! You can log in now.")
            return JsonResponse({'status': 'success', 'msg': "Account created successfully! You can log in now."})

    return render(request, 'sign_up.html')


def login_user(request):

    if request.method == 'POST':
        user_ = request.POST.get('email')
        pass_ = request.POST.get('password')

        if not user_:
            msg = 'Please, username field should be filled'
            return JsonResponse({'status': 'error', 'msg': msg})

        if not pass_:
            msg = 'Please, password field should be filled'
            return JsonResponse({'status': 'error', 'msg': msg})

        user = authenticate(username=user_, password=pass_)
        print(user_, pass_)
        print(user)

        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success', 'msg': 'Login successful.'})
        else:
            msg = "Please provide valid login credentials"
            return JsonResponse({'status': 'error', 'msg': msg})

    return render(request, 'login.html')


@login_required(login_url='/login')
def logout_user(request):
    
    logout(request)

    return redirect('login')


@login_required(login_url='/login')
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required(login_url='/login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required(login_url='/login')
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return JsonResponse({'status': 'success', 'message': 'Account deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required(login_url='/login')
def home(request):

    men_perfumes = MenPerfume.objects.all()
    women_perfumes = WomenPerfume.objects.all()
    return render(request, 'home.html', {'men_perfumes': men_perfumes, 'women_perfumes': women_perfumes})


@login_required(login_url='/login')
def product_detail(request, product_type, product_id):
    # Dynamically select the correct model based on the URL parameter
    if product_type == 'men':
        product = get_object_or_404(MenPerfume, pk=product_id)
        content_type = ContentType.objects.get_for_model(MenPerfume)
    elif product_type == 'women':
        product = get_object_or_404(WomenPerfume, pk=product_id)
        content_type = ContentType.objects.get_for_model(WomenPerfume)
    else:
        return render(request, '404.html')

    # Fetch reviews related to this specific product
    reviews = Review.objects.filter(content_type=content_type, object_id=product.id)

    # Handle review submission
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.user = request.user.customer # Using the updated related name
            new_review.content_type = content_type
            new_review.object_id = product.id
            new_review.save()
            return redirect('product_detail', product_type=product_type, product_id=product.id)
    else:
        review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'perfume_details_page.html', context)

@login_required(login_url='/login')
def product_review(request, product_id):
    # Retrieve the product based on the provided product_id
    try:
        item = get_object_or_404(MenPerfume, id=product_id)
    except:
        item = get_object_or_404(WomenPerfume, id=product_id)

    return render(request, 'perfume_review.html', {'item': item})


@login_required(login_url='/login')
def buy_now(request, product_type, product_id):
    cities = ["Igarra", "Irrua", "Uselu", "Agenebode", "Uromi", "Auchi", "Ubiaja", "Fugar", "Ekpoma", "Iguegben",
              "Idogbo", "Afuze", "Abudu", "Okada", "Oredo", "Iguobazuwa", "Sabongida Ora", "Ehor"]
    discount_code = request.POST.get('discount_code')

    if discount_code:
        customer = request.user.customer
        if discount_code == customer.applied_coupon:
            messages.error(request, 'Coupon already used')
            discount_code = None

    # Strict check using the URL parameter
    if product_type == 'men':
        product = get_object_or_404(MenPerfume, pk=product_id)
    elif product_type == 'women':
        product = get_object_or_404(WomenPerfume, pk=product_id)
    else:
        return render(request, '404.html')

    context = {
        'cities': cities,
        'discount_code': discount_code,
        'product': product,
        'product_type': product_type, # Pass this to the template for checkout routing
    }

    request.session['product_id'] = product_id
    request.session['product_type'] = product_type

    return render(request, 'buy_now.html', context)


@login_required(login_url='/login')
def buy_as_distributor(request, product_type, product_id):
    # Strictly route based on the URL parameter
    if product_type == 'men':
        product = get_object_or_404(MenPerfume, pk=product_id)
    elif product_type == 'women':
        product = get_object_or_404(WomenPerfume, pk=product_id)
    else:
        return render(request, '404.html')  # Handle unknown product type

    cities = ['Lagos', 'Abuja', 'Jos', 'Rivers', 'Benin', 'Aba']

    context = {
        'product': product,
        'product_type': product_type, # Passing this so the template knows what we're buying
        'cities': cities
    }

    return render(request, 'buy_as_distributor.html', context)


@csrf_exempt
def save_session_data(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Store all fields in session storage, including product_id
        request.session['billing_name'] = data.get('billing_name')
        request.session['billing_address'] = data.get('billing_address')
        request.session['billing_city'] = data.get('billing_city')
        request.session['phone-number'] = data.get('phone-number')
        request.session['quantity'] = data.get('quantity')
        request.session['finalPrice'] = data.get('finalPrice')
        request.session['discountCode'] = data.get('discountCode')
        request.session['product_id'] = data.get('product_id')  # Save product_id in session

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required(login_url='/login')
def checkout(request):
    final_price = request.session.get('finalPrice')
    product_id = request.session.get('product_id')
    # ADD THIS LINE: Retrieve the product type from the session
    product_type = request.session.get('product_type')

    if request.method == 'POST' and final_price:
        # Your payment logic here...
        return redirect('confirm_payment')

    context = {
        'billing_name': request.session.get('billing_name'),
        'billing_address': request.session.get('billing_address'),
        'billing_city': request.session.get('billing_city'),
        'phone_number': request.session.get('phone-number'),
        'quantity': request.session.get('quantity'),
        'final_price': final_price,
        'discount_code': request.session.get('discountCode'),
        'product_id': product_id,
        # ADD THIS LINE: Pass it to the template
        'product_type': product_type
    }
    return render(request, 'checkout.html', context)


@login_required(login_url='/login')
def confirm_payment(request):
    final_price = request.session.get('finalPrice')
    product_id = request.session.get('product_id')
    product_type = request.session.get('product_type')

    if not final_price:
        return redirect('home')

    if request.method == 'POST':

        order = Order(
            customer=request.user.customer,  # Ensure the customer is linked to the current user
            billing_name=request.session.get('billing_name'),
            billing_address=request.session.get('billing_address'),
            billing_city=request.session.get('billing_city'),
            phone_number=request.session.get('phone-number'),
            quantity=request.session.get('quantity'),
            total=final_price  # Set the final price as the total
        )
        print('okay')
        order.save()

        receipt = request.FILES.get('receipt')

        # Attach the receipt and update order status
        order.receipt = receipt

        # Check if a discount code was used and save it to applied_coupon
        discount_code = request.session.get('discountCode')
        if discount_code:
            request.user.customer.applied_coupon = discount_code
            request.user.customer.save()

        order.save()

        messages.success(request, 'Your payment has been submitted successfully and is awaiting confirmation.')

        try:
            subject = 'Your Odyce Fragrance Order is Confirmed'
            # You can use a simple string or a fancy HTML template
            message = f"Hello {request.user.first_name},\n\nThank you for your purchase of ₦{final_price}. Your scent journey with Odyce has begun! We are preparing your order for shipment to {request.session.get('billing_city')}."
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]

            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(f"Email error: {e}")  # Log error but don't stop the user experience

        # Clear session data
        keys_to_clear = ['finalPrice', 'product_id', 'product_type', 'quantity', 'discountCode']
        for key in keys_to_clear:
            if key in request.session:
                del request.session[key]

        return render(request, 'success_page.html', {'price': final_price})  # Replace 'success_page' with the actual page name

    # Payment details (adjust as needed)
    bank_name = "Your Bank Name"
    account_number = "1234567890"

    context = {
        'bank_name': bank_name,
        'account_number': account_number,
        'final_price': final_price,
        'product_id': product_id
    }

    return render(request, 'customer_payment_page.html', context)


@login_required(login_url='/login')
def success_page(request):

    return render(request, 'success_page.html')


@login_required(login_url='/login')
def customer_orders(request):

    # Retrieve all orders for the current user
    orders = Order.objects.filter(customer__user=request.user).order_by('-date_created')

    context = {
        'orders': orders,
    }

    return render(request, 'customer_order_history.html', context)


@login_required(login_url='/login')
def add_to_wishlist(request, product_type, product_id):
    # 1. SAFETY CHECK: Guard against Admin/Superusers who don't have a Customer profile
    try:
        customer = request.user.customer
    except ObjectDoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Admin accounts cannot use the wishlist. Please use a customer profile."
        }, status=400)

    # 2. Determine the correct model and ContentType
    if product_type == 'men':
        product = get_object_or_404(MenPerfume, pk=product_id)
        content_type = ContentType.objects.get_for_model(MenPerfume)
    elif product_type == 'women':
        product = get_object_or_404(WomenPerfume, pk=product_id)
        content_type = ContentType.objects.get_for_model(WomenPerfume)
    else:
        return JsonResponse({"status": "error", "message": "Invalid product type."}, status=400)

    # 3. Create or update the wishlist item using the safely retrieved 'customer'
    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=customer,
        content_type=content_type,
        object_id=product.id
    )

    if not created:
        wishlist_item.quantity += 1
        wishlist_item.save()

    return JsonResponse({"status": "success", "message": "Item added to your Odyce wishlist."})


@login_required
def view_wishlist(request):
    try:
        # Attempt to get the customer profile
        customer = request.user.customer
        wishlist_items = WishlistItem.objects.filter(user=customer)

        # Helper to identify product type (men/women)
        for item in wishlist_items:
            item.product_type = item.content_type.model.replace('perfume', '').lower()

        return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

    except ObjectDoesNotExist:
        # If no customer profile exists, show an empty wishlist or a message
        messages.warning(request, "Your account does not have a customer profile.")
        return render(request, 'wishlist.html', {'wishlist_items': []})

@login_required(login_url='/login')
def remove_from_wishlist(request, item_id):
    try:
        # Get the Customer instance linked to the logged-in User
        customer_profile = request.user.customer

        # Query using the Customer instance
        wishlist_item = get_object_or_404(WishlistItem, id=item_id, user=customer_profile)
        wishlist_item.delete()
        messages.success(request, "Item removed from your vault.")

    except ObjectDoesNotExist:
        # Fallback for Superusers/Admins without a Customer profile
        messages.error(request, "Admin accounts do not have access to customer wishlist items.")
        return redirect("home")

    return redirect("view_wishlist")


@login_required
def become_distributor(request):
    try:
        # 1. Attempt to get the profile
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        # 2. If it doesn't exist (like for an admin), create it on the fly
        customer = Customer.objects.create(user=request.user)
        # Or redirect them to a "Complete Profile" page

    if request.method == 'POST':
        # Your logic for distributor application here...
        pass

    return render(request, 'be_a_distributor.html', {'customer': customer})


@login_required(login_url='/login')
def distributor_checkout(request, product_type):
    if request.method == 'POST':
        # Retrieve product details based on product type (men or women)
        product_id = request.POST.get('product_id')
        if product_type == 'men':
            product = get_object_or_404(MenPerfume, pk=product_id)
        elif product_type == 'women':
            product = get_object_or_404(WomenPerfume, pk=product_id)
        else:
            return render(request, '404.html')  # Return 404 if the product type is invalid

        # Set minimum quantity for distributors
        quantity = int(request.POST.get('quantity', 20))
        if quantity < 20:
            messages.error(request, "Minimum order quantity for distributors is 20 units.")
            return redirect('buy_as_distributor')  # Adjust as necessary

        # Calculate total price for distributor purchase
        total_price = product.price * quantity
        discount_code = request.POST.get('discount_code')

        # Store relevant data in session
        request.session['product_id'] = product.id
        request.session['quantity'] = quantity
        request.session['final_price'] = total_price
        request.session['product_type'] = product_type
        if discount_code:
            request.session['discountCode'] = discount_code  # For `confirm_payment()` to access

        # Create an order instance
        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total=total_price,
            status='distributor_pending'
        )

        # Redirect to checkout with the distributor order context
        return redirect('distributor_checkout')  # Replace with your actual checkout page URL

    # If GET request, show distributor product page
    return render(request, 'distributor_checkout.html', {'product_type': product_type})


@login_required(login_url='/login')
def create_article(request):

    if request.method == "POST":
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        content = request.POST.get('content')

        article = Articles(
            title=title,
            summary=summary,
            content=content,
        )
        article.save()
        return redirect('articles')

    return render(request, 'create_article.html')


@login_required(login_url='/login')
def edit_article(request, article_id):
    post = get_object_or_404(Articles, id=article_id)

    if request.method == "POST":
        post.title = request.POST['title']
        post.publish_date = request.POST['publish_date']
        post.content = request.POST['content']
        post.save()

        messages.success(request, 'Article updated successfully!')
        return redirect('article_detail', article_id=post.id)

    return render(request, 'edit_article.html', {'post': post})


@login_required(login_url='/login')
def articles(request):

    posts = Articles.objects.all()

    return render(request, 'article_list.html', {'posts': posts})


@login_required(login_url='/login')
def article_details(request, title):

    post = get_object_or_404(Articles, title=title)

    return render(request, 'article_details.html', {'post': post})


@login_required(login_url='/login')
def delete_article(request, post_id):
    post = get_object_or_404(Articles, id=post_id)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Article deleted successfully!")
        return redirect('article_list')  # Replace with the URL name for your article list

    return render(request, 'confirm_article_delete.html', {'post': post})


@login_required(login_url='/login')
def men(request):

    mens_perfumes = MenPerfume.objects.all()

    return render(request, 'men.html', {'mens_perfumes': mens_perfumes})


@login_required(login_url='/login')
def women(request):

    womens_perfumes = WomenPerfume.objects.all()

    return render(request, 'women.html', {'womens_perfumes': womens_perfumes})


def faq(request):

    return render(request, 'faq.html')


@login_required(login_url='/login')
def contact_us(request):

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        contact = ContactUS(
            name=name,
            email=email,
            message=message,
        )
        contact.save()

        # i want an alert kind of message here

        return redirect('contact_us')

    return render(request, 'contact_us.html')


@login_required(login_url='/login')
def reviews(request):

    review_ = Review.objects.all()

    return render(request, 'reviews.html', {'reviews': review_})


# User Activity View
@login_required(login_url='/login')
def user_activity(request):
    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )
    # Users who have ever logged in (users with a non-null 'last_login' in the related User model)
    users_logged_in = Customer.objects.filter(user__last_login__isnull=False)

    # Get active sessions (i.e., currently logged-in users)
    active_sessions = Session.objects.filter(expire_date__gte=now())

    # Extract user IDs from active sessions by looking in the session_data
    active_user_ids = []
    for session in active_sessions:
        session_data = session.get_decoded()  # Get decoded session data
        user_id = session_data.get('_auth_user_id')  # The user ID is stored in _auth_user_id
        if user_id:
            active_user_ids.append(user_id)

    # Get the users who are currently logged in based on the extracted user IDs
    current_users = User.objects.filter(id__in=active_user_ids)

    # Paginate both lists
    logged_in_paginator = Paginator(users_logged_in, 10)  # Show 10 per page
    current_users_paginator = Paginator(current_users, 10)  # Show 10 per page

    # Get the current page number for each list
    logged_in_page = request.GET.get('logged_in_page')
    current_users_page = request.GET.get('current_users_page')

    # Get the respective page of users
    users_logged_in_page = logged_in_paginator.get_page(logged_in_page)
    for customer in users_logged_in:
        print(customer.user.last_login, 'jjj')
    current_users_page = current_users_paginator.get_page(current_users_page)

    context = {
        'users_logged_in': users_logged_in_page,
        'current_users': current_users_page,
        'confirmed_orders_locations': confirmed_orders_locations,
        'pending_orders_by_location': pending_orders_by_location,
    }

    return render(request, 'user_activity.html', context)


# User Detail View
@login_required(login_url='/login')
def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    try:
        customer = user.customer  # Access the related Customer instance
        print(customer.first_name)
    except Customer is None:
        return render(request, 'user_detail.html', {'user': user, 'orders': []})

    # Retrieve all orders associated with this customer
    orders = Order.objects.filter(customer=customer)

    return render(request, 'user_detail.html', {'user': customer, 'orders': orders})


# Dashboard View
@login_required(login_url='/login')
def dashboard(request):

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )
    print(confirmed_orders_locations)

    context = {
        'pending_orders_by_location': pending_orders_by_location,
        'confirmed_orders_locations': confirmed_orders_locations,
    }
    return render(request, 'dashboard.html', context)


# Pending Orders View (Grouped by location)
@login_required(login_url='/login')
def pending_orders(request):

    # Group pending orders by billing city
    pending_orders_by_location = (
        Order.objects.filter(status="pending")
        .values("billing_city")
        .annotate(count=Count("id"))
    )

    context = {
        "pending_orders_by_location": pending_orders_by_location,
    }
    return render(request, "pending_orders.html", context)


@login_required(login_url='/login')
def orders_by_location(request, location):

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )

    # Fetch all pending orders for the specified billing city
    orders = Order.objects.filter(billing_city=location, status="pending")

    context = {
        'pending_orders_by_location': pending_orders_by_location,
        "location": location,
        "orders": orders,
        'confirmed_orders_locations': confirmed_orders_locations,
    }
    return render(request, "orders_by_location.html", context)


@login_required(login_url='/login')
def confirmed_orders_by_location(request, location):

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))

    # Fetch confirmed orders for the specified billing city
    orders = Order.objects.filter(billing_city=location, status="confirmed")

    # Fetch confirmed orders grouped by location
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )

    print(confirmed_orders_locations)

    context = {
        "location": location,  # Pass the location directly as a string
        "orders": orders,
        'confirmed_orders_locations': confirmed_orders_locations,
        'pending_orders_by_location': pending_orders_by_location
    }
    return render(request, "confirmed_orders_by_location.html", context)


# Order Details View
@login_required(login_url='/login')
def order_details(request, order_id):
    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )

    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'confirmed_orders_locations': confirmed_orders_locations,
        'pending_orders_by_location': pending_orders_by_location,
    }
    return render(request, 'order_details.html', context)


@login_required(login_url='/login')
def confirm_order(request, order_id):

    # this is for the dashboard
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.confirm_order()
        # Notify user (e.g., via email) - Placeholder for notification code
        send_mail(
            'Order Confirmed',
            f'Your order has been confirmed. Your confirmation code is {order.confirmed_order_code}.',
            'OdyceForBenin@gmail.com',
            [order.customer.email],
            fail_silently=False,
        )
        return redirect('dashboard')


@login_required(login_url='/login')
def contact_us_messages(request):

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )
    messages_ = ContactUS.objects.all()

    context = {
        'pending_orders_by_location': pending_orders_by_location,
        'confirmed_orders_locations': confirmed_orders_locations,
        'messages': messages_
    }

    return render(request, 'contact-us_messages.html', context)


@login_required(login_url='/login')
def add_for_men(request):
    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )

    context = {
        'pending_orders_by_location': pending_orders_by_location,
        'confirmed_orders_locations': confirmed_orders_locations,
    }

    if request.method == 'POST':
        name = request.POST.get('name')
        scent = request.POST.get('scent')
        description = request.POST.get('description')
        price = request.POST.get('price')
        myfile = request.FILES.get('myfile')  # Get the file directly

        if myfile:
            product = MenPerfume(
                name=name,
                pic_name=myfile.name,  # Optional now, but kept for your schema
                picurl=myfile,  # Pass the raw file directly to the ImageField
                price=price,
                description=description,
                scent=scent
            )
            product.save()
            return redirect('men_list')

    return render(request, 'add_for_men.html', context)


@login_required(login_url='/login')
def add_for_women(request):

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )

    context = {
        'pending_orders_by_location': pending_orders_by_location,
        'confirmed_orders_locations': confirmed_orders_locations,
    }

    if request.method == 'POST':
        name = request.POST.get('name')
        scent = request.POST.get('scent')
        description = request.POST.get('description')
        price = request.POST.get('price')
        myfile = request.FILES.get('myfile')  # Get the file directly

        if myfile:
            product = MenPerfume(
                name=name,
                pic_name=myfile.name,  # Optional now, but kept for your schema
                picurl=myfile,  # Pass the raw file directly to the ImageField
                price=price,
                description=description,
                scent=scent
            )
            product.save()
            return redirect('men_list')

    return render(request, 'add_for_women.html', context)


@login_required(login_url='/login')
def men_list(request):

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )
    men_products = MenPerfume.objects.all()

    context = {
        'pending_orders_by_location': pending_orders_by_location,
        'confirmed_orders_locations': confirmed_orders_locations,
        'products': men_products
    }
    return render(request, 'men_list.html', context)


@login_required(login_url='/login')
def women_list(request):
    women_products = WomenPerfume.objects.all()

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )

    context = {
        'pending_orders_by_location': pending_orders_by_location,
        'confirmed_orders_locations': confirmed_orders_locations,
        'products': women_products
    }
    return render(request, 'women_list.html', context)


@login_required(login_url='/login')
def edit_product(request, product_type, product_id):
    if product_type == 'men':
        product = get_object_or_404(MenPerfume, id=product_id)
    elif product_type == 'women':
        product = get_object_or_404(WomenPerfume, id=product_id)
    else:
        return render(request, '404.html')

    if request.method == "POST":
        product.name = request.POST['name']
        product.scent = request.POST['scent']
        product.description = request.POST['description']
        product.price = request.POST['price']

        if 'myfile' in request.FILES:
            product.picurl = request.FILES['myfile']  # Updated to match your ImageField name

        product.save()
        messages.success(request, 'Product updated successfully!')

        # Include product_type in the redirect!
        return redirect('product_detail', product_type=product_type, product_id=product.id)

    return render(request, 'edit_product.html', {'product': product, 'product_type': product_type})


@login_required(login_url='/login')
def product_detail_back(request, product_type, product_id):
    # Admin view for viewing product details
    if product_type == 'men':
        product = get_object_or_404(MenPerfume, pk=product_id)
    elif product_type == 'women':
        product = get_object_or_404(WomenPerfume, pk=product_id)
    else:
        return render(request, '404.html')

    return render(request, 'product_detail.html', {'product': product, 'product_type': product_type})


@login_required(login_url='/login')
def delete_product(request, product_type, product_id):
    if product_type == 'men':
        product = get_object_or_404(MenPerfume, id=product_id)
        redirect_url = 'men_list'
    elif product_type == 'women':
        product = get_object_or_404(WomenPerfume, id=product_id)
        redirect_url = 'women_list'
    else:
        return render(request, '404.html')

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect(redirect_url)

    return render(request, 'confirm_delete.html', {'product': product, 'product_type': product_type})


@login_required(login_url='/login')
def all_list(request):
    men_products = MenPerfume.objects.all()
    women_products = WomenPerfume.objects.all()

    context = {
        'men_products': men_products,
        'women_products': women_products
    }

    return render(request, 'perfume_list.html', context)


@login_required(login_url='/login')
def view_users(request):

    pending_orders_by_location = Order.objects.filter(status='pending').values('billing_city').annotate(
        count=Count('id'))
    confirmed_orders_locations = (
        Order.objects
        .filter(status='confirmed')
        .values('billing_city')
        .annotate(count=Count('id'))
        .order_by('billing_city')
    )

    users = User.objects.all()
    context = {
        'users': users,
        'confirmed_orders_locations': confirmed_orders_locations,
        'pending_orders_by_location': pending_orders_by_location,
    }

    return render(request, 'view_users.html', context)


@login_required
def submit_review(request, model_name, product_id):
    # 1. Map the string from the URL to the actual Model class
    model_map = {
        'men': MenPerfume,
        'women': WomenPerfume,
    }

    selected_model = model_map.get(model_name)
    if not selected_model:
        return redirect('home')

    # 2. Get the specific perfume instance
    product = get_object_or_404(selected_model, id=product_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # 3. Get the ContentType for this specific model
        content_type = ContentType.objects.get_for_model(selected_model)

        # 4. Create the Review using the Generic Foreign Key fields
        Review.objects.create(
            user=request.user.customer,  # Assuming request.user has a .customer profile
            content_type=content_type,
            object_id=product.id,
            rating=rating,
            comment=comment
        )

        messages.success(request, f"Your impression of {product.name} has been shared.")
        return redirect('home')  # Or back to the product detail

    return render(request, 'submit_review.html', {'product': product, 'model_name': model_name})


@login_required
def view_invoice(request, order_id):
    # 1. Fetch the order
    order = get_object_or_404(Order, id=order_id)

    # 2. Security Check: Only the order owner or staff can see the invoice
    # If your Order model links to 'User' directly, use order.user
    # If it links to 'Customer', use order.user.customer
    if order.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this invoice.")

    # 3. Calculate subtotal if it's not stored in the DB
    # This ensures the invoice always shows the math correctly
    subtotal = order.unit_price * order.quantity

    context = {
        'order': order,
        'subtotal': subtotal,
    }

    return render(request, 'invoice_template.html', context)