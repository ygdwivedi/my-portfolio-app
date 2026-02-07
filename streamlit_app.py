import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Yash's Command Center", layout="wide")

st.title("🎛️ Portfolio Command Center")
st.markdown("### Step 1: Your Holdings (Editable)")
st.info("Add new stocks below. Valid Tickers only.")

# --- 1. SETUP: THE EDITABLE TABLE ---
# Default starting data
default_data = [
    {"Ticker": "FUBO",  "Quantity": 1000, "Avg_Cost": 5.00},
    {"Ticker": "NVDA",  "Quantity": 50,   "Avg_Cost": 450.00},
    {"Ticker": "META",  "Quantity": 20,   "Avg_Cost": 300.00},
    {"Ticker": "GOOGL", "Quantity": 100,  "Avg_Cost": 120.00},
    {"Ticker": "RKLB",  "Quantity": 200,  "Avg_Cost": 4.50},
    {"Ticker": "SMR",   "Quantity": 100,  "Avg_Cost": 6.00},
    {"Ticker": "FIG",   "Quantity": 150,  "Avg_Cost": 10.00},
    {"Ticker": "BTC",   "Quantity": 0.5,  "Avg_Cost": 40000.00},
    {"Ticker": "ETH",   "Quantity": 5.0,  "Avg_Cost": 2500.00},
]

df_input = pd.DataFrame(default_data)

# The Editor - Add up to 100 rows
edited_df = st.data_editor(
    df_input, 
    num_rows="dynamic", 
    use_container_width=True,
    key="data_editor"
)

# --- 2. THE SIMULATION LOGIC ---
st.divider()
st.markdown("### Step 2: Live Simulator")

# We need columns to show the "List of Sliders" on the left, and "Pie Chart" on the right
col_controls, col_visuals = st.columns([1.5, 1])

simulated_portfolio = []

with col_controls:
    st.write("Adjust sliders to simulate individual stock performance.")
    
    # LOOP: Create a slider for EVERY stock in the table
    for index, row in edited_df.iterrows():
        ticker = row['Ticker']
        qty = row['Quantity']
        avg_cost = row['Avg_Cost']
        
        # We assume Current Price = Avg Cost for the baseline (since we aren't fetching live data yet)
        current_price = avg_cost 
        
        # Create a visual container for this stock
        with st.container():
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.subheader(f"**{ticker}**")
                st.caption(f"Qty: {qty} | Cost: ${avg_cost}")
            
            with c2:
                # The Slider specific to this stock
                growth_pct = st.slider(
                    f"Growth %", 
                    min_value=-100, 
                    max_value=400, 
                    value=0, 
                    step=5, 
                    key=f"slider_{index}"
                )
            
            # Calculate the "New" Reality for this stock
            sim_price = current_price * (1 + (growth_pct / 100))
            market_val = sim_price * qty
            profit = market_val - (avg_cost * qty)
            
            # Store this data to build the pie chart later
            simulated_portfolio.append({
                "Ticker": ticker,
                "Market_Value": market_val,
                "Profit": profit,
                "Simulated_Price": sim_price
            })
            
            # Show the live stats for this stock right below the slider
            st.write(
                f"💰 Value: **${market_val:,.0f}** | "
                f"Profit: <span style='color:{'green' if profit >= 0 else 'red'}'>${profit:,.0f}</span>", 
                unsafe_allow_html=True
            )
            st.divider()

# --- 3. THE VISUALS (Right Side) ---
# Convert list to dataframe for plotting
df_sim = pd.DataFrame(simulated_portfolio)

if not df_sim.empty:
    total_value = df_sim['Market_Value'].sum()
    total_profit = df_sim['Profit'].sum()
    
    with col_visuals:
        # Fixed container so the chart stays visible while you scroll the list
        with st.container():
            st.markdown("### 🎯 Portfolio Outcome")
            
            # Big Metrics
            m1, m2 = st.columns(2)
            m1.metric("Total Value", f"${total_value:,.0f}")
            m2.metric("Total Profit", f"${total_profit:,.0f}", delta=f"{(total_profit/(total_value-total_profit))*100:.1f}%" if total_value != total_profit else "0%")
            
            # Dynamic Pie Chart
            fig = px.pie(
                df_sim, 
                values='Market_Value', 
                names='Ticker', 
                title="Projected Allocation",
                hole=0.4
            )
            # Put the legend at the bottom to save width
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
            st.plotly_chart(fig, use_container_width=True)
            
            # Breakdown Table
            st.markdown("#### Breakdown")
            df_sim['% Portfolio'] = (df_sim['Market_Value'] / total_value) * 100
            st.dataframe(
                df_sim[['Ticker', '% Portfolio', 'Market_Value', 'Profit']],
                column_config={
                    "Market_Value": st.column_config.NumberColumn("Value", format="$%d"),
                    "Profit": st.column_config.NumberColumn("Profit", format="$%d"),
                    "% Portfolio": st.column_config.NumberColumn("%", format="%.1f%%"),
                },
                hide_index=True
            )
