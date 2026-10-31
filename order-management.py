import streamlit as st
import sqlite3
from datetime import datetime
from fpdf import FPDF
import os
import pandas as pd
import io

# --- DATABASE SETUP & AUTO-MIGRATION ---
def get_connection():
    conn = sqlite3.connect("business_tracker.db", check_same_thread=False)
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users Table for Access Control
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    # Seed default users if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'Admin')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('sales', 'sales123', 'Sales')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('finance', 'finance123', 'Finance')")
        conn.commit()

    # Quotations Header Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_ref TEXT UNIQUE,
            client_name TEXT,
            currency TEXT DEFAULT 'USD ($)',
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

    # LPOs Header Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lpos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lpo_number TEXT UNIQUE,
            quote_ref TEXT,
            client_name TEXT,
            currency TEXT DEFAULT 'USD ($)',
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

    # Auto-migration checks
    try:
        cursor.execute("ALTER TABLE quotations ADD COLUMN currency TEXT DEFAULT 'USD ($)'")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE lpos ADD COLUMN currency TEXT DEFAULT 'USD ($)'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

create_tables()

# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(
    page_title="Enterprise Order & Quotation Management", 
    page_icon="💼", 
    layout="wide"
)

st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .metric-container {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 10px;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 12px; background-color: transparent; }
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
        h1, h2, h3 { color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

COMPANY_NAME = "MY COMPANY NAME LLC"
COMPANY_ADDRESS = "123 Business Ave, Suite 100 | Phone: +1 234 567 8900 | Email: info@mycompany.com"
LOGO_FILE = "logo.png"
CURRENCIES = ["USD ($)", "EUR (€)", "GBP (£)", "AED (د.إ)", "SGD ($)", "CAD ($)", "AUD ($)"]

# --- SESSION STATE FOR AUTHENTICATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🔐 Enterprise Login Portal")
    st.markdown("Please log in with your credentials to access the system.")
    
    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")
        
        if login_submit:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username_input.strip(), password_input.strip()))
            user_record = cursor.fetchone()
            conn.close()
            
            if user_record:
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.session_state.role = user_record[0]
                st.success(f"Welcome back, {username_input} ({user_record[0]})!")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")
    st.stop()

# ==========================================
# AUTHENTICATED APP LAYOUT
# ==========================================
st.sidebar.title("💼 Management Suite")
if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, use_container_width=True)

st.sidebar.markdown(f"**User:** `{st.session_state.username}`")
st.sidebar.markdown(f"**Role:** `{st.session_state.role}`")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

st.sidebar.markdown("---")

menu_options = ["📊 Executive Dashboard"]

if st.session_state.role in ["Admin", "Sales"]:
    menu_options.extend(["📝 Manage Quotations", "📦 LPO & Deliveries", "🖨️ Print Documents"])

if st.session_state.role in ["Admin", "Finance"]:
    menu_options.extend(["💰 Payment Tracking", "📈 Reports & Analytics"])

if st.session_state.role == "Admin":
    menu_options.append("👥 User Management")

menu = st.sidebar.radio("Navigation Menu", menu_options)

conn = get_connection()
cursor = conn.cursor()

# ==========================================
# 1. EXECUTIVE DASHBOARD (Multi-Currency Breakdown)
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Business Dashboard")
    st.markdown("Real-time overview of active quotations, order fulfillments, deliveries, and pending payments grouped by currency.")
    st.markdown("---")

    cursor.execute("SELECT COUNT(*) FROM quotations WHERE status = 'Active'")
    pending_quotes_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Open'")
    open_lpos_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Fulfilled'")
    fulfilled_lpos_count = cursor.fetchone()[0]

    col1, col2, col3 = st.columns(3)
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("💰 Pending Payments Breakdown (Currency-Wise)")

    # Query pending payments grouped by currency
    cursor.execute('''
        SELECT l.currency, SUM(p.amount) 
        FROM payments p 
        JOIN lpos l ON p.lpo_number = l.lpo_number 
        WHERE p.status = 'Pending' 
        GROUP BY l.currency
    ''')
    currency_totals = cursor.fetchall()

    if currency_totals:
        cols = st.columns(min(len(currency_totals), 4))
        for idx, (curr, total_amt) in enumerate(currency_totals):
            col_idx = idx % 4
            amt_val = total_amt if total_amt else 0.0
            cols[col_idx].markdown(f"""
                <div class="metric-container">
                    <p style="color: #64748b; font-size: 13px; font-weight: 600; margin-bottom: 5px;">PENDING ({curr})</p>
                    <h3 style="color: #d97706; margin: 0; font-size: 24px;">{amt_val:,.2f}</h3>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No pending payments recorded across any currency right now.")

    st.markdown("<br>", unsafe_allow_html=True)
    dash_tab1, dash_tab2, dash_tab3 = st.tabs(["📦 Open LPO Tracker", "⏳ Pending Quotations", "✅ Completed LPOs"])

    with dash_tab1:
        st.subheader("Active LPOs & Item Fulfillment Status")
        cursor.execute("SELECT lpo_number, client_name, currency, delivery_schedule, payment_terms FROM lpos WHERE status = 'Open'")
        open_lpos = cursor.fetchall()
        
        if open_lpos:
            for lpo in open_lpos:
                with st.expander(f"📋 LPO: {lpo[0]} | Client: {lpo[1]} | Currency: {lpo[2]} | Due: {lpo[3]}", expanded=True):
                    st.markdown(f"**Payment Terms:** `{lpo[4]}`")
                    
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
            st.info("No open LPOs found right now.")

    with dash_tab2:
        st.subheader("Quotations Awaiting LPO Confirmation")
        cursor.execute("SELECT quote_ref, client_name, currency, validity_date FROM quotations WHERE status = 'Active'")
        pending_quotes = cursor.fetchall()
        if pending_quotes:
            for q in pending_quotes:
                with st.expander(f"Quote Ref: {q[0]} | Client: {q[1]} | Currency: {q[2]} | Valid Until: {q[3]}"):
                    cursor.execute("SELECT item_details, unit_price, quantity FROM quotation_items WHERE quote_ref = ?", (q[0],))
                    q_items = cursor.fetchall()
                    st.dataframe([{
                        "Item Description": i[0], 
                        f"Unit Price ({q[2]})": f"{i[1]:,.2f}", 
                        "Quantity": i[2], 
                        f"Line Total ({q[2]})": f"{i[1]*i[2]:,.2f}"
                    } for i in q_items], use_container_width=True)
        else:
            st.success("No pending quotations awaiting confirmation.")

    with dash_tab3:
        st.subheader("Successfully Fulfilled LPOs")
        cursor.execute("SELECT lpo_number, client_name, currency, delivery_schedule FROM lpos WHERE status = 'Fulfilled'")
        fulfilled_lpos = cursor.fetchall()
        if fulfilled_lpos:
            st.dataframe(
                [{"LPO Number": f[0], "Client Name": f[1], "Currency": f[2], "Delivery Schedule": f[3]} for f in fulfilled_lpos],
                use_container_width=True
            )
        else:
            st.info("No completed LPOs recorded yet.")

# ==========================================
# 2. MANAGE QUOTATIONS
# ==========================================
elif menu == "📝 Manage Quotations":
    st.title("📝 Quotation Management Suite")
    st.markdown("Create and manage multi-currency quotations with multiple line items.")
    
    tab1, tab2 = st.tabs(["Create Quotation", "View / Edit Quotations"])

    with tab1:
        st.subheader("New Commercial Quotation Form")
        with st.form("create_quote_form"):
            col1, col2 = st.columns(2)
            with col1:
                q_ref = st.text_input("Quotation Reference (e.g., QT-2026-001)")
                client = st.text_input("Client Name")
                currency = st.selectbox("Select Currency", CURRENCIES)
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
                it_price = cols[1].number_input(f"Unit Price #{i+1}", min_value=0.0, step=10.0, key=f"price_{i}")
                it_qty = cols[2].number_input(f"Qty #{i+1}", min_value=1, value=1, key=f"qty_{i}")
                item_data.append((it_name, it_price, it_qty))

            submitted = st.form_submit_button("Save Quotation")
            if submitted:
                if not q_ref.strip() or not client.strip():
                    st.error("Please enter a valid Quotation Reference and Client Name.")
                else:
                    try:
                        cursor.execute('''
                            INSERT INTO quotations (quote_ref, client_name, currency, pricing_terms, payment_terms, validity_date, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'Active')
                        ''', (q_ref, client, currency, pricing_terms, payment_terms, str(validity_date)))

                        for it_name, it_price, it_qty in item_data:
                            if it_name.strip():
                                cursor.execute('''
                                    INSERT INTO quotation_items (quote_ref, item_details, unit_price, quantity)
                                    VALUES (?, ?, ?, ?)
                                ''', (q_ref, it_name, it_price, it_qty))

                        conn.commit()
                        st.success(f"Quotation '{q_ref}' successfully saved in {currency}!")
                    except sqlite3.IntegrityError:
                        st.error(f"Error: Quotation reference '{q_ref}' already exists. Duplication prevented!")

    with tab2:
        st.subheader("Existing Quotations Database")
        cursor.execute("SELECT quote_ref, client_name, currency, pricing_terms, payment_terms, validity_date, status FROM quotations")
        all_quotes = cursor.fetchall()
        
        if all_quotes:
            for q in all_quotes:
                with st.expander(f"Ref: {q[0]} | Client: {q[1]} | Currency: {q[2]} | Status: {q[6]}"):
                    st.write(f"**Pricing Terms:** {q[3]} | **Payment Terms:** {q[4]} | **Valid Until:** {q[5]}")
                    cursor.execute("SELECT item_details, unit_price, quantity FROM quotation_items WHERE quote_ref = ?", (q[0],))
                    items = cursor.fetchall()
                    st.dataframe([{
                        "Item": i[0], 
                        f"Unit Price ({q[2]})": f"{i[1]:,.2f}", 
                        "Qty": i[2], 
                        f"Total ({q[2]})": f"{i[1]*i[2]:,.2f}"
                    } for i in items], use_container_width=True)
        else:
            st.info("No quotations found.")

# ==========================================
# 3. LPO & DELIVERIES
# ==========================================
elif menu == "📦 LPO & Deliveries":
    st.title("📦 LPO Tracking, Schedules & Deliveries")
    st.markdown("Convert quotations into LPOs, track delivery schedules, and record running item balances.")

    tab1, tab2, tab3 = st.tabs(["Create LPO", "Record Delivery", "Edit LPO Quantities"])

    with tab1:
        st.subheader("Convert Active Quotation to LPO")
        cursor.execute("SELECT quote_ref, currency FROM quotations WHERE status = 'Active'")
        active_quotes_data = cursor.fetchall()
        active_quotes = [row[0] for row in active_quotes_data