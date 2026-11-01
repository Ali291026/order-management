import io
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Product-Wise Formulation & Production Costing Dashboard",
    page_icon="🏭",
    layout="wide",
)

# Custom CSS Styling
st.markdown(
    """
<style>
.main-header {
    font-size: 2.2rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 0.2rem;
}
.sub-header {
    font-size: 1.1rem;
    color: #475569;
    margin-bottom: 1.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)


# Initialize Session State for Products, BOMs, and Raw Materials
@st.cache_data
def load_initial_data():
    # Raw Materials & Global Rates/Stock
    raw_materials = [
        {
            "Item": "Calcium Stearate",
            "Stock_System": 396.0,
            "Stock_Physical": 396.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 335.0,
            "Nov_2025_Rate": 310.0,
            "June_2026_Rate": 335.0,
            "Source": "Local",
        },
        {
            "Item": "Calcium Carbonate",
            "Stock_System": 22619.0,
            "Stock_Physical": 22619.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 12.0,
            "Nov_2025_Rate": 11.5,
            "June_2026_Rate": 12.0,
            "Source": "Local",
        },
        {
            "Item": "OB-1",
            "Stock_System": 98.14,
            "Stock_Physical": 98.14,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 750.0,
            "Nov_2025_Rate": 720.0,
            "June_2026_Rate": 750.0,
            "Source": "Local",
        },
        {
            "Item": "SGT-01/PA",
            "Stock_System": 1908.0,
            "Stock_Physical": 3700.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 285.0,
            "Nov_2025_Rate": 265.0,
            "June_2026_Rate": 285.0,
            "Source": "Import",
        },
        {
            "Item": "Stabilizer",
            "Stock_System": 4050.7,
            "Stock_Physical": 4050.7,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 225.0,
            "Nov_2025_Rate": 210.0,
            "June_2026_Rate": 225.0,
            "Source": "Local",
        },
        {
            "Item": "Stearic Acid",
            "Stock_System": 795.0,
            "Stock_Physical": 795.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 235.0,
            "Nov_2025_Rate": 220.0,
            "June_2026_Rate": 235.0,
            "Source": "Local",
        },
        {
            "Item": "SGT - 13G / SGL24B",
            "Stock_System": 6173.0,
            "Stock_Physical": 5950.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 180.0,
            "Nov_2025_Rate": 165.0,
            "June_2026_Rate": 180.0,
            "Source": "Import",
        },
        {
            "Item": "PE Wax",
            "Stock_System": 35.0,
            "Stock_Physical": 450.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 272.0,
            "Nov_2025_Rate": 255.0,
            "June_2026_Rate": 272.0,
            "Source": "Import",
        },
        {
            "Item": "Resin",
            "Stock_System": 9175.0,
            "Stock_Physical": 9175.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 130.0,
            "Nov_2025_Rate": 125.0,
            "June_2026_Rate": 130.0,
            "Source": "Local",
        },
        {
            "Item": "Epoxy",
            "Stock_System": 231.0,
            "Stock_Physical": 231.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 350.0,
            "Nov_2025_Rate": 330.0,
            "June_2026_Rate": 350.0,
            "Source": "Local",
        },
        {
            "Item": "DOP",
            "Stock_System": 854.0,
            "Stock_Physical": 854.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 200.0,
            "Nov_2025_Rate": 190.0,
            "June_2026_Rate": 200.0,
            "Source": "Local",
        },
        {
            "Item": "Titanium Dioxide",
            "Stock_System": 1438.0,
            "Stock_Physical": 875.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 350.0,
            "Nov_2025_Rate": 335.0,
            "June_2026_Rate": 350.0,
            "Source": "Local",
        },
        {
            "Item": "PVC SGT",
            "Stock_System": 47307.0,
            "Stock_Physical": 45000.0,
            "In_Transit": 50000.0,
            "Unit_Rate_KES": 93.0,
            "Nov_2025_Rate": 88.0,
            "June_2026_Rate": 93.0,
            "Source": "Import",
        },
        {
            "Item": "PVC Nbi",
            "Stock_System": 29976.0,
            "Stock_Physical": 29976.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 60.0,
            "Nov_2025_Rate": 58.0,
            "June_2026_Rate": 60.0,
            "Source": "Local",
        },
    ]

    # Finished Products & Planned Production Units (e.g., batches or pieces for 1M, 2M, 3M)
    # Proportions representing your initial baseline dataset split across products
    products = [
        {"Product": "Standard PVC Pipe (Class 1)", "Target_1M_Units": 1000, "Target_2M_Units": 2000, "Target_3M_Units": 3000},
        {"Product": "Heavy Duty Conduit (Class 2)", "Target_1M_Units": 500, "Target_2M_Units": 1000, "Target_3M_Units": 1500},
    ]

    # Bill of Materials (BOM): kg required per 1 unit of Product
    # Derived proportionally from your original aggregate numbers
    bom_data = [
        # Product A: Standard PVC Pipe
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "Calcium Stearate", "Kg_Per_Unit": 0.20},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "Calcium Carbonate", "Kg_Per_Unit": 25.00},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "OB-1", "Kg_Per_Unit": 0.002},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "SGT-01/PA", "Kg_Per_Unit": 0.80},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "Stabilizer", "Kg_Per_Unit": 1.45},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "Stearic Acid", "Kg_Per_Unit": 0.12},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "SGT - 13G / SGL24B", "Kg_Per_Unit": 1.75},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "PE Wax", "Kg_Per_Unit": 0.10},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "Resin", "Kg_Per_Unit": 2.00},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "Epoxy", "Kg_Per_Unit": 0.46},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "DOP", "Kg_Per_Unit": 0.14},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "Titanium Dioxide", "Kg_Per_Unit": 1.39},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "PVC SGT", "Kg_Per_Unit": 21.40},
        {"Product": "Standard PVC Pipe (Class 1)", "Item": "PVC Nbi", "Kg_Per_Unit": 27.45},

        # Product B: Heavy Duty Conduit
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "Calcium Stearate", "Kg_Per_Unit": 0.22},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "Calcium Carbonate", "Kg_Per_Unit": 26.90},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "OB-1", "Kg_Per_Unit": 0.0022},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "SGT-01/PA", "Kg_Per_Unit": 0.88},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "Stabilizer", "Kg_Per_Unit": 1.54},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "Stearic Acid", "Kg_Per_Unit": 0.13},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "SGT - 13G / SGL24B", "Kg_Per_Unit": 1.90},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "PE Wax", "Kg_Per_Unit": 0.11},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "Resin", "Kg_Per_Unit": 2.15},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "Epoxy", "Kg_Per_Unit": 0.50},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "DOP", "Kg_Per_Unit": 0.15},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "Titanium Dioxide", "Kg_Per_Unit": 1.50},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "PVC SGT", "Kg_Per_Unit": 23.19},
        {"Product": "Heavy Duty Conduit (Class 2)", "Item": "PVC Nbi", "Kg_Per_Unit": 29.74},
    ]

    return pd.DataFrame(raw_materials), pd.DataFrame(products), pd.DataFrame(bom_data)


if "raw_materials_df" not in st.session_state:
    rm, prod, bom = load_initial_data()
    st.session_state["raw_materials_df"] = rm
    st.session_state["products_df"] = prod
    st.session_state["bom_df"] = bom

rm_df = st.session_state["raw_materials_df"]
prod_df = st.session_state["products_df"]
bom_df = st.session_state["bom_df"]

# App Header
st.markdown(
    '<p class="main-header">🏭 Product-Wise Formulation & Production Costing Dashboard</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Define finished product targets, manage product Bill of Materials (BOM), analyze raw material requirements, and track procurement orders.</p>',
    unsafe_allow_html=True,
)

# Sidebar Simulation Controls
st.sidebar.header("🎛️ Global Simulation Controls")
production_scale = st.sidebar.slider(
    "Production Volume Scale (%)",
    min_value=50,
    max_value=200,
    value=100,
    step=5,
)
scale_multiplier = production_scale / 100.0

# Calculate total required raw materials based on Product Targets and BOMs
# Scaled Targets per Product
prod_df["Scaled_1M_Units"] = prod_df["Target_1M_Units"] * scale_multiplier
prod_df["Scaled_2M_Units"] = prod_df["Target_2M_Units"] * scale_multiplier
prod_df["Scaled_3M_Units"] = prod_df["Target_3M_Units"] * scale_multiplier

# Merge BOM with Scaled Production Targets to calculate total raw material demand
merged_demand = pd.merge(bom_df, prod_df, on="Product", how="inner")
merged_demand["Req_1M_kg"] = merged_demand["Kg_Per_Unit"] * merged_demand["Scaled_1M_Units"]
merged_demand["Req_2M_kg"] = merged_demand["Kg_Per_Unit"] * merged_demand["Scaled_2M_Units"]
merged_demand["Req_3M_kg"] = merged_demand["Kg_Per_Unit"] * merged_demand["Scaled_3M_Units"]

# Aggregate raw material demand across all products
agg_demand = merged_demand.groupby("Item")[["Req_1M_kg", "Req_2M_kg", "Req_3M_kg"]].sum().reset_index()

# Merge back with raw materials master table
df = pd.merge(rm_df, agg_demand, on="Item", how="left").fillna(0)

# Compute financial and procurement metrics
df["One_Month_kg"] = df["Req_1M_kg"]
df["Two_Months_kg"] = df["Req_2M_kg"]
df["Three_Months_kg"] = df["Req_3M_kg"]

# Use Physical Count if available, otherwise System Stock
df["Effective_Stock"] = df.apply(
    lambda r: r["Stock_System"] if r["Stock_Physical"] == 0.0 and r["Stock_System"] > 0 else r["Stock_Physical"],
    axis=1,
)
df["Total_Available_kg"] = df["Effective_Stock"] + df["In_Transit"]

# To Order = 2-Month Requirement minus Total Available (minimum 0)
df["To_Order_kg"] = (df["Two_Months_kg"] - df["Total_Available_kg"]).apply(lambda x: max(0.0, x))
df["Total_Cost_KES"] = df["Two_Months_kg"] * df["Unit_Rate_KES"]
df["PO_Cost_KES"] = df["To_Order_kg"] * df["Unit_Rate_KES"]

# Tabs Setup
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard & Trend Projection",
    "📑 Supplier Purchase Orders",
    "📦 Warehouse & Low-Stock Alerts",
    "📈 Cost Variance (Nov '25 vs June '26)",
    "🎯 Finished Product Targets",
    "✏️ Edit BOM & Formulations",
])

with tab1:
    st.subheader("Key Performance Metrics (2-Month Production Target)")
    total_qty = df["Two_Months_kg"].sum()
    total_cost = df["Total_Cost_KES"].sum()
    total_local_cost = df[df["Source"] == "Local"]["Total_Cost_KES"].sum()
    total_import_cost = df[df["Source"] == "Import"]["Total_Cost_KES"].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total 2-Month Req.",
            f"{total_qty:,.1f} kg",
            delta=f"{production_scale - 100}% vs Baseline",
        )
    with col2:
        st.metric("Total Material Cost", f"KES {total_cost:,.2f}")
    with col3:
        st.metric("Local Material Cost", f"KES {total_local_cost:,.2f}")
    with col4:
        st.metric("Import Material Cost", f"KES {total_import_cost:,.2f}")

    st.markdown("---")
    st.subheader("📈 Multi-Month Material Requirement Trend Projection (1M vs 2M vs 3M)")

    trend_melted = df.melt(
        id_vars=["Item", "Source"],
        value_vars=["One_Month_kg", "Two_Months_kg", "Three_Months_kg"],
        var_name="Cycle",
        value_name="Requirement_kg",
    )
    trend_melted["Cycle"] = trend_melted["Cycle"].map({
        "One_Month_kg": "1 Month",
        "Two_Months_kg": "2 Months",
        "Three_Months_kg": "3 Months",
    })

    fig_trend = px.bar(
        trend_melted.sort_values(by="Requirement_kg", ascending=False),
        x="Item",
        y="Requirement_kg",
        color="Cycle",
        barmode="group",
        labels={
            "Item": "Raw Material Item",
            "Requirement_kg": "Required Quantity (kg)",
            "Cycle": "Production Cycle",
        },
        color_discrete_map={
            "1 Month": "#93C5FD",
            "2 Months": "#2563EB",
            "3 Months": "#1E3A8A",
        },
    )
    fig_trend.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=50), xaxis_tickangle=-30)
    st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("📑 Supplier Purchase Order Generation")
    po_type = st.radio("Select Vendor Purchase Category:", ["All Vendors", "Local", "Import"], horizontal=True)
    po_df = df[df["Source"] == po_type] if po_type in ["Local", "Import"] else df

    po_display = po_df[["Item", "Source", "To_Order_kg", "Unit_Rate_KES", "PO_Cost_KES"]].copy()
    po_display.columns = ["Material Item", "Vendor Category", "Order Qty (kg)", "Unit Rate (KES/kg)", "Total PO Cost (KES)"]
    po_display = po_display.round(2)
    total_po_cost = po_display["Total PO Cost (KES)"].sum()
    st.info(f"Total Purchase Order Value ({po_type}): KES {total_po_cost:,.2f}")
    st.dataframe(po_display.sort_values(by="Total PO Cost (KES)", ascending=False), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("📦 Warehouse Stock Audit & Automated Low-Stock Alerts")
    st.markdown("Monitor physical warehouse counts against system records and review automated reorder point alerts.")

    stock_df = df[["Item", "Source", "Stock_System", "Effective_Stock", "In_Transit", "Total_Available_kg", "Unit_Rate_KES", "To_Order_kg"]].copy()
    stock_df["Variance (kg)"] = stock_df["Effective_Stock"] - stock_df["Stock_System"]
    stock_df["Inventory Value (KES)"] = stock_df["Total_Available_kg"] * stock_df["Unit_Rate_KES"]

    stock_df["Stock Status"] = stock_df.apply(
        lambda r: "🚨 CRITICAL LOW STOCK" if r["Total_Available_kg"] < (r["To_Order_kg"] * 0.5) else (
            "⚠️ Reorder Recommended" if r["Total_Available_kg"] < r["To_Order_kg"] else "✅ Adequate Stock"
        ),
        axis=1,
    )

    low_stock_items = stock_df[stock_df["Stock Status"].isin(["🚨 CRITICAL LOW STOCK", "⚠️ Reorder Recommended"])]
    if not low_stock_items.empty:
        st.warning(f"⚠️ Inventory Alert: {len(low_stock_items)} material items require attention based on current production targets.")
    else:
        st.success("✅ All warehouse stock levels are currently adequate.")

    stock_display = stock_df[["Item", "Source", "Stock_System", "Effective_Stock", "In_Transit", "Total_Available_kg", "Stock Status", "Inventory Value (KES)"]].copy()
    stock_display.columns = ["Material Item", "Source", "System Stock (kg)", "Physical Count (kg)", "In Transit (kg)", "Total Available (kg)", "Stock Status", "Inventory Value (KES)"]
    stock_display = stock_display.round(2)

    total_inv_val = stock_display["Inventory Value (KES)"].sum()
    st.info(f"Total Available Inventory Valuation: KES {total_inv_val:,.2f}")
    st.dataframe(stock_display.sort_values(by="Inventory Value (KES)", ascending=False), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("📈 Cost Variance Analysis: Nov 2025 Baseline vs June 2026 Projected")
    var_df = df[["Item", "Source", "Two_Months_kg", "Nov_2025_Rate", "June_2026_Rate"]].copy()
    var_df["Nov_2025_Total_KES"] = var_df["Two_Months_kg"] * var_df["Nov_2025_Rate"]
    var_df["June_2026_Total_KES"] = var_df["Two_Months_kg"] * var_df["June_2026_Rate"]
    var_df["Rate Variance (KES)"] = var_df["June_2026_Rate"] - var_df["Nov_2025_Rate"]
    var_df["Pct Variance (%)"] = ((var_df["Rate Variance (KES)"] / var_df["Nov_2025_Rate"]) * 100).round(2)
    var_df["Total Cost Variance (KES)"] = var_df["June_2026_Total_KES"] - var_df["Nov_2025_Total_KES"]

    total_nov_cost = var_df["Nov_2025_Total_KES"].sum()
    total_jun_cost = var_df["June_2026_Total_KES"].sum()
    total_variance_cost = total_jun_cost - total_nov_cost

    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.metric("Nov 2025 Baseline Cost", f"KES {total_nov_cost:,.2f}")
    with col_v2:
        st.metric("June 2026 Projected Cost", f"KES {total_jun_cost:,.2f}", delta=f"KES {total_variance_cost:,.2f}", delta_color="inverse")
    with col_v3:
        overall_pct = (total_variance_cost / total_nov_cost) * 100
        st.metric("Overall Cost Variance", f"{overall_pct:+.2f}%")

    st.markdown("---")
    var_display = var_df[["Item", "Source", "Nov_2025_Rate", "June_2026_Rate", "Pct Variance (%)", "Total Cost Variance (KES)"]].copy()
    var_display.columns = ["Material Item", "Source", "Nov '25 Rate (KES)", "June '26 Rate (KES)", "Rate Variance (%)", "Cost Variance (KES)"]
    var_display = var_display.round(2)
    st.dataframe(var_display.sort_values(by="Cost Variance (KES)", ascending=False), use_container_width=True, hide_index=True)

with tab5:
    st.subheader("🎯 Finished Product Production Targets")
    st.markdown("Configure planned production volume (units/batches) for each finished product across 1, 2, and 3-month cycles.")
    
    edited_products = st.data_editor(
        st.session_state["products_df"],
        num_rows="dynamic",
        use_container_width=True,
        key="products_editor",
    )
    if not edited_products.equals(st.session_state["products_df"]):
        st.session_state["products_df"] = edited_products
        st.rerun()

with tab6:
    st.subheader("✏️ Edit Bill of Materials (BOM) & Raw Material Master")
    st.markdown("Modify raw material consumption per unit of finished product, stock counts, and procurement rates.")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("#### **Raw Material Master & Rates**")
        edited_rm = st.data_editor(
            st.session_state["raw_materials_df"],
            num_rows="dynamic",
            use_container_width=True,
            key="rm_editor",
        )
        if not edited_rm.equals(st.session_state["raw_materials_df"]):
            st.session_state["raw_materials_df"] = edited_rm
            st.rerun()
            
    with col_e2:
        st.markdown("#### **Bill of Materials (BOM - kg per unit)**")
        edited_bom = st.data_editor(
            st.session_state["bom_df"],
            num_rows="dynamic",
            use_container_width=True,
            key="bom_editor",
        )
        if not edited_bom.equals(st.session_state["bom_df"]):
            st.session_state["bom_df"] = edited_bom
            st.rerun()

# --- Consolidated Excel Export Module ---
st.markdown("---")
st.subheader("📥 Export Consolidated Workbook")

def generate_consolidated_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        prod_df.to_excel(writer, sheet_name="Product_Targets", index=False)
        bom_df.to_excel(writer, sheet_name="Bill_Of_Materials", index=False)
        df[["Item", "Source", "One_Month_kg", "Two_Months_kg", "Three_Months_kg", "Unit_Rate_KES", "Total_Cost_KES"]].round(2).to_excel(writer, sheet_name="Dashboard_Summary", index=False)
        df[["Item", "Source", "To_Order_kg", "Unit_Rate_KES"]].assign(
            Total_PO_Cost=lambda r: r["To_Order_kg"] * r["Unit_Rate_KES"]
        ).round(2).to_excel(writer, sheet_name="Purchase_Orders", index=False)
        stock_df.round(2).to_excel(writer, sheet_name="Warehouse_Stock", index=False)
        var_df.round(2).to_excel(writer, sheet_name="Cost_Variance", index=False)
    output.seek(0)
    return output.getvalue()

st.download_button(
    label="📥 Download Consolidated Multi-Tab Excel Workbook (.xlsx)",
    data=generate_consolidated_excel(),
    file_name="product_wise_costing_dashboard.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)