import streamlit as st
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime

st.set_page_config(page_title="StoreSight - Bangalore D2C", layout="wide")

# --- DATA ---
BANGALORE_MARKETS = [
    {"area": "Indiranagar 100ft Road", "pincode": "560038", "lat": 12.9784, "lon": 77.6408, 
     "rent_psf": 180, "affluence": 0.95, "competition": 8, "digital_penetration": 0.92},
    {"area": "Koramangala 80ft Road", "pincode": "560034", "lat": 12.9352, "lon": 77.6245,
     "rent_psf": 130, "affluence": 0.92, "competition": 7, "digital_penetration": 0.90},
    {"area": "Jayanagar 4th Block", "pincode": "560011", "lat": 12.9308, "lon": 77.5832,
     "rent_psf": 100, "affluence": 0.88, "competition": 5, "digital_penetration": 0.85},
    {"area": "HSR Layout Sector 7", "pincode": "560102", "lat": 12.9116, "lon": 77.6389,
     "rent_psf": 95, "affluence": 0.85, "competition": 6, "digital_penetration": 0.88},
    {"area": "Whitefield ITPL", "pincode": "560066", "lat": 12.9698, "lon": 77.7499,
     "rent_psf": 70, "affluence": 0.78, "competition": 4, "digital_penetration": 0.82},
    {"area": "Electronic City Phase 1", "pincode": "560103", "lat": 12.8399, "lon": 77.6770,
     "rent_psf": 55, "affluence": 0.72, "competition": 3, "digital_penetration": 0.75},
    {"area": "Malleshwaram 8th Cross", "pincode": "560003", "lat": 13.0034, "lon": 77.5660,
     "rent_psf": 90, "affluence": 0.87, "competition": 5, "digital_penetration": 0.83},
    {"area": "JP Nagar 3rd Phase", "pincode": "560560", "lat": 12.9100, "lon": 77.6000,
     "rent_psf": 85, "affluence": 0.82, "competition": 4, "digital_penetration": 0.80},
]

@dataclass
class MarketResult:
    area: str
    pincode: str
    score: float
    format: str
    investment_lakhs: float
    monthly_revenue: float
    break_even_months: int
    cannibalization_risk: str

def calculate_expansion_score(market, category, aov):
    """Calculate expansion viability score 0-100"""
    # Category multipliers
    cat_mult = {
        'Fashion': {'affluence': 1.3, 'digital': 0.8},
        'Beauty': {'affluence': 1.2, 'digital': 1.0},
        'Home': {'affluence': 1.0, 'digital': 0.9},
        'Food': {'affluence': 0.9, 'digital': 1.1}
    }
    mult = cat_mult.get(category, {'affluence': 1.0, 'digital': 1.0})
    
    # Scoring components
    affluence_score = market['affluence'] * 30 * mult['affluence']
    digital_score = market['digital_penetration'] * 25 * mult['digital']
    competition_score = max(0, 20 - market['competition'] * 2.5)
    rent_efficiency = max(0, 15 - abs(market['rent_psf'] - 100) / 10)
    
    total = affluence_score + digital_score + competition_score + rent_efficiency + 10
    return min(100, total)

def get_format_recommendation(score, affluence, competition):
    """Recommend store format"""
    if score >= 80 and affluence >= 0.85:
        return "Flagship Store (1200 sqft)"
    elif score >= 65:
        return "Community Store (600 sqft)"
    elif competition >= 6:
        return "Pop-up/Experimental"
    else:
        return "Retail Partner (Low risk entry)"

def calculate_financials(market, format_type, aov):
    """Calculate investment and returns"""
    if "Flagship" in format_type:
        sqft = 1200
        monthly_orders = 450
    elif "Community" in format_type:
        sqft = 600
        monthly_orders = 280
    elif "Pop-up" in format_type:
        sqft = 400
        monthly_orders = 150
    else:  # Partnership
        return 20, monthly_orders * aov, 8  # ₹20L investment, 8mo break-even
    
    investment = (market['rent_psf'] * sqft) + (8000 * sqft)  # Rent deposit + fit-out
    monthly_revenue = monthly_orders * aov
    break_even = int(investment / (monthly_revenue * 0.22))  # 22% net margin
    
    return investment/100000, monthly_revenue, break_even

def get_cannibalization_risk(digital_pen, competition):
    if digital_pen > 0.88 and competition < 5:
        return "High (Strong online presence)"
    elif digital_pen > 0.80:
        return "Medium"
    return "Low (Expand online reach)"

def analyze_markets(category, aov):
    """Main analysis function"""
    results = []
    for market in BANGALORE_MARKETS:
        score = calculate_expansion_score(market, category, aov)
        fmt = get_format_recommendation(score, market['affluence'], market['competition'])
        inv, rev, be = calculate_financials(market, fmt, aov)
        risk = get_cannibalization_risk(market['digital_penetration'], market['competition'])
        
        results.append(MarketResult(
            area=market['area'],
            pincode=market['pincode'],
            score=round(score, 1),
            format=fmt,
            investment_lakhs=round(inv, 1),
            monthly_revenue=rev,
            break_even_months=be,
            cannibalization_risk=risk
        ))
    
    return sorted(results, key=lambda x: x.score, reverse=True)

# --- UI ---
st.title("🎯 StoreSight - Bangalore D2C Expansion Intelligence")
st.markdown("**Pincode-level analysis for offline retail expansion**")

# Sidebar inputs
with st.sidebar:
    st.header("Brand Profile")
    category = st.selectbox("Category", ["Fashion", "Beauty", "Home", "Food"])
    aov = st.number_input("Average Order Value (₹)", min_value=500, max_value=10000, value=1500, step=100)
    current_online = st.selectbox("Current Online Presence", ["Strong (Tier 1)", "Growing (Tier 2)", "New to Market"])
    
    st.markdown("---")
    st.caption("Powered by spatial analysis of 8 Bangalore micro-markets")
    
    analyze_btn = st.button("🚀 Generate Expansion Report", type="primary", use_container_width=True)

if analyze_btn:
    results = analyze_markets(category, aov)
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Markets Analyzed", "8")
    col2.metric("Avg Break-even", f"{int(np.mean([r.break_even_months for r in results[:3]]))} months")
    col3.metric("Total Investment", f"₹{sum([r.investment_lakhs for r in results[:3]]):.1f}L")
    col4.metric("Top Score", f"{results[0].score}/100")
    
    st.markdown("---")
    
    # Top 3 highlighted
    st.subheader("🏆 Top 3 Expansion Opportunities")
    cols = st.columns(3)
    emojis = ["🥇", "🥈", "🥉"]
    colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    
    for i, (col, result) in enumerate(zip(cols, results[:3])):
        with col:
            st.markdown(f"""
            <div style='background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border-left: 4px solid {colors[i]}'>
                <h3>{emojis[i]} {result.area}</h3>
                <p style='font-size: 24px; font-weight: bold; margin: 0;'>{result.score}/100</p>
                <p style='color: #888;'>{result.format}</p>
                <hr style='border-color: #333;'>
                <p>💰 Investment: <b>₹{result.investment_lakhs}L</b></p>
                <p>📅 Break-even: <b>{result.break_even_months} months</b></p>
                <p>⚠️ Risk: <b>{result.cannibalization_risk}</b></p>
            </div>
            """, unsafe_allow_html=True)
    
    # Full table
    st.markdown("---")
    st.subheader("📊 Complete Market Ranking")
    
    df = pd.DataFrame([
        {
            "Rank": i+1,
            "Area": r.area,
            "Pincode": r.pincode,
            "Score": r.score,
            "Recommended Format": r.format,
            "Investment (₹L)": r.investment_lakhs,
            "Monthly Revenue (₹)": f"{r.monthly_revenue:,.0f}",
            "Break-even": f"{r.break_even_months} mo",
            "Cannibalization": r.cannibalization_risk.split("(")[0]
        }
        for i, r in enumerate(results)
    ])
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Generate report text
    report = f"""
STORESIGHT - BANGALORE D2C EXPANSION REPORT
Generated: {datetime.now().strftime('%B %d, %Y')}
Brand Category: {category}
Average Order Value: ₹{aov}
Current Online Presence: {current_online}

EXECUTIVE SUMMARY
================
Bangalore Market Opportunity: HIGH
Recommended Entry: {results[0].format} in {results[0].area}
Investment Required: ₹{results[0].investment_lakhs} Lakhs
Expected Break-even: {results[0].break_even_months} months
Market Score: {results[0].score}/100

TOP 3 LOCATIONS
================
1. {results[0].area} (Pincode: {results[0].pincode})
   Score: {results[0].score}/100 | Format: {results[0].format}
   Investment: ₹{results[0].investment_lakhs}L | Monthly Revenue: ₹{results[0].monthly_revenue:,.0f}
   Break-even: {results[0].break_even_months} months
   Risk: {results[0].cannibalization_risk}

2. {results[1].area} (Pincode: {results[1].pincode})
   Score: {results[1].score}/100 | Format: {results[1].format}
   Investment: ₹{results[1].investment_lakhs}L | Break-even: {results[1].break_even_months} months

3. {results[2].area} (Pincode: {results[2].pincode})
   Score: {results[2].score}/100 | Format: {results[2].format}
   Investment: ₹{results[2].investment_lakhs}L | Break-even: {results[2].break_even_months} months

INVESTMENT SUMMARY
================
Total for Top 3 Locations: ₹{sum([r.investment_lakhs for r in results[:3]]):.1f} Lakhs
Projected Annual Revenue: ₹{sum([r.monthly_revenue * 12 for r in results[:3]])/100000:.1f} Lakhs
Average Break-even Timeline: {int(np.mean([r.break_even_months for r in results[:3]]))} months

RISK ASSESSMENT
================
Highest Risk: {results[0].cannibalization_risk}
Mitigation Strategy: Start with {results[-1].format} in {results[-1].area} to test market

Next Steps:
1. Visit {results[0].pincode} for site selection
2. Negotiate rent (Market rate: ₹{[m for m in BANGALORE_MARKETS if m['area']==results[0].area][0]['rent_psf']}/sqft)
3. Launch with {results[0].format} model
4. Expand to secondary locations after break-even

---
Report generated by StoreSight AI
For queries: contact@storesight.ai
    """
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📄 Download Full Report (TXT)",
            report,
            file_name=f"bangalore_expansion_{category.lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
            use_container_width=True
        )
    with col2:
        csv = df.to_csv(index=False)
        st.download_button(
            "📊 Download Data (CSV)",
            csv,
            file_name=f"bangalore_data_{category.lower()}.csv",
            use_container_width=True
        )
    
    # Action items
    st.markdown("---")
    st.subheader("✅ Immediate Action Items")
    st.markdown(f"""
    1. **Schedule site visit** to {results[0].area} (Pin: {results[0].pincode}) this week
    2. **Broker outreach**: Contact 3 commercial brokers in {results[0].area.split()[0]}
    3. **Competitive audit**: Visit existing stores in {results[0].area} to assess positioning
    4. **Test pop-up**: Consider {results[-1].format} in {results[-1].area} first (₹{results[-1].investment_lakhs}L investment)
    """)

else:
    # Landing state
    st.markdown("""
    ### How it works:
    1. Select your brand category and AOV
    2. We analyze 8 premium Bangalore micro-markets
    3. Get ranked recommendations with investment requirements
    4. Download report for your investors/board
    
    **Markets covered:** Indiranagar, Koramangala, Jayanagar, HSR Layout, Whitefield, Electronic City, Malleshwaram, JP Nagar
    """)

st.markdown("---")
st.caption("StoreSight v1.0 | Bangalore D2C Expansion Intelligence")
