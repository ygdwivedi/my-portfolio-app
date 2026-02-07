import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Portfolio Command Center", layout="wide")
st.title("🎛️ Portfolio Command Center")

# --- 1. SETUP & DATA HANDLING ---

# Robust function to get prices one by one (Slower but 100% reliable)
@st.cache_data(ttl=300)
def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Get the last 5 days history to be safe
        history = stock.history(period="5d")
        if not history.empty:
            return history['Close'].iloc[-1]
        return None
    except:
        return None

# Initialize Session State for the dataframe if it doesn't exist
if 'portfolio_df' not in st.session_state:
    # Default Starting Data
    default_data = [
        {"Ticker": "NVDA",  "Quantity": 50,   "Avg_Cost": 450.00},
        {"Ticker": "GOOGL", "Quantity": 100,  "Avg_Cost": 120.00},
        {"Ticker": "BTC-USD", "Quantity": 1.5, "Avg_Cost": 60000.00},
    ]
    st.session_state.portfolio_df = pd.DataFrame(default_data)

# --- 2. SIDEBAR: SAVE & LOAD ---
with st.sidebar:
    st.header("💾 Save/Load")
    
    # DOWNLOAD BUTTON
    csv = st.session_state.portfolio_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Portfolio (CSV)",
        data=csv,
        file_name='my_portfolio.csv',
        mime='text/csv',
    )
    
    # UPLOAD BUTTON
    uploaded_file = st.file_uploader("Upload Portfolio (CSV)", type="csv")
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            # Basic validation
            if {'Ticker', 'Quantity', 'Avg_Cost'}.issubset(uploaded_df.columns):
                st.session_state.portfolio_df = uploaded_df
                st.success("Loaded successfully!")
            else:
                st.error("CSV must have columns: Ticker, Quantity, Avg_Cost")
        except Exception as e:
            st.error(f"Error loading file: {e}")

# --- 3. MAIN EDITOR ---
with st.expander("📝 Edit Portfolio (Add/Remove Stocks)", expanded=False):
    # The Editor updates the Session State directly
    st.session_state.portfolio_df = st.data_editor(
        st.session_state.portfolio_df, 
        num_rows="dynamic", 
        use_container_width=True,
        key="main_editor"
    )

df = st.session_state.portfolio_df

# --- 4. THE SIMULATOR ---
st.divider()

if df.empty:
    st.warning("Your portfolio is empty! Add stocks in the expander above.")
else:
    # Prepare list for the final pie chart
    simulated_results = []
    
    # MAIN LOOP: Row by Row
    for index, row in df.iterrows():
        ticker = str(row['Ticker']).upper().strip() # Clean up ticker name
        qty = float(row['Quantity'])
        avg_cost = float(row['Avg_Cost'])
        
        # 1. Get Price
        current_price = get_current_price(ticker)
        
        # Handle invalid tickers
        if current_price is None:
            current_price = 0.0
            price_display = "Error"
        else:
            price_display = f"${current_price:,.2f}"

        # 2. Layout
        with st.container():
            # Create a 4-column layout
            c1, c2, c3, c4 = st.columns([1, 1.5, 2, 1.5])
            
            # --- COL 1: NAME ---
            with c1:
                st.subheader(ticker)
                st.caption(f"{qty} Shares")

            # --- COL 2: REALITY ---
            with c2:
                cur_val = current_price * qty
                cur_profit = cur_val - (avg_cost * qty)
                st.metric(
                    "Current Reality", 
                    price_display, 
                    delta=f"{cur_profit:,.0f}"
                )

            # --- COL 3: SLIDER ---
            with c3:
                # Custom slider layout
                st.write("") # Spacer
                growth = st.slider(
                    f"Simulator ({ticker})", -100, 400, 0, step=10, 
                    key=f"slide_{index}", 
                    label_visibility="collapsed"
                )
                st.caption(f"Simulate Move: **{growth}%**")

            # --- COL 4: FUTURE ---
            with c4:
                sim_price = current_price * (1 + (growth/100))
                sim_val = sim_price * qty
                sim_profit = sim_val - (avg_cost * qty)
                
                # Check if we are profiting MORE than reality
                profit_diff = sim_profit - cur_profit
                
                st.metric(
                    f"Price at {growth}%", 
                    f"${sim_price:,.2f}", 
                    delta=f"{sim_profit:,.0f}"
                )
            
            st.divider()
            
            # Add to results for Pie Chart
            simulated_results.append({
                "Ticker": ticker,
                "Market Value": sim_val,
                "Profit": sim_profit
            })

    # --- 5. TOTALS & PIE CHART ---
    st.header("🎯 Final Projection")
    
    results_df = pd.DataFrame(simulated_results)
    
    if not results_df.empty:
        total_val = results_df['Market Value'].sum()
        total_profit = results_df['Profit'].sum()
        
        # Big Numbers
        m1, m2 = st.columns(2)
        m1.metric("Total Simulated Value", f"${total_val:,.0f}")
        m2.metric("Total Simulated Profit", f"${total_profit:,.0f}", delta_color="normal")
        
        # Pie Chart
        fig = px.pie(
            results_df, 
            values='Market Value', 
            names='Ticker', 
            title="Projected Allocation",
            hole=0.5
        )
        st.plotly_chart(fig, use_container_width=True)
