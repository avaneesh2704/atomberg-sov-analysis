# test_apify.py
import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

token = os.getenv('APIFY_TOKEN')
print(f"Token loaded: {token[:20]}..." if token else "❌ No token")

try:
    client = ApifyClient(token)
    
    # Get account info
    user = client.user().get()
    print(f"✅ Apify working! Account: {user.get('username', 'Unknown')}")
    
except Exception as e:
    print(f"❌ Error: {e}")