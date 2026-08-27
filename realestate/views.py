from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Buyer, Seller, Surveyor
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from realestate.models import Seller
from django.contrib.auth import login
from django.urls import reverse
from .models import Seller
from django.urls import path
from .models import Land
from realestate.models import Buyer, Seller, Surveyor
from django.contrib.auth import get_user_model
from .forms import SellerRegistrationForm
from .forms import BuyerForm
from.forms import Surveyor
from .models import Seller
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from .forms import EditListingForm
from django.shortcuts import render, get_object_or_404, redirect
from .forms import SellerContactForm
from .forms import SurveyorLoginForm
from realestate.models import Buyer
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .forms import SurveyorForm
from .forms import SurveyorProfileForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import ChatRoom, Message
from .models import ChatRoom
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import ChatRoom, Message
import json
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from .models import ChatRoom, Seller, Surveyor
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import Message, ChatRoom
from django.http import HttpResponse
from django.conf import settings
import pusher
from django.http import JsonResponse
from pusher import Pusher
from realestate.forms import LandForm
from .forms import LandForm
from .forms import LandForm
from .models import Land, Seller, ChatRoom
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from functools import wraps
from realestate.decorators import seller_login_required
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import Buyer, Seller, Surveyor
import json
from django.contrib.auth import get_user_model
import traceback
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
import logging
from .models import Land
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .mpesa.stk_push import lipa_na_mpesa_online
logger = logging.getLogger(__name__)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect
from django.contrib import messages
from .mpesa.stk_push import lipa_na_mpesa_online
from .models import Surveyor 
from .forms import SurveyorPromotionForm
import threading
import time
from .forms import PhoneNumberForm
from django.urls import reverse
from django.utils import timezone
from .models import ChatRoom 
from realestate.models import Payment
from realestate.mpesa.stk_push import send_stk_push
from realestate.mpesa.stk_push import send_seller_verification_stk_push

@login_required
def initiate_seller_verification_payment(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        payment = Payment.objects.create(
            seller=request.user,  # Storing seller in buyer field (Option 2)
            amount=1,
            phone_number=phone_number,
            purpose='seller_verification',
            status='pending',
            created_at=timezone.now()
        )

        checkout_id = send_seller_verification_stk_push(
            phone_number,
            amount=1,
            account_reference=f"verification-{seller.id}",
            payment_id=payment.id
        )

        if checkout_id:
            payment.checkout_request_id = checkout_id
            payment.save()


        # Show waiting page that redirects after 10 seconds
        return render(request, 'waiting_for_seller_verification_payment.html')

    return render(request, 'enter_phone_number_for_seller_verification.html', {'seller': seller})

 

@login_required
def initiate_chat_payment(request, seller_id):
    seller = get_object_or_404(Seller, id=seller_id)

    # ✅ Check if buyer already paid to chat with this seller
    existing_payment = Payment.objects.filter(
        buyer=request.user,
        seller=seller,
        purpose='chat_unlock',
        status='success'
    ).first()

    if existing_payment:
        chat_room, _ = ChatRoom.objects.get_or_create(buyer=request.user, seller=seller)
        return redirect('chat_room', chat_room_id=chat_room.id)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        # Create a Payment record
        payment = Payment.objects.create(
            buyer=request.user,
            seller=seller,
            amount=50,
            phone_number=phone_number,
            purpose='chat_unlock',
            status='pending',
            created_at=timezone.now()
        )

        # Send STK push
        checkout_id = send_stk_push(
            phone_number,
            amount=50,
            account_reference=f"chat-{request.user.id}-{seller.id}",
            payment_id=payment.id
        )

        # Save checkout ID
        if checkout_id:
            payment.checkout_request_id = checkout_id
            payment.status = 'success'  # Mark as paid for testing
            payment.save()

        # ✅ Create or get the chat room
        chat_room, created = ChatRoom.objects.get_or_create(buyer=request.user, seller=seller)

        # ✅ Pass chat_room_id to the template
        return render(request, 'waiting_for_payment.html', {
            'payment': payment,
            'chat_room_id': chat_room.id
        })

    return render(request, 'enter_phone_number.html', {'seller': seller})






@csrf_exempt
def buyer_mpesa_callback(request):
    logger.info("Received buyer callback: %s", request.body)
    if request.method == 'POST':
        data = json.loads(request.body)
        print("CALLBACK RECEIVED:", data)

        result_code = data['Body']['stkCallback']['ResultCode']
        checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']

        try:
            # Get the payment using checkout_request_id
            payment = Payment.objects.get(checkout_request_id=checkout_request_id)
        except Payment.DoesNotExist:
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Transaction not found"}, status=404)

        if result_code == 0:
            # Payment was successful
            payment.status = 'paid'
            payment.save()

            # Unlock the chat
            UnlockedChat.objects.get_or_create(
                buyer=payment.buyer,
                seller=payment.seller
            )

            print(f"Chat unlocked for {payment.buyer.username} and {payment.seller.name}!")

        else:
            print(f"Payment failed or cancelled for CheckoutRequestID {checkout_request_id}")

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    return JsonResponse({"message": "Method not allowed"}, status=405)

@csrf_exempt
def seller_mpesa_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("SELLER CALLBACK RECEIVED:", data)

        result_code = data['Body']['stkCallback']['ResultCode']
        checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']

        try:
            payment = Payment.objects.get(
                checkout_request_id=checkout_request_id,
                purpose='seller_verification'
            )
        except Payment.DoesNotExist:
            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Transaction not found"
            }, status=404)

        if result_code == 0:
            payment.status = 'paid'
            payment.save()

            seller = payment.seller
            seller.is_verified = True
            seller.save()

            print(f"Seller {seller.id} verified successfully after payment!")

        else:
            payment.status = 'failed'
            payment.save()

            print(
                f"Seller verification payment failed or cancelled "
                f"for CheckoutRequestID {checkout_request_id}"
            )

        return JsonResponse({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        })

    return JsonResponse({"message": "Method not allowed"}, status=405)




def promote_in_progress(request):
    return render(request, 'promote_in_progress.html')

from .models import Surveyor 
@csrf_exempt
def promote_surveyor(request):
    if request.method == 'POST':
        form = SurveyorPromotionForm(request.POST)

        if form.is_valid():
            surveyor_id = form.cleaned_data['surveyor_id']
            phone_number = form.cleaned_data['phone_number']

            surveyor = get_object_or_404(Surveyor, id=surveyor_id)

            response = lipa_na_mpesa_online(phone_number, 500, surveyor_id)
            print("MPESA Response:", response)  # 🔥 Debugging print

            if response and response.get('ResponseCode') == "0":  # ✅ Safe check
                messages.success(request, "STK Push sent! Please complete the payment on your phone.")

                # 🔥 Start a background thread to promote after 10 seconds
                def promote_after_delay():
                    time.sleep(10)
                    surveyor.is_promoted = True
                    surveyor.save()
                    print(f"Surveyor {surveyor_id} promoted automatically after 10 seconds.")

                threading.Thread(target=promote_after_delay).start()

                return redirect('promote_in_progress')  # ✅ Redirect to spinner page
            else:
                messages.error(request, "Failed to initiate payment. Please try again.")
                return redirect('surveyor_dashboard')
        else:
            messages.error(request, "Invalid form submission.")
            return redirect('surveyor_dashboard')
    else:
        form = SurveyorPromotionForm()

    return render(request, 'promote_surveyor.html', {'form': form})



    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(auth_url, auth=(consumer_key, consumer_secret))
    access_token = r.json()['access_token']
    return access_token

def stk_push(phone_number, amount, account_reference, transaction_desc):
    access_token = get_access_token()
    headers = {"Authorization": "Bearer %s" % access_token}

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((settings.BUSINESS_SHORTCODE + settings.PASSKEY + timestamp).encode()).decode()

    payload = {
        "BusinessShortCode": settings.BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/callback_url/",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
    return response.json()
@login_required(login_url='/login/seller/') 
def feature_land(request, land_id):
    print(f"User: {request.user}")
    print(f"Is authenticated: {request.user.is_authenticated}")
    print(f"Request method: {request.method}")
    print("Feature land view called.")


    if request.method == 'POST':
        try:
            land = get_object_or_404(Land, id=land_id)
            print(f"Land object found: {land}")
            
            # Proceed with the STK push logic...
            request.session['land_to_feature'] = land.id

            phone_number = '254723175831'  # or dynamically get seller's phone
            amount = 200

            lipa_na_mpesa_online(phone_number, amount)
            
            return JsonResponse({'success': True, 'message': 'STK Push Sent. Please complete payment.'})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'message': 'Error processing request.'}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)



@csrf_exempt
def mpesa_callback(request):
    logger.info("Received callback: %s", request.body)
    if request.method == 'POST':
        data = json.loads(request.body)
        print("CALLBACK RECEIVED:", data)

        result_code = data['Body']['stkCallback']['ResultCode']
        checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']

        try:
            # Find the transaction by checkout_request_id
            transaction = STKPushTransaction.objects.get(checkout_request_id=checkout_request_id)
        except STKPushTransaction.DoesNotExist:
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Transaction not found"}, status=404)

        if result_code == 0:
            # Payment was successful
            transaction.paid = True
            transaction.save()

            # Promote the surveyor
            surveyor = transaction.surveyor
            surveyor.is_promoted = True
            surveyor.save()

            print(f"Surveyor {surveyor.id} promoted successfully after payment!")

        else:
            print(f"Payment failed or cancelled for CheckoutRequestID {checkout_request_id}")

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    return JsonResponse({"message": "Method not allowed"}, status=405)



def surveyor_dashboard(request):
    surveyor_id = request.session.get('surveyor_id')
    if not surveyor_id:
        return redirect('login_surveyor')  # Ensure this URL exists

    try:
        surveyor = Surveyor.objects.get(id=surveyor_id)
    except Surveyor.DoesNotExist:
        return redirect('login_surveyor')

    # Fetch chat rooms where the surveyor is involved
    chat_rooms = ChatRoom.objects.filter(surveyor=surveyor)

    # Render the dashboard
    return render(
        request,
        'surveyor_dashboard.html',
        {'surveyor': surveyor, 'chat_rooms': chat_rooms}
    )
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def seller_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'email') and request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect('/login/seller/?next=' + request.path)
    return _wrapped_view
def seller_dashboard(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')  # not logged in

    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return redirect('seller_login')  # session tampered

    land_listings = Land.objects.filter(seller=seller)
    chat_rooms = ChatRoom.objects.filter(seller=seller)

    return render(request, 'seller_dashboard.html', {
        'seller': seller,
        'land_listings': land_listings,
        'chat_rooms': chat_rooms,
    })
def seller_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(f"Email entered: {email}")
        print(f"Password entered: {password}")

        try:
            seller = Seller.objects.get(email=email)
        except Seller.DoesNotExist:
            messages.error(request, 'Seller does not exist.')
            return redirect('seller_login')

        if seller.check_password(password):
            print(f"Logged in seller: {seller.email}")
            
            # ✅ Set the correct backend explicitly
            login(request, seller, backend='realestate.backends.SellerAuthBackend')
            
            # You can still store seller ID in session if needed
            request.session['seller_id'] = seller.id
            return redirect('seller_dashboard')
        else:
            messages.error(request, 'Invalid password')
            return redirect('seller_login')

    return render(request, 'seller_login.html')

def edit_contact_details(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')  # Redirect if the seller is not logged in

    # Fetch the seller instance
    seller = Seller.objects.get(id=seller_id)

    if request.method == "POST":
        # Bind form with POST data
        form = SellerContactForm(request.POST, instance=seller)
        if form.is_valid():
            # Save the form and redirect to seller dashboard
            form.save()
            return redirect('seller_dashboard')
    else:
        # Initialize form with the seller's current details
        form = SellerContactForm(instance=seller)

    # Render the template with the form
    return render(request, 'edit_contact_details.html', {'form': form})


def landing_page(request):
    return render(request, 'realestate/landing_page.html')

def register_buyer(request):
    if request.method == 'POST':
        form = BuyerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Buyer registration successful!')
            return redirect('login')  # Adjust this to the login page
    else:
        form = BuyerForm()
    return render(request, 'realestate/register_buyer.html', {'form': form})

def register_seller(request):
    if request.method == "POST":
        form = SellerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            seller = form.save(commit=True)  # Seller instance is saved here

            messages.success(request, "Registration successful. Please log in.")
            return redirect("seller_login")
    else:
        form = SellerRegistrationForm()

    return render(request, "realestate/register_seller.html", {"form": form})


def register_surveyor(request):
    if request.method == 'POST':
        form = SurveyorForm(request.POST)
        
        if form.is_valid():
            # Save the form, but hash the password before saving the surveyor
            surveyor = form.save(commit=False)
            surveyor.password = make_password(form.cleaned_data['password'])
            surveyor.save()

            messages.success(request, 'Surveyor registered successfully!')
            return redirect('login_surveyor')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = SurveyorForm()

    return render(request, 'realestate/register_surveyor.html', {'form': form})

from django.shortcuts import render



from .models import Land  # or wherever your Land model is

@login_required
def buyer_dashboard(request):
    lands = Land.objects.select_related('seller').all()
    surveyors = Surveyor.objects.all().order_by('-is_promoted', 'id')
    return render(request, 'buyer_dashboard.html', {'lands': lands, 'surveyors': surveyors})


def add_land(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')

    try:
        seller = Seller.objects.get(id=seller_id)
    except Seller.DoesNotExist:
        return redirect('seller_login')

    if request.method == 'POST':
        form = LandForm(request.POST, request.FILES)
        if form.is_valid():
            land = form.save(commit=False)
            land.seller = seller  # ✅ Correct seller assignment
            land.save()
            return redirect('seller_dashboard')
    else:
        form = LandForm()

    return render(request, 'realestate/add_land.html', {'form': form})

def land_listings(request):
    lands = Land.objects.all()  # Fetch all land listings
    return render(request, 'realestate/land_listings.html', {'lands': lands})

def edit_listing(request, listing_id):
    # Retrieve the specific land listing (not the seller) for the seller
    listing = get_object_or_404(Land, id=listing_id)

    if request.method == 'POST':
        # Bind the form with POST data and files (for image uploads)
        form = EditListingForm(request.POST, request.FILES, instance=listing)
        
        if form.is_valid():
            form.save()  # Save the updated listing
            messages.success(request, 'Listing updated successfully!')
            return redirect('seller_dashboard')  # Redirect to the seller dashboard after updating
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize the form with the current listing instance
        form = EditListingForm(instance=listing)

    # Render the edit listing page with the form
    return render(request, 'edit_listing.html', {'form': form, 'listing': listing})

    return render(request, 'edit_listing.html', {'form': form, 'listing': listing})
def add_land_listing(request):
    # Ensure the seller is logged in
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')  # Redirect to login if not logged in

    seller = Seller.objects.get(id=seller_id)  # Fetch the logged-in seller

    if request.method == "POST":
        form = LandForm(request.POST, request.FILES)  # Handle form with file uploads
        if form.is_valid():
            land_listing = form.save(commit=False)  # Create the object without saving to DB
            land_listing.seller = seller  # Associate the listing with the logged-in seller
            land_listing.save()  # Save the new land listing
            return redirect('seller_dashboard')  # Redirect to the seller dashboard
    else:
        form = LandForm()

    return render(request, 'add_land_listing.html', {'form': form})

User = get_user_model()

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']  # The email (username) of the buyer
        password = request.POST['password']

        print(f"Trying to authenticate with email: {username}")

        # Authenticate using Django's built-in User model
        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"Authenticated user: {user.username}, Email: {user.email}")  # Debugging log
            # Log the user in
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('buyer_dashboard')  # Redirect to buyer's dashboard
        else:
            print("Authentication failed.")  # Debugging log
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'realestate/login.html')

logger = logging.getLogger(__name__)

def login_surveyor(request):
    logger.debug("Surveyor login view called")
    if request.method == 'POST':
        logger.debug("Processing POST request")
        form = SurveyorLoginForm(request.POST)
        if form.is_valid():
            logger.debug("Form is valid")
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate using the custom backend
            logger.debug(f"Attempting surveyor login: {email}")
            surveyor = authenticate(request, email=email, password=password)
            logger.debug(f"Surveyor after authenticate: {surveyor}")

            if surveyor is not None:
                login(request, surveyor, backend='realestate.backends.SurveyorAuthBackend')
                logger.debug("Login successful")
                
                # Store the surveyor's ID in the session
                request.session['surveyor_id'] = surveyor.id
                logger.debug(f"Surveyor ID stored in session: {request.session['surveyor_id']}")
                
                return redirect('surveyor_dashboard')
            else:
                logger.error(f"Surveyor authentication failed: {email}")
                messages.error(request, 'Invalid email or password.')
        else:
            logger.debug("Form is invalid")
            logger.debug(form.errors)
    else:
        logger.debug("Not a POST request")
        form = SurveyorLoginForm()
    
    return render(request, 'realestate/login_surveyor.html', {'form': form})


# Initialize Pusher client
pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True,
    timeout=15,
)



@login_required
def start_chat(request, target_type, target_id):
    try:
       buyer = Buyer.objects.get(id=request.user.id)

    except Buyer.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Only buyers can start chats.'}, status=403)

    # 🔁 If target is seller: redirect to payment initiation
    if target_type == "seller":
        return redirect('initiate_chat_payment', seller_id=target_id)

    # ✅ For surveyors, proceed as before (no changes)
    elif target_type == "surveyor":
        target = get_object_or_404(Surveyor, id=target_id)
        chat_room, created = ChatRoom.objects.get_or_create(buyer=buyer, surveyor=target)

        channel = f'chat-{chat_room.id}'
        payload = {
            'buyer_id': buyer.id,
            'message': 'You have a new message from a buyer.',
        }

        try:
            pusher_client.trigger(channel, 'chat-started', payload)
        except Exception as e:
            print("⚠️ Pusher trigger failed:", e)

        return JsonResponse({
            'status': 'Chat started',
            'channel': channel,
            'chat_room_id': chat_room.id,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid target type'}, status=400)

@csrf_protect
@require_POST
@login_required
def send_message(request, chat_room_id):
    print("=== [send_message view called] ===")
    print(f"Logged-in user: {request.user} (ID: {request.user.id})")

    try:
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        print(f"Loaded ChatRoom: {chat_room}")

        # Display chat participants
        if chat_room.buyer:
            print(f"Buyer: {chat_room.buyer.username} (ID: {chat_room.buyer.id})")
        if chat_room.seller:
            print(f"Seller: {chat_room.seller.email} (ID: {chat_room.seller.id})")
        if chat_room.surveyor:
            print(f"Surveyor: {chat_room.surveyor.username} (ID: {chat_room.surveyor.id})")

        # Parse incoming data
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        print(f"Message text: '{message_text}'")

        if not message_text:
            print("⚠️ Message content is missing")
            return JsonResponse({'error': 'Message content is required'}, status=400)

        user = request.user
        actual_sender = None

        print("🔍 Verifying sender identity from ChatRoom...")
        if isinstance(user, Buyer) and chat_room.buyer and chat_room.buyer.id == user.id:
            actual_sender = chat_room.buyer
            print("✅ Sender confirmed as Buyer")
        elif isinstance(user, Seller) and chat_room.seller and chat_room.seller.id == user.id:
            actual_sender = chat_room.seller
            print("✅ Sender confirmed as Seller")
        elif isinstance(user, Surveyor) and chat_room.surveyor and chat_room.surveyor.id == user.id:
            actual_sender = chat_room.surveyor
            print("✅ Sender confirmed as Surveyor")
        else:
            print("❌ Unauthorized sender")
            return JsonResponse({'error': 'Unauthorized sender for this chat'}, status=403)

        content_type = ContentType.objects.get_for_model(actual_sender.__class__)
        print(f"📦 ContentType: {content_type}, Object ID: {actual_sender.id}")

        # Save the message
        message = Message.objects.create(
            chat_room=chat_room,
            content_type=content_type,
            object_id=actual_sender.id,
            content=message_text
        )
        print("💾 Message saved successfully:", message)

        sender_username = getattr(actual_sender, 'username', None) or getattr(actual_sender, 'email', 'Unknown')
        sender_type = actual_sender.__class__.__name__.lower()

        # Push to Pusher
        pusher_client.trigger(
            f'chatroom-{chat_room_id}',
            'new-message',
            {
                'sender': sender_username,
                'sender_type': sender_type,
                'sender_id': actual_sender.id,
                'message': message.content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        print("📡 Message pushed to Pusher successfully")

        return JsonResponse({
            'status': 'Message sent successfully',
            'sender': sender_username,
            'sender_type': sender_type
        })

    except json.JSONDecodeError:
        print("❌ JSON decoding failed")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    except Exception as e:
        print("🔥 An error occurred while sending the message:")
        traceback.print_exc()
        return JsonResponse({'error': f'Failed to send message: {str(e)}'}, status=500)



    
@login_required
def respond_to_message(request, message_id):
    # Fetch the message that needs to be responded to
    message = Message.objects.get(id=message_id)
    
    # Check if the user is the seller or surveyor
    if message.seller == request.user or message.surveyor == request.user:
        # If the logged-in user is the seller or surveyor, allow them to respond
        
        if request.method == "POST":
            # Get the response content from the POST request
            response_content = request.POST.get("response_content")

            # Create a new message from the seller/surveyor to the buyer
            new_message = Message.objects.create(
                buyer=message.buyer,
                seller=message.seller if message.seller else None,
                surveyor=message.surveyor if message.surveyor else None,
                content=response_content
            )
            
            # You could trigger a Pusher event here if you're using Pusher for real-time updates

            return JsonResponse({"status": "Message sent", "message": new_message.content})
        
        # Render the response form
        return render(request, 'respond_to_message.html', {'message': message})

    # If the logged-in user is neither the seller nor surveyor, deny access
    return JsonResponse({"status": "Unauthorized", "message": "You are not authorized to respond to this message."})


@login_required
def chat_room(request, chat_room_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    messages = Message.objects.filter(chat_room=chat_room).order_by('timestamp')

    if (request.user != chat_room.buyer and 
        request.user != chat_room.seller and 
        (not chat_room.surveyor or request.user != chat_room.surveyor)):
        return render(request, 'chat/error.html', {
            'error': 'You are not authorized to access this chat room.'
        }, status=403)

    return render(request, 'chat/chat_room.html', {
        'chat_room': chat_room,
        'messages': messages,
        'user': request.user
    })
@login_required
def get_surveyor_messages(request):
    if not hasattr(request.user, 'surveyor'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    surveyor = request.user.surveyor
    messages = ChatMessage.objects.filter(receiver=surveyor).values(
        'id', 'text', 'sender__username', 'timestamp'
    ).order_by('timestamp')

    return JsonResponse(list(messages), safe=False)

@login_required
def get_seller_messages(request):
    if not hasattr(request.user, 'seller'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    seller = request.user.seller
    messages = ChatMessage.objects.filter(receiver=seller).values(
        'id', 'text', 'sender__username', 'timestamp'
    ).order_by('timestamp')

    return JsonResponse(list(messages), safe=False)

def chat_error(request):
    return render(request, 'chat/error.html', {'message': 'You are not authorized to view this chat room.'})

    from django.contrib import messages

def logout_user(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


def feature_land(request, land_id):
    land = get_object_or_404(Land, id=land_id, seller=request.user)

    if request.method == 'POST':
        # Simulate successful payment
        land.is_featured = True
        land.save()
        messages.success(request, "Your land has been featured successfully!")

    return redirect('seller_dashboard')
