import streamlit as st
import sqlite3
from datetime import datetime

# --- DATABASE SETUP ---
def get_connection():
    # check_same_thread=False allows Streamlit to handle SQLite across threads safely
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
            item_details TEXT,
            unit_price REAL,
            quantity INTEGER,
            pricing_terms TEXT,
            payment_terms TEXT,
            validity_date TEXT,
            status TEXT DEFAULT 'Active'
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
st.set_page_config(page_title="Order & Quotation Management System", layout="wide")

COMPANY_NAME = "MY COMPANY NAME LLC"
COMPANY_ADDRESS = "123 Business Ave, Suite 100 | Phone: +1 234 567 8900 | Email: info@mycompany.com"

st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Go to", [
    "📊 Executive Dashboard", 
    "📝 Manage Quotations", 
    "📦 LPO & Deliveries", 
    "💰 Payment Tracking", 
    "🖨️ Print Documents"
])

conn = get_connection()
cursor = conn.cursor()

# ==========================================
# 1. EXECUTIVE DASHBOARD
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Business Dashboard")
    st.markdown(f"**Company:** {COMPANY_NAME}")
    st.markdown("---")

    # Metrics overview
    cursor.execute("SELECT COUNT(*) FROM quotations WHERE status = 'Active'")
    pending_quotes_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Open'")
    open_lpos_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lpos WHERE status = 'Fulfilled'")
    fulfilled_lpos_count = cursor.fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Pending Quotations", pending_quotes_count)
    col2.metric("Open / Pending LPOs", open_lpos_count)
    col3.metric("Completed LPOs", fulfilled_lpos_count)
    st.markdown("---")

    # Section 1: Pending Quotations
    st.subheader("⏳ Pending Quotations (Awaiting LPO Confirmation)")
    cursor.execute("SELECT quote_ref, client_name, item_details, quantity, unit_price, validity_date FROM quotations WHERE status = 'Active'")
    pending_quotes = cursor.fetchall()
    if pending_quotes:
        st.dataframe(
            [{"Quote Ref": q[0], "Client": q[1], "Item": q[2], "Qty": q[3], "Unit Price ($)": q[4], "Valid Until": q[5]} for q in pending_quotes],
            use_container_width=True
        )
    else:
        st.info("No pending quotations found.")

    # Section 2: Open LPOs
    st.subheader("📦 Pending / Open LPOs (Active Deliveries & Balances)")
    cursor.execute("SELECT lpo_number, client_name, delivery_schedule, payment_terms FROM lpos WHERE status = 'Open'")
    open_lpos = cursor.fetchall()
    if open_lpos:
        for lpo in open_lpos:
            with st.expander(f"LPO: {lpo[0]} | Client: {lpo[1]} | Schedule: {lpo[2]}"):
                st.write(f"**Payment Terms:** {lpo[3]}")
                cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (lpo[0],))
                items = cursor.fetchall()
                st.dataframe(
                    [{"Item": i[0], "Ordered": i[1], "Delivered": i[2], "Balance Remaining": i[3]} for i in items],
                    use_container_width=True
                )
    else:
        st.info("No open LPOs found.")

    # Section 3: Fulfilled LPOs
    st.subheader("✅ Completed / Fulfilled LPOs")
    cursor.execute("SELECT lpo_number, client_name, delivery_schedule FROM lpos WHERE status = 'Fulfilled'")
    fulfilled_lpos = cursor.fetchall()
    if fulfilled_lpos:
        st.dataframe(
            [{"LPO Number": f[0], "Client": f[1], "Delivery Schedule": f[2]} for f in fulfilled_lpos],
            use_container_width=True
        )
    else:
        st.info("No completed LPOs found.")

# ==========================================
# 2. MANAGE QUOTATIONS
# ==========================================
elif menu == "📝 Manage Quotations":
    st.title("📝 Quotation Management & Editing")
    
    tab1, tab2 = st.tabs(["Create Quotation", "View / Edit Quotations"])

    with tab1:
        st.subheader("Create New Quotation (Duplication Protected)")
        with st.form("create_quote_form"):
            q_ref = st.text_input("Quotation Reference (e.g., QT-2026-001)")
            client = st.text_input("Client Name")
            item_details = st.text_input("Item Details / Description")
            unit_price = st.number_input("Unit Price ($)", min_value=0.0, step=10.0)
            quantity = st.number_input("Quantity", min_value=1, step=1)
            pricing_terms = st.text_input("Pricing Terms", value="Fixed pricing")
            payment_terms = st.text_input("Payment Terms", value="Net 30")
            validity_date = st.date_input("Validity Date")

            submitted = st.form_submit_button("Save Quotation")
            if submitted:
                try:
                    cursor.execute('''
                        INSERT INTO quotations (quote_ref, client_name, item_details, unit_price, quantity, pricing_terms, payment_terms, validity_date, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')
                    ''', (q_ref, client, item_details, unit_price, quantity, pricing_terms, payment_terms, str(validity_date)))
                    conn.commit()
                    st.success(f"Quotation '{q_ref}' created successfully!")
                except sqlite3.IntegrityError:
                    st.error(f"Error: Quotation reference '{q_ref}' already exists. Duplication prevented!")

    with tab2:
        st.subheader("Existing Quotations & Corrections")
        cursor.execute("SELECT * FROM quotations")
        all_quotes = cursor.fetchall()
        
        if all_quotes:
            st.dataframe([{
                "ID": r[0], "Ref": r[1], "Client": r[2], "Item": r[3], 
                "Price": r[4], "Qty": r[5], "Valid Until": r[8], "Status": r[9]
            } for r in all_quotes], use_container_width=True)

            st.markdown("### Edit / Correct Quotation")
            selected_ref = st.selectbox("Select Quotation Ref to Edit", [r[1] for r in all_quotes])
            
            cursor.execute("SELECT * FROM quotations WHERE quote_ref = ?", (selected_ref,))
            q_data = cursor.fetchone()

            with st.form("edit_quote_form"):
                new_client = st.text_input("Client Name", value=q_data[2])
                new_item = st.text_input("Item Details", value=q_data[3])
                new_price = st.number_input("Unit Price ($)", value=float(q_data[4]))
                new_qty = st.number_input("Quantity", value=int(q_data[5]))
                new_pricing = st.text_input("Pricing Terms", value=q_data[6])
                new_payment = st.text_input("Payment Terms", value=q_data[7])
                new_status = st.selectbox("Status", ["Active", "Confirmed", "Cancelled"], index=0 if q_data[9]=="Active" else 1)

                update_btn = st.form_submit_button("Update Quotation")
                if update_btn:
                    cursor.execute('''
                        UPDATE quotations 
                        SET client_name = ?, item_details = ?, unit_price = ?, quantity = ?, pricing_terms = ?, payment_terms = ?, status = ?
                        WHERE quote_ref = ?
                    ''', (new_client, new_item, new_price, new_qty, new_pricing, new_payment, new_status, selected_ref))
                    conn.commit()
                    st.success(f"Quotation '{selected_ref}' updated successfully!")
                    st.rerun()

# ==========================================
# 3. LPO & DELIVERIES
# ==========================================
elif menu == "📦 LPO & Deliveries":
    st.title("📦 LPO Tracking, Schedules & Deliveries")

    tab1, tab2, tab3 = st.tabs(["Create LPO", "Record Delivery", "Edit LPO Quantities"])

    with tab1:
        st.subheader("Convert Quotation to LPO")
        cursor.execute("SELECT quote_ref FROM quotations WHERE status = 'Active'")
        active_quotes = [row[0] for row in cursor.fetchall()]

        if not active_quotes:
            st.warning("No active quotations available to build an LPO from.")
        else:
            with st.form("create_lpo_form"):
                lpo_num = st.text_input("LPO Number (e.g., LPO-9988)")
                selected_quote = st.selectbox("Select Quotation Reference", active_quotes)
                delivery_sched = st.date_input("Delivery Schedule Date")
                lpo_payment_terms = st.text_input("LPO Payment Terms", value="Net 30")
                
                st.markdown("---")
                st.markdown("**LPO Item Setup**")
                item_name = st.text_input("Item Name / Description")
                ordered_qty = st.number_input("Ordered Quantity", min_value=1, value=1)

                lpo_submit = st.form_submit_button("Generate LPO")
                if lpo_submit:
                    try:
                        cursor.execute("SELECT client_name FROM quotations WHERE quote_ref = ?", (selected_quote,))
                        client_name = cursor.fetchone()[0]

                        cursor.execute('''
                            INSERT INTO lpos (lpo_number, quote_ref, client_name, delivery_schedule, payment_terms, status)
                            VALUES (?, ?, ?, ?, ?, 'Open')
                        ''', (lpo_num, selected_quote, client_name, str(delivery_sched), lpo_payment_terms))

                        cursor.execute('''
                            INSERT INTO lpo_items (lpo_number, item_name, ordered_qty, delivered_qty, balance_qty)
                            VALUES (?, ?, ?, 0, ?)
                        ''', (lpo_num, item_name, ordered_qty, ordered_qty))

                        cursor.execute("UPDATE quotations SET status = 'Confirmed' WHERE quote_ref = ?", (selected_quote,))
                        conn.commit()
                        st.success(f"LPO '{lpo_num}' created successfully!")
                    except sqlite3.IntegrityError:
                        st.error(f"Error: LPO Number '{lpo_num}' already exists.")

    with tab2:
        st.subheader("Record Delivery & Track Balance")
        cursor.execute("SELECT lpo_number FROM lpos WHERE status = 'Open'")
        open_lpos = [row[0] for row in cursor.fetchall()]

        if not open_lpos:
            st.info("No open LPOs available for delivery tracking.")
        else:
            selected_lpo = st.selectbox("Select Open LPO", open_lpos)
            
            cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (selected_lpo,))
            items = cursor.fetchall()

            for item in items:
                st.write(f"**Item:** {item[0]} | Ordered: {item[1]} | Delivered: {item[2]} | **Balance:** {item[3]}")

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
                        
                        # Check if fully fulfilled
                        cursor.execute("SELECT SUM(balance_qty) FROM lpo_items WHERE lpo_number = ?", (selected_lpo,))
                        total_bal = cursor.fetchone()[0]
                        if total_bal == 0:
                            cursor.execute("UPDATE lpos SET status = 'Fulfilled' WHERE lpo_number = ?", (selected_lpo,))
                        
                        conn.commit()
                        st.success(f"Delivery logged! New balance for {item_to_deliver}: {new_bal}")
                        st.rerun()

    with tab3:
        st.subheader("Correct / Edit LPO Ordered Quantities")
        cursor.execute("SELECT lpo_number FROM lpos")
        all_lpos = [row[0] for row in cursor.fetchall()]
        if all_lpos:
            edit_lpo = st.selectbox("Select LPO to Edit Items", all_lpos, key="edit_lpo_sel")
            cursor.execute("SELECT item_name, ordered_qty, delivered_qty FROM lpo_items WHERE lpo_number = ?", (edit_lpo,))
            lpo_itms = cursor.fetchall()

            with st.form("edit_lpo_qty_form"):
                target_item = st.selectbox("Select Item", [i[0] for i in lpo_itms])
                new_ordered = st.number_input("New Corrected Ordered Quantity", min_value=1, step=1)
                corr_sub = st.form_submit_button("Save Quantity Correction")

                if corr_sub:
                    # fetch current delivered
                    cursor.execute("SELECT delivered_qty FROM lpo_items WHERE lpo_number = ? AND item_name = ?", (edit_lpo, target_item))
                    current_del = cursor.fetchone()[0]
                    if new_ordered < current_del:
                        st.error(f"Cannot set ordered qty below already delivered quantity ({current_del}).")
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

    tab1, tab2 = st.tabs(["Add Payment Milestone", "Track & Update Payments"])

    cursor.execute("SELECT lpo_number FROM lpos")
    all_lpos = [row[0] for row in cursor.fetchall()]

    with tab1:
        st.subheader("Add Payment Milestone / Terms")
        if not all_lpos:
            st.warning("Create an LPO first.")
        else:
            with st.form("payment_schedule_form"):
                pay_lpo = st.selectbox("Select LPO Number", all_lpos)
                term_desc = st.text_input("Term Description (e.g., 50% Advance, Net 30)")
                due_date = st.date_input("Due Date")
                amount = st.number_input("Amount ($)", min_value=0.0, step=100.0)
                
                pay_sub = st.form_submit_button("Add Payment Milestone")
                if pay_sub:
                    cursor.execute('''
                        INSERT INTO payments (lpo_number, term_description, due_date, amount, status)
                        VALUES (?, ?, ?, ?, 'Pending')
                    ''', (pay_lpo, term_desc, str(due_date), amount))
                    conn.commit()
                    st.success("Payment milestone added successfully!")

    with tab2:
        st.subheader("Manage Payment Status & Corrections")
        if all_lpos:
            selected_pay_lpo = st.selectbox("Filter by LPO", all_lpos, key="pay_lpo_filter")
            cursor.execute("SELECT id, term_description, due_date, amount, status FROM payments WHERE lpo_number = ?", (selected_pay_lpo,))
            milestones = cursor.fetchall()

            if milestones:
                st.dataframe([{
                    "ID": m[0], "Milestone": m[1], "Due Date": m[2], "Amount ($)": m[3], "Status": m[4]
                } for m in milestones], use_container_width=True)

                st.markdown("### Update Status or Edit Milestone")
                m_id = st.selectbox("Select Milestone ID to Update", [m[0] for m in milestones])
                
                cursor.execute("SELECT term_description, due_date, amount, status FROM payments WHERE id = ?", (m_id,))
                m_data = cursor.fetchone()

                with st.form("edit_payment_form"):
                    e_desc = st.text_input("Description", value=m_data[0])
                    e_date = st.text_input("Due Date", value=m_data[1])
                    e_amt = st.number_input("Amount ($)", value=float(m_data[2]))
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
# 5. PRINT DOCUMENTS ON LETTERHEAD
# ==========================================
elif menu == "🖨️ Print Documents":
    st.title("🖨️ Generate & Print Documents on Letterhead")

    cursor.execute("SELECT lpo_number FROM lpos")
    lpo_list = [row[0] for row in cursor.fetchall()]

    if not lpo_list:
        st.warning("No LPOs available to print documents for.")
    else:
        doc_type = st.radio("Select Document Type", ["Delivery Note", "Warranty Certificate"])
        doc_lpo = st.selectbox("Select LPO Number", lpo_list)

        def make_letterhead():
            return f"""================================================================================
{COMPANY_NAME.center(80)}
{COMPANY_ADDRESS.center(80)}
================================================================================
"""

        if doc_type == "Delivery Note":
            if st.button("Generate Delivery Note Preview"):
                cursor.execute("SELECT client_name, delivery_schedule FROM lpos WHERE lpo_number = ?", (doc_lpo,))
                lpo_info = cursor.fetchone()
                cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (doc_lpo,))
                items_info = cursor.fetchall()

                doc_text = make_letterhead()
                doc_text += f"\nDELIVERY NOTE\n".center(80)
                doc_text += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
                doc_text += f"LPO Reference: {doc_lpo}\n"
                doc_text += f"Client Name:   {lpo_info[0]}\n"
                doc_text += f"Delivery Date: {lpo_info[1]}\n"
                doc_text += "-" * 80 + "\n"
                doc_text += f"{'Item Description':<35} | {'Ordered':<8} | {'Delivered':<10} | {'Balance':<8}\n"
                doc_text += "-" * 80 + "\n"
                for i in items_info:
                    doc_text += f"{i[0]:<35} | {i[1]:<8} | {i[2]:<10} | {i[3]:<8}\n"
                doc_text += "-" * 80 + "\n\n\nReceiver's Signature: ______________________    Company Stamp:\n"

                st.text_area("Printable Text Layout (Copy or Save):", doc_text, height=300)
                st.download_button("Download Delivery Note (.txt)", doc_text, file_name=f"Delivery_Note_{doc_lpo}.txt")

        elif doc_type == "Warranty Certificate":
            warranty_period = st.text_input("Warranty Duration", value="1 Year Standard Warranty")
            if st.button("Generate Warranty Certificate Preview"):
                cursor.execute("SELECT client_name FROM lpos WHERE lpo_number = ?", (doc_lpo,))
                client_name = cursor.fetchone()[0]
                cursor.execute("SELECT item_name, delivered_qty FROM lpo_items WHERE lpo_number = ?", (doc_lpo,))
                items_info = cursor.fetchall()

                doc_text = make_letterhead()
                doc_text += f"\nCERTIFICATE OF WARRANTY\n".center(80)
                doc_text += f"Issue Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                doc_text += f"This document certifies that products supplied under LPO: {doc_lpo}\n"
                doc_text += f"for client {client_name} are covered under warranty.\n\n"
                doc_text += f"Warranty Duration: {warranty_period}\n"
                doc_text += "-" * 80 + "\n"
                doc_text += f"{'Covered Item Description':<50} | {'Quantity Covered':<15}\n"
                doc_text += "-" * 80 + "\n"
                for i in items_info:
                    doc_text += f"{i[0]:<50} | {i[1]:<15}\n"
                doc_text += "-" * 80 + "\n\nTerms & Conditions:\n1. Covers manufacturing defects under normal usage.\n\n\nAuthorized Signature: ______________________\n"

                st.text_area("Printable Text Layout (Copy or Save):", doc_text, height=300)
                st.download_button("Download Warranty Document (.txt)", doc_text, file_name=f"Warranty_{doc_lpo}.txt")

conn.close()