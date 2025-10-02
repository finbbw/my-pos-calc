import streamlit as st
import pandas as pd
import math

# --- Configuration and Constants ---
st.set_page_config(
    page_title="Advanced Position Size Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Risk levels from the original script
RISK_LEVELS_PCT = [0.0025, 0.0050, 0.0075, 0.0100, 0.0200]

# --- Helper Functions (Replicating original formatting) ---

def fmt_currency(x, symbol="$", decimals=2):
    """Replicates the original currency formatting."""
    return f"{symbol}{x:,.{decimals}f}"

def build_rows(portfolio_value, price, stop, currency_symbol, risk_cap_pct, position_value_cap, position_cap_pct):
    """
    Translates the core position sizing and capping logic from the original script.
    """
    per_share_risk = abs(price - stop)
    stop_dist_pct = (per_share_risk / price * 100.0)
    max_shares_by_cash = math.floor(portfolio_value / price)

    risk_cap_budget = portfolio_value * risk_cap_pct
    shares_by_pos_cap = math.floor(position_value_cap / price)

    rows = []
    any_zero = False

    for pct in RISK_LEVELS_PCT:
        risk_budget = portfolio_value * pct
        eff_heat_budget = min(risk_budget, risk_cap_budget)

        shares_risk_intended = math.floor(risk_budget / per_share_risk)
        shares_heat_cap = math.floor(eff_heat_budget / per_share_risk)
        shares_cash_cap = max_shares_by_cash
        shares_pos_cap_curr = shares_by_pos_cap

        # Final shares is the minimum of the three cap constraints
        final_shares = min(shares_heat_cap, shares_cash_cap, shares_pos_cap_curr)

        position_value = final_shares * price
        heat = final_shares * per_share_risk
        heat_pct = (heat / portfolio_value * 100) if portfolio_value > 0 else 0.0

        # $Risk_SL: Calculated based on per-share risk and final shares (using abs value of risk)
        risk_sl = per_share_risk * final_shares 

        # $invested: Final Shares * Entry price (equals position_value)
        invested = position_value
        
        # Determine limiting caps
        limiting_caps = []
        # Check for Heat cap limitation
        if final_shares == shares_heat_cap and shares_heat_cap > 0:
            limiting_caps.append("Heat")
        # Check for Cash cap limitation
        if final_shares == shares_cash_cap and shares_cash_cap > 0:
            limiting_caps.append("Cash")
        # Check for Position cap limitation
        if final_shares == shares_pos_cap_curr and shares_pos_cap_curr > 0:
            limiting_caps.append("Pos")
            
        limiting_cap = ",".join(limiting_caps) if limiting_caps else "-"
        
        # Simplified logic for applied caps (to avoid redundant 'Yes' when multiple caps are equal)
        heat_cap_applied = shares_heat_cap < shares_risk_intended
        pos_cap_applied = shares_pos_cap_curr < shares_heat_cap 
        cash_cap_applied = shares_cash_cap < shares_heat_cap

        if final_shares == 0:
            any_zero = True

        rows.append({
            # Display/Sort Keys
            "Sort_Risk_Pct": pct * 100, # for sorting Table 1
            "Risk %": f"{pct*100:.2f}%",
            "Stop %": stop_dist_pct,
            "Final Shares": int(final_shares),
            "Limiting Cap": limiting_cap,

            # Calculated Values
            "Risk Budget": risk_budget,
            "Eff Heat<=Cap": eff_heat_budget,
            "Per-Share Risk": per_share_risk,
            "Shares(Intended)": shares_risk_intended,
            "Shares(HeatCap)": shares_heat_cap,
            "Shares(CashCap)": shares_cash_cap,
            "Shares(PosCap)": shares_pos_cap_curr,
            "$Risk_SL": risk_sl,
            "$invested": invested,
            "Position Value": position_value,
            "Portfolio Heat": heat,
            "Heat %": heat_pct,
            "HeatCap?": 'Yes' if heat_cap_applied else 'No',
            "PosCap?": 'Yes' if pos_cap_applied else 'No',
            "CashCap?": 'Yes' if cash_cap_applied else 'No',
            
            # Consts for final column formatting
            "Position Cap Data": {
                "val_cap": position_value_cap,
                "shares_cap": shares_by_pos_cap,
                "pct_cap": position_cap_pct * 100,
                "currency": currency_symbol
            }
        })

    return pd.DataFrame(rows), any_zero

# --- Streamlit UI ---

st.title("💸 Advanced Position Sizing & Capping Calculator")
st.markdown("Replicates the full console logic including Risk Heat Cap, Cash Cap, and Position Value Cap.")

# Sidebar for Inputs
with st.sidebar:
    st.header("Trade and Portfolio Inputs")

    # Entry price, Stop loss
    price = st.number_input("1. Entry Price", min_value=0.01, value=100.00, step=0.10, format="%.4f")
    stop = st.number_input("2. Stop Loss Price", min_value=0.01, value=98.00, step=0.10, format="%.4f")
    
    # Portfolio value
    portfolio_value = st.number_input(
        "3. Portfolio Value",
        min_value=100.0,
        value=50000.00,
        step=1000.0,
        help="Your total account trading capital."
    )

    # Currency symbol
    currency_symbol = st.text_input("4. Currency Symbol", value="$", max_chars=4)
    
    # Risk cap (Heat)
    risk_cap_pct = st.slider(
        "5. Max Risk per Trade (Heat Cap %)",
        min_value=0.0,
        max_value=5.0,
        value=1.0,
        step=0.05,
        format="%.2f%%",
        help="Maximum percentage of Portfolio Value allowed to be risked on any single trade."
    ) / 100.0 # Convert to decimal

    # Position cap
    position_cap_pct = st.slider(
        "6. Max Position Value Cap (% of Portfolio)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.5,
        format="%.2f%%",
        help="Maximum percentage of Portfolio Value allowed to be invested in any single position."
    ) / 100.0 # Convert to decimal


# --- Validation and Calculation ---

# Initial checks
if price <= 0 or stop <= 0 or portfolio_value <= 0:
    st.error("Please ensure Entry Price, Stop Loss, and Portfolio Value are greater than zero.")
    st.stop()

per_share_risk = abs(price - stop)
if per_share_risk <= 0:
    st.error("Stop Loss must differ from Entry Price to define risk per share.")
    st.stop()

# Derive constants
position_value_cap = portfolio_value * position_cap_pct
risk_cap_budget = portfolio_value * risk_cap_pct
max_shares_by_cash = math.floor(portfolio_value / price)
stop_dist_pct = (per_share_risk / price * 100.0)

# Run core calculation logic
df_results, any_zero = build_rows(
    portfolio_value, price, stop, currency_symbol, risk_cap_pct, position_value_cap, position_cap_pct
)

# --- Output Section ---

st.header("Input Summary")
col_p, col_c, col_r = st.columns(3)

with col_p:
    st.markdown(f"- **Entry price:** {fmt_currency(price, currency_symbol, 4)}")
    st.markdown(f"- **Stop loss:** {fmt_currency(stop, currency_symbol, 4)}")
    st.markdown(f"- **Stop distance:** {fmt_currency(per_share_risk, currency_symbol, 4)} ({stop_dist_pct:.2f}%) of entry price")

with col_c:
    st.markdown(f"- **Portfolio value:** {fmt_currency(portfolio_value, currency_symbol)}")
    st.markdown(f"- **Max shares by cash:** {max_shares_by_cash:,.0f}")

with col_r:
    shares_by_pos_cap = math.floor(position_value_cap / price)
    st.markdown(f"- **Risk cap (heat):** {risk_cap_pct*100:.2f}% ({fmt_currency(risk_cap_budget, currency_symbol)} max heat)")
    st.markdown(f"- **Position value cap:** {fmt_currency(position_value_cap, currency_symbol)} (shares cap: {shares_by_pos_cap:,.0f}) [{position_cap_pct*100:.2f}%]")

st.markdown("---")


# 1. Table 1: Summary (ascending by Risk %)
st.header("Table 1: Summary (ascending by Risk %)")

# Define columns specifically for Table 1 and their display order
table1_cols = [
    "Risk %", 
    "Risk Budget", 
    "Stop %", 
    "Final Shares", 
    "$Risk_SL", 
    "$invested", 
    "Position value cap (shares cap)"
]

# Create the specific column for the final display string (replicating the original output)
df_results['Position value cap (shares cap)'] = df_results['Position Cap Data'].apply(
    lambda d: f"{fmt_currency(d['val_cap'], d['currency'])} ({d['shares_cap']}) [{d['pct_cap']:.2f}%]"
)

# Sort and select columns for Table 1
df_table1 = df_results.sort_values(by="Sort_Risk_Pct", ascending=True)[table1_cols]

# Apply styling for Table 1
st.dataframe(
    df_table1.style.format({
        "Risk Budget": lambda x: fmt_currency(x, currency_symbol, 2),
        "$Risk_SL": lambda x: fmt_currency(x, currency_symbol, 2),
        "$invested": lambda x: fmt_currency(x, currency_symbol, 2),
        "Stop %": "{:.2f}%",
        "Final Shares": "{:,.0f}",
    }),
    width='stretch', # Replaced use_container_width=True
    hide_index=True
)

st.markdown(f"\nInputed Entry price: **{fmt_currency(price, currency_symbol, 4)}**")
st.markdown(f"Inputed Stop loss: **{fmt_currency(stop, currency_symbol, 4)}**")

# 2. Table 2: Details (descending by Heat %)
st.header("\nTable 2: Details (descending by Heat %)")

# Define columns specifically for Table 2
table2_cols = [
    "Risk %", 
    "Eff Heat<=Cap", 
    "Per-Share Risk",
    "Shares(Intended)", 
    "Shares(HeatCap)", 
    "Shares(CashCap)", 
    "Shares(PosCap)", 
    "Position Value", 
    "Portfolio Heat", 
    "Heat %", 
    "Limiting Cap", 
    "HeatCap?", 
    "PosCap?", 
    "CashCap?"
]

# Sort and select columns for Table 2 (Original script sorted by Heat % descending)
df_table2 = df_results.sort_values(by="Heat %", ascending=False)[table2_cols]

# Apply styling for Table 2
st.dataframe(
    df_table2.style.format({
        "Eff Heat<=Cap": lambda x: fmt_currency(x, currency_symbol, 2),
        "Per-Share Risk": lambda x: fmt_currency(x, currency_symbol, 4),
        "Position Value": lambda x: fmt_currency(x, currency_symbol, 2),
        "Portfolio Heat": lambda x: fmt_currency(x, currency_symbol, 2),
        "Heat %": "{:.2f}%",
        "Shares(Intended)": "{:,.0f}",
        "Shares(HeatCap)": "{:,.0f}",
        "Shares(CashCap)": "{:,.0f}",
        "Shares(PosCap)": "{:,.0f}",
        "Risk %": "{}" # Already formatted string
    }),
    width='stretch', # Replaced use_container_width=True
    hide_index=True
)


if any_zero:
    st.warning("""
    **Warning:** With the current caps and stop distance, some rows result in **0 final shares**.
    Consider reducing the stop distance, lowering entry price, increasing portfolio value, or raising the position value cap.
    """)
