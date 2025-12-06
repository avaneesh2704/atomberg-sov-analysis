# test_youtube.py
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

api_key = os.getenv('YOUTUBE_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "❌ No key found")

try:
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Try a simple search
    request = youtube.search().list(
        q="test",
        part="snippet",
        maxResults=1
    )
    response = request.execute()
    
    print("✅ YouTube API working perfectly!")
    print(f"Test search found: {response['items'][0]['snippet']['title']}")
    
except Exception as e:
    print(f"❌ Error: {e}")