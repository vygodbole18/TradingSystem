from kiteconnect import KiteConnect
import os 
from dotenv import load_dotenv


def get_kite():
    load_dotenv()
    kite_object = KiteConnect(api_key=os.getenv("API_KEY"))
    access_token_for_other = os.getenv("ACCESS_TOKEN")
    kite_object.set_access_token(access_token_for_other)
    return kite_object 