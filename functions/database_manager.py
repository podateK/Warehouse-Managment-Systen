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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                description TEXT,
                status TEXT,
                user TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                date_created TEXT NOT NULL,
                status TEXT,
                client_name TEXT,
                total_value REAL,
                items_count INTEGER
            )
        ''')

        cursor.execute('SELECT COUNT(*) FROM operations_log')
        if cursor.fetchone()[0] == 0:
            self._populate_sample_operations(cursor)
        
        cursor.execute('SELECT COUNT(*) FROM orders')
        if cursor.fetchone()[0] == 0:
            self._populate_sample_orders(cursor)
        
        cursor.execute('SELECT COUNT(*) FROM warehouse_data')
        if cursor.fetchone()[0] == 0:
            self._populate_sample_warehouse_data(cursor)

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

    def _populate_sample_operations(self, cursor):
        """Populate with sample operations data - REALISTIC BUSINESS LOG"""
        operations = [
            ("2026-03-28 14:35", "RECEIVE", "PZ/2026/001 - Odebrano 240m rur stalowych od Global Steel", "Ukończone", "admin"),
            ("2026-03-28 14:15", "SHIPMENT", "WZ/2026/001 - Wysłano zamówienie do Budtrans Sp. z o.o.", "Ukończone", "admin"),
            ("2026-03-28 13:45", "INVENTORY", "Sprawdzenie magazynu sekcja A - 905 jednostek", "Ukończone", "user"),
            ("2026-03-28 13:20", "QUALITY_CHECK", "Kontrola jakości rur stalowych - OK", "Ukończone", "system"),
            ("2026-03-28 11:30", "ROBOT_MOVE", "Robot AGV-01 przeniósł paletę z magazynu A do C", "Ukończone", "system"),
            ("2026-03-27 16:45", "RECEIVE", "PZ/2026/002 - Odebrano styropian 200mm od IsoTerm Polska", "Ukończone", "admin"),
            ("2026-03-27 16:15", "ORDER_CREATED", "Nowe zamówienie ZAM/2026/025 od Budtrans - 12100 PLN", "Ukończone", "admin"),
            ("2026-03-27 14:00", "SHIPMENT", "WZ/2026/002 - Wysłano zamówienie do Projekt Domów Sp. z o.o.", "Ukończone", "user"),
            ("2026-03-27 13:30", "INVENTORY", "Sprawdzenie magazynu sekcja C - 620 jednostek", "Ukończone", "admin"),
            ("2026-03-26 15:45", "RECEIVE", "PZ/2026/003 - Odebrano 2500 kartonów do opakowania", "Ukończone", "admin"),
            ("2026-03-26 15:15", "PACKAGING_CHECK", "Weryfikacja materiałów pakunkowych - załącznik OK", "Ukończone", "system"),
            ("2026-03-26 14:00", "SHIPMENT", "WZ/2026/003 - Wysłano zamówienie do E-sklep Europa", "Ukończone", "admin"),
            ("2026-03-26 10:30", "ROBOT_MAINTENANCE", "Przegląd rutynowy robota AGV-01 i AGV-02", "Ukończone", "system"),
            ("2026-03-25 17:00", "RECEIVE", "PZ/2026/004 - Odebrano części mechaniczne od MechDev", "Ukończone", "admin"),
            ("2026-03-25 16:30", "QUALITY_CHECK", "Test łożysk SKF i sprzęgieł elastycznych - PASS", "Ukończone", "system"),
            ("2026-03-25 14:00", "SHIPMENT", "WZ/2026/004 - Wysłano zamówienie do ProMetech Sp. z o.o.", "Ukończone", "user"),
            ("2026-03-25 11:45", "INVENTORY", "Sprawdzenie magazynu sekcja D - 385 jednostek", "Ukończone", "admin"),
            ("2026-03-24 16:20", "RECEIVE", "PZ/2026/005 - Odebrano sterowniki i elektronikę od ElectroCode", "Ukończone", "admin"),
            ("2026-03-24 15:00", "SHIPMENT", "WZ/2026/005 - Wysłano zamówienie do Elektro Sieć Sp. z o.o.", "Ukończone", "admin"),
            ("2026-03-24 10:00", "SYSTEM_CHECK", "Sprawdzenie integracji systemu WMS - bez błędów", "Ukończone", "system"),
        ]
        
        for timestamp, op_type, desc, status, user in operations:
            cursor.execute('''
                INSERT INTO operations_log (timestamp, operation_type, description, status, user)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, op_type, desc, status, user))

    def _populate_sample_orders(self, cursor):
        """Populate with sample orders data - REALISTIC BUSINESS ORDERS"""
        orders = [
            ("ZAM/2026/025", "2026-03-28", "Do wysłania", "Budtrans Sp. z o.o.", 12100.00, 4),
            ("ZAM/2026/024", "2026-03-27", "Do wysłania", "Projekt Domów Sp. z o.o.", 16800.00, 3),
            ("ZAM/2026/023", "2026-03-26", "W trakcie przygotowania", "E-sklep Europa Sp. z o.o.", 5200.00, 4),
            ("ZAM/2026/022", "2026-03-25", "W trakcie przygotowania", "ProMetech Sp. z o.o.", 18900.00, 5),
            ("ZAM/2026/021", "2026-03-24", "Wysłane", "Elektro Sieć Sp. z o.o.", 9800.00, 4),
            ("ZAM/2026/020", "2026-03-23", "Wysłane", "Global Industries", 14650.00, 6),
            ("ZAM/2026/019", "2026-03-22", "Wysłane", "konstruktor.pl Sp. z o.o.", 22400.00, 8),
            ("ZAM/2026/018", "2026-03-21", "Wysłane", "OEM Partner Logistics", 11200.00, 5),
            ("ZAM/2026/017", "2026-03-20", "Wysłane", "FrameWorks International", 19800.00, 7),
            ("ZAM/2026/016", "2026-03-19", "Wysłane", "BuildRight Contractors", 8900.00, 3),
        ]
        
        for order_num, date_created, status, client, value, items in orders:
            cursor.execute('''
                INSERT INTO orders (order_number, date_created, status, client_name, total_value, items_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (order_num, date_created, status, client, value, items))

    def _populate_sample_warehouse_data(self, cursor):
        """Populate with sample warehouse receipts and shipments"""
        pz_documents = [
            ("PZ/2026/001", "2026-03-28", "001/PZ/2026", "Global Steel Sp. z o.o.", "Magazyn A", 28500.00, 1500.00),
            ("PZ/2026/002", "2026-03-27", "002/PZ/2026", "IsoTerm Polska", "Magazyn B", 12300.00, 650.00),
            ("PZ/2026/003", "2026-03-26", "003/PZ/2026", "KartonBox Sp. z o.o.", "Magazyn C", 8900.00, 450.00),
            ("PZ/2026/004", "2026-03-25", "004/PZ/2026", "MechDev Sp. z o.o.", "Magazyn D", 15600.00, 820.00),
            ("PZ/2026/005", "2026-03-24", "005/PZ/2026", "ElectroCode Sp. z o.o.", "Magazyn A", 22400.00, 1200.00),
        ]
        
        wz_documents = [
            ("WZ/2026/001", "2026-03-28", "001/WZ/2026", "Budtrans Sp. z o.o.", "Odbior magazyn", 5800.00, 300.00),
            ("WZ/2026/002", "2026-03-27", "002/WZ/2026", "Projekt Domów Sp. z o.o.", "Odbiór magazyn", 8200.00, 420.00),
            ("WZ/2026/003", "2026-03-26", "003/WZ/2026", "E-sklep Europa", "Odbiór magazyn", 3400.00, 180.00),
            ("WZ/2026/004", "2026-03-25", "004/WZ/2026", "ProMetech Sp. z o.o.", "Odbiór magazyn", 7100.00, 380.00),
            ("WZ/2026/005", "2026-03-24", "005/WZ/2026", "Elektro Sieć Sp. z o.o.", "Odbiór magazyn", 4900.00, 250.00),
        ]
        
        pz_items_data = [
            [(1, "Rury stalowe 100x100mm", 240, 240, "m", 85.00, 20400.00)],
            [(2, "Styropian 200mm", 500, 500, "m2", 18.00, 9000.00)],
            [(3, "Kartony uniwersalne 400x300x250", 2500, 2500, "szt", 3.00, 7500.00)],
            [(4, "Łożyska SKF 6204", 800, 800, "szt", 12.00, 9600.00), (4, "Sprzęgła elastyczne", 400, 400, "szt", 15.00, 6000.00)],
            [(5, "Sterowniki PLC Siemens", 150, 150, "szt", 120.00, 18000.00), (5, "Elektronika kontrolna", 200, 200, "szt", 22.00, 4400.00)],
        ]
        
        wz_items_data = [
            [(1, "Rury stalowe 100x100mm", 120, 120, "m", 85.00, 10200.00)],
            [(2, "Styropian 200mm", 300, 300, "m2", 18.00, 5400.00)],
            [(3, "Kartony uniwersalne 400x300x250", 1200, 1200, "szt", 3.00, 3600.00)],
            [(4, "Łożyska SKF 6204", 300, 300, "szt", 12.00, 3600.00), (4, "Sprzęgła elastyczne", 150, 150, "szt", 15.00, 2250.00)],
            [(5, "Sterowniki PLC Siemens", 80, 80, "szt", 120.00, 9600.00), (5, "Elektronika kontrolna", 120, 120, "szt", 22.00, 2640.00)],
        ]
        
        for i, (number, date, orig_num, contractor, receiver, value, cost) in enumerate(pz_documents):
            cursor.execute('''
                INSERT INTO warehouse_data (doc_type, date, number, original_number, contractor, receiver, value, cost, related_document)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('PZ', date, number, orig_num, contractor, receiver, value, cost, None))
            doc_id = cursor.lastrowid
            
            for item_doc_id, name, qty, qty_delivered, unit, price, val in pz_items_data[i]:
                cursor.execute('''
                    INSERT INTO warehouse_receipt_items (receipt_id, name, quantity, quantity_delivered, unit, price_netto, value_netto)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (doc_id, name, qty, qty_delivered, unit, price, val))
        
        for i, (number, date, orig_num, client, receiver, value, cost) in enumerate(wz_documents):
            cursor.execute('''
                INSERT INTO warehouse_data (doc_type, date, number, original_number, contractor, receiver, value, cost, related_document)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('WZ', date, number, orig_num, client, receiver, value, cost, None))
            doc_id = cursor.lastrowid
            
            for item_doc_id, name, qty, qty_delivered, unit, price, val in wz_items_data[i]:
                cursor.execute('''
                    INSERT INTO warehouse_receipt_items (receipt_id, name, quantity, quantity_delivered, unit, price_netto, value_netto)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (doc_id, name, qty, qty_delivered, unit, price, val))

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
        
        if (value_netto == 0 or value_netto is None) and price_netto > 0:
            value_netto = quantity_delivered * price_netto
        
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

    def get_recent_operations(self, limit=10):
        """Get recent operations from log"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, operation_type, description, status, user
            FROM operations_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_pending_orders(self):
        """Get orders that are not yet shipped"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, order_number, date_created, status, client_name, total_value, items_count
            FROM orders
            WHERE status LIKE '%trakcie%' OR status = 'Do wysłania'
            ORDER BY date_created DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_orders(self):
        """Get all orders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, order_number, date_created, status, client_name, total_value, items_count
            FROM orders
            ORDER BY date_created DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_operation(self, operation_type, description, status, user):
        """Log an operation"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO operations_log (timestamp, operation_type, description, status, user)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, operation_type, description, status, user))
        conn.commit()
        conn.close()
