import io
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Production Costing & Warehouse Alert Dashboard",
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


# Load Data Function
@st.cache_data
def load_data():
    data = [
        {
            "Item": "Calcium Stearate",
            "One_Month_kg": 312.15,
            "Two_Months_kg": 624.31,
            "Three_Months_kg": 936.46,
            "To_Order_kg": 936.46,
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
            "One_Month_kg": 38484.54,
            "Two_Months_kg": 76969.09,
            "Three_Months_kg": 115453.63,
            "To_Order_kg": 115453.63,
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
            "One_Month_kg": 3.08,
            "Two_Months_kg": 6.15,
            "Three_Months_kg": 9.23,
            "To_Order_kg": 9.23,
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
            "One_Month_kg": 1240.11,
            "Two_Months_kg": 2480.22,
            "Three_Months_kg": 3720.33,
            "To_Order_kg": 20.33,
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
            "One_Month_kg": 2223.88,
            "Two_Months_kg": 4447.75,
            "Three_Months_kg": 6671.63,
            "To_Order_kg": 6671.63,
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
            "One_Month_kg": 192.78,
            "Two_Months_kg": 385.56,
            "Three_Months_kg": 578.34,
            "To_Order_kg": 578.34,
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
            "One_Month_kg": 2724.89,
            "Two_Months_kg": 5449.78,
            "Three_Months_kg": 8174.68,
            "To_Order_kg": 2224.68,
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
            "One_Month_kg": 162.69,
            "Two_Months_kg": 325.39,
            "Three_Months_kg": 488.08,
            "To_Order_kg": 38.08,
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
            "One_Month_kg": 3075.03,
            "Two_Months_kg": 6150.06,
            "Three_Months_kg": 9225.09,
            "To_Order_kg": 9225.09,
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
            "One_Month_kg": 709.98,
            "Two_Months_kg": 1419.95,
            "Three_Months_kg": 2129.93,
            "To_Order_kg": 2129.93,
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
            "One_Month_kg": 216.49,
            "Two_Months_kg": 432.98,
            "Three_Months_kg": 649.46,
            "To_Order_kg": 649.46,
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
            "One_Month_kg": 2141.94,
            "Two_Months_kg": 4283.87,
            "Three_Months_kg": 6425.81,
            "To_Order_kg": 5550.81,
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
            "One_Month_kg": 32992.75,
            "Two_Months_kg": 65985.50,
            "Three_Months_kg": 98978.25,
            "To_Order_kg": 3978.25,
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
            "One_Month_kg": 42292.41,
            "Two_Months_kg": 84584.81,
            "Three_Months_kg": 126877.22,
            "To_Order_kg": 126877.22,
            "Stock_System": 29976.0,
            "Stock_Physical": 29976.0,
            "In_Transit": 0.0,
            "Unit_Rate_KES": 60.0,
            "Nov_2025_Rate": 58.0,
            "June_2026_Rate": 60.0,
            "Source": "Local",
        },
    ]
    return pd.DataFrame(data)


# Initialize Session State for dynamic editing
if "df" not in st.session_state:
    st.session_state["df"] = load_data()

df = st.session_state["df"]

# App Header
st.markdown(
    '<p class="main-header">🏭 Production Costing & Warehouse Alert'
    " Dashboard</p>",
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Multi-month production trend projections, split'
    " purchase orders, automated low-stock warnings, and consolidated Excel"
    " export.</p>",
    unsafe_allow_html=True,
)

# Sidebar Controls
st.sidebar.header("🎛️ Simulation Controls")
production_scale = st.sidebar.slider(
    "Production Volume Scale (%)",
    min_value=50,
    max_value=200,
    value=100,
    step=5,
)

scale_multiplier = production_scale / 100.0
df["Scaled_1M_kg"] = df["One_Month_kg"] * scale_multiplier
df["Scaled_2M_kg"] = df["Two_Months_kg"] * scale_multiplier
df["Scaled_3M_kg"] = df["Three_Months_kg"] * scale_multiplier
df["Scaled_To_Order_kg"] = (df["To_Order_kg"] * scale_multiplier).apply(
    lambda x: max(0.0, x)
)
df["Total_Cost_KES"] = df["Scaled_2M_kg"] * df["Unit_Rate_KES"]
df["PO_Cost_KES"] = df["Scaled_To_Order_kg"] * df["Unit_Rate_KES"]

# Tabs Setup (Added Edit Formulations Tab)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard & Trend Projection",
    "📑 Supplier Purchase Orders",
    "📦 Warehouse & Low-Stock Alerts",
    "📈 Cost Variance (Nov '25 vs June '26)",
    "✏️ Edit Formulations",
])

with tab1:
    st.subheader("Key Performance Metrics (2-Month Baseline)")
    total_qty = df["Scaled_2M_kg"].sum()
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
    st.subheader(
        "📈 Multi-Month Material Requirement Trend Projection (1M vs 2M vs 3M)"
    )

    trend_melted = df.melt(
        id_vars=["Item", "Source"],
        value_vars=["Scaled_1M_kg", "Scaled_2M_kg", "Scaled_3M_kg"],
        var_name="Cycle",
        value_name="Requirement_kg",
    )
    trend_melted["Cycle"] = trend_melted["Cycle"].map({
        "Scaled_1M_kg": "1 Month",
        "Scaled_2M_kg": "2 Months",
        "Scaled_3M_kg": "3 Months",
    })

    fig_trend = px.bar(
        trend_melted.sort_values(by="Requirement_kg", ascending=False),
        x="Item",
        y="Requirement_kg",
        color="Cycle",
        barmode="group",
        labels={
            "Item": "Material Item",
            "Requirement_kg": "Required Quantity (kg)",
            "Cycle": "Production Cycle",
        },
        color_discrete_map={
            "1 Month": "#93C5FD",
            "2 Months": "#2563EB",
            "3 Months": "#1E3A8A",
        },
    )
    fig_trend.update_layout(
        height=450, margin=dict(l=10, r=10, t=10, b=50), xaxis_tickangle=-30
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("📑 Supplier Purchase Order Generation")
    po_type = st.radio(
        "Select Vendor Purchase Category:",
        ["All Vendors", "Local", "Import"],
        horizontal=True,
    )
    po_df = (
        df[df["Source"] == po_type]
        if po_type in ["Local", "Import"]
        else df
    )

    po_display = po_df[
        [
            "Item",
            "Source",
            "Scaled_To_Order_kg",
            "Unit_Rate_KES",
            "PO_Cost_KES",
        ]
    ].copy()
    po_display.columns = [
        "Material Item",
        "Vendor Category",
        "Order Qty (kg)",
        "Unit Rate (KES/kg)",
        "Total PO Cost (KES)",
    ]
    po_display = po_display.round(2)
    total_po_cost = po_display["Total PO Cost (KES)"].sum()
    st.info(
        f"Total Purchase Order Value ({po_type}): KES"
        f" {total_po_cost:,.2f}"
    )
    st.dataframe(
        po_display.sort_values(by="Total PO Cost (KES)", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    st.subheader("📦 Warehouse Stock Audit & Automated Low-Stock Alerts")
    st.markdown(
        "Monitor physical warehouse counts against system records and review"
        " automated reorder point alerts."
    )

    stock_df = df[
        [
            "Item",
            "Source",
            "Stock_System",
            "Stock_Physical",
            "In_Transit",
            "Unit_Rate_KES",
            "Scaled_To_Order_kg",
        ]
    ].copy()
    stock_df["Physical Count (kg)"] = stock_df.apply(
        lambda r: (
            r["Stock_System"]
            if r["Stock_Physical"] == 0.0 and r["Stock_System"] > 0
            else r["Stock_Physical"]
        ),
        axis=1,
    )
    stock_df["Variance (kg)"] = (
        stock_df["Physical Count (kg)"] - stock_df["Stock_System"]
    )
    stock_df["Total Available (kg)"] = (
        stock_df["Physical Count (kg)"] + stock_df["In_Transit"]
    )
    stock_df["Inventory Value (KES)"] = (
        stock_df["Total Available (kg)"] * stock_df["Unit_Rate_KES"]
    )

    # Automated Reorder Alert logic: Flag if Total Available < 50% of Scaled Requirement
    stock_df["Stock Status"] = stock_df.apply(
        lambda r: (
            "🚨 CRITICAL LOW STOCK"
            if r["Total Available (kg)"] < (r["Scaled_To_Order_kg"] * 0.5)
            else (
                "⚠️ Reorder Recommended"
                if r["Total Available (kg)"] < r["Scaled_To_Order_kg"]
                else "✅ Adequate Stock"
            )
        ),
        axis=1,
    )

    # Low Stock Warning Banners
    low_stock_items = stock_df[
        stock_df["Stock Status"].isin(
            ["🚨 CRITICAL LOW STOCK", "⚠️ Reorder Recommended"]
        )
    ]
    if not low_stock_items.empty:
        st.warning(
            f"⚠️ Inventory Alert: {len(low_stock_items)} material items require"
            " immediate attention or reordering based on current production"
            " targets."
        )
    else:
        st.success("✅ All warehouse stock levels are currently adequate.")

    stock_display = stock_df[
        [
            "Item",
            "Source",
            "Stock_System",
            "Physical Count (kg)",
            "In_Transit",
            "Total Available (kg)",
            "Stock Status",
            "Inventory Value (KES)",
        ]
    ].copy()
    stock_display.columns = [
        "Material Item",
        "Source",
        "System Stock (kg)",
        "Physical Count (kg)",
        "In Transit (kg)",
        "Total Available (kg)",
        "Stock Status",
        "Inventory Value (KES)",
    ]
    stock_display = stock_display.round(2)

    total_inv_val = stock_display["Inventory Value (KES)"].sum()
    st.info(
        f"Total Available Inventory Valuation: KES {total_inv_val:,.2f}"
    )
    st.dataframe(
        stock_display.sort_values(
            by="Inventory Value (KES)", ascending=False
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab4:
    st.subheader(
        "📈 Cost Variance Analysis: Nov 2025 Baseline vs June 2026 Projected"
    )
    var_df = df[
        [
            "Item",
            "Source",
            "Scaled_2M_kg",
            "Nov_2025_Rate",
            "June_2026_Rate",
        ]
    ].copy()
    var_df["Nov_2025_Total_KES"] = var_df["Scaled_2M_kg"] * var_df["Nov_2025_Rate"]
    var_df["June_2026_Total_KES"] = (
        var_df["Scaled_2M_kg"] * var_df["June_2026_Rate"]
    )
    var_df["Rate Variance (KES)"] = (
        var_df["June_2026_Rate"] - var_df["Nov_2025_Rate"]
    )
    var_df["Pct Variance (%)"] = (
        (var_df["Rate Variance (KES)"] / var_df["Nov_2025_Rate"]) * 100
    ).round(2)
    var_df["Total Cost Variance (KES)"] = (
        var_df["June_2026_Total_KES"] - var_df["Nov_2025_Total_KES"]
    )

    total_nov_cost = var_df["Nov_2025_Total_KES"].sum()
    total_jun_cost = var_df["June_2026_Total_KES"].sum()
    total_variance_cost = total_jun_cost - total_nov_cost

    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.metric("Nov 2025 Baseline Cost", f"KES {total_nov_cost:,.2f}")
    with col_v2:
        st.metric(
            "June 2026 Projected Cost",
            f"KES {total_jun_cost:,.2f}",
            delta=f"KES {total_variance_cost:,.2f}",
            delta_color="inverse",
        )
    with col_v3:
        overall_pct = (total_variance_cost / total_nov_cost) * 100
        st.metric("Overall Cost Variance", f"{overall_pct:+.2f}%")

    st.markdown("---")
    var_display = var_df[
        [
            "Item",
            "Source",
            "Nov_2025_Rate",
            "June_2026_Rate",
            "Pct Variance (%)",
            "Total Cost Variance (KES)",
        ]
    ].copy()
    var_display.columns = [
        "Material Item",
        "Source",
        "Nov '25 Rate (KES)",
        "June '26 Rate (KES)",
        "Rate Variance (%)",
        "Cost Variance (KES)",
    ]
    var_display = var_display.round(2)
    st.dataframe(
        var_display.sort_values(by="Cost Variance (KES)", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

with tab5:
    st.subheader("✏️ Interactive Formulation & Rate Editor")
    st.markdown(
        "Modify baseline quantities, rates, stock levels, or add/remove rows"
        " below. Changes instantly update all metrics, charts, and exports across"
        " the app."
    )

    edited_df = st.data_editor(
        st.session_state["df"],
        num_rows="dynamic",
        use_container_width=True,
        key="formulation_table_editor",
    )

    # Update session state with edited dataframe
    if not edited_df.equals(st.session_state["df"]):
        st.session_state["df"] = edited_df
        st.rerun()

    if st.button("🔄 Reset to Default Formulations"):
        st.session_state["df"] = load_data()
        st.rerun()

# --- Consolidated Excel Export Module ---
st.markdown("---")
st.subheader("📥 Export Consolidated Workbook")


def generate_consolidated_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df[
            [
                "Item",
                "Source",
                "Scaled_1M_kg",
                "Scaled_2M_kg",
                "Scaled_3M_kg",
                "Unit_Rate_KES",
                "Total_Cost_KES",
            ]
        ].round(2).to_excel(writer, sheet_name="Dashboard_Summary", index=False)
        df[["Item", "Source", "Scaled_To_Order_kg", "Unit_Rate_KES"]].assign(
            Total_PO_Cost=lambda r: r["Scaled_To_Order_kg"] * r["Unit_Rate_KES"]
        ).round(2).to_excel(writer, sheet_name="Purchase_Orders", index=False)
        stock_df.round(2).to_excel(writer, sheet_name="Warehouse_Stock", index=False)
        var_df.round(2).to_excel(writer, sheet_name="Cost_Variance", index=False)
    output.seek(0)
    return output.getvalue()


st.download_button(
    label="📥 Download Consolidated Multi-Tab Excel Workbook (.xlsx)",
    data=generate_consolidated_excel(),
    file_name="production_costing_consolidated_dashboard.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ),
)