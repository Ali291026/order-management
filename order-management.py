import streamlit as st
import sqlite3
from datetime import datetime
from fpdf import FPDF
import os
import pandas as pd
import io

# --- DATABASE SETUP ---
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
            currency TEXT DEFAULT 'USD',
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
            currency TEXT DEFAULT 'USD',
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

# Role-Based Navigation Options
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
# 1. EXECUTIVE DASHBOARD
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Business Dashboard")
    st.markdown("Real-time overview of active quotations, order fulfillments, deliveries, and pending billings.")
    st.markdown("---")

    cursor.execute("SELECT COUNT(*) FROM quotations WHERE status = 'Active'")
    pending_quotes_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Open'")
    open_lpos_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Fulfilled'")
    fulfilled_lpos_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'Pending'")
    total_pending_revenue = cursor.fetchone()[0] or 0.0

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
        active_quotes = [row[0] for row in active_quotes_data]

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
                        cursor.execute("SELECT client_name, currency FROM quotations WHERE quote_ref = ?", (selected_quote,))
                        q_info = cursor.fetchone()
                        client_name = q_info[0]
                        q_currency = q_info[1]

                        cursor.execute('''
                            INSERT INTO lpos (lpo_number, quote_ref, client_name, currency, delivery_schedule, payment_terms, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'Open')
                        ''', (lpo_num, selected_quote, client_name, q_currency, str(delivery_sched), lpo_payment_terms))

                        cursor.execute("SELECT item_details, quantity FROM quotation_items WHERE quote_ref = ?", (selected_quote,))
                        quote_items = cursor.fetchall()

                        for it_name, it_qty in quote_items:
                            cursor.execute('''
                                INSERT INTO lpo_items (lpo_number, item_name, ordered_qty, delivered_qty, balance_qty)
                                VALUES (?, ?, ?, 0, ?)
                            ''', (lpo_num, it_name, it_qty, it_qty))

                        cursor.execute("UPDATE quotations SET status = 'Confirmed' WHERE quote_ref = ?", (selected_quote,))
                        conn.commit()
                        st.success(f"LPO '{lpo_num}' successfully generated in {q_currency}!")
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
        cursor.execute("SELECT lpo_number FROM lpos")
        all_lpos = [row[0] for row in cursor.fetchall()]
        if all_lpos:
            edit_lpo = st.selectbox("Select LPO to Edit", all_lpos, key="edit_lpo_sel")
            cursor.execute("SELECT item_name, ordered_qty, delivered_qty FROM lpo_items WHERE lpo_number = ?", (edit_lpo,))
            lpo_itms = cursor.fetchall()

            with st.form("edit_lpo_qty_form"):
                target_item = st.selectbox("Select Item Line", [i[0] for i in lpo_itms])
                new_ordered = st.number_input("New Corrected Ordered Quantity", min_value=1, step=1)
                corr_sub = st.form_submit_button("Save Quantity Correction")

                if corr_sub:
                    cursor.execute("SELECT delivered_qty FROM lpo_items WHERE lpo_number = ? AND item_name = ?", (edit_lpo, target_item))
                    current_del = cursor.fetchone()[0]
                    if new_ordered < current_del:
                        st.error(f"Cannot set ordered quantity below already delivered units ({current_del}).")
                    else:
                        new_balance = new_ordered - current_del
                        cursor.execute("UPDATE lpo_items SET ordered_qty = ?, balance_qty = ? WHERE lpo_number = ? AND item_name = ?", 
                                       (new_ordered, new_balance, edit_lpo, target_item))
                        conn.commit()
                        st.success("LPO item quantity corrected successfully!")
                        st.rerun()

# ==========================================
# 4. PAYMENT TRACKING
# ==========================================
elif menu == "💰 Payment Tracking":
    st.title("💰 LPO Payment Terms & Milestone Tracking")
    st.markdown("Set up milestones, track advance payments, net terms, and update payment statuses.")

    tab1, tab2 = st.tabs(["Add Payment Milestone", "Track & Update Payments"])

    cursor.execute("SELECT lpo_number, currency FROM lpos")
    lpo_records = cursor.fetchall()
    all_lpos = [row[0] for row in lpo_records]

    with tab1:
        st.subheader("Add Payment Milestone")
        if not all_lpos:
            st.warning("Create an LPO first.")
        else:
            with st.form("payment_schedule_form"):
                pay_lpo = st.selectbox("Select LPO Number", all_lpos)
                
                cursor.execute("SELECT currency FROM lpos WHERE lpo_number = ?", (pay_lpo,))
                lpo_curr = cursor.fetchone()[0]
                
                term_desc = st.text_input("Term Description (e.g., 50% Advance, Net 30)")
                due_date = st.date_input("Due Date")
                amount = st.number_input(f"Amount ({lpo_curr})", min_value=0.0, step=100.0)
                
                pay_sub = st.form_submit_button("Add Milestone")
                if pay_sub:
                    cursor.execute('''
                        INSERT INTO payments (lpo_number, term_description, due_date, amount, status)
                        VALUES (?, ?, ?, ?, 'Pending')
                    ''', (pay_lpo, term_desc, str(due_date), amount))
                    conn.commit()
                    st.success("Payment milestone added successfully!")

    with tab2:
        st.subheader("Manage Payment Status")
        if all_lpos:
            selected_pay_lpo = st.selectbox("Filter by LPO", all_lpos, key="pay_lpo_filter")
            
            cursor.execute("SELECT currency FROM lpos WHERE lpo_number = ?", (selected_pay_lpo,))
            curr_row = cursor.fetchone()
            curr_symbol = curr_row[0] if curr_row else "USD"

            cursor.execute("SELECT id, term_description, due_date, amount, status FROM payments WHERE lpo_number = ?", (selected_pay_lpo,))
            milestones = cursor.fetchall()

            if milestones:
                st.dataframe([{
                    "ID": m[0], "Milestone": m[1], "Due Date": m[2], f"Amount ({curr_symbol})": f"{m[3]:,.2f}", "Status": m[4]
                } for m in milestones], use_container_width=True)

                st.markdown("### Update Milestone Record")
                m_id = st.selectbox("Select Milestone ID to Update", [m[0] for m in milestones])
                
                cursor.execute("SELECT term_description, due_date, amount, status FROM payments WHERE id = ?", (m_id,))
                m_data = cursor.fetchone()

                with st.form("edit_payment_form"):
                    e_desc = st.text_input("Description", value=m_data[0])
                    e_date = st.text_input("Due Date", value=m_data[1])
                    e_amt = st.number_input(f"Amount ({curr_symbol})", value=float(m_data[2]))
                    e_status = st.selectbox("Payment Status", ["Pending", "Paid"], index=0 if m_data[3]=="Pending" else 1)
                    
                    e_sub = st.form_submit_button("Save Payment Update")
                    if e_sub:
                        cursor.execute("UPDATE payments SET term_description = ?, due_date = ?, amount = ?, status = ? WHERE id = ?",
                                       (e_desc, e_date, e_amt, e_status, m_id))
                        conn.commit()
                        st.success("Payment record updated successfully!")
                        st.rerun()
            else:
                st.info("No payment terms recorded for this LPO.")

# ==========================================
# 5. REPORTS & ANALYTICS
# ==========================================
elif menu == "📈 Reports & Analytics":
    st.title("📈 Advanced Reporting & Filtered Exports")
    st.markdown("Filter records by module, status, or client name, and export data directly to **Excel (.xlsx)** or **PDF**.")

    report_type = st.selectbox("Select Report Category", ["Quotations Report", "LPO Status Report", "Payments & Billing Report"])

    st.markdown("---")
    st.subheader("🔍 Filter Options")

    col1, col2 = st.columns(2)
    
    cursor.execute("SELECT DISTINCT client_name FROM quotations UNION SELECT DISTINCT client_name FROM lpos")
    clients = [row[0] for row in cursor.fetchall() if row[0]]
    client_filter = col1.selectbox("Filter by Client Name", ["All Clients"] + clients)

    if report_type == "Quotations Report":
        status_filter = col2.selectbox("Filter by Status", ["All", "Active", "Confirmed", "Cancelled"])
        
        query = "SELECT quote_ref, client_name, currency, pricing_terms, payment_terms, validity_date, status FROM quotations WHERE 1=1"
        params = []
        if client_filter != "All Clients":
            query += " AND client_name = ?"
            params.append(client_filter)
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)
            
        cursor.execute(query, params)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["Quote Ref", "Client Name", "Currency", "Pricing Terms", "Payment Terms", "Validity Date", "Status"])

    elif report_type == "LPO Status Report":
        status_filter = col2.selectbox("Filter by LPO Status", ["All", "Open", "Fulfilled"])
        
        query = "SELECT lpo_number, quote_ref, client_name, currency, delivery_schedule, payment_terms, status FROM lpos WHERE 1=1"
        params = []
        if client_filter != "All Clients":
            query += " AND client_name = ?"
            params.append(client_filter)
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)
            
        cursor.execute(query, params)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["LPO Number", "Quote Ref", "Client Name", "Currency", "Delivery Schedule", "Payment Terms", "Status"])

    else:
        status_filter = col2.selectbox("Filter by Payment Status", ["All", "Pending", "Paid"])
        
        query = '''
            SELECT p.id, p.lpo_number, l.client_name, l.currency, p.term_description, p.due_date, p.amount, p.status 
            FROM payments p JOIN lpos l ON p.lpo_number = l.lpo_number WHERE 1=1
        '''
        params = []
        if client_filter != "All Clients":
            query += " AND l.client_name = ?"
            params.append(client_filter)
        if status_filter != "All":
            query += " AND p.status = ?"
            params.append(status_filter)
            
        cursor.execute(query, params)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["ID", "LPO Number", "Client Name", "Currency", "Term Description", "Due Date", "Amount", "Status"])

    st.markdown(f"**Filtered Results:** `{len(df)}` records found.")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📥 Export Filtered Data")

    col_ex1, col_ex2 = st.columns(2)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    excel_data = output.getvalue()

    col_ex1.download_button(
        label="📊 Download Excel Report (.xlsx)",
        data=excel_data,
        file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    class PDFReportSummary(FPDF):
        def header(self):
            if os.path.exists(LOGO_FILE):
                try:
                    self.image(LOGO_FILE, 10, 8, 25)
                except Exception:
                    pass
            self.set_font("Arial", "B", 13)
            self.cell(0, 6, COMPANY_NAME, 0, 1, "R")
            self.set_font("Arial", "", 8)
            self.cell(0, 4, COMPANY_ADDRESS, 0, 1, "R")
            self.ln(5)
            self.set_draw_color(200, 200, 200)
            self.line(10, 25, 200, 25)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    if col_ex2.button("📑 Generate Summary Report PDF"):
        pdf = PDFReportSummary()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, report_type.upper(), 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Generated On: {datetime.now().strftime('%Y-%m-%d')} | Filter: {client_filter}", 0, 1)
        pdf.ln(5)

        cols = df.columns.tolist()
        col_width = 190 / len(cols)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 9)
        for col in cols:
            pdf.cell(col_width, 8, str(col)[:15], 1, 0, "C", True)
        pdf.ln()

        pdf.set_font("Arial", "", 8)
        for row in data:
            for val in row:
                pdf.cell(col_width, 7, str(val)[:18], 1, 0, "C")
            pdf.ln()

        pdf_bytes = pdf.output(dest="S").encode("latin1")
        st.success("PDF Report generated successfully!")
        st.download_button("Download PDF Report", pdf_bytes, file_name=f"{report_type.replace(' ', '_')}.pdf", mime="application/pdf")

# ==========================================
# 6. USER MANAGEMENT (Admin Only)
# ==========================================
elif menu == "👥 User Management" and st.session_state.role == "Admin":
    st.title("👥 User Account Management")
    st.markdown("Create new user accounts and assign roles (`Admin`, `Sales`, `Finance`).")

    tab1, tab2 = st.tabs(["Create User", "View Users"])

    with tab1:
        with st.form("create_user_form"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("Password", type="password")
            new_role = st.selectbox("Assign Role", ["Admin", "Sales", "Finance"])
            
            user_sub = st.form_submit_button("Create User Account")
            if user_sub:
                if not new_user.strip() or not new_pass.strip():
                    st.error("Please provide both username and password.")
                else:
                    try:
                        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user.strip(), new_pass.strip(), new_role))
                        conn.commit()
                        st.success(f"User '{new_user}' created successfully with role '{new_role}'!")
                    except sqlite3.IntegrityError:
                        st.error(f"Error: Username '{new_user}' already exists.")

    with tab2:
        st.subheader("Registered System Users")
        cursor.execute("SELECT id, username, role FROM users")
        users_list = cursor.fetchall()
        st.dataframe([{"ID": u[0], "Username": u[1], "Role": u[2]} for u in users_list], use_container_width=True)

# ==========================================
# 7. PRINT DOCUMENTS ON LETTERHEAD
# ==========================================
elif menu == "🖨️ Print Documents":
    st.title("🖨️ Document Generation & Letterhead Printing")
    st.markdown("Instantly generate professional Quotations, Delivery Notes, and Warranty Certificates on company letterhead.")

    doc_type = st.radio("Select Document Type", ["Quotation", "Delivery Note", "Warranty Certificate"], horizontal=True)

    class PDFReport(FPDF):
        def header(self):
            if os.path.exists(LOGO_FILE):
                try:
                    self.image(LOGO_FILE, 10, 8, 25)
                except Exception:
                    pass
            
            self.set_font("Arial", "B", 13)
            self.cell(0, 6, COMPANY_NAME, 0, 1, "R")
            self.set_font("Arial", "", 8)
            self.cell(0, 4, COMPANY_ADDRESS, 0, 1, "R")
            self.ln(5)
            self.set_draw_color(200, 200, 200)
            self.line(10, 25, 200, 25)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    if doc_type == "Quotation":
        cursor.execute("SELECT quote_ref FROM quotations")
        quote_list = [row[0] for row in cursor.fetchall()]

        if not quote_list:
            st.warning("No quotations available to print.")
        else:
            doc_quote = st.selectbox("Select Quotation Reference", quote_list)
            if st.button("Generate Quotation PDF"):
                cursor.execute("SELECT client_name, currency, pricing_terms, payment_terms, validity_date FROM quotations WHERE quote_ref = ?", (doc_quote,))
                q_info = cursor.fetchone()
                q_client = q_info[0]
                q_currency = q_info[1]
                
                cursor.execute("SELECT item_details, unit_price, quantity FROM quotation_items WHERE quote_ref = ?", (doc_quote,))
                q_items = cursor.fetchall()

                pdf = PDFReport()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "COMMERCIAL QUOTATION", 0, 1, "C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"Quotation Reference: {doc_quote}", 0, 1)
                pdf.cell(0, 6, f"Client Name: {q_client}", 0, 1)
                pdf.cell(0, 6, f"Currency: {q_currency}", 0, 1)
                pdf.cell(0, 6, f"Valid Until: {q_info[4]}", 0, 1)
                pdf.cell(0, 6, f"Pricing Terms: {q_info[2]} | Payment Terms: {q_info[3]}", 0, 1)
                pdf.ln(5)

                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(90, 8, "Item Description", 1, 0, "L", True)
                pdf.cell(20, 8, "Qty", 1, 0, "C", True)
                pdf.cell(40, 8, f"Unit Price ({q_currency.split()[0]})", 1, 0, "R", True)
                pdf.cell(40, 8, f"Total ({q_currency.split()[0]})", 1, 1, "R", True)

                pdf.set_font("Arial", "", 10)
                grand_total = 0.0
                for item in q_items:
                    line_total = item[1] * item[2]
                    grand_total += line_total
                    pdf.cell(90, 8, str(item[0]), 1, 0, "L")
                    pdf.cell(20, 8, str(item[2]), 1, 0, "C")
                    pdf.cell(40, 8, f"{item[1]:,.2f}", 1, 0, "R")
                    pdf.cell(40, 8, f"{line_total:,.2f}", 1, 1, "R")

                pdf.set_font("Arial", "B", 10)
                pdf.cell(150, 8, f"Grand Total ({q_currency.split()[0]}):", 1, 0, "R")
                pdf.cell(40, 8, f"{grand_total:,.2f}", 1, 1, "R")
                pdf.ln(15)

                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, "Authorized Signature: ______________________", 0, 1)

                pdf_bytes = pdf.output(dest="S").encode("latin1")
                st.success("Quotation PDF generated successfully!")
                st.download_button("Download Quotation PDF", pdf_bytes, file_name=f"Quotation_{doc_quote}.pdf", mime="application/pdf")

    elif doc_type == "Delivery Note":
        cursor.execute("SELECT lpo_number FROM lpos")
        lpo_list = [row[0] for row in cursor.fetchall()]

        if not lpo_list:
            st.warning("No LPOs available to print delivery notes for.")
        else:
            doc_lpo = st.selectbox("Select LPO Number", lpo_list)
            if st.button("Generate Delivery Note PDF"):
                cursor.execute("SELECT client_name, currency, delivery_schedule FROM lpos WHERE lpo_number = ?", (doc_lpo,))
                lpo_info = cursor.fetchone()
                cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (doc_lpo,))
                items_info = cursor.fetchall()

                pdf = PDFReport()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "DELIVERY NOTE", 0, 1, "C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"LPO Reference: {doc_lpo}", 0, 1)
                pdf.cell(0, 6, f"Client Name: {lpo_info[0]}", 0, 1)
                pdf.cell(0, 6, f"Currency: {lpo_info[1]}", 0, 1)
                pdf.cell(0, 6, f"Delivery Date: {lpo_info[2]}", 0, 1)
                pdf.ln(5)

                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(90, 8, "Item Description", 1, 0, "L", True)
                pdf.cell(30, 8, "Ordered", 1, 0, "C", True)
                pdf.cell(35, 8, "Delivered", 1, 0, "C", True)
                pdf.cell(35, 8, "Balance", 1, 1, "C", True)

                pdf.set_font("Arial", "", 10)
                for i in items_info:
                    pdf.cell(90, 8, str(i[0]), 1, 0, "L")
                    pdf.cell(30, 8, str(i[1]), 1, 0, "C")
                    pdf.cell(35, 8, str(i[2]), 1, 0, "C")
                    pdf.cell(35, 8, str(i[3]), 1, 1, "C")

                pdf.ln(15)
                pdf.cell(0, 6, "Receiver's Signature: ______________________    Company Stamp: ______________", 0, 1)

                pdf_bytes = pdf.output(dest="S").encode("latin1")
                st.success("Delivery Note PDF generated successfully!")
                st.download_button("Download Delivery Note PDF", pdf_bytes, file_name=f"Delivery_Note_{doc_lpo}.pdf", mime="application/pdf")

    elif doc_type == "Warranty Certificate":
        cursor.execute("SELECT lpo_number FROM lpos")
        lpo_list = [row[0] for row in cursor.fetchall()]

        if not lpo_list:
            st.warning("No LPOs available to print warranty documents for.")
        else:
            doc_lpo = st.selectbox("Select LPO Number", lpo_list, key="warranty_lpo_sel")
            warranty_period = st.text_input("Warranty Duration", value="1 Year Standard Warranty")
            if st.button("Generate Warranty Certificate PDF"):
                cursor.execute("SELECT client_name, currency FROM lpos WHERE lpo_number = ?", (doc_lpo,))
                lpo_data = cursor.fetchone()
                client_name = lpo_data[0]
                lpo_curr = lpo_data[1]
                
                cursor.execute("SELECT item_name, delivered_qty FROM lpo_items WHERE lpo_number = ?", (doc_lpo,))
                items_info = cursor.fetchall()

                pdf = PDFReport()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "CERTIFICATE OF WARRANTY", 0, 1, "C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"LPO Reference: {doc_lpo} | Client: {client_name}", 0, 1)
                pdf.cell(0, 6, f"Currency: {lpo_curr} | Warranty Period: {warranty_period}", 0, 1)
                pdf.ln(5)

                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(130, 8, "Covered Item Description", 1, 0, "L", True)
                pdf.cell(60, 8, "Quantity Covered", 1, 1, "C", True)

                pdf.set_font("Arial", "", 10)
                for i in items_info:
                    pdf.cell(130, 8, str(i[0]), 1, 0, "L")
                    pdf.cell(60, 8, str(i[1]), 1, 1, "C")

                pdf.ln(10)
                pdf.set_font("Arial", "I", 9)
                pdf.multi_cell(0, 5, "Terms & Conditions:\n1. This warranty covers manufacturing defects under normal usage conditions.\n2. Physical damage or unauthorized repairs void this certificate.")
                pdf.ln(10)

                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, "Authorized Signature: ______________________", 0, 1)

                pdf_bytes = pdf.output(dest="S").encode("latin1")
                st.success("Warranty Certificate PDF generated successfully!")
                st.download_button("Download Warranty PDF", pdf_bytes, file_name=f"Warranty_{doc_lpo}.pdf", mime="application/pdf")

conn.close()