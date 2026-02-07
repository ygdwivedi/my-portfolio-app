import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# --- PAGE SETUP ---
st.set_page_config(page_title="Portfolio Command Center", layout="wide")

st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎛️ Portfolio Command Center")

# --- 1. DATA LOADING & SETUP ---

# This function fetches live prices from Yahoo Finance
@st.cache_data(ttl=300) # Cache data for 5 minutes so it's fast
def get_live_prices(tickers):
    if not tickers:
        return {}
    try:
        # Download all tickers at once
        data = yf.download(tickers, period="1d")['Close'].iloc[-1]
        return data
    except Exception as e:
        st.error(f"Could not fetch prices: {e}")
        return {}

# Default Portfolio (This is your "Permanent" list)
default_data = [
    {"Ticker": "NVDA",  "Quantity": 50,   "Avg_Cost": 450.00},
    {"Ticker": "GOOGL", "Quantity": 100,  "Avg_Cost": 120.00},
    {"Ticker": "BTC-USD", "Quantity": 0.5, "Avg_Cost": 40000.00}, # Use Yahoo Tickers (BTC-USD)
    {"Ticker": "META",  "Quantity": 20,   "Avg_Cost": 300.00},
]

# --- 2. EDITABLE PORTFOLIO SECTION ---
with st.expander("📝 Manage Portfolio (Add/Edit Stocks)", expanded=False):
    st.caption("Edit below. To save permanently, copy the code generated at the bottom.")
    df_input = pd.DataFrame(default_data)
    edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True, key="editor")
    
    # "Save" Helper
    st.write("---")
    st.write("**Want to save these changes permanently?**")
    st.write("Copy this list below and paste it into your code in the `default_data` section:")
    st.code(edited_df.to_dict('records'))

# --- 3. FETCH LIVE PRICES ---
# Get list of unique tickers from the table
if not edited_df.empty:
    ticker_list = edited_df['Ticker'].unique().tolist()
    live_prices = get_live_prices(ticker_list)
else:
    live_prices = {}

# --- 4. SIMULATION LOOP ---
st.divider()
st.subheader("Live Simulation")

simulated_results = []

# Loop through every stock in your table
for index, row in edited_df.iterrows():
    ticker = row['Ticker']
    qty = row['Quantity']
    avg_cost = row['Avg_Cost']
    
    # Get Live Price (Fallback to Avg Cost if API fails or ticker is wrong)
    current_price = live_prices.get(ticker, avg_cost)
    if isinstance(current_price, pd.Series): # Handle edge case with single result
        current_price = current_price.item()
        
    current_val = current_price * qty
    current_profit = current_val - (avg_cost * qty)

    # --- THE ROW LAYOUT ---
    # We create a "Card" for each stock
    with st.container():
        c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
        
        # COL 1: Ticker Info
        with c1:
            st.subheader(ticker)
            st.caption(f"{qty} Shares")
        
        # COL 2: REALITY (The Current Live Stats)
        with c2:
            st.metric(
                label="Current Reality",
                value=f"${current_price:,.2f}",
                delta=f"${current_profit:,.0f} Profit"
            )

        # COL 3: THE SLIDER
        with c3:
            growth_pct = st.slider(
                f"Simulate {ticker}", 
                min_value=-100, 
                max_value=400, 
                value=0, 
                step=5,
                key=f"slide_{index}",
                label_visibility="collapsed" # Hides label for cleaner look
            )
            st.caption(f"Simulate Move: **{growth_pct}%**")

        # COL 4: SIMULATION (The "What If" Stats)
        with c4:
            # Math
            sim_price = current_price * (1 + (growth_pct / 100))
            sim_val = sim_price * qty
            sim_profit = sim_val - (avg_cost * qty)
            
            # Color logic for the delta
            delta_color = "normal"
            if sim_profit > current_profit: delta_color = "normal" # Green (standard)
            else: delta_color = "inverse" 

            st.metric(
                label=f"Price at {growth_pct}%",
                value=f"${sim_price:,.2f}",
                delta=f"${sim_profit:,.0f} Future Profit"
            )
            
        st.divider()
        
        # Save data for the total calculation
        simulated_results.append({
            "Ticker": ticker,
            "Market_Value": sim_val,
            "Profit": sim_profit
        })

# --- 5. TOTALS & PIE CHART ---
if simulated_results:
    df_sim = pd.DataFrame(simulated_results)
    total_val = df_sim['Market_Value'].sum()
    total_profit = df_sim['Profit'].sum()
    
    # Sticky header at the bottom or top for totals
    st.markdown("### 🎯 Projected Totals")
    t1, t2 = st.columns(2)
    t1.metric("Total Simulated Value", f"${total_val:,.0f}")
    t2.metric("Total Simulated Profit", f"${total_profit:,.0f}")
    
    st.write("Allocation based on simulation:")
    fig = px.pie(df_sim, values='Market_Value', names='Ticker', hole=0.4)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig, use_container_width=True)
