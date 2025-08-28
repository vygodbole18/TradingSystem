from kiteconnect import KiteConnect
import os 
from dotenv import load_dotenv

# load .env file to environment
load_dotenv()

kite = KiteConnect(api_key=os.getenv("API_KEY"))
login_url = kite.login_url()

print("Login to this URL", login_url)

request_token = os.getenv("REQUEST_TOKEN")
api_secret = os.getenv("API_SECRET")

session_data = kite.generate_session(request_token, api_secret)

access_token = session_data["access_token"]
print(access_token)

kite.set_access_token(access_token)
