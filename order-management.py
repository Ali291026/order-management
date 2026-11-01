import io
import pandas as pd
import plotly.express as px
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Multi-Layer Product Formulation & Costing Dashboard",
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


# Initialize Session State for Products, Layered BOMs, and Raw Materials
@st.cache_data
def load_initial_data():
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

    products = [
        {"Product": "3-Layer PVC Pipe (Standard)", "Target_1M_Units": 1000, "Target_2M_Units": 2000, "Target_3M_Units": 3000, "Total_Weight_Kg_Per_Unit": 50.0},
    ]

    # Layered BOM Data: Specifying Layer name, Item, and Kg required per unit
    bom_data = [
        # Inner Layer (e.g., 20% of total weight)
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Inner Layer", "Item": "Resin", "Kg_Per_Unit": 5.0},
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Inner Layer", "Item": "Stabilizer", "Kg_Per_Unit": 0.5},
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Inner Layer", "Item": "Calcium Carbonate", "Kg_Per_Unit": 4.5},
        
        # Middle Layer (e.g., 60% of total weight - high filler)
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Middle Layer", "Item": "PVC Nbi", "Kg_Per_Unit": 15.0},
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Middle Layer", "Item": "Calcium Carbonate", "Kg_Per_Unit": 12.0},
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Middle Layer", "Item": "Resin", "Kg_Per_Unit": 3.0},
        
        # Outer Layer (e.g., 20% of total weight - UV resistant / pigment)
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Outer Layer", "Item": "PVC SGT", "Kg_Per_Unit": 6.0},
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Outer Layer", "Item": "Titanium Dioxide", "Kg_Per_Unit": 2.0},
        {"Product": "3-Layer PVC Pipe (Standard)", "Layer": "Outer Layer", "Item": "Stabilizer", "Kg_Per_Unit": 2.0},
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
    '<p class="main-header">🏭 Multi-Layer Product Formulation & Costing Dashboard</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">Manage multi-layer product BOMs, analyze compound percentage distribution, and track unit production costs.</p>',
    unsafe_allow_html=True,
)

# --- SIDEBAR CONTROLS & NAVIGATION ---
st.sidebar.header("🎛️ Global Simulation Controls")
production_scale = st.sidebar.slider(
    "Production Volume Scale (%)",
    min_value=50,
    max_value=200,
    value=100,
    step=5,
)
scale_multiplier = production_scale / 100.0

st.sidebar.markdown("---")
st.sidebar.header("📌 Navigation Menu")
selected_page = st.sidebar.radio(
    "Go to:",
    [
        "📊 Dashboard & Trend Projection",
        "💰 Product Cost & Unit Pricing",
        "📑 Supplier Purchase Orders",
        "📦 Warehouse & Low-Stock Alerts",
        "🎯 Finished Product Targets",
        "✏️ Edit Multi-Layer BOM",
    ],
)

st.sidebar.markdown("---")
st.sidebar.header("📦 Product & Material Manager")

existing_products = st.session_state["products_df"]["Product"].tolist()
selected_product = st.sidebar.selectbox("Select Product to Edit Layers:", existing_products)

with st.sidebar.expander("➕ Add New Multi-Layer Product"):
    new_prod_name = st.text_input("Product Name:")
    new_prod_wt = st.number_input("Total Weight per Unit (kg):", value=50.0)
    if st.button("Create Product"):
        if new_prod_name and new_prod_name not in existing_products:
            new_row = pd.DataFrame([{
                "Product": new_prod_name, 
                "Target_1M_Units": 100, 
                "Target_2M_Units": 200, 
                "Target_3M_Units": 300,
                "Total_Weight_Kg_Per_Unit": new_prod_wt
            }])
            st.session_state["products_df"] = pd.concat([st.session_state["products_df"], new_row], ignore_index=True)
            
            # Add default layers
            current_rms = st.session_state["raw_materials_df"]["Item"].tolist()
            init_boms = pd.DataFrame([
                {"Product": new_prod_name, "Layer": "Outer Layer", "Item": current_rms[0], "Kg_Per_Unit": 0.0}
            ])
            st.session_state["bom_df"] = pd.concat([st.session_state["bom_df"], init_boms], ignore_index=True)
            st.success(f"Created Multi-Layer Product: {new_prod_name}")
            st.rerun()

# --- CALCULATIONS ---
prod_df["Scaled_1M_Units"] = prod_df["Target_1M_Units"] * scale_multiplier
prod_df["Scaled_2M_Units"] = prod_df["Target_2M_Units"] * scale_multiplier
prod_df["Scaled_3M_Units"] = prod_df["Target_3M_Units"] * scale_multiplier

# Merge BOM with Scaled Targets
merged_demand = pd.merge(bom_df, prod_df, on="Product", how="inner")
merged_demand["Req_1M_kg"] = merged_demand["Kg_Per_Unit"] * merged_demand["Scaled_1M_Units"]
merged_demand["Req_2M_kg"] = merged_demand["Kg_Per_Unit"] * merged_demand["Scaled_2M_Units"]
merged_demand["Req_3M_kg"] = merged_demand["Kg_Per_Unit"] * merged_demand["Scaled_3M_Units"]

# Aggregate raw material demand across all layers and products
agg_demand = merged_demand.groupby("Item")[["Req_1M_kg", "Req_2M_kg", "Req_3M_kg"]].sum().reset_index()
df = pd.merge(rm_df, agg_demand, on="Item", how="left").fillna(0)

df["One_Month_kg"] = df["Req_1M_kg"]
df["Two_Months_kg"] = df["Req_2M_kg"]
df["Three_Months_kg"] = df["Req_3M_kg"]

total_1m_sum = df["One_Month_kg"].sum()
total_2m_sum = df["Two_Months_kg"].sum()
total_3m_sum = df["Three_Months_kg"].sum()

df["One_Month_Pct"] = (df["One_Month_kg"] / total_1m_sum * 100) if total_1m_sum > 0 else 0
df["Two_Months_Pct"] = (df["Two_Months_kg"] / total_2m_sum * 100) if total_2m_sum > 0 else 0
df["Three_Months_Pct"] = (df["Three_Months_kg"] / total_3m_sum * 100) if total_3m_sum > 0 else 0

df["Effective_Stock"] = df.apply(
    lambda r: r["Stock_System"] if r["Stock_Physical"] == 0.0 and r["Stock_System"] > 0 else r["Stock_Physical"],
    axis=1,
)
df["Total_Available_kg"] = df["Effective_Stock"] + df["In_Transit"]
df["To_Order_kg"] = (df["Two_Months_kg"] - df["Total_Available_kg"]).apply(lambda x: max(0.0, x))
df["Total_Cost_KES"] = df["Two_Months_kg"] * df["Unit_Rate_KES"]
df["PO_Cost_KES"] = df["To_Order_kg"] * df["Unit_Rate_KES"]

# --- PAGE ROUTING ---
if selected_page == "📊 Dashboard & Trend Projection":
    st.subheader("Key Performance Metrics (2-Month Multi-Layer Production)")
    total_qty = df["Two_Months_kg"].sum()
    total_cost = df["Total_Cost_KES"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total 2-Month Req.", f"{total_qty:,.1f} kg", delta=f"{production_scale - 100}% vs Baseline")
    with col2:
        st.metric("Total Material Cost", f"KES {total_cost:,.2f}")
    with col3:
        st.metric("Active Products", f"{len(prod_df)}")

    st.markdown("---")
    st.subheader("📈 Aggregated Raw Material Requirements Across Layers")
    summary_display = df[[
        "Item", "Source", "Two_Months_kg", "Two_Months_Pct", "Unit_Rate_KES", "Total_Cost_KES"
    ]].copy()
    summary_display.columns = ["Material Item", "Source", "2M Qty (kg)", "Share (%)", "Rate (KES)", "2M Cost (KES)"]
    summary_display = summary_display.round(2)
    st.dataframe(summary_display.sort_values(by="2M Qty (kg)", ascending=False), use_container_width=True, hide_index=True)

elif selected_page == "💰 Product Cost & Unit Pricing":
    st.subheader("💰 Product-Wise Layer Cost & Cost Per Kg Breakdown")
    st.markdown("Calculates total compound cost per finished product unit and effective cost per kg based on layer formulations.")

    # Calculate cost per unit per product by merging BOM with Raw Material rates
    bom_with_rates = pd.merge(bom_df, rm_df[["Item", "Unit_Rate_KES"]], on="Item", how="inner")
    bom_with_rates["Line_Cost_KES"] = bom_with_rates["Kg_Per_Unit"] * bom_with_rates["Unit_Rate_KES"]
    
    product_cost_summary = bom_with_rates.groupby("Product").agg(
        Total_Kg_Per_Unit=("Kg_Per_Unit", "sum"),
        Total_Cost_Per_Unit_KES=("Line_Cost_KES", "sum")
    ).reset_index()
    
    product_cost_summary["Cost_Per_Kg_KES"] = product_cost_summary["Total_Cost_Per_Unit_KES"] / product_cost_summary["Total_Kg_Per_Unit"]
    product_cost_summary = product_cost_summary.round(2)
    
    st.dataframe(product_cost_summary, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📋 Layer-by-Layer Breakdown")
    layer_summary = bom_with_rates.groupby(["Product", "Layer"]).agg(
        Layer_Kg=("Kg_Per_Unit", "sum"),
        Layer_Cost_KES=("Line_Cost_KES", "sum")
    ).reset_index().round(2)
    st.dataframe(layer_summary, use_container_width=True, hide_index=True)

elif selected_page == "📑 Supplier Purchase Orders":
    st.subheader("📑 Supplier Purchase Orders")
    po_display = df[["Item", "Source", "To_Order_kg", "Unit_Rate_KES", "PO_Cost_KES"]].copy()
    po_display.columns = ["Material Item", "Vendor", "Order Qty (kg)", "Rate (KES)", "Total PO Cost (KES)"]
    st.dataframe(po_display.round(2), use_container_width=True, hide_index=True)

elif selected_page == "📦 Warehouse & Low-Stock Alerts":
    st.subheader("📦 Warehouse Stock Audit")
    stock_display = df[["Item", "Source", "Stock_System", "Total_Available_kg", "To_Order_kg"]].copy()
    stock_display.columns = ["Material", "Source", "System Stock", "Available", "Required Order"]
    st.dataframe(stock_display.round(2), use_container_width=True, hide_index=True)

elif selected_page == "🎯 Finished Product Targets":
    st.subheader("🎯 Finished Product Production Targets")
    edited_products = st.data_editor(st.session_state["products_df"], num_rows="dynamic", use_container_width=True)
    if not edited_products.equals(st.session_state["products_df"]):
        st.session_state["products_df"] = edited_products
        st.rerun()

elif selected_page == "✏️ Edit Multi-Layer BOM":
    st.subheader(f"✏️ Edit Layers & Formulations for: **{selected_product}**")
    st.markdown("Define layers (e.g., Inner, Middle, Outer), compound items, and kg required per unit.")

    product_bom = st.session_state["bom_df"][st.session_state["bom_df"]["Product"] == selected_product].copy()
    
    edited_product_bom = st.data_editor(
        product_bom[["Layer", "Item", "Kg_Per_Unit"]],
        num_rows="dynamic",
        use_container_width=True,
        key=f"layer_bom_editor_{selected_product}",
    )
    
    if not edited_product_bom.equals(product_bom[["Layer", "Item", "Kg_Per_Unit"]]):
        edited_product_bom["Product"] = selected_product
        other_boms = st.session_state["bom_df"][st.session_state["bom_df"]["Product"] != selected_product]
        st.session_state["bom_df"] = pd.concat([other_boms, edited_product_bom], ignore_index=True)
        st.rerun()