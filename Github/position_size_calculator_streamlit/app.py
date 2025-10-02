import streamlit as st
import numpy as np

# --- Application Configuration ---
# Set the page title and layout
st.set_page_config(
    page_title="Position Size Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Functions for Calculation ---

def calculate_position_size(account_balance, risk_percent, entry_price, stop_loss_price):
    """
    Calculates the maximum number of shares/units to purchase based on risk.

    Args:
        account_balance (float): Total account capital.
        risk_percent (float): Percentage of the account balance willing to risk.
        entry_price (float): The price at which the position is entered.
        stop_loss_price (float): The price at which the position will be closed for a loss.

    Returns:
        tuple: (risk_amount, stop_loss_per_share, position_size)
    """
    if account_balance <= 0 or risk_percent <= 0 or entry_price <= 0:
        return 0, 0, 0, "Please ensure Account Balance, Risk %, and Entry Price are positive."

    # 1. Calculate the total monetary amount to risk
    risk_amount = account_balance * (risk_percent / 100)

    # 2. Calculate the monetary loss per share/unit (Stop Loss Distance)
    # Use np.abs to handle both long (Entry > Stop) and short (Entry < Stop) positions
    stop_loss_per_share = np.abs(entry_price - stop_loss_price)

    if stop_loss_per_share <= 0:
        return 0, 0, 0, "Stop Loss Price cannot be equal to Entry Price. Please adjust."

    # 3. Calculate the position size (Shares/Units)
    position_size = risk_amount / stop_loss_per_share

    # 4. Calculate the total capital required for the position
    capital_needed = position_size * entry_price

    return risk_amount, stop_loss_per_share, position_size, capital_needed


# --- Streamlit UI Layout ---

st.title("💰 Universal Position Size Calculator")
st.markdown("Easily determine the maximum safe position size for any trade based on your risk tolerance.")

# Sidebar for Inputs
with st.sidebar:
    st.header("Trade Inputs")

    # Account and Risk Inputs
    account_balance = st.number_input(
        "Account Balance ($)",
        min_value=1000.0,
        value=10000.0,
        step=100.0,
        help="Your total trading capital."
    )

    risk_percent = st.slider(
        "Risk % of Account (per trade)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Percentage of your total account you are willing to lose on this one trade."
    )

    st.subheader("Price Parameters")

    # Price Inputs
    entry_price = st.number_input(
        "Entry Price ($)",
        min_value=0.01,
        value=100.00,
        step=0.10,
        help="The price where you enter the trade (buy or short sell)."
    )

    stop_loss_price = st.number_input(
        "Stop Loss Price ($)",
        min_value=0.01,
        value=99.00,
        step=0.10,
        help="The price where you will exit the trade if it goes against you."
    )

# Main Calculation and Results Display
st.header("Calculation Results")

# Run calculation
risk_amount, stop_loss_per_share, position_size, capital_needed = calculate_position_size(
    account_balance,
    risk_percent,
    entry_price,
    stop_loss_price
)

# Display results in columns for clarity
col1, col2 = st.columns(2)

with col1:
    st.subheader("Risk Metrics")
    st.metric(
        label="Total Capital at Risk (USD)",
        value=f"${risk_amount:,.2f}",
        help="This is your maximum loss based on your risk percentage."
    )
    st.metric(
        label="Stop Loss Distance (USD/share)",
        value=f"${stop_loss_per_share:,.2f}",
        help="The price difference between entry and stop loss."
    )

with col2:
    st.subheader("Position Metrics")

    # Display position size as an integer (for shares) or float (for units)
    if position_size > 0:
        st.metric(
            label="Maximum Position Size (Shares/Units)",
            value=f"{position_size:,.0f} units (suggested)",
            delta=f"or {position_size:,.2f} units (exact)",
            delta_color="off",
            help="The maximum number of shares/units you can buy while respecting your risk limit."
        )
        st.metric(
            label="Total Capital for Position (USD)",
            value=f"${capital_needed:,.2f}",
            help="The capital required to purchase the maximum position size at the entry price."
        )
    elif isinstance(capital_needed, str):
        st.error(capital_needed) # Display error message if calculation failed
    else:
        st.warning("Please adjust your inputs to calculate the position size.")


# --- Instructions and Notes ---
st.markdown("---")
with st.expander("💡 How the calculation works"):
    st.markdown(r"""
    This calculator uses the core formula for risk management:

    $$
    \text{Position Size (Shares)} = \frac{\text{Account Balance} \times \text{Risk \%}}{\text{Entry Price} - \text{Stop Loss Price}}
    $$

    1.  **Risk Amount:** Calculated as `Account Balance * (Risk % / 100)`.
    2.  **Stop Loss Distance:** Calculated as `|Entry Price - Stop Loss Price|`.
    3.  **Position Size:** Calculated as `Risk Amount / Stop Loss Distance`.

    *Note: The calculator automatically handles both long positions (Entry > Stop) and short positions (Entry < Stop) by using the absolute difference for the Stop Loss Distance.*
    """)
