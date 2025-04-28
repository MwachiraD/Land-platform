import requests
from requests.auth import HTTPBasicAuth

# Your app credentials
consumer_key = "vpAEBXncQhEmNqIkEZoIDk444NOU4cMAAQ20A1CC8ofaczBk"
consumer_secret = "S7LqBoPAKjAA13WgbmpGfPqkAy8EAdIRLFglNrQRdAuTZgKF4T8fbkLbSEWvNRG0"

# Access token URL
url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

# Send request
response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

# Check if the request was successful
if response.status_code == 200:
    # Parse the response to get the access token
    access_token = response.json()['access_token']
    print(f"Access Token: {access_token}")
else:
    print(f"Error: {response.status_code}, {response.text}")
