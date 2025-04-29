import requests
from requests.auth import HTTPBasicAuth
import base64
import datetime
from realestate.models import STKPushTransaction, Surveyor  # ✅ combined import
from django.utils import timezone
from realestate.models import Payment




# Credentials
consumer_key = 'vpAEBXncQhEmNqIkEZoIDk444NOU4cMAAQ20A1CC8ofaczBk'
consumer_secret = 'S7LqBoPAKjAA13WgbmpGfPqkAy8EAdIRLFglNrQRdAuTZgKF4T8fbkLbSEWvNRG0'
shortcode = "174379"
passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"


# Function to send STK Push
def lipa_na_mpesa_online(phone_number, amount, surveyor_id):
    callback_url = "https://bce8-105-230-156-204.ngrok-free.app/mpesa/callback/"  # ✅ your ngrok URL

    # 1. Fetch the Surveyor object first
    try:
        surveyor = Surveyor.objects.get(id=surveyor_id)
    except Surveyor.DoesNotExist:
        raise ValueError("Surveyor not found")

    # 2. Get access token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth_response = requests.get(auth_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = auth_response.json().get('access_token')

    # 3. Generate password
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = shortcode + passkey + timestamp
    online_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

    # 4. Prepare headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 5. Prepare request payload
    payload = {
        "BusinessShortCode": shortcode,
        "Password": online_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": str(surveyor_id),
        "TransactionDesc": "Payment for LandPlatform Service"
    }

    # 6. Send STK Push
    stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(stk_push_url, json=payload, headers=headers)

    res_data = response.json()

    if res_data.get('ResponseCode') == '0':
        STKPushTransaction.objects.create(
            surveyor=surveyor,  # ✅ Pass full surveyor object, not ID
            phone_number=phone_number,
            checkout_request_id=res_data['CheckoutRequestID'],
            merchant_request_id=res_data['MerchantRequestID'],
            amount=amount,
            paid=False,  # Payment is not yet confirmed
        )

    return res_data


def send_stk_push(phone_number, amount, account_reference, payment_id):
    callback_url = "https://your-ngrok-url.ngrok-free.app/mpesa/buyer/callback/"

    # 1. Get access token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth_response = requests.get(auth_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = auth_response.json().get('access_token')

    # 2. Generate password
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = shortcode + passkey + timestamp
    online_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

    # 3. Prepare headers and payload
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": online_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": "Unlock Chat with Seller"
    }

    # 4. Send STK Push
    stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(stk_push_url, json=payload, headers=headers)

    res_data = response.json()

    if res_data.get('ResponseCode') == '0':
        # Optional: store identifiers for future verification
        payment = Payment.objects.get(id=payment_id)
        payment.checkout_request_id = res_data['CheckoutRequestID']
        payment.merchant_request_id = res_data['MerchantRequestID']
        payment.save()

    return res_data.get('CheckoutRequestID')


def send_seller_verification_stk_push(phone_number, amount, account_reference, payment_id):
    callback_url = "https://your-ngrok-url.ngrok-free.app/mpesa/seller/callback/"

    # 1. Get access token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth_response = requests.get(auth_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    access_token = auth_response.json().get('access_token')

    # 2. Generate password
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = shortcode + passkey + timestamp
    online_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

    # 3. Prepare headers and payload
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": online_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": "Seller Verification"
    }

    # 4. Send STK Push
    stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(stk_push_url, json=payload, headers=headers)

    res_data = response.json()

    if res_data.get('ResponseCode') == '0':
        # Optional: store identifiers for future verification
        payment = Payment.objects.get(id=payment_id)
        payment.checkout_request_id = res_data['CheckoutRequestID']
        payment.merchant_request_id = res_data['MerchantRequestID']
        payment.save()

    return res_data.get('CheckoutRequestID')