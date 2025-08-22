const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class Database {
  constructor() {
    this.dbPath = path.join(__dirname, '../../data/agua.db');
    this.ensureDataDirectory();
    this.db = new sqlite3.Database(this.dbPath);
    this.init();
  }

  ensureDataDirectory() {
    const dataDir = path.dirname(this.dbPath);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
  }

  init() {
    this.db.serialize(() => {
      // Admin table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS admin (
          id INTEGER PRIMARY KEY,
          pin TEXT NOT NULL
        )
      `);

      // Clients table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS clients (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          address TEXT NOT NULL,
          status TEXT DEFAULT 'active',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Payments table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS payments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          client_id INTEGER,
          amount REAL NOT NULL,
          payment_date DATE NOT NULL,
          status TEXT DEFAULT 'paid',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (client_id) REFERENCES clients (id)
        )
      `);

      // Consumption table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS consumption (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          client_id INTEGER,
          month TEXT NOT NULL,
          year INTEGER NOT NULL,
          normal_consumption REAL DEFAULT 0,
          excess_consumption REAL DEFAULT 0,
          notes TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (client_id) REFERENCES clients (id)
        )
      `);

      // Insert default admin PIN if not exists
      this.db.get("SELECT COUNT(*) as count FROM admin", (err, row) => {
        if (!err && row.count === 0) {
          this.db.run("INSERT INTO admin (pin) VALUES (?)", ["1234"]);
        }
      });
    });
  }

  verifyLogin(pin) {
    return new Promise((resolve, reject) => {
      this.db.get("SELECT * FROM admin WHERE pin = ?", [pin], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(!!row);
        }
      });
    });
  }

  getClients() {
    return new Promise((resolve, reject) => {
      const query = `
        SELECT 
          c.*,
          COALESCE(latest_payment.payment_date, '') as last_payment_date,
          COALESCE(latest_payment.status, 'pending') as payment_status,
          COALESCE(consumption.excess_consumption, 0) as excess_consumption
        FROM clients c
        LEFT JOIN (
          SELECT client_id, payment_date, status,
                 ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY payment_date DESC) as rn
          FROM payments
        ) latest_payment ON c.id = latest_payment.client_id AND latest_payment.rn = 1
        LEFT JOIN (
          SELECT client_id, excess_consumption,
                 ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY created_at DESC) as rn
          FROM consumption
        ) consumption ON c.id = consumption.client_id AND consumption.rn = 1
        ORDER BY c.name
      `;
      
      this.db.all(query, [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  searchClients(query) {
    return new Promise((resolve, reject) => {
      const searchQuery = `
        SELECT 
          c.*,
          COALESCE(latest_payment.payment_date, '') as last_payment_date,
          COALESCE(latest_payment.status, 'pending') as payment_status,
          COALESCE(consumption.excess_consumption, 0) as excess_consumption
        FROM clients c
        LEFT JOIN (
          SELECT client_id, payment_date, status,
                 ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY payment_date DESC) as rn
          FROM payments
        ) latest_payment ON c.id = latest_payment.client_id AND latest_payment.rn = 1
        LEFT JOIN (
          SELECT client_id, excess_consumption,
                 ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY created_at DESC) as rn
          FROM consumption
        ) consumption ON c.id = consumption.client_id AND consumption.rn = 1
        WHERE c.name LIKE ? OR c.address LIKE ? OR c.id LIKE ?
        ORDER BY c.name
      `;
      
      const searchTerm = `%${query}%`;
      this.db.all(searchQuery, [searchTerm, searchTerm, searchTerm], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  addClient(clientData) {
    return new Promise((resolve, reject) => {
      const { name, address, status = 'active' } = clientData;
      this.db.run(
        "INSERT INTO clients (name, address, status) VALUES (?, ?, ?)",
        [name, address, status],
        function(err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id: this.lastID, ...clientData });
          }
        }
      );
    });
  }

  updateClient(id, clientData) {
    return new Promise((resolve, reject) => {
      const { name, address, status } = clientData;
      this.db.run(
        "UPDATE clients SET name = ?, address = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        [name, address, status, id],
        function(err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id, ...clientData });
          }
        }
      );
    });
  }

  getClient(id) {
    return new Promise((resolve, reject) => {
      this.db.get("SELECT * FROM clients WHERE id = ?", [id], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  addPayment(paymentData) {
    return new Promise((resolve, reject) => {
      const { client_id, amount, payment_date, status = 'paid' } = paymentData;
      this.db.run(
        "INSERT INTO payments (client_id, amount, payment_date, status) VALUES (?, ?, ?, ?)",
        [client_id, amount, payment_date, status],
        function(err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id: this.lastID, ...paymentData });
          }
        }
      );
    });
  }

  getPayments(clientId) {
    return new Promise((resolve, reject) => {
      this.db.all(
        "SELECT * FROM payments WHERE client_id = ? ORDER BY payment_date DESC",
        [clientId],
        (err, rows) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows);
          }
        }
      );
    });
  }

  getPaymentsByDate(date) {
    return new Promise((resolve, reject) => {
      const query = `
        SELECT p.*, c.name, c.address 
        FROM payments p
        JOIN clients c ON p.client_id = c.id
        WHERE DATE(p.payment_date) = ?
        ORDER BY p.payment_date DESC
      `;
      
      this.db.all(query, [date], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  updateConsumption(clientId, consumption) {
    return new Promise((resolve, reject) => {
      const { month, year, normal_consumption, excess_consumption, notes } = consumption;
      
      // First check if record exists
      this.db.get(
        "SELECT id FROM consumption WHERE client_id = ? AND month = ? AND year = ?",
        [clientId, month, year],
        (err, row) => {
          if (err) {
            reject(err);
            return;
          }

          if (row) {
            // Update existing record
            this.db.run(
              "UPDATE consumption SET normal_consumption = ?, excess_consumption = ?, notes = ? WHERE id = ?",
              [normal_consumption, excess_consumption, notes, row.id],
              function(err) {
                if (err) {
                  reject(err);
                } else {
                  resolve({ id: row.id, ...consumption });
                }
              }
            );
          } else {
            // Insert new record
            this.db.run(
              "INSERT INTO consumption (client_id, month, year, normal_consumption, excess_consumption, notes) VALUES (?, ?, ?, ?, ?, ?)",
              [clientId, month, year, normal_consumption, excess_consumption, notes],
              function(err) {
                if (err) {
                  reject(err);
                } else {
                  resolve({ id: this.lastID, ...consumption });
                }
              }
            );
          }
        }
      );
    });
  }

  getDashboardStats() {
    return new Promise((resolve, reject) => {
      const queries = {
        totalClients: "SELECT COUNT(*) as count FROM clients WHERE status = 'active'",
        clientsWithDebt: `
          SELECT COUNT(DISTINCT c.id) as count 
          FROM clients c 
          LEFT JOIN payments p ON c.id = p.client_id 
          WHERE c.status = 'active' AND (p.id IS NULL OR p.status = 'pending')
        `,
        clientsPaid: `
          SELECT COUNT(DISTINCT c.id) as count 
          FROM clients c 
          JOIN payments p ON c.id = p.client_id 
          WHERE c.status = 'active' AND p.status = 'paid'
        `,
        excessConsumption: `
          SELECT COUNT(DISTINCT client_id) as count 
          FROM consumption 
          WHERE excess_consumption > 0
        `
      };

      const results = {};
      let completed = 0;
      const total = Object.keys(queries).length;

      Object.entries(queries).forEach(([key, query]) => {
        this.db.get(query, [], (err, row) => {
          if (err) {
            reject(err);
            return;
          }
          
          results[key] = row.count;
          completed++;
          
          if (completed === total) {
            resolve(results);
          }
        });
      });
    });
  }
}

module.exports = Database;
