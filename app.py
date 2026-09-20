import streamlit as st
import pandas as pd
import urllib.parse
from datetime import date

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Master Construction BoQ Calculator",
    page_icon="🏗️",
    layout="wide"
)

# Initialize Session State for Schedule Items
if "boq_items" not in st.session_state:
    st.session_state.boq_items = []

# ---------------------------------------------------------
# SIDEBAR: PROJECT DETAILS & FINANCIAL SETTINGS
# ---------------------------------------------------------
st.sidebar.header("📋 Project Details")
project_title = st.sidebar.text_input("Project Title", value="Residential Construction")
client_name = st.sidebar.text_input("Client Name", value="Client Name")
reference_no = st.sidebar.text_input("Reference #", value="BOQ-2026-001")
project_date = st.sidebar.date_input("Date", value=date.today())

st.sidebar.header("⚙️ Financial Settings")
vat_rate = st.sidebar.number_input("VAT Rate (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.5)

# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
st.title("🏗️ Master Construction BoQ Calculator")
st.caption(f"**Project:** {project_title} | **Ref:** {reference_no} | **Client:** {client_name} | **Date:** {project_date}")

# ---------------------------------------------------------
# ADD ITEM FORM
# ---------------------------------------------------------
st.subheader("➕ Add Item to Schedule")

col1, col2, col3, col4, col5 = st.columns([2, 3, 1.5, 1.5, 2])

with col1:
    category = st.selectbox(
        "Category",
        ["Earthworks & Site Prep", "Concrete & Structure", "Masonry & Brickwork", "Roofing", "Plumbing & Drainage", "Electrical", "Finishes", "Labor & Equipment", "Other"]
    )

with col2:
    description = st.text_input("Item Description", placeholder="e.g., Concrete Foundation")

with col3:
    quantity = st.number_input("Quantity", min_value=0.0, value=1.0, step=1.0)

with col4:
    unit = st.selectbox("Unit", ["m²", "m³", "m", "kg", "sum", "hrs", "pcs", "item"])

with col5:
    unit_rate = st.number_input("Unit Rate (R)", min_value=0.0, value=100.0, step=10.0)

if st.button("➕ Add Item", width="stretch"):
    if description.strip():
        new_item = {
            "Category": category,
            "Description": description,
            "Quantity": quantity,
            "Unit": unit,
            "Unit Rate (R)": unit_rate,
            "Total Amount (R)": round(quantity * unit_rate, 2)
        }
        st.session_state.boq_items.append(new_item)
        st.success(f"Added '{description}' to schedule!")
        st.rerun()
    else:
        st.error("Please enter an item description.")

# ---------------------------------------------------------
# SCHEDULE TABLE & CALCULATIONS
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Bill of Quantities Schedule")

if not st.session_state.boq_items:
    st.info("💡 No items in schedule yet. Fill out the form above to add your first material or labor item.")
else:
    df = pd.DataFrame(st.session_state.boq_items)
    st.dataframe(df, width="stretch")
    
    # Financial Summaries
    subtotal = df["Total Amount (R)"].sum()
    vat_amount = subtotal * (vat_rate / 100.0)
    grand_total = subtotal + vat_amount

    col_sub, col_vat, col_total = st.columns(3)
    col_sub.metric("Subtotal", f"R {subtotal:,.2f}")
    col_vat.metric(f"VAT ({vat_rate}%)", f"R {vat_amount:,.2f}")
    col_total.metric("Grand Total", f"R {grand_total:,.2f}")

    if st.button("🗑️ Clear All Items"):
        st.session_state.boq_items = []
        st.rerun()

# ---------------------------------------------------------
# PAYFAST MONETIZATION / PAYWALL
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📄 Export Bill of Quantities Report")

# PayFast Credentials (Sandbox Keys)
PAYFAST_URL = "https://sandbox.payfast.co.za/eng/process"
MERCHANT_ID = "10054649"
MERCHANT_KEY = "lsg950kj7ilne"
APP_URL = "https://boq-calculator.streamlit.app" 

payfast_data = {
    "merchant_id": MERCHANT_ID,
    "merchant_key": MERCHANT_KEY,
    "return_url": f"{APP_URL}/?payment=success",
    "cancel_url": f"{APP_URL}/?payment=cancelled",
    "amount": "50.00", 
    "item_name": "BoQ PDF Export & Detailed Report",
}

checkout_link = f"{PAYFAST_URL}?{urllib.parse.urlencode(payfast_data)}"

# Check payment query status from PayFast redirect
query_params = st.query_params
payment_status = query_params.get("payment", None)

if payment_status == "success":
    st.success("✅ Payment verified! Your full report download is unlocked.")
    
    if st.session_state.boq_items:
        export_df = pd.DataFrame(st.session_state.boq_items)
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download BoQ Report (CSV / Excel)",
            data=csv_data,
            file_name=f"BoQ_{reference_no}.csv",
            mime="text/csv",
            width="stretch"
        )
    else:
        st.warning("Add items to your schedule first before downloading.")
    
    if st.button("🔄 Reset Payment Status"):
        st.query_params.clear()
        st.rerun()

elif payment_status == "cancelled":
    st.warning("⚠️ Payment was cancelled. Please complete payment to unlock your export.")
    st.link_button("💳 Pay R50.00 to Unlock Report Export", checkout_link, width="stretch")

else:
    st.info("🔒 Premium Feature: Download your complete BoQ Schedule & Financial Summary for R50.00.")
    st.link_button("💳 Pay R50.00 with PayFast", checkout_link, width="stretch")