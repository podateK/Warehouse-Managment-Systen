import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="wms_database.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouse_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT DEFAULT 'PZ',
                date TEXT NOT NULL,
                number TEXT NOT NULL,
                original_number TEXT,
                contractor TEXT,
                receiver TEXT,
                value REAL,
                cost REAL,
                related_document TEXT
            )
        ''')
        
        try:
            cursor.execute("ALTER TABLE warehouse_data ADD COLUMN doc_type TEXT DEFAULT 'PZ'")
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute("ALTER TABLE warehouse_data ADD COLUMN receiver TEXT")
        except sqlite3.OperationalError:
            pass

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouse_receipt_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                name TEXT,
                quantity REAL,
                quantity_delivered REAL,
                unit TEXT,
                price_netto REAL,
                value_netto REAL,
                FOREIGN KEY(receipt_id) REFERENCES warehouse_data(id)
            )
        ''')
        
        try:
            cursor.execute("ALTER TABLE warehouse_receipt_items ADD COLUMN quantity_delivered REAL")
        except sqlite3.OperationalError:
            pass
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'admin', 1)")
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('user', 'user', 0)")

        conn.commit()
        conn.close()

    def check_login(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE username = ? AND password = ?', (username, password))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, bool(result[0])
        return False, False

    def add_receipt(self, doc_type, date, number, original_number, contractor, receiver, value, cost, related_document):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO warehouse_data (doc_type, date, number, original_number, contractor, receiver, value, cost, related_document)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (doc_type, date, number, original_number, contractor, receiver, value, cost, related_document))
        receipt_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return receipt_id

    def add_receipt_item(self, receipt_id, name, quantity, quantity_delivered, unit, price_netto, value_netto):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO warehouse_receipt_items (receipt_id, name, quantity, quantity_delivered, unit, price_netto, value_netto)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (receipt_id, name, quantity, quantity_delivered, unit, price_netto, value_netto))
        conn.commit()
        conn.close()

    
    def get_all_receipts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                d.id, d.doc_type, d.date, d.number, 
                GROUP_CONCAT(i.name || ' (' || i.quantity || ' ' || i.unit || ')', ', ') as items,
                d.original_number, d.contractor, d.value, d.cost, d.related_document, d.receiver
            FROM warehouse_data d
            LEFT JOIN warehouse_receipt_items i ON d.id = i.receipt_id
            GROUP BY d.id
            ORDER BY d.date DESC, d.id DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_inventory(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                i.name, 
                i.unit, 
                SUM(CASE WHEN d.doc_type = 'PZ' THEN i.quantity ELSE -i.quantity END) as quantity
            FROM warehouse_receipt_items i
            JOIN warehouse_data d ON i.receipt_id = d.id
            GROUP BY i.name, i.unit
            HAVING quantity > 0
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def remove_item_from_stock(self, name, quantity, unit):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT i.id, i.quantity 
            FROM warehouse_receipt_items i
            JOIN warehouse_data d ON i.receipt_id = d.id
            WHERE i.name = ? AND i.unit = ? AND d.doc_type = 'PZ'
            ORDER BY d.date ASC, i.id ASC
        ''', (name, unit))
        
        rows = cursor.fetchall()
        
        remaining_to_remove = quantity
        
        for item_id, item_qty in rows:
            if remaining_to_remove <= 0:
                break
                
            if item_qty <= remaining_to_remove:
                cursor.execute('DELETE FROM warehouse_receipt_items WHERE id = ?', (item_id,))
                remaining_to_remove -= item_qty
            else:
                new_qty = item_qty - remaining_to_remove
                cursor.execute('UPDATE warehouse_receipt_items SET quantity = ? WHERE id = ?', (new_qty, item_id))
                remaining_to_remove = 0
        
        cursor.execute('''
            DELETE FROM warehouse_data 
            WHERE id NOT IN (SELECT DISTINCT receipt_id FROM warehouse_receipt_items)
            AND doc_type = 'PZ'
        ''')
        
        conn.commit()
        conn.close()

    def delete_document(self, doc_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM warehouse_receipt_items WHERE receipt_id = ?', (doc_id,))
        
        cursor.execute('DELETE FROM warehouse_data WHERE id = ?', (doc_id,))
        
        conn.commit()
        conn.close()

    def add_user(self, username, password, is_admin):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, 1 if is_admin else 0))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
