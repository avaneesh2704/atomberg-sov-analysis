"""
Streamlit Interactive Dashboard for Atomberg SoV Analysis
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import ast

# Page config
st.set_page_config(
    page_title="Atomberg SoV Analysis",
    page_icon="🌀",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    """Load all analysis results"""
    try:
        analyzed_df = pd.read_csv('analyzed_social_data.csv')
        # Parse detected_brands if it's a string
        analyzed_df['detected_brands'] = analyzed_df['detected_brands'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
        
        sov_results = pd.read_csv('sov_results.csv')
        
        return analyzed_df, sov_results
    except FileNotFoundError:
        st.error("⚠️ Data files not found! Please run the scraper and analyzer first.")
        st.stop()

df, sov_df = load_data()

# ============================================
# SIDEBAR
# ============================================
st.sidebar.image("https://via.placeholder.com/200x80/FF6B6B/FFFFFF?text=Atomberg", use_container_width=True)
st.sidebar.title("🔍 Analysis Filters")

# Brand filter
selected_brands = st.sidebar.multiselect(
    "Select Brands to Compare",
    options=sov_df['brand'].tolist(),
    default=['Atomberg', 'Havells', 'Orient']
)

# Platform filter
platforms = df['platform'].unique().tolist()
selected_platforms = st.sidebar.multiselect(
    "Select Platforms",
    options=platforms,
    default=platforms
)

# Sentiment filter
sentiments = ['positive', 'neutral', 'negative']
selected_sentiments = st.sidebar.multiselect(
    "Select Sentiments",
    options=sentiments,
    default=sentiments
)

# Date range (if available)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Summary")
st.sidebar.metric("Total Posts Analyzed", len(df))
st.sidebar.metric("Brands Detected", len(sov_df))
st.sidebar.metric("Platforms Covered", len(platforms))

# ============================================
# MAIN DASHBOARD
# ============================================

# Header
st.markdown('<div class="main-header">🌀 Atomberg Share of Voice Analysis</div>', unsafe_allow_html=True)
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

atomberg_sov = sov_df[sov_df['brand'] == 'Atomberg']['sov_score'].values[0] if 'Atomberg' in sov_df['brand'].values else 0
atomberg_rank = sov_df[sov_df['brand'] == 'Atomberg'].index[0] + 1 if 'Atomberg' in sov_df['brand'].values else 0

with col1:
    st.metric(
        "Atomberg SoV Score",
        f"{atomberg_sov:.2f}%",
        delta=f"Rank #{atomberg_rank}"
    )

with col2:
    atomberg_mentions = len(df[df['detected_brands'].apply(lambda x: 'Atomberg' in x if isinstance(x, list) else False)])
    st.metric(
        "Total Mentions",
        atomberg_mentions
    )

with col3:
    atomberg_engagement = df[df['detected_brands'].apply(lambda x: 'Atomberg' in x if isinstance(x, list) else False)]['total_engagement'].sum()
    st.metric(
        "Total Engagement",
        f"{int(atomberg_engagement):,}"
    )

with col4:
    atomberg_sentiment = df[df['detected_brands'].apply(lambda x: 'Atomberg' in x if isinstance(x, list) else False)]['sentiment_score'].mean()
    st.metric(
        "Avg Sentiment",
        f"{atomberg_sentiment:.2f}",
        delta="Positive" if atomberg_sentiment > 0 else "Negative"
    )

st.markdown("---")

# ============================================
# VISUALIZATIONS
# ============================================

# Row 1: SoV Comparison
st.subheader("📊 Share of Voice Comparison")

col1, col2 = st.columns([2, 1])

with col1:
    # Bar chart
    filtered_sov = sov_df[sov_df['brand'].isin(selected_brands)]
    
    fig_sov = px.bar(
        filtered_sov,
        x='brand',
        y='sov_score',
        title="Overall SoV Score by Brand",
        color='brand',
        color_discrete_map={'Atomberg': '#FF6B6B'},
        text='sov_score'
    )
    fig_sov.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_sov.update_layout(showlegend=False, yaxis_title="SoV Score (%)")
    st.plotly_chart(fig_sov, use_container_width=True)

with col2:
    # Pie chart for market share
    fig_pie = px.pie(
        filtered_sov,
        values='sov_score',
        names='brand',
        title="Market Share Distribution",
        color='brand',
        color_discrete_map={'Atomberg': '#FF6B6B'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Row 2: Component Breakdown
st.subheader("🎯 SoV Component Breakdown")

filtered_sov_components = filtered_sov[['brand', 'mention_share', 'engagement_share', 'sentiment_share', 'reach_share']]

fig_components = go.Figure()

for brand in selected_brands:
    brand_data = filtered_sov_components[filtered_sov_components['brand'] == brand]
    if not brand_data.empty:
        fig_components.add_trace(go.Bar(
            name=brand,
            x=['Mention', 'Engagement', 'Sentiment', 'Reach'],
            y=[
                brand_data['mention_share'].values[0],
                brand_data['engagement_share'].values[0],
                brand_data['sentiment_share'].values[0],
                brand_data['reach_share'].values[0]
            ]
        ))

fig_components.update_layout(
    barmode='group',
    title="Component-wise Share Comparison",
    yaxis_title="Share (%)",
    xaxis_title="Component"
)
st.plotly_chart(fig_components, use_container_width=True)

st.markdown("---")

# Row 3: Platform Analysis
st.subheader("📱 Platform-wise Performance")

col1, col2 = st.columns(2)

with col1:
    # Mentions by platform
    platform_mentions = []
    for platform in selected_platforms:
        platform_df = df[df['platform'] == platform]
        for brand in selected_brands:
            mentions = sum(platform_df['detected_brands'].apply(lambda x: brand in x if isinstance(x, list) else False))
            platform_mentions.append({
                'Platform': platform,
                'Brand': brand,
                'Mentions': mentions
            })
    
    platform_df_chart = pd.DataFrame(platform_mentions)
    
    fig_platform = px.bar(
        platform_df_chart,
        x='Platform',
        y='Mentions',
        color='Brand',
        title="Mentions by Platform",
        barmode='group',
        color_discrete_map={'Atomberg': '#FF6B6B'}
    )
    st.plotly_chart(fig_platform, use_container_width=True)

with col2:
    # Engagement by platform
    platform_engagement = []
    for platform in selected_platforms:
        platform_df = df[df['platform'] == platform]
        for brand in selected_brands:
            brand_posts = platform_df[platform_df['detected_brands'].apply(lambda x: brand in x if isinstance(x, list) else False)]
            engagement = brand_posts['total_engagement'].sum()
            platform_engagement.append({
                'Platform': platform,
                'Brand': brand,
                'Engagement': engagement
            })
    
    engagement_df_chart = pd.DataFrame(platform_engagement)
    
    fig_engagement = px.bar(
        engagement_df_chart,
        x='Platform',
        y='Engagement',
        color='Brand',
        title="Engagement by Platform",
        barmode='group',
        color_discrete_map={'Atomberg': '#FF6B6B'}
    )
    st.plotly_chart(fig_engagement, use_container_width=True)

st.markdown("---")

# Row 4: Sentiment Analysis
st.subheader("😊 Sentiment Analysis")

col1, col2 = st.columns(2)

with col1:
    # Sentiment distribution for Atomberg
    atomberg_posts = df[df['detected_brands'].apply(lambda x: 'Atomberg' in x if isinstance(x, list) else False)]
    sentiment_counts = atomberg_posts['sentiment'].value_counts()
    
    fig_sentiment = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="Atomberg Sentiment Distribution",
        color=sentiment_counts.index,
        color_discrete_map={'positive': '#4CAF50', 'neutral': '#FFC107', 'negative': '#F44336'}
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

with col2:
    # Sentiment comparison across brands
    sentiment_comparison = []
    for brand in selected_brands:
        brand_posts = df[df['detected_brands'].apply(lambda x: brand in x if isinstance(x, list) else False)]
        avg_sentiment = brand_posts['sentiment_score'].mean()
        sentiment_comparison.append({
            'Brand': brand,
            'Avg Sentiment Score': avg_sentiment
        })
    
    sentiment_comp_df = pd.DataFrame(sentiment_comparison)
    
    fig_sent_comp = px.bar(
        sentiment_comp_df,
        x='Brand',
        y='Avg Sentiment Score',
        title="Average Sentiment Score Comparison",
        color='Brand',
        color_discrete_map={'Atomberg': '#FF6B6B'}
    )
    fig_sent_comp.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_sent_comp, use_container_width=True)

st.markdown("---")

# Row 5: Data Table
st.subheader("📋 Detailed Brand Comparison")
st.dataframe(
    filtered_sov.style.highlight_max(subset=['sov_score'], color='lightgreen'),
    use_container_width=True
)

# ============================================
# EXPORT OPTIONS
# ============================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Export Options")

if st.sidebar.button("📥 Download SoV Report (CSV)"):
    csv = filtered_sov.to_csv(index=False)
    st.sidebar.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"atomberg_sov_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Built with ❤️ for Atomberg | Powered by AI & Data Science</p>
    </div>
""", unsafe_allow_html=True)