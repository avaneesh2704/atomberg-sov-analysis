# Atomberg Share of Voice (SoV) Analysis Agent  

**Developer:** Avaneesh Ingale  
**Technologies:** Python · Streamlit · NLP · TextBlob · APIFY · YouTube API 

*Demo Video:* https://drive.google.com/file/d/1V6MO5hbYCWmfQd0y8a052WcePinDJvNL/view?usp=sharing
*Demo:* https://atombergsovagent.streamlit.app/
---

## 📌 Overview  

This project builds an **AI-powered Share of Voice (SoV) Intelligence System** designed for the **Smart Fan market**, analyzing Atomberg’s visibility relative to key competitors such as **Havells, Crompton, Orient, Polycab, and Usha**.

The system collects content from **YouTube, Instagram, Twitter/X, and Google Search**, runs sentiment & engagement analysis, and computes a **weighted Share of Voice score** using a custom formula.

The output includes:

- ✔ Interactive Streamlit Dashboard  
- ✔ Brand-wise SoV Ranking  
- ✔ Sentiment & Engagement Insights  
- ✔ Platform-wise Performance  
- ✔ Competitor Benchmarking  
- ✔ Strategic Recommendations  

---

## 🚀 Key Features

### **1️⃣ Multi-Platform Data Collection**
Scrapes data from:

- **YouTube Data API v3**
- **Instagram via Apify Hashtag Scraper**
- **Twitter/X via snscrape / Apify Actor**
- **Google Search via SerpAPI**

Supports multiple keywords:

- `"smart fan"`
- `"BLDC fan"`
- `"energy efficient fan"`
- `"ceiling fan with remote"`
- `"Atomberg vs Havells"`

---

### **2️⃣ Intelligent Analysis Engine**
Includes:

- Brand detection using **regex + pattern matching**
- Sentiment analysis using **TextBlob**
- Platform-specific **engagement scoring**
- Custom **Share of Voice (SoV) calculation**
- Data normalization & classification

---

### **3️⃣ Custom Share of Voice Formula (SoV Score™)**


SoV = 0.35M + 0.30E + 0.25S + 0.10R


Where:

| Component | Meaning | Weight |
|----------|---------|--------|
| **M** | Mention Share | 35% |
| **E** | Engagement Share | 30% |
| **S** | Sentiment Share | 25% |
| **R** | Reach Share | 10% |

This ensures a balanced view of **visibility**, **interaction quality**, **brand perception**, and **audience reach**.

---

## 📊 Interactive Dashboard

Built using **Streamlit**, the dashboard includes:

- SoV score & brand ranking  
- Mentions, engagement & sentiment insights  
- Platform breakdown (YouTube, Instagram, Twitter, Google)  
- Radar chart of SoV components  
- Brand comparison visuals  
- Downloadable data tables  

> The dashboard can be deployed on **Streamlit Cloud** and shared via a public URL.

---

## 🧱 System Architecture

       ┌─────────────────────────────────┐
       │         Data Collection          │
       │ YouTube | Instagram | Twitter | Google│
       └─────────────────────────────────┘
                       │
                       ▼
       ┌─────────────────────────────────┐
       │        Processing Layer          │
       │ Brand Detection | Sentiment | Engagement│
       └─────────────────────────────────┘
                       │
                       ▼
       ┌─────────────────────────────────┐
       │        SoV Calculation Engine    │
       │  Weighted Formula (MS, ES, SS, RS)│
       └─────────────────────────────────┘
                       │
                       ▼
       ┌─────────────────────────────────┐
       │        Streamlit Dashboard       │
       │ Charts | Tables | Insights | Export│
       └─────────────────────────────────┘
## ⚙️ Installation & Local Setup
1. Clone the repository
git clone https://github.com/yourusername/atomberg-sov.git
cd atomberg-sov

2. Install dependencies
pip install -r requirements.txt

3. Add API keys

Create .streamlit/secrets.toml and paste your keys.

4. Run the full pipeline
python scraper.py
python analyzer.py
python sov_calculator.py

5. Launch the dashboard
streamlit run dashboard.py
