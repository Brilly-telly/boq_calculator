import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Master Construction BoQ Calculator",
    page_icon="🏗️",
    layout="wide"
)

# Initialize Session State
if "items" not in st.session_state:
    st.session_state["items"] = []

# --- SIDEBAR: Project & Financial Settings ---
st.sidebar.header("📋 Project Details")
project_title = st.sidebar.text_input("Project Title", value="Residential Construction")
client_name = st.sidebar.text_input("Client Name", value="Client Name")
project_ref = st.sidebar.text_input("Reference #", value="BOQ-2026-001")
quote_date = st.sidebar.date_input("Date", value=datetime.date.today())

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Financial Settings")
vat_rate = st.sidebar.number_input("VAT Rate (%)", min_value=0.0, max_value=30.0, value=15.0, step=0.5)
contingency_rate = st.sidebar.number_input("Contingency Allowance (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)

# --- MAIN HEADER ---
st.title("🏗️ Master Construction BoQ Calculator")
st.caption(f"Project: **{project_title}** | Ref: **{project_ref}** | Client: **{client_name}** | Date: **{quote_date}**")

st.markdown("---")

# --- ITEM ENTRY FORM ---
st.subheader("➕ Add Item to Schedule")
with st.form("add_item_form", clear_on_submit=True):
    col_cat, col_desc, col_qty, col_unit, col_rate = st.columns([2, 3, 1.5, 1.5, 2])
    
    with col_cat:
        category = st.selectbox(
            "Category",
            ["Earthworks & Site Prep", "Concrete & Structure", "Masonry & Brickwork", 
             "Roofing & Waterproofing", "Plumbing & Drainage", "Electrical Works", 
             "Finishes & Carpentry", "Labor & Supervision", "General / Misc"]
        )
    with col_desc:
        desc = st.text_input("Item Description", placeholder="e.g., Concrete Foundation")
    with col_qty:
        qty = st.number_input("Quantity", min_value=0.01, value=1.0, step=1.0)
    with col_unit:
        unit = st.selectbox("Unit", ["m³", "m²", "m", "kg", "bags", "hrs", "days", "sum", "item"])
    with col_rate:
        rate = st.number_input("Unit Rate (R)", min_value=0.0, value=100.0, step=10.0)
        
    submitted = st.form_submit_button("➕ Add Item", width="stretch")
    if submitted:
        if desc.strip():
            total = qty * rate
            st.session_state["items"].append({
                "Category": category,
                "Description": desc,
                "Quantity": float(qty),
                "Unit": unit,
                "Unit Rate": float(rate),
                "Total Amount": float(total)
            })
            st.success(f"Added '{desc}' under {category}!")
            st.rerun()
        else:
            st.warning("Please enter an item description.")

st.markdown("---")

# --- BOQ SCHEDULE TABLE & CALCULATIONS ---
df = pd.DataFrame(st.session_state["items"])

# Safety check for items saved before category update
if not df.empty and "Category" not in df.columns:
    df["Category"] = "General / Misc"

if not df.empty:
    st.subheader("📊 Bill of Quantities Schedule")
    
    # Category Filter
    categories = ["All Categories"] + list(df["Category"].unique())
    selected_cat = st.selectbox("Filter Schedule by Category:", categories)
    
    display_df = df if selected_cat == "All Categories" else df[df["Category"] == selected_cat]
    
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Description": st.column_config.TextColumn("Description", width="large"),
            "Quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
            "Unit": st.column_config.TextColumn("Unit", width="small"),
            "Unit Rate": st.column_config.NumberColumn("Unit Rate", format="R %.2f"),
            "Total Amount": st.column_config.NumberColumn("Total Amount", format="R %.2f")
        }
    )
    
    # Financial Calculations
    subtotal = float(df["Total Amount"].sum())
    contingency = subtotal * (contingency_rate / 100.0)
    subtotal_with_contingency = subtotal + contingency
    vat_amount = subtotal_with_contingency * (vat_rate / 100.0)
    grand_total = subtotal_with_contingency + vat_amount
    
    st.markdown("### 💰 Financial Breakdown")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Base Subtotal", f"R {subtotal:,.2f}")
    f2.metric(f"Contingency ({contingency_rate:.1f}%)", f"R {contingency:,.2f}")
    f3.metric(f"VAT ({vat_rate:.1f}%)", f"R {vat_amount:,.2f}")
    f4.metric("Grand Total (Incl. VAT)", f"R {grand_total:,.2f}")
    
    st.markdown("---")
    
    # Export & Actions
    st.subheader("🛠️ Actions & Exports")
    act_col1, act_col2, act_col3 = st.columns([1, 1, 1])
    
    with act_col1:
        meta_header = f"# Project: {project_title}\n# Ref: {project_ref}\n# Client: {client_name}\n# Date: {quote_date}\n# Grand Total: R {grand_total:,.2f}\n\n"
        csv_data = meta_header + df.to_csv(index=False)
        
        st.download_button(
            label="📥 Export Full BoQ (CSV)",
            data=csv_data.encode("utf-8"),
            file_name=f"BoQ_{project_ref}_{quote_date}.csv",
            mime="text/csv",
            width="stretch"
        )
        
    with act_col2:
        summary_text = f"""
====================================================
           BILL OF QUANTITIES SUMMARY REPORT        
====================================================
Project   : {project_title}
Ref No.   : {project_ref}
Client    : {client_name}
Date      : {quote_date}
----------------------------------------------------
Total Line Items: {len(df)}

FINANCIAL SUMMARY:
----------------------------------------------------
Base Subtotal (Excl. Tax) : R {subtotal:,.2f}
Contingency ({contingency_rate}%)        : R {contingency:,.2f}
VAT ({vat_rate}%)                 : R {vat_amount:,.2f}
----------------------------------------------------
GRAND TOTAL COST          : R {grand_total:,.2f}
====================================================
"""
        st.download_button(
            label="📄 Download Text Summary",
            data=summary_text,
            file_name=f"Summary_{project_ref}.txt",
            mime="text/plain",
            width="stretch"
        )
        
    with act_col3:
        if st.button("🗑️ Clear Entire Schedule", width="stretch"):
            st.session_state["items"] = []
            st.rerun()

else:
    st.info("💡 No items in schedule yet. Fill out the form above to add your first material or labor item.")