"""
Share of Voice (SoV) Calculator for Atomberg
Custom weighted formula combining mentions, engagement, sentiment, and reach
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

# ============================================
# SOV CALCULATOR
# ============================================
class ShareOfVoiceCalculator:
    def __init__(self, 
                 mention_weight=0.35,
                 engagement_weight=0.30,
                 sentiment_weight=0.25,
                 reach_weight=0.10):
        """
        Initialize SoV calculator with custom weights
        
        Default weights:
        - Mention Share: 35% (brand visibility)
        - Engagement Share: 30% (interaction quality)
        - Sentiment Share: 25% (positive perception)
        - Reach Share: 10% (potential impressions)
        """
        self.weights = {
            'mention': mention_weight,
            'engagement': engagement_weight,
            'sentiment': sentiment_weight,
            'reach': reach_weight
        }
        
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def calculate_mention_share(self, df, target_brand='Atomberg'):
        """
        Calculate Mention Share: Brand mentions / Total brand mentions
        """
        # Get all posts that mention any brand
        branded_posts = df[df['brand_count'] > 0].copy()
        
        # Count mentions for each brand
        brand_mentions = {}
        for _, row in branded_posts.iterrows():
            for brand in row['detected_brands']:
                brand_mentions[brand] = brand_mentions.get(brand, 0) + 1
        
        total_mentions = sum(brand_mentions.values())
        
        if total_mentions == 0:
            return 0, brand_mentions
        
        target_mentions = brand_mentions.get(target_brand, 0)
        mention_share = (target_mentions / total_mentions) * 100
        
        return mention_share, brand_mentions
    
    def calculate_engagement_share(self, df, target_brand='Atomberg'):
        """
        Calculate Engagement Share: Weighted engagement for target brand / Total
        Weights: likes×1, comments×2, shares×3
        """
        # Filter for posts mentioning each brand
        brand_engagement = {}
        
        for _, row in df.iterrows():
            brands = row.get('detected_brands', [])
            if not brands:
                continue
            
            engagement = row.get('total_engagement', 0)
            
            # Split engagement equally among all brands mentioned
            engagement_per_brand = engagement / len(brands)
            
            for brand in brands:
                brand_engagement[brand] = brand_engagement.get(brand, 0) + engagement_per_brand
        
        total_engagement = sum(brand_engagement.values())
        
        if total_engagement == 0:
            return 0, brand_engagement
        
        target_engagement = brand_engagement.get(target_brand, 0)
        engagement_share = (target_engagement / total_engagement) * 100
        
        return engagement_share, brand_engagement
    
    def calculate_sentiment_share(self, df, target_brand='Atomberg'):
        """
        Calculate Sentiment-Weighted Share
        Positive mentions × 1.5, Neutral × 1.0, Negative × 0.5
        """
        sentiment_weights = {
            'positive': 1.5,
            'neutral': 1.0,
            'negative': 0.5
        }
        
        brand_weighted_mentions = {}
        
        for _, row in df.iterrows():
            brands = row.get('detected_brands', [])
            if not brands:
                continue
            
            sentiment = row.get('sentiment', 'neutral')
            weight = sentiment_weights.get(sentiment, 1.0)
            
            # Split weighted mention among brands
            weight_per_brand = weight / len(brands)
            
            for brand in brands:
                brand_weighted_mentions[brand] = brand_weighted_mentions.get(brand, 0) + weight_per_brand
        
        total_weighted = sum(brand_weighted_mentions.values())
        
        if total_weighted == 0:
            return 0, brand_weighted_mentions
        
        target_weighted = brand_weighted_mentions.get(target_brand, 0)
        sentiment_share = (target_weighted / total_weighted) * 100
        
        return sentiment_share, brand_weighted_mentions
    
    def calculate_reach_share(self, df, target_brand='Atomberg'):
        """
        Calculate Reach Share based on follower counts / views
        """
        brand_reach = {}
        
        for _, row in df.iterrows():
            brands = row.get('detected_brands', [])
            if not brands:
                continue
            
            # Get reach based on platform
            platform = row.get('platform')
            if platform == 'YouTube':
                reach = row.get('views', 0)
            elif platform == 'Twitter':
                reach = row.get('followers', 0)
            elif platform == 'Instagram':
                reach = row.get('likes', 0) * 10  # Estimate: likes × 10
            else:
                reach = 0
            
            reach_per_brand = reach / len(brands)
            
            for brand in brands:
                brand_reach[brand] = brand_reach.get(brand, 0) + reach_per_brand
        
        total_reach = sum(brand_reach.values())
        
        if total_reach == 0:
            return 0, brand_reach
        
        target_reach = brand_reach.get(target_brand, 0)
        reach_share = (target_reach / total_reach) * 100
        
        return reach_share, brand_reach
    
    def calculate_sov(self, df, target_brand='Atomberg'):
        """
        Calculate overall Share of Voice using weighted formula
        
        SoV = (0.35 × Mention_Share) + (0.30 × Engagement_Share) + 
              (0.25 × Sentiment_Share) + (0.10 × Reach_Share)
        """
        # Calculate each component
        mention_share, mention_data = self.calculate_mention_share(df, target_brand)
        engagement_share, engagement_data = self.calculate_engagement_share(df, target_brand)
        sentiment_share, sentiment_data = self.calculate_sentiment_share(df, target_brand)
        reach_share, reach_data = self.calculate_reach_share(df, target_brand)
        
        # Calculate weighted SoV
        sov_score = (
            self.weights['mention'] * mention_share +
            self.weights['engagement'] * engagement_share +
            self.weights['sentiment'] * sentiment_share +
            self.weights['reach'] * reach_share
        )
        
        results = {
            'brand': target_brand,
            'sov_score': round(sov_score, 2),
            'components': {
                'mention_share': round(mention_share, 2),
                'engagement_share': round(engagement_share, 2),
                'sentiment_share': round(sentiment_share, 2),
                'reach_share': round(reach_share, 2)
            },
            'raw_data': {
                'mentions': mention_data,
                'engagement': engagement_data,
                'sentiment': sentiment_data,
                'reach': reach_data
            }
        }
        
        return results
    
    def calculate_all_brands_sov(self, df):
        """Calculate SoV for all detected brands"""
        # Get all unique brands
        all_brands = set()
        for brands_list in df['detected_brands']:
            if isinstance(brands_list, list):
                all_brands.update(brands_list)
        
        results = []
        for brand in all_brands:
            sov = self.calculate_sov(df, brand)
            results.append({
                'brand': brand,
                'sov_score': sov['sov_score'],
                'mention_share': sov['components']['mention_share'],
                'engagement_share': sov['components']['engagement_share'],
                'sentiment_share': sov['components']['sentiment_share'],
                'reach_share': sov['components']['reach_share']
            })
        
        results_df = pd.DataFrame(results).sort_values('sov_score', ascending=False)
        return results_df
    
    def generate_sov_report(self, df, target_brand='Atomberg'):
        """Generate comprehensive SoV report"""
        print(f"\n{'='*60}")
        print(f"SHARE OF VOICE ANALYSIS FOR {target_brand.upper()}")
        print(f"{'='*60}\n")
        
        # Calculate SoV
        sov_results = self.calculate_sov(df, target_brand)
        
        print(f"📊 Overall SoV Score: {sov_results['sov_score']:.2f}%\n")
        
        print("Component Breakdown:")
        print(f"  • Mention Share:     {sov_results['components']['mention_share']:.2f}% (weight: {self.weights['mention']:.0%})")
        print(f"  • Engagement Share:  {sov_results['components']['engagement_share']:.2f}% (weight: {self.weights['engagement']:.0%})")
        print(f"  • Sentiment Share:   {sov_results['components']['sentiment_share']:.2f}% (weight: {self.weights['sentiment']:.0%})")
        print(f"  • Reach Share:       {sov_results['components']['reach_share']:.2f}% (weight: {self.weights['reach']:.0%})")
        
        # All brands comparison
        print("\n\n🏆 Competitive Landscape:")
        all_brands_sov = self.calculate_all_brands_sov(df)
        print(all_brands_sov.to_string(index=False))
        
        # Platform breakdown
        print("\n\n📱 Platform-wise Performance:")
        platform_analysis = self._analyze_by_platform(df, target_brand)
        print(platform_analysis.to_string(index=False))
        
        # Sentiment breakdown
        print("\n\n😊 Sentiment Analysis:")
        sentiment_analysis = self._analyze_sentiment_breakdown(df, target_brand)
        print(sentiment_analysis.to_string(index=False))
        
        return sov_results, all_brands_sov
    
    def _analyze_by_platform(self, df, target_brand):
        """Analyze brand performance by platform"""
        platform_stats = []
        
        for platform in df['platform'].unique():
            platform_df = df[df['platform'] == platform]
            
            # Count mentions
            mentions = sum(platform_df['detected_brands'].apply(lambda x: target_brand in x if isinstance(x, list) else False))
            
            # Total engagement
            engagement = platform_df[platform_df['detected_brands'].apply(lambda x: target_brand in x if isinstance(x, list) else False)]['total_engagement'].sum()
            
            platform_stats.append({
                'platform': platform,
                'mentions': mentions,
                'total_engagement': int(engagement)
            })
        
        return pd.DataFrame(platform_stats)
    
    def _analyze_sentiment_breakdown(self, df, target_brand):
        """Analyze sentiment for target brand"""
        brand_df = df[df['detected_brands'].apply(lambda x: target_brand in x if isinstance(x, list) else False)]
        
        sentiment_counts = brand_df['sentiment'].value_counts()
        
        return pd.DataFrame({
            'sentiment': sentiment_counts.index,
            'count': sentiment_counts.values,
            'percentage': (sentiment_counts.values / len(brand_df) * 100).round(2)
        })


# ============================================
# VISUALIZATION GENERATOR
# ============================================
class SoVVisualizer:
    @staticmethod
    def plot_sov_comparison(all_brands_df, save_path='sov_comparison.png'):
        """Create bar chart comparing SoV across brands"""
        plt.figure(figsize=(12, 6))
        
        brands = all_brands_df['brand'][:5]  # Top 5 brands
        scores = all_brands_df['sov_score'][:5]
        
        colors = ['#FF6B6B' if b == 'Atomberg' else '#4ECDC4' for b in brands]
        
        plt.bar(brands, scores, color=colors)
        plt.xlabel('Brand', fontsize=12)
        plt.ylabel('Share of Voice (%)', fontsize=12)
        plt.title('Share of Voice Comparison - Top 5 Brands', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Saved: {save_path}")
        plt.close()
    
    @staticmethod
    def plot_component_breakdown(sov_results, save_path='sov_components.png'):
        """Create radar/spider chart for SoV components"""
        components = sov_results['components']
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        categories = ['Mention\nShare', 'Engagement\nShare', 'Sentiment\nShare', 'Reach\nShare']
        values = [
            components['mention_share'],
            components['engagement_share'],
            components['sentiment_share'],
            components['reach_share']
        ]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#FF6B6B')
        ax.fill(angles, values, alpha=0.25, color='#FF6B6B')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title(f"Atomberg SoV Components", fontsize=14, fontweight='bold', pad=20)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Saved: {save_path}")
        plt.close()


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    import os
    import ast
    
    # Check if input file exists
    if not os.path.exists('analyzed_social_data.csv'):
        print("❌ Error: analyzed_social_data.csv not found!")
        print("   Please run analyzer.py first.")
        exit(1)
    
    print("\n" + "="*60)
    print("📊 ATOMBERG SOV AGENT - SOV CALCULATION")
    print("="*60)
    
    # Load analyzed data
    print("\n📂 Loading analyzed data...")
    df = pd.read_csv('analyzed_social_data.csv')
    
    # Parse detected_brands back to list (if saved as string)
    print("🔧 Processing brand data...")
    df['detected_brands'] = df['detected_brands'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    print(f"   Loaded {len(df)} analyzed posts")
    print(f"   Platforms: {df['platform'].unique().tolist()}")
    
    # Initialize SoV calculator
    calculator = ShareOfVoiceCalculator()
    
    # Generate comprehensive report
    print("\n" + "="*60)
    sov_results, all_brands = calculator.generate_sov_report(df, 'Atomberg')
    print("="*60)
    
    # Create visualizations
    print("\n📊 Generating visualizations...")
    visualizer = SoVVisualizer()
    visualizer.plot_sov_comparison(all_brands)
    visualizer.plot_component_breakdown(sov_results)
    
    # Save results
    print("\n💾 Saving final results...")
    all_brands.to_csv('sov_results.csv', index=False)
    print("   ✅ sov_results.csv")
    print("   ✅ sov_comparison.png")
    print("   ✅ sov_components.png")
    
    print("\n" + "="*60)
    print("🎉 SOV ANALYSIS COMPLETE!")
    print("="*60)
    print("\n🚀 Next step: Launch dashboard")
    print("   → streamlit run dashboard.py")
    print("\n📊 Or view the PNG visualizations directly!")