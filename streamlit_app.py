import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Yash's Portfolio HQ", layout="wide")

# --- 1. YOUR PORTFOLIO DATA ---
# Since we don't have live API keys set up yet, we will use this 'manual' list.
# You can edit these numbers right here in the code later.
data = [
    {"Ticker": "FUBO",  "Quantity": 1000, "Avg_Cost": 5.00,  "Type": "Stock"},
    {"Ticker": "NVDA",  "Quantity": 50,   "Avg_Cost": 450.00, "Type": "Stock"},
    {"Ticker": "META",  "Quantity": 20,   "Avg_Cost": 300.00, "Type": "Stock"},
    {"Ticker": "GOOGL", "Quantity": 100,  "Avg_Cost": 120.00, "Type": "Stock"},
    {"Ticker": "RKLB",  "Quantity": 200,  "Avg_Cost": 4.50,  "Type": "Stock"},
    {"Ticker": "SMR",   "Quantity": 100,  "Avg_Cost": 6.00,  "Type": "Stock"},
    {"Ticker": "FIG",   "Quantity": 150,  "Avg_Cost": 10.00, "Type": "Stock"},
    {"Ticker": "BTC",   "Quantity": 0.5,  "Avg_Cost": 40000.00, "Type": "Crypto"},
    {"Ticker": "ETH",   "Quantity": 5.0,  "Avg_Cost": 2500.00,  "Type": "Crypto"},
]

# Create the base dataframe
df_base = pd.DataFrame(data)
# For this demo, we assume Current Price starts equal to Avg Cost (Break Even)
# In a real app, we would fetch live prices here.
df_base['Current_Price'] = df_base['Avg_Cost'] 

# --- DASHBOARD TITLE ---
st.title("🚀 Portfolio Simulator & Vision")
st.markdown("Interactive dashboard to simulate growth scenarios.")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Scenario Controls")

# TABS for different simulation modes
mode = st.sidebar.radio("Simulation Mode:", ["Global Market Move", "Single Stock Moonshot"])

simulation_df = df_base.copy()

if mode == "Global Market Move":
    st.sidebar.write("Simulate the **entire** portfolio moving up or down.")
    
    # 1. The Slider (Rough Control)
    slide_val = st.sidebar.slider("Global Growth %", min_value=-90, max_value=400, value=0, step=10)
    
    # 2. The Exact Input (Fine Control)
    # If user types here, it overrides the slider visually in their head
    exact_val = st.sidebar.number_input("Or type exact % (e.g. 153.5)", value=float(slide_val))
    
    # Apply logic
    simulation_df['Simulated_Price'] = simulation_df['Current_Price'] * (1 + (exact_val / 100))

elif mode == "Single Stock Moonshot":
    st.sidebar.write("Pick **ONE** asset to explode while others stay flat.")
    
    # Select the stock
    target_stock = st.sidebar.selectbox("Select Asset", simulation_df['Ticker'])
    
    # Slider for that specific stock
    moon_val = st.sidebar.slider(f"{target_stock} Growth %", min_value=-90, max_value=1000, value=0, step=10)
    
    # Apply logic: Only change the target stock, keep others at 0% change
    simulation_df['Simulated_Price'] = simulation_df.apply(
        lambda x: x['Current_Price'] * (1 + (moon_val / 100)) if x['Ticker'] == target_stock else x['Current_Price'], 
        axis=1
    )

# --- CALCULATE METRICS ---
simulation_df['Market_Value'] = simulation_df['Simulated_Price'] * simulation_df['Quantity']
simulation_df['Profit'] = simulation_df['Market_Value'] - (simulation_df['Avg_Cost'] * simulation_df['Quantity'])

total_val = simulation_df['Market_Value'].sum()
total_cost = (simulation_df['Avg_Cost'] * simulation_df['Quantity']).sum()
total_profit = total_val - total_cost
roi = (total_profit / total_cost) * 100 if total_cost > 0 else 0

# --- DISPLAY METRICS ---
c1, c2, c3 = st.columns(3)
c1.metric("Projected Portfolio Value", f"${total_val:,.0f}")
c2.metric("Projected Profit", f"${total_profit:,.0f}", delta=f"{roi:.2f}%")
c3.metric("Initial Cost", f"${total_cost:,.0f}")

st.divider()

# --- VISUALIZATIONS ---
col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    st.subheader("Asset Allocation")
    # This Pie Chart will ANIMATE/MOVE when you use 'Single Stock Moonshot'
    fig_pie = px.pie(simulation_df, values='Market_Value', names='Ticker', title="Portfolio Weight", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.subheader("Gains by Asset")
    fig_bar = px.bar(simulation_df, x='Ticker', y='Profit', color='Profit', title="Profit in $")
    st.plotly_chart(fig_bar, use_container_width=True)
