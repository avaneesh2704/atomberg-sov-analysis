

import pandas as pd
import re
from collections import Counter
from textblob import TextBlob
from transformers import pipeline
import numpy as np


class BrandDetector:
    def __init__(self):
        # Define brand  and keywords
        self.brands = {
            'Atomberg': ['atomberg', 'atom berg', 'gorilla fan'],
            'Havells': ['havells', 'havell'],
            'Orient': ['orient electric', 'orient'],
            'Crompton': ['crompton', 'crompton greaves'],
            'Usha': ['usha'],
            'Bajaj': ['bajaj'],
            'Superfan': ['superfan', 'super fan'],
            'Luminous': ['luminous'],
            'Anchor': ['anchor'],
            'Polycab': ['polycab']
        }
        
        # Compile regex patterns for efficient matching
        self.brand_patterns = {}
        for brand, variations in self.brands.items():
            pattern = '|'.join([re.escape(v) for v in variations])
            self.brand_patterns[brand] = re.compile(pattern, re.IGNORECASE)
    
    def detect_brands(self, text):
        """Detect all brands mentioned in text"""
        if not isinstance(text, str):
            return []
        
        detected = []
        for brand, pattern in self.brand_patterns.items():
            if pattern.search(text):
                detected.append(brand)
        
        return detected
    
    def is_atomberg_mention(self, text):
        """Check if Atomberg is specifically mentioned"""
        return 'Atomberg' in self.detect_brands(text)
    
    def get_primary_brand(self, text):
        """Get the most prominent brand in text"""
        brands = self.detect_brands(text)
        if not brands:
            return 'Generic'
        return brands[0]  # Return first detected brand



class SentimentAnalyzer:
    def __init__(self, use_transformer=False):
        self.use_transformer = use_transformer
        
        if use_transformer:
            # Use Hugging Face sentiment model (more accurate but slower)
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
    
    def analyze_sentiment_simple(self, text):
        """Fast sentiment analysis using TextBlob"""
        if not isinstance(text, str) or not text.strip():
            return {'polarity': 0, 'sentiment': 'neutral', 'score': 0}
        
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'polarity': round(polarity, 3),
            'sentiment': sentiment,
            'score': round(polarity, 3)
        }
    
    def analyze_sentiment_advanced(self, text):
        """Advanced sentiment using transformers"""
        if not isinstance(text, str) or not text.strip():
            return {'sentiment': 'neutral', 'score': 0}
        
        try:
            result = self.sentiment_pipeline(text[:512])[0]  # Truncate to 512 chars
            label = result['label'].lower()
            score = result['score']
            
            # Convert to polarity scale (-1 to 1)
            if label == 'positive':
                polarity = score
            else:
                polarity = -score
            
            return {
                'sentiment': label,
                'score': round(polarity, 3),
                'confidence': round(score, 3)
            }
        except Exception as e:
            print(f"Transformer sentiment error: {e}")
            return self.analyze_sentiment_simple(text)
    
    def analyze(self, text):
        """Main sentiment analysis method"""
        if self.use_transformer:
            return self.analyze_sentiment_advanced(text)
        else:
            return self.analyze_sentiment_simple(text)



class ContentAnalyzer:
    def __init__(self, use_advanced_sentiment=False):
        self.brand_detector = BrandDetector()
        self.sentiment_analyzer = SentimentAnalyzer(use_transformer=use_advanced_sentiment)
    
    def analyze_content(self, df):
        """Analyze entire dataframe of social media content"""
        print(" Analyzing content...")
        
        # Determine text column based on platform
        def get_text(row):
            if row.get('platform') == 'YouTube':
                return f"{row.get('title', '')} {row.get('description', '')}"
            elif row.get('platform') == 'Instagram':
                return row.get('caption', '')
            elif row.get('platform') == 'Twitter':
                return row.get('text', '')
            return ''
        
        # Extract text content
        df['full_text'] = df.apply(get_text, axis=1)
        
        # Detect brands
        print("    Detecting brands...")
        df['detected_brands'] = df['full_text'].apply(self.brand_detector.detect_brands)
        df['brand_count'] = df['detected_brands'].apply(len)
        df['primary_brand'] = df['full_text'].apply(self.brand_detector.get_primary_brand)
        df['mentions_atomberg'] = df['detected_brands'].apply(lambda x: 'Atomberg' in x)
        
        # Analyze sentiment
        print("   Analyzing sentiment...")
        sentiments = df['full_text'].apply(self.sentiment_analyzer.analyze)
        df['sentiment'] = sentiments.apply(lambda x: x['sentiment'])
        df['sentiment_score'] = sentiments.apply(lambda x: x['score'])
        
        # Calculate engagement metrics
        print("   Calculating engagement...")
        df['total_engagement'] = self._calculate_engagement(df)
        
        print(f" Analysis complete! Processed {len(df)} items")
        return df
    
    def _calculate_engagement(self, df):
        """Calculate unified engagement score across platforms"""
        engagement = pd.Series(0, index=df.index)
        
        for idx, row in df.iterrows():
            platform = row.get('platform')
            
            if platform == 'YouTube':
                # Views are less valuable than active engagement
                engagement[idx] = (
                    row.get('likes', 0) * 1 +
                    row.get('comments', 0) * 2 +
                    row.get('views', 0) * 0.001  # Views weighted very low
                )
            
            elif platform == 'Instagram':
                engagement[idx] = (
                    row.get('likes', 0) * 1 +
                    row.get('comments', 0) * 2
                )
            
            elif platform == 'Twitter':
                engagement[idx] = (
                    row.get('likes', 0) * 1 +
                    row.get('retweets', 0) * 3 +
                    row.get('replies', 0) * 2
                )
        
        return engagement
    
    def get_brand_summary(self, df):
        """Generate summary statistics for each brand"""
        # Filter only rows with detected brands
        branded = df[df['brand_count'] > 0].copy()
        
        # Explode brands so each brand gets its own row
        branded_exploded = branded.explode('detected_brands')
        
        summary = branded_exploded.groupby('detected_brands').agg({
            'full_text': 'count',
            'total_engagement': 'sum',
            'sentiment_score': 'mean'
        }).rename(columns={
            'full_text': 'mention_count',
            'total_engagement': 'total_engagement',
            'sentiment_score': 'avg_sentiment'
        })
        
        # Add sentiment breakdown
        sentiment_breakdown = branded_exploded.groupby(['detected_brands', 'sentiment']).size().unstack(fill_value=0)
        summary = summary.join(sentiment_breakdown)
        
        summary = summary.sort_values('mention_count', ascending=False)
        
        return summary



if __name__ == "__main__":
    import os
    
    # Check if input file exists
    if not os.path.exists('social_media_data.csv'):
        print(" Error: social_media_data.csv not found!")
        print("   Please run scraper.py first to collect data.")
        exit(1)
    
    print("\n" + "="*60)
    print("ATOMBERG SOV AGENT - CONTENT ANALYSIS")
    print("="*60 + "\n")
    
    # Load scraped data
    print(" Loading data...")
    df = pd.read_csv('social_media_data.csv')
    print(f"   Loaded {len(df)} posts from {df['platform'].nunique()} platforms")
    
    # Initialize analyzer
    print("\n Initializing analyzer...")
    analyzer = ContentAnalyzer(use_advanced_sentiment=False)  # Set True for better accuracy
    print("   Using TextBlob for fast sentiment analysis")
    
    # Analyze content
    analyzed_df = analyzer.analyze_content(df)
    
    # Get brand summary
    print("\n" + "="*60)
    brand_summary = analyzer.get_brand_summary(analyzed_df)
    print("\n Brand Summary:")
    print(brand_summary)
    print("="*60)
    
    # Save analyzed data
    print("\n Saving results...")
    analyzed_df.to_csv('analyzed_social_data.csv', index=False)
    brand_summary.to_csv('brand_summary.csv')
    
