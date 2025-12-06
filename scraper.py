"""
Multi-Platform Social Media Scraper for SoV Analysis
ENHANCED VERSION: Added Google Search (4 platforms total)
YouTube: Google Cloud API | Twitter, Instagram, Google: Apify
"""

import pandas as pd
import json
import time
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# ============================================
# YOUTUBE SCRAPER (using YouTube Data API v3)
# ============================================
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        if not api_key or api_key == "YOUR_YOUTUBE_API_KEY":
            print("⚠️  YouTube API key not set properly!")
            self.youtube = None
        else:
            try:
                self.youtube = build('youtube', 'v3', developerKey=api_key)
                print("✅ YouTube API initialized successfully")
            except Exception as e:
                print(f"❌ YouTube API initialization failed: {e}")
                self.youtube = None
        
    def search_videos(self, query, max_results=20):
        """Search for videos and get detailed stats"""
        if not self.youtube:
            print("⚠️  Skipping YouTube (API not configured)")
            return pd.DataFrame()
            
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance'
            ).execute()
            
            if not search_response.get('items'):
                print("   No YouTube videos found")
                return pd.DataFrame()
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get detailed video statistics
            videos_response = self.youtube.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()
            
            results = []
            for video in videos_response['items']:
                stats = video['statistics']
                snippet = video['snippet']
                
                results.append({
                    'platform': 'YouTube',
                    'id': video['id'],
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'channel': snippet['channelTitle'],
                    'published_at': snippet['publishedAt'],
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'url': f"https://youtube.com/watch?v={video['id']}"
                })
            
            return pd.DataFrame(results)
            
        except HttpError as e:
            print(f"   YouTube API Error: {e}")
            print("   💡 Check your API key in .env file")
            return pd.DataFrame()
        except Exception as e:
            print(f"   YouTube Error: {e}")
            return pd.DataFrame()


# ============================================
# X/TWITTER SCRAPER (Using Apify: apidojo/tweet-scraper)
# ============================================
try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False
    print("⚠️  apify-client not installed")

class TwitterScraper:
    def __init__(self, apify_token):
        self.client = None
        if not APIFY_AVAILABLE:
            print("⚠️  apify-client not installed. Twitter scraping disabled.")
            return

        if not apify_token or apify_token == "YOUR_APIFY_TOKEN":
            print("⚠️  Apify token not set - Twitter scraping disabled")
        else:
            try:
                self.client = ApifyClient(apify_token)
                print("✅ Twitter/Apify initialized successfully")
            except Exception as e:
                print(f"❌ Apify initialization failed for Twitter: {e}")

    def search_tweets(self, query, max_results=50):
        """Search tweets using Apify"""
        if not self.client:
            print("⚠️  Skipping Twitter (Apify not configured)")
            return pd.DataFrame()

        try:
            run_input = {
                "searchTerms": [query],
                "sort": "Latest",
                "maxItems": max_results, 
                "proxyConfig": { "useApifyProxy": True }
            }
            
            # Execute the run
            run = self.client.actor("apidojo/tweet-scraper").call(run_input=run_input)
            
            if not run:
                print("   ⚠️  Twitter scraper failed to start")
                return pd.DataFrame()

            # Fetch results
            dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items
            
            tweets = []
            for item in dataset_items:
                tweets.append({
                    'platform': 'Twitter',
                    'id': item.get('id_str') or item.get('id'),
                    'text': item.get('full_text') or item.get('text', '')[:500],
                    'author': item.get('user', {}).get('screen_name', 'unknown'),
                    'followers': item.get('user', {}).get('followers_count', 0),
                    'likes': item.get('favorite_count', 0),
                    'retweets': item.get('retweet_count', 0),
                    'replies': item.get('reply_count', 0),
                    'published_at': item.get('created_at'),
                    'url': item.get('url') or f"https://twitter.com/x/status/{item.get('id_str')}"
                })

            if not tweets:
                print("   No tweets found")
            
            return pd.DataFrame(tweets)

        except Exception as e:
            print(f"   Twitter error: {str(e)[:100]}")
            return pd.DataFrame()


# ============================================
# INSTAGRAM SCRAPER (using Apify API)
# ============================================
class InstagramScraper:
    def __init__(self, apify_token):
        self.apify_token = apify_token
        
        if not APIFY_AVAILABLE:
            print("⚠️  Apify client not available")
            self.client = None
            return
            
        if not apify_token or apify_token == "YOUR_APIFY_TOKEN":
            print("⚠️  Apify token not set - Instagram scraping disabled")
            self.client = None
        else:
            try:
                self.client = ApifyClient(apify_token)
                print("✅ Instagram/Apify initialized successfully")
            except Exception as e:
                print(f"❌ Apify initialization failed: {e}")
                self.client = None
        
    def search_posts(self, hashtag, max_results=30):
        """Search Instagram posts by hashtag"""
        if not self.client:
            print("   ⚠️  Skipping Instagram (Apify not configured)")
            return pd.DataFrame()
            
        try:
            # Use Instagram Hashtag Scraper
            run_input = {
                "hashtags": [hashtag.replace('#', '').replace(' ', '')],
                "resultsLimit": max_results
            }
            
            print(f"   Searching Instagram for #{hashtag}...")
            run = self.client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
            
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append({
                    'platform': 'Instagram',
                    'id': item.get('id', 'unknown'),
                    'caption': item.get('caption', '')[:500],
                    'username': item.get('ownerUsername', 'unknown'),
                    'likes': item.get('likesCount', 0),
                    'comments': item.get('commentsCount', 0),
                    'type': item.get('type', 'photo'),
                    'published_at': item.get('timestamp'),
                    'url': item.get('url', '')
                })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            print(f"   Instagram error: {str(e)[:150]}")
            print("   💡 Check your Apify token or try reducing resultsLimit")
            return pd.DataFrame()


# ============================================
# GOOGLE SEARCH SCRAPER (FIXED VERSION)
# ============================================
# Copy this entire class and REPLACE the GoogleSearchScraper class in your scraper.py

class GoogleSearchScraper:
    def __init__(self, apify_token):
        self.apify_token = apify_token
        
        if not APIFY_AVAILABLE:
            print("⚠️  Apify client not available")
            self.client = None
            return
            
        if not apify_token or apify_token == "YOUR_APIFY_TOKEN":
            print("⚠️  Apify token not set - Google Search scraping disabled")
            self.client = None
        else:
            try:
                self.client = ApifyClient(apify_token)
                print("✅ Google Search/Apify initialized successfully")
            except Exception as e:
                print(f"❌ Apify initialization failed: {e}")
                self.client = None
    
    def search_google(self, query, max_results=15, country_code='in'):  # FIXED: lowercase 'in'
        """
        Search Google and get top organic results
        
        Args:
            query: Search query
            max_results: Number of results (default 15)
            country_code: Country for localized results (default 'in' for India)
        """
        if not self.client:
            print("   ⚠️  Skipping Google Search (Apify not configured)")
            return pd.DataFrame()
        
        try:
            # Create search variations for better coverage
            search_variations = [
                f"{query} review India",
                f"{query} best brands",
                f"buy {query}"
            ]
            
            all_results = []
            results_per_variation = max_results // len(search_variations)
            
            for search_query in search_variations:
                try:
                    print(f"   Searching: '{search_query[:40]}...'")
                    
                    run_input = {
                        "queries": search_query,
                        "maxPagesPerQuery": 1,
                        "resultsPerPage": results_per_variation,
                        "countryCode": country_code,  # Now lowercase 'in'
                        "languageCode": "en",
                        "mobileResults": False,
                        "includeUnfilteredResults": False  # ADDED: This parameter
                    }
                    
                    # Run Google Search Scraper
                    run = self.client.actor("apify/google-search-scraper").call(run_input=run_input)
                    
                    # Extract organic results
                    for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                        for result in item.get('organicResults', []):
                            all_results.append({
                                'platform': 'Google',
                                'id': result.get('url', 'unknown'),
                                'title': result.get('title', ''),
                                'description': result.get('description', ''),
                                'url': result.get('url', ''),
                                'domain': result.get('displayedUrl', ''),
                                'position': result.get('rank', 0),
                                'channel': result.get('displayedUrl', '').split('/')[0],  # Extract domain
                                'published_at': None,
                                'views': 0,
                                'likes': 0,
                                'comments': 0,
                                'search_variation': search_query
                            })
                    
                    # Small delay between variations to avoid rate limits
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"   Error in variation '{search_query[:30]}': {str(e)[:80]}")
                    continue
            
            if not all_results:
                print("   No Google results found")
                return pd.DataFrame()
            
            df = pd.DataFrame(all_results)
            # Remove duplicates based on URL
            df = df.drop_duplicates(subset=['url'], keep='first')
            
            return df
            
        except Exception as e:
            print(f"   Google Search error: {str(e)[:150]}")
            print("   💡 Tip: Check Apify quota or reduce max_results")
            return pd.DataFrame()


# ============================================
# UNIFIED SCRAPER ORCHESTRATOR - ENHANCED
# ============================================
class MultiPlatformScraper:
    def __init__(self, youtube_api_key=None, apify_token=None, include_google=True):
        """
        Initialize multi-platform scraper
        
        Args:
            youtube_api_key: Google Cloud YouTube API key
            apify_token: Apify API token (for Twitter, Instagram, Google)
            include_google: Whether to include Google Search (default True)
        """
        print("\n🔧 Initializing scrapers...")
        
        self.youtube = YouTubeScraper(youtube_api_key) if youtube_api_key else None
        self.twitter = TwitterScraper(apify_token)
        self.instagram = InstagramScraper(apify_token) if apify_token else None
        self.google = GoogleSearchScraper(apify_token) if (apify_token and include_google) else None
        
        # Count active platforms
        active_platforms = sum([
            self.youtube and self.youtube.youtube is not None,
            self.twitter.client is not None,
            self.instagram and self.instagram.client is not None,
            self.google and self.google.client is not None
        ])
        
        print(f"\n✅ {active_platforms} platform(s) ready for scraping")
        print()  # Blank line for readability
        
    def scrape_all_platforms(self, query, youtube_n=20, twitter_n=50, instagram_n=30, google_n=15):
        """Scrape all platforms and combine results"""
        all_data = []
        
        print(f"🔍 Searching for: '{query}'")
        
        # YouTube
        if self.youtube and self.youtube.youtube:
            print("📹 Scraping YouTube...")
            yt_data = self.youtube.search_videos(query, youtube_n)
            if not yt_data.empty:
                all_data.append(yt_data)
                print(f"   ✅ Found {len(yt_data)} videos")
            else:
                print(f"   ⚠️  No YouTube data collected")
        
        # Twitter
        if self.twitter.client:
            print("🐦 Scraping Twitter/X...")
            tw_data = self.twitter.search_tweets(query, twitter_n)
            if not tw_data.empty:
                all_data.append(tw_data)
                print(f"   ✅ Found {len(tw_data)} tweets")
            else:
                print(f"   ⚠️  No Twitter data collected")
        
        # Instagram
        if self.instagram and self.instagram.client:
            print("📸 Scraping Instagram...")
            hashtag = query.replace(' ', '')
            ig_data = self.instagram.search_posts(hashtag, instagram_n)
            if not ig_data.empty:
                all_data.append(ig_data)
                print(f"   ✅ Found {len(ig_data)} posts")
            else:
                print(f"   ⚠️  No Instagram data collected")
        
        # Google Search - NEW!
        if self.google and self.google.client:
            print("🔍 Scraping Google Search...")
            google_data = self.google.search_google(query, google_n)
            if not google_data.empty:
                all_data.append(google_data)
                print(f"   ✅ Found {len(google_data)} results")
            else:
                print(f"   ⚠️  No Google data collected")
        
        # Combine all data
        if not all_data:
            print("\n❌ ERROR: No data collected from any platform!")
            print("   Please check your API keys and try again.")
            return pd.DataFrame()
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        print(f"\n✅ Total results scraped: {len(combined_df)}")
        return combined_df
    
    def scrape_multiple_keywords(self, keywords):
        """Scrape multiple keywords and combine"""
        all_results = []
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n{'='*60}")
            print(f"Keyword {i}/{len(keywords)}: {keyword}")
            print(f"{'='*60}")
            
            result = self.scrape_all_platforms(keyword)
            
            if not result.empty:
                result['search_keyword'] = keyword
                all_results.append(result)
            else:
                print(f"⚠️  No data for keyword: {keyword}")
            
            # Rate limiting between searches (important for Apify)
            if i < len(keywords):
                print("\n⏳ Waiting 5 seconds before next search...")
                time.sleep(5)  # Increased from 3 to 5 for Google Search
        
        if not all_results:
            print("\n❌ FATAL: No data collected for any keyword!")
            print("Please check your API configuration.")
            return pd.DataFrame()
        
        return pd.concat(all_results, ignore_index=True)


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    print("="*60)
    print("🌀 ATOMBERG SOV AGENT - DATA COLLECTION (4 PLATFORMS)")
    print("="*60)
    
    # Load API keys from environment
    youtube_key = st.secrets('YOUTUBE_API_KEY')
    apify_token = st.secrets('APIFY_TOKEN')
    
    # Validate keys
    print("\n🔑 Checking API Keys...")
    if not youtube_key or youtube_key == "YOUR_YOUTUBE_API_KEY":
        print("❌ YouTube API key not found or invalid!")
        print("   Add it to .env file: YOUTUBE_API_KEY=your_actual_key")
    else:
        print(f"✅ YouTube API key loaded: {youtube_key[:15]}...")
    
    if not apify_token or apify_token == "YOUR_APIFY_TOKEN":
        print("⚠️  Apify token not found (Twitter, Instagram & Google will be skipped)")
        print("   Add it to .env file: APIFY_TOKEN=your_token")
    else:
        print(f"✅ Apify token loaded: {apify_token[:15]}...")
    
    # Ask user if they want to include Google
    print("\n" + "="*60)
    include_google = input("Include Google Search? (y/n) [default: y]: ").lower() != 'n'
    print("="*60)
    
    # Initialize scraper
    scraper = MultiPlatformScraper(
        youtube_api_key=youtube_key,
        apify_token=apify_token,
        include_google=include_google
    )
    
    # Define keywords to search
    keywords = [
        "smart fan",
        "BLDC fan",
        "energy efficient fan",
        "atomberg fan",
        "ceiling fan with remote"
    ]
    
    # For quick testing, uncomment below:
    # keywords = ["smart fan"]
    
    # Scrape all platforms for all keywords
    print(f"\n📋 Will search for {len(keywords)} keywords")
    print(f"⏱️  Estimated time: {len(keywords) * 2} minutes\n")
    
    data = scraper.scrape_multiple_keywords(keywords)
    
    if data.empty:
        print("\n" + "="*60)
        print("❌ NO DATA COLLECTED")
        print("="*60)
    else:
        # Save to CSV
        output_file = 'social_media_data.csv'
        data.to_csv(output_file, index=False)
        
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"\n💾 Data saved to: {output_file}")
        print(f"📊 Total rows: {len(data)}")
        print(f"📱 Platforms: {data['platform'].unique().tolist()}")
        print(f"🔑 Keywords: {data['search_keyword'].unique().tolist()}")
        
        # Show platform breakdown
        print("\n📊 Platform Breakdown:")
        print(data['platform'].value_counts().to_string())
        
        print("\n✅ Next step: Run analyzer.py")