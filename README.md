#  Atomberg Share of Voice (SoV) Analysis Agent
AI-powered Social Listening & Competitor Intelligence System

Developer: Avaneesh Ingale

Technologies: Python, Streamlit, NLP, Transformers, APIFY, YouTube API

Overview

This project builds an AI-powered Share of Voice (SoV) intelligence system designed for the smart fan market, focusing on Atomberg and its competitors (Havells, Crompton, Orient, Polycab, Usha, etc.).

The system collects data from YouTube, Instagram, Twitter, and Google Search, analyzes:

Brand mentions

Customer sentiment

Engagement

Reach

Keyword performance

and calculates a weighted Share of Voice score using a custom SoV formula.

The final output includes:

✔ Interactive dashboard
✔ SoV ranking
✔ Sentiment analysis
✔ Platform-wise breakdown
✔ Competitor benchmarking
✔ Strategic recommendations

# Key Features
1. Multi-Platform Data Collection

Scrapes content from:

YouTube Data API

Instagram (Apify Hashtag Scraper)

Twitter/X (snscrape or Apify Actor)

Google Search (SerpAPI)

Supports multi-keyword analysis:

“smart fan”

“BLDC fan”

“energy efficient fan”

“ceiling fan with remote”

“Atomberg vs Havells”

2. Intelligent Analysis Engine

Includes:

Brand detection using regex + pattern matching

Sentiment analysis (TextBlob + Transformer model)

Platform-specific engagement scoring

Weighted SoV calculation

3. Custom Share of Voice (SoV) Formula
𝑆
𝑜
𝑉
=
0.35
𝑀
+
0.30
𝐸
+
0.25
𝑆
+
0.10
𝑅
SoV=0.35M+0.30E+0.25S+0.10R

Where:

M = Mention Share

E = Engagement Share

S = Sentiment Share

R = Reach Share

This formula balances visibility, interaction quality, perception, and audience size.

4. Visual & Interactive Dashboard

Built using Streamlit with:

SoV score & brand ranking

Mention, engagement, sentiment insights

Platform breakdown

Radar chart of SoV components

Competitor comparison charts

Data tables and downloadable reports

System Architecture
Keywords → Scrapers (YouTube, Instagram/APIFY, Twitter/snscrape, Google/SerpAPI)
         ↓
      Data Processing (Brand Detection, NLP, Engagement Scoring)
         ↓
      SoV Engine (Weighted Formula for MS, ES, SS, RS)
         ↓
     Streamlit Dashboard (Charts, Tables, Insights)

Repository Structure
├── scraper.py              # Collects data from all platforms
├── analyzer.py             # Sentiment + brand detection + engagement
├── sov_calculator.py       # SoV formula & component breakdown
├── dashboard.py            # Streamlit UI
├── requirements.txt        # Dependencies
├── README.md               # Project documentation
└── .streamlit/
     └── secrets.toml       # API keys (not pushed to GitHub)

API Keys Required

Create .streamlit/secrets.toml:

YOUTUBE_API_KEY = "your_key"
APIFY_TOKEN = "your_token"



These are automatically loaded inside Streamlit Cloud.

# Installation & Local Setup
1. Clone the repository
git clone https://github.com/yourusername/atomberg-sov.git
cd atomberg-sov

2. Install dependencies
pip install -r requirements.txt

3. Add API keys

Create .streamlit/secrets.toml and add required keys.

4. Run the pipeline
python scraper.py
python analyzer.py
python sov_calculator.py

5. Launch the dashboard
streamlit run dashboard.py
