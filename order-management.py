import streamlit as st
import sqlite3
from datetime import datetime

# --- DATABASE SETUP ---
def get_connection():
    conn = sqlite3.connect("business_tracker.db", check_same_thread=False)
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_ref TEXT UNIQUE,
            client_name TEXT,
            pricing_terms TEXT,
            payment_terms TEXT,
            validity_date TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotation_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_ref TEXT,
            item_details TEXT,
            unit_price REAL,
            quantity INTEGER,
            FOREIGN KEY (quote_ref) REFERENCES quotations (quote_ref)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lpos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lpo_number TEXT UNIQUE,
            quote_ref TEXT,
            client_name TEXT,
            delivery_schedule TEXT,
            payment_terms TEXT,
            status TEXT DEFAULT 'Open',
            FOREIGN KEY (quote_ref) REFERENCES quotations (quote_ref)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lpo_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lpo_number TEXT,
            item_name TEXT,
            ordered_qty INTEGER,
            delivered_qty INTEGER DEFAULT 0,
            balance_qty INTEGER,
            FOREIGN KEY (lpo_number) REFERENCES lpos (lpo_number)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lpo_number TEXT,
            term_description TEXT,
            due_date TEXT,
            amount REAL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (lpo_number) REFERENCES lpos (lpo_number)
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(
    page_title="Enterprise Order & Quotation Management", 
    page_icon="💼", 
    layout="wide"
)

# Custom Enterprise UI Theme Styling
st.markdown("""
    <style>
        /* Main background & font adjustments */
        .main {
            background-color: #f8f9fa;
        }
        /* Metric Card Container Styling */
        .metric-container {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
        /* Custom Tabs Styling */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 12px; 
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            color: #4a5568;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2563eb !important;
            color: white !important;
            border-color: #2563eb !important;
        }
        /* Clean headers */
        h1, h2, h3 {
            color: #1e293b;
        }
    </style>
""", unsafe_allow_html=True)

COMPANY_NAME = "MY COMPANY NAME LLC"
COMPANY_ADDRESS = "123 Business Ave, Suite 100 | Phone: +1 234 567 8900 | Email: info@mycompany.com"

# Sidebar Navigation Design
st.sidebar.title("💼 Management Suite")
st.sidebar.markdown(f"**Entity:** `{COMPANY_NAME}`")
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigation Menu", [
    "📊 Executive Dashboard", 
    "📝 Manage Quotations", 
    "📦 LPO & Deliveries", 
    "💰 Payment Tracking", 
    "🖨️ Print Documents"
])

conn = get_connection()
cursor = conn.cursor()

# ==========================================
# 1. EXECUTIVE DASHBOARD (Polished UI)
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Business Dashboard")
    st.markdown("Real-time overview of active quotations, order fulfillments, deliveries, and pending billings.")
    st.markdown("---")

    # Fetch metric counts
    cursor.execute("SELECT COUNT(*) FROM quotations WHERE status = 'Active'")
    pending_quotes_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Open'")
    open_lpos_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Fulfilled'")
    fulfilled_lpos_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'Pending'")
    total_pending_revenue = cursor.fetchone()[0] or 0.0

    # Modern KPI Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-container">
                <p style="color: #64748b; font-size: 14px; font-weight: 600; margin-bottom: 5px;">⏳ PENDING QUOTATIONS</p>
                <h2 style="color: #0f172a; margin: 0; font-size: 28px;">{pending_quotes_count}</h2>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <p style="color: #64748b; font-size: 14px; font-weight: 600; margin-bottom: 5px;">📦 OPEN LPOS</p>
                <h2 style="color: #2563eb; margin: 0; font-size: 28px;">{open_lpos_count}</h2>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-container">
                <p style="color: #64748b; font-size: 14px; font-weight: 600; margin-bottom: 5px;">✅ COMPLETED LPOS</p>
                <h2 style="color: #16a34a; margin: 0; font-size: 28px;">{fulfilled_lpos_count}</h2>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-container">
                <p style="color: #64748b; font-size: 14px; font-weight: 600; margin-bottom: 5px;">💰 PENDING PAYMENTS</p>
                <h2 style="color: #d97706; margin: 0; font-size: 28px;">${total_pending_revenue:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sub-tabs for Dashboard Sections
    dash_tab1, dash_tab2, dash_tab3 = st.tabs(["📦 Open LPO Tracker", "⏳ Pending Quotations", "✅ Completed LPOs"])

    with dash_tab1:
        st.subheader("Active LPOs & Item Fulfillment Status")
        cursor.execute("SELECT lpo_number, client_name, delivery_schedule, payment_terms FROM lpos WHERE status = 'Open'")
        open_lpos = cursor.fetchall()
        
        if open_lpos:
            for lpo in open_lpos:
                with st.expander(f"📋 LPO Reference: {lpo[0]}  |  Client: {lpo[1]}  |  Due: {lpo[2]}", expanded=True):
                    st.markdown(f"**Payment Terms:** `{lpo[3]}`")
                    
                    cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (lpo[0],))
                    items = cursor.fetchall()
                    
                    for item in items:
                        item_name, ordered, delivered, balance = item
                        progress = float(delivered) / float(ordered) if ordered > 0 else 0.0
                        
                        cols = st.columns([3, 1, 1, 1])
                        cols[0].markdown(f"• **{item_name}**")
                        cols[1].text(f"Ordered: {ordered}")
                        cols[2].text(f"Delivered: {delivered}")
                        cols[3].text(f"Balance: {balance}")
                        st.progress(progress)
                    st.markdown("---")
        else:
            st.info("No open LPOs found right now. All deliveries are up to date!")

    with dash_tab2:
        st.subheader("Quotations Awaiting LPO Confirmation")
        cursor.execute("SELECT quote_ref, client_name, validity_date FROM quotations WHERE status = 'Active'")
        pending_quotes = cursor.fetchall()
        if pending_quotes:
            for q in pending_quotes:
                with st.expander(f"Quote Ref: {q[0]} | Client: {q[1]} | Valid Until: {q[2]}"):
                    cursor.execute("SELECT item_details, unit_price, quantity FROM quotation_items WHERE quote_ref = ?", (q[0],))
                    q_items = cursor.fetchall()
                    st.dataframe([{"Item Description": i[0], "Unit Price ($)": f"${i[1]:,.2f}", "Quantity": i[2], "Line Total ($)": f"${i[1]*i[2]:,.2f}"} for i in q_items], use_container_width=True)
        else:
            st.success("No pending quotations awaiting confirmation.")

    with dash_tab3:
        st.subheader("Successfully Fulfilled LPOs")
        cursor.execute("SELECT lpo_number, client_name, delivery_schedule FROM lpos WHERE status = 'Fulfilled'")
        fulfilled_lpos = cursor.fetchall()
        if fulfilled_lpos:
            st.dataframe(
                [{"LPO Number": f[0], "Client Name": f[1], "Delivery Schedule": f[2]} for f in fulfilled_lpos],
                use_container_width=True
            )
        else:
            st.info("No completed LPOs recorded yet.")

# ==========================================
# 2. MANAGE QUOTATIONS (Multi-Item)
# ==========================================
elif menu == "📝 Manage Quotations":
    st.title("📝 Quotation Management Suite")
    st.markdown("Create, view, and maintain quotations with multiple line items and strict duplication prevention.")
    
    tab1, tab2 = st.tabs(["Create Quotation", "View / Edit Quotations"])

    with tab1:
        st.subheader("New Commercial Quotation Form")
        with st.form("create_quote_form"):
            col1, col2 = st.columns(2)
            with col1:
                q_ref = st.text_input("Quotation Reference (e.g., QT-2026-001)")
                client = st.text_input("Client Name")
            with col2:
                pricing_terms = st.text_input("Pricing Terms", value="Fixed pricing")
                payment_terms = st.text_input("Payment Terms", value="Net 30")
                validity_date = st.date_input("Validity Date")

            st.markdown("---")
            st.markdown("### 📋 Quotation Item Lines")
            
            num_items = st.number_input("Number of item lines to add:", min_value=1, max_value=15, value=2)
            
            item_data = []
            for i in range(int(num_items)):
                cols = st.columns([3, 1, 1])
                it_name = cols[0].text_input(f"Item #{i+1} Description", key=f"item_{i}")
                it_price = cols[1].number_input(f"Unit Price #{i+1} ($)", min_value=0.0, step=10.0, key=f"price_{i}")
                it_qty = cols[2].number_input(f"Qty #{i+1}", min_value=1, value=1, key=f"qty_{i}")
                item_data.append((it_name, it_price, it_qty))

            submitted = st.form_submit_button("Save Quotation")
            if submitted:
                if not q_ref.strip() or not client.strip():
                    st.error("Please enter a valid Quotation Reference and Client Name.")
                else:
                    try:
                        cursor.execute('''
                            INSERT INTO quotations (quote_ref, client_name, pricing_terms, payment_terms, validity_date, status)
                            VALUES (?, ?, ?, ?, ?, 'Active')
                        ''', (q_ref, client, pricing_terms, payment_terms, str(validity_date)))

                        for it_name, it_price, it_qty in item_data:
                            if it_name.strip():
                                cursor.execute('''
                                    INSERT INTO quotation_items (quote_ref, item_details, unit_price, quantity)
                                    VALUES (?, ?, ?, ?)
                                ''', (q_ref, it_name, it_price, it_qty))

                        conn.commit()
                        st.success(f"Quotation '{q_ref}' successfully saved with all line items!")
                    except sqlite3.IntegrityError:
                        st.error(f"Error: Quotation reference '{q_ref}' already exists. Duplication prevented!")

    with tab2:
        st.subheader("Existing Quotations Database")
        cursor.execute("SELECT quote_ref, client_name, pricing_terms, payment_terms, validity_date, status FROM quotations")
        all_quotes = cursor.fetchall()
        
        if all_quotes:
            for q in all_quotes:
                with st.expander(f"Ref: {q[0]} | Client: {q[1]} | Status: {q[5]}"):
                    st.write(f"**Pricing Terms:** {q[2]} | **Payment Terms:** {q[3]} | **Valid Until:** {q[4]}")
                    cursor.execute("SELECT item_details, unit_price, quantity FROM quotation_items WHERE quote_ref = ?", (q[0],))
                    items = cursor.fetchall()
                    st.dataframe([{"Item": i[0], "Unit Price ($)": f"${i[1]:,.2f}", "Qty": i[2], "Total ($)": f"${i[1]*i[2]:,.2f}"} for i in items], use_container_width=True)
        else:
            st.info("No quotations found.")

# ==========================================
# 3. LPO & DELIVERIES
# ==========================================
elif menu == "📦 LPO & Deliveries":
    st.title("📦 LPO Tracking, Schedules & Deliveries")
    st.markdown("Convert confirmed quotations into LPOs, track delivery schedules, and record running item balances.")

    tab1, tab2, tab3 = st.tabs(["Create LPO", "Record Delivery", "Edit LPO Quantities"])

    with tab1:
        st.subheader("Convert Active Quotation to LPO")
        cursor.execute("SELECT quote_ref FROM quotations WHERE status = 'Active'")
        active_quotes = [row[0] for row in cursor.fetchall()]

        if not active_quotes:
            st.warning("No active quotations available to convert.")
        else:
            with st.form("create_lpo_form"):
                lpo_num = st.text_input("LPO Number (e.g., LPO-9988)")
                selected_quote = st.selectbox("Select Quotation Reference", active_quotes)
                delivery_sched = st.date_input("Delivery Schedule Date")
                lpo_payment_terms = st.text_input("LPO Payment Terms", value="Net 30")

                lpo_submit = st.form_submit_button("Generate LPO From Quotation")
                if lpo_submit:
                    try:
                        cursor.execute("SELECT client_name FROM quotations WHERE quote_ref = ?", (selected_quote,))
                        client_name = cursor.fetchone()[0]

                        cursor.execute('''
                            INSERT INTO lpos (lpo_number, quote_ref, client_name, delivery_schedule, payment_terms, status)
                            VALUES (?, ?, ?, ?, ?, 'Open')
                        ''', (lpo_num, selected_quote, client_name, str(delivery_sched), lpo_payment_terms))

                        cursor.execute("SELECT item_details, quantity FROM quotation_items WHERE quote_ref = ?", (selected_quote,))
                        quote_items = cursor.fetchall()

                        for it_name, it_qty in quote_items:
                            cursor.execute('''
                                INSERT INTO lpo_items (lpo_number, item_name, ordered_qty, delivered_qty, balance_qty)
                                VALUES (?, ?, ?, 0, ?)
                            ''', (lpo_num, it_name, it_qty, it_qty))

                        cursor.execute("UPDATE quotations SET status = 'Confirmed' WHERE quote_ref = ?", (selected_quote,))
                        conn.commit()
                        st.success(f"LPO '{lpo_num}' successfully generated!")
                    except sqlite3.IntegrityError:
                        st.error(f"Error: LPO Number '{lpo_num}' already exists.")

    with tab2:
        st.subheader("Log Deliveries & Maintain Balances")
        cursor.execute("SELECT lpo_number FROM lpos WHERE status = 'Open'")
        open_lpos = [row[0] for row in cursor.fetchall()]

        if not open_lpos:
            st.info("No open LPOs available for delivery tracking.")
        else:
            selected_lpo = st.selectbox("Select Open LPO Number", open_lpos)
            
            cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (selected_lpo,))
            items = cursor.fetchall()

            for item in items:
                st.write(f"• **{item[0]}** | Ordered: {item[1]} | Delivered: {item[2]} | **Balance:** {item[3]}")

            with st.form("delivery_form"):
                item_to_deliver = st.selectbox("Select Item to Deliver", [i[0] for i in items])
                qty_del = st.number_input("Quantity Being Delivered Now", min_value=1, step=1)
                del_submit = st.form_submit_button("Confirm Delivery")

                if del_submit:
                    cursor.execute("SELECT ordered_qty, delivered_qty FROM lpo_items WHERE lpo_number = ? AND item_name = ?", (selected_lpo, item_to_deliver))
                    ord_q, del_q = cursor.fetchone()
                    new_del = del_q + qty_del
                    new_bal = ord_q - new_del

                    if new_bal < 0:
                        st.error("Error: Delivered quantity cannot exceed ordered quantity!")
                    else:
                        cursor.execute("UPDATE lpo_items SET delivered_qty = ?, balance_qty = ? WHERE lpo_number = ? AND item_name = ?", 
                                       (new_del, new_bal, selected_lpo, item_to_deliver))
                        
                        cursor.execute("SELECT SUM(balance_qty) FROM lpo_items WHERE lpo_number = ?", (selected_lpo,))
                        total_bal = cursor.fetchone()[0]
                        if total_bal == 0:
                            cursor.execute("UPDATE lpos SET status = 'Fulfilled' WHERE lpo_number = ?", (selected_lpo,))
                        
                        conn.commit()
                        st.success(f"Delivery recorded! Remaining balance for {item_to_deliver}: {new_bal}")
                        st.rerun()

    with tab3:
        st.subheader("Correct / Edit LPO Ordered Quantities")
        cursor.execute("