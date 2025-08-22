const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const Database = require('./database/db');

let mainWindow;
let db;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, '../assets/icon.png'),
    show: false
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Remove menu bar in production
  if (!process.argv.includes('--dev')) {
    mainWindow.setMenuBarVisibility(false);
  }
}

app.whenReady().then(() => {
  // Initialize database
  db = new Database();
  
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC handlers for database operations
ipcMain.handle('db-login', async (event, pin) => {
  return await db.verifyLogin(pin);
});

ipcMain.handle('db-get-clients', async () => {
  return await db.getClients();
});

ipcMain.handle('db-search-clients', async (event, query) => {
  return await db.searchClients(query);
});

ipcMain.handle('db-add-client', async (event, clientData) => {
  return await db.addClient(clientData);
});

ipcMain.handle('db-update-client', async (event, id, clientData) => {
  return await db.updateClient(id, clientData);
});

ipcMain.handle('db-get-client', async (event, id) => {
  return await db.getClient(id);
});

ipcMain.handle('db-add-payment', async (event, paymentData) => {
  return await db.addPayment(paymentData);
});

ipcMain.handle('db-get-payments', async (event, clientId) => {
  return await db.getPayments(clientId);
});

ipcMain.handle('db-get-payments-by-date', async (event, date) => {
  return await db.getPaymentsByDate(date);
});

ipcMain.handle('db-update-consumption', async (event, clientId, consumption) => {
  return await db.updateConsumption(clientId, consumption);
});

ipcMain.handle('db-get-dashboard-stats', async () => {
  return await db.getDashboardStats();
});
