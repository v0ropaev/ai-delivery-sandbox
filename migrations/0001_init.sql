CREATE TABLE clients (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT, phone TEXT, manager_id INTEGER);
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, number TEXT NOT NULL, client_id INTEGER NOT NULL, status TEXT NOT NULL,
                     total TEXT NOT NULL, external_id TEXT, created_at TEXT NOT NULL);
CREATE TABLE invoices (id INTEGER PRIMARY KEY, number TEXT NOT NULL, client_id INTEGER NOT NULL, order_id INTEGER,
                       total TEXT NOT NULL, status TEXT NOT NULL, issued_at TEXT NOT NULL);
CREATE TABLE payments (id INTEGER PRIMARY KEY, invoice_id INTEGER NOT NULL, amount TEXT NOT NULL, paid_at TEXT NOT NULL);
