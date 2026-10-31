import sqlite3
from datetime import datetime

class OrderManagementSystem:
    def __init__(self, db_name="business_tracker.db", company_name="MY COMPANY NAME LLC", company_address="123 Business Ave, Suite 100 | Phone: +1 234 567 8900 | Email: info@mycompany.com"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.company_name = company_name
        self.company_address = company_address
        self.create_tables()

    def create_tables(self):
        """Creates the necessary database tables if they don't exist."""
        self.cursor.execute('''
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

        self.cursor.execute('''
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

        self.cursor.execute('''
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

        self.cursor.execute('''
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
        self.conn.commit()

    # --- 1. QUOTATION TRACKING & EDITING ---
    def create_quotation(self, quote_ref, client_name, item_details, unit_price, quantity, pricing_terms, payment_terms, validity_date):
        self.cursor.execute("SELECT id FROM quotations WHERE quote_ref = ?", (quote_ref,))
        if self.cursor.fetchone():
            print(f"❌ Error: Quotation reference '{quote_ref}' already exists. Duplication prevented.")
            return False

        try:
            self.cursor.execute('''
                INSERT INTO quotations (quote_ref, client_name, item_details, unit_price, quantity, pricing_terms, payment_terms, validity_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')
            ''', (quote_ref, client_name, item_details, unit_price, quantity, pricing_terms, payment_terms, validity_date))
            self.conn.commit()
            print(f"✅ Quotation '{quote_ref}' successfully created.")
            return True
        except Exception as e:
            print(f"❌ Error creating quotation: {e}")
            return False

    def edit_quotation(self, quote_ref, client_name=None, item_details=None, unit_price=None, quantity=None, pricing_terms=None, payment_terms=None, validity_date=None, status=None):
        self.cursor.execute("SELECT * FROM quotations WHERE quote_ref = ?", (quote_ref,))
        row = self.cursor.fetchone()
        if not row:
            print(f"❌ Error: Quotation '{quote_ref}' not found.")
            return False

        client_name = client_name or row[2]
        item_details = item_details or row[3]
        unit_price = unit_price if unit_price is not None else row[4]
        quantity = quantity if quantity is not None else row[5]
        pricing_terms = pricing_terms or row[6]
        payment_terms = payment_terms or row[7]
        validity_date = validity_date or row[8]
        status = status or row[9]

        try:
            self.cursor.execute('''
                UPDATE quotations 
                SET client_name = ?, item_details = ?, unit_price = ?, quantity = ?, pricing_terms = ?, payment_terms = ?, validity_date = ?, status = ?
                WHERE quote_ref = ?
            ''', (client_name, item_details, unit_price, quantity, pricing_terms, payment_terms, validity_date, status, quote_ref))
            self.conn.commit()
            print(f"✏️ Quotation '{quote_ref}' successfully updated.")
            return True
        except Exception as e:
            print(f"❌ Error updating quotation: {e}")
            return False

    def view_quotations(self):
        self.cursor.execute("SELECT * FROM quotations")
        rows = self.cursor.fetchall()
        print("\n--- QUOTATIONS ---")
        for row in rows:
            print(f"Ref: {row[1]} | Client: {row[2]} | Item: {row[3]} | Qty: {row[5]} | Price: ${row[4]} | Valid Until: {row[8]} | Status: {row[9]}")

    # --- 2. LPO & DELIVERY TRACKING & EDITING ---
    def create_lpo(self, lpo_number, quote_ref, delivery_schedule, payment_terms, items):
        self.cursor.execute("SELECT client_name, validity_date FROM quotations WHERE quote_ref = ?", (quote_ref,))
        quote = self.cursor.fetchone()
        if not quote:
            print(f"❌ Error: Quotation reference '{quote_ref}' not found.")
            return False
        
        client_name = quote[0]
        try:
            self.cursor.execute('''
                INSERT INTO lpos (lpo_number, quote_ref, client_name, delivery_schedule, payment_terms, status)
                VALUES (?, ?, ?, ?, ?, 'Open')
            ''', (lpo_number, quote_ref, client_name, delivery_schedule, payment_terms))

            for item_name, ordered_qty in items.items():
                self.cursor.execute('''
                    INSERT INTO lpo_items (lpo_number, item_name, ordered_qty, delivered_qty, balance_qty)
                    VALUES (?, ?, ?, 0, ?)
                ''', (lpo_number, item_name, ordered_qty, ordered_qty))

            # Automatically mark quotation status as 'Confirmed' once an LPO is generated from it
            self.cursor.execute("UPDATE quotations SET status = 'Confirmed' WHERE quote_ref = ?", (quote_ref,))

            self.conn.commit()
            print(f"✅ LPO '{lpo_number}' created successfully (Quotation '{quote_ref}' marked as Confirmed).")
            return True
        except Exception as e:
            print(f"❌ Error creating LPO: {e}")
            return False

    def edit_lpo_item_quantity(self, lpo_number, item_name, new_ordered_qty):
        self.cursor.execute('''
            SELECT ordered_qty, delivered_qty FROM lpo_items 
            WHERE lpo_number = ? AND item_name = ?
        ''', (lpo_number, item_name))
        item = self.cursor.fetchone()

        if not item:
            print(f"❌ Error: Item '{item_name}' not found under LPO '{lpo_number}'.")
            return False

        _, current_delivered = item
        if new_ordered_qty < current_delivered:
            print(f"❌ Error: New ordered quantity ({new_ordered_qty}) cannot be less than delivered quantity ({current_delivered}).")
            return False

        new_balance = new_ordered_qty - current_delivered
        try:
            self.cursor.execute('''
                UPDATE lpo_items 
                SET ordered_qty = ?, balance_qty = ? 
                WHERE lpo_number = ? AND item_name = ?
            ''', (new_ordered_qty, new_balance, lpo_number, item_name))
            self.conn.commit()
            print(f"✏️ LPO item '{item_name}' corrected. New Ordered Qty: {new_ordered_qty}, Balance: {new_balance}")
            return True
        except Exception as e:
            print(f"❌ Error updating LPO item quantity: {e}")
            return False

    def record_delivery(self, lpo_number, item_name, qty_delivered):
        self.cursor.execute('''
            SELECT ordered_qty, delivered_qty FROM lpo_items 
            WHERE lpo_number = ? AND item_name = ?
        ''', (lpo_number, item_name))
        item = self.cursor.fetchone()

        if not item:
            print(f"❌ Error: Item '{item_name}' not found under LPO '{lpo_number}'.")
            return

        ordered, current_delivered = item
        new_delivered = current_delivered + qty_delivered
        new_balance = ordered - new_delivered

        if new_balance < 0:
            print(f"❌ Error: Delivered quantity exceeds ordered quantity for '{item_name}'.")
            return

        self.cursor.execute('''
            UPDATE lpo_items 
            SET delivered_qty = ?, balance_qty = ? 
            WHERE lpo_number = ? AND item_name = ?
        ''', (new_delivered, new_balance, lpo_number, item_name))
        
        # Check if entire LPO is fulfilled
        self.cursor.execute("SELECT SUM(balance_qty) FROM lpo_items WHERE lpo_number = ?", (lpo_number,))
        total_balance = self.cursor.fetchone()[0]
        if total_balance == 0:
            self.cursor.execute("UPDATE lpos SET status = 'Fulfilled' WHERE lpo_number = ?", (lpo_number,))

        self.conn.commit()
        print(f"📦 Delivery recorded for '{item_name}': +{qty_delivered}. New Balance: {new_balance}")

    def track_lpo_deliveries(self, lpo_number):
        self.cursor.execute("SELECT * FROM lpos WHERE lpo_number = ?", (lpo_number,))
        lpo = self.cursor.fetchone()
        if not lpo:
            print(f"❌ LPO '{lpo_number}' not found.")
            return

        print(f"\n--- LPO STATUS: {lpo[1]} (Client: {lpo[3]}) ---")
        print(f"Delivery Schedule: {lpo[4]} | Payment Terms: {lpo[5]} | Status: {lpo[6]}")
        
        self.cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (lpo_number,))
        items = self.cursor.fetchall()
        print("Items Breakdown:")
        for item in items:
            print(f"  • {item[0]} | Ordered: {item[1]} | Delivered: {item[2]} | Balance: {item[3]}")

    # --- 3. PAYMENT TERM TRACKING & EDITING ---
    def add_payment_schedule(self, lpo_number, term_description, due_date, amount):
        try:
            self.cursor.execute('''
                INSERT INTO payments (lpo_number, term_description, due_date, amount, status)
                VALUES (?, ?, ?, ?, 'Pending')
            ''', (lpo_number, term_description, due_date, amount))
            self.conn.commit()
            print(f"💰 Payment term added for LPO '{lpo_number}': {term_description} (${amount}) due on {due_date}")
        except Exception as e:
            print(f"❌ Error adding payment schedule: {e}")

    def edit_payment_term(self, payment_id, term_description=None, due_date=None, amount=None, status=None):
        self.cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        p = self.cursor.fetchone()
        if not p:
            print(f"❌ Error: Payment ID {payment_id} not found.")
            return False

        term_description = term_description or p[2]
        due_date = due_date or p[3]
        amount = amount if amount is not None else p[4]
        status = status or p[5]

        try:
            self.cursor.execute('''
                UPDATE payments 
                SET term_description = ?, due_date = ?, amount = ?, status = ?
                WHERE id = ?
            ''', (term_description, due_date, amount, status, payment_id))
            self.conn.commit()
            print(f"✏️ Payment ID {payment_id} successfully updated.")
            return True
        except Exception as e:
            print(f"❌ Error updating payment term: {e}")
            return False

    def track_payments(self, lpo_number):
        self.cursor.execute("SELECT id, term_description, due_date, amount, status FROM payments WHERE lpo_number = ?", (lpo_number,))
        payments = self.cursor.fetchall()
        print(f"\n--- PAYMENT TERMS FOR LPO: {lpo_number} ---")
        for p in payments:
            print(f"ID: {p[0]} | Term: {p[1]} | Due: {p[2]} | Amount: ${p[3]} | Status: {p[4]}")

    # --- 4. BUSINESS DASHBOARD ---
    def show_dashboard(self):
        """Displays an operational dashboard showing Pending LPOs, Completed LPOs, and Pending Quotations."""
        print("\n" + "=" * 90)
        print(f" {self.company_name} - EXECUTIVE BUSINESS DASHBOARD ".center(90, "="))
        print("=" * 90)

        # 1. Pending Quotations Awaiting Confirmation
        print("\n⏳ PENDING QUOTATIONS (Awaiting LPO Confirmation):")
        print("-" * 90)
        self.cursor.execute("SELECT quote_ref, client_name, item_details, quantity, validity_date FROM quotations WHERE status = 'Active'")
        pending_quotes = self.cursor.fetchall()
        if not pending_quotes:
            print("  (No pending quotations found)")
        else:
            print(f"{'Quote Ref':<15} | {'Client Name':<20} | {'Item Details':<25} | {'Qty':<5} | {'Valid Until'}")
            print("-" * 90)
            for q in pending_quotes:
                print(f"{q[0]:<15} | {q[1]:<20} | {q[2]:<25} | {q[3]:<5} | {q[4]}")

        # 2. Pending / Open LPOs
        print("\n📦 PENDING / OPEN LPOS (Active Deliveries & Balances):")
        print("-" * 90)
        self.cursor.execute("SELECT lpo_number, client_name, delivery_schedule, payment_terms FROM lpos WHERE status = 'Open'")
        open_lpos = self.cursor.fetchall()
        if not open_lpos:
            print("  (No open LPOs found)")
        else:
            for lpo in open_lpos:
                print(f"• LPO: {lpo[0]} | Client: {lpo[1]} | Schedule: {lpo[2]} | Terms: {lpo[3]}")
                # Fetch item breakdown and balances
                self.cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (lpo[0],))
                items = self.cursor.fetchall()
                for item in items:
                    print(f"    - [{item[0]}] -> Ordered: {item[1]} | Delivered: {item[2]} | Balance Remaining: {item[3]}")

        # 3. Completed / Fulfilled LPOs
        print("\n✅ COMPLETED / FULFILLED LPOS:")
        print("-" * 90)
        self.cursor.execute("SELECT lpo_number, client_name, delivery_schedule FROM lpos WHERE status = 'Fulfilled'")
        fulfilled_lpos = self.cursor.fetchall()
        if not fulfilled_lpos:
            print("  (No completed LPOs found)")
        else:
            print(f"{'LPO Number':<15} | {'Client Name':<25} | {'Delivery Schedule'}")
            print("-" * 90)
            for f in fulfilled_lpos:
                print(f"{f[0]:<15} | {f[1]:<25} | {f[2]}")

        print("=" * 90 + "\n")

    # --- 5. PRINTING / DOCUMENT GENERATION ON LETTERHEAD ---
    def generate_letterhead(self):
        return f"""
================================================================================
{self.company_name.center(80)}
{self.company_address.center(80)}
================================================================================
"""

    def print_delivery_note(self, lpo_number, filename=None):
        self.cursor.execute("SELECT lpo_number, client_name, delivery_schedule FROM lpos WHERE lpo_number = ?", (lpo_number,))
        lpo = self.cursor.fetchone()
        if not lpo:
            print(f"❌ LPO '{lpo_number}' not found.")
            return

        self.cursor.execute("SELECT item_name, ordered_qty, delivered_qty, balance_qty FROM lpo_items WHERE lpo_number = ?", (lpo_number,))
        items = self.cursor.fetchall()

        doc = self.generate_letterhead()
        doc += f"\nDELIVERY NOTE\n".center(80)
        doc += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        doc += f"LPO Reference: {lpo[0]}\n"
        doc += f"Client Name:   {lpo[1]}\n"
        doc += f"Delivery Date: {lpo[2]}\n"
        doc += "-" * 80 + "\n"
        doc += f"{'Item Description':<35} | {'Ordered':<8} | {'Delivered':<10} | {'Balance':<8}\n"
        doc += "-" * 80 + "\n"

        for item in items:
            doc += f"{item[0]:<35} | {item[1]:<8} | {item[2]:<10} | {item[3]:<8}\n"

        doc += "-" * 80 + "\n\n\n"
        doc += "Receiver's Signature: ______________________    Company Stamp:\n\n"
        doc += "Name: ______________________________________    ____________________\n"

        file_name = filename or f"Delivery_Note_{lpo_number}.txt"
        with open(file_name, "w") as f:
            f.write(doc)
        print(f"📄 Delivery Note saved to '{file_name}'.")

    def print_warranty_document(self, lpo_number, warranty_period="1 Year", filename=None):
        self.cursor.execute("SELECT lpo_number, client_name FROM lpos WHERE lpo_number = ?", (lpo_number,))
        lpo = self.cursor.fetchone()
        if not lpo:
            print(f"❌ LPO '{lpo_number}' not found.")
            return

        self.cursor.execute("SELECT item_name, delivered_qty FROM lpo_items WHERE lpo_number = ? AND delivered_qty > 0", (lpo_number,))
        items = self.cursor.fetchall()

        doc = self.generate_letterhead()
        doc += f"\nCERTIFICATE OF WARRANTY\n".center(80)
        doc += f"Issue Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        doc += f"This document certifies that products supplied under LPO: **{lpo[0]}**\n"
        doc += f"for client **{lpo[1]}** are covered under warranty.\n\n"
        doc += f"Warranty Duration: {warranty_period}\n"
        doc += "-" * 80 + "\n"
        doc += f"{'Covered Item Description':<50} | {'Quantity Covered':<15}\n"
        doc += "-" * 80 + "\n"

        for item in items:
            doc += f"{item[0]:<50} | {item[1]:<15}\n"

        doc += "-" * 80 + "\n\n"
        doc += "Terms & Conditions:\n"
        doc += "1. Covers manufacturing defects under normal usage.\n\n\n"
        doc += "Authorized Signature: ______________________\n"
        doc += f"For {self.company_name}\n"

        file_name = filename or f"Warranty_Doc_{lpo_number}.txt"
        with open(file_name, "w") as f:
            f.write(doc)
        print(f"📜 Warranty Document saved to '{file_name}'.")

    def close(self):
        self.conn.close()


# --- EXAMPLE WORKFLOW DEMO WITH DASHBOARD ---
if __name__ == "__main__":
    oms = OrderManagementSystem()

    # 1. Create a couple of quotations (Some will become LPOs, some will stay pending)
    oms.create_quotation("QT-2026-101", "Beta Ltd", "Cloud Hosting Subscriptions", 150.00, 10, "Monthly Fixed", "Net 30", "2026-08-30")
    oms.create_quotation("QT-2026-102", "Gamma Corp", "Cybersecurity Software Licenses", 300.00, 50, "Annual Bulk", "Net 60", "2026-09-15")

    # 2. Turn Quotation 101 into an LPO (leaving 102 as a pending quotation)
    oms.create_lpo(
        lpo_number="LPO-7711",
        quote_ref="QT-2026-101",
        delivery_schedule="2026-07-10",
        payment_terms="Net 30",
        items={"Cloud Hosting Subscriptions": 10}
    )

    # 3. Partially fulfill LPO-7711
    oms.record_delivery("LPO-7711", "Cloud Hosting Subscriptions", 4) # Leaves balance of 6 (Still Open/Pending)

    # 4. View the Executive Dashboard
    oms.show_dashboard()

    oms.close()