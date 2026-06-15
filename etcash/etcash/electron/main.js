'use strict';
const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path   = require('path');
const fs     = require('fs');
const crypto = require('crypto');
const { spawn } = require('child_process');
const kill   = require('tree-kill');
const Store  = require('electron-store');

const store = new Store();
const isDev = process.env.NODE_ENV === 'development';
const resourcesPath = isDev ? path.join(__dirname, '..') : process.resourcesPath;
const backendPath   = path.join(resourcesPath, 'backend');
const frontendPath  = path.join(resourcesPath, isDev ? 'frontend/dist' : 'frontend');

const DJANGO_PORT = 8765;
const DJANGO_URL  = `http://127.0.0.1:${DJANGO_PORT}`;

let mainWindow    = null;
let djangoProcess = null;

function getSecretKey() {
  let key = store.get('secretKey');
  if (!key) {
    key = crypto.randomBytes(50).toString('hex');
    store.set('secretKey', key);
  }
  return key;
}

function getPythonBin() {
  if (isDev) return process.platform === 'win32' ? 'python' : 'python3';
  const candidates = [
    path.join(resourcesPath, 'resources', 'python', 'python.exe'),
    path.join(resourcesPath, 'resources', 'python', 'python'),
    'python3', 'python'
  ];
  return candidates.find(p => { try { return fs.existsSync(p); } catch { return false; } }) || 'python3';
}

function getDjangoEnv() {
  return {
    ...process.env,
    DJANGO_SETTINGS_MODULE: 'etcash.settings',
    ETCASH_SECRET_KEY:      getSecretKey(),
    ETCASH_DATA_DIR:        app.getPath('userData'),
    ETCASH_DB_PATH:         path.join(app.getPath('userData'), 'etcash.db'),
    PYTHONUNBUFFERED:       '1'
  };
}

function startDjango() {
  return new Promise((resolve, reject) => {
    const python   = getPythonBin();
    const managePy = path.join(backendPath, 'manage.py');
    const env      = getDjangoEnv();

    const migrate = spawn(python, [managePy, 'migrate', '--run-syncdb'], { cwd: backendPath, env });
    migrate.stderr.on('data', d => console.error('[migrate]', d.toString()));
    migrate.on('close', () => {
      djangoProcess = spawn(python, [managePy, 'runserver', `127.0.0.1:${DJANGO_PORT}`, '--noreload'], {
        cwd: backendPath, env
      });
      let resolved = false;
      const tryResolve = (data) => {
        if (!resolved && data.toString().includes('Starting development server')) {
          resolved = true;
          resolve();
        }
      };
      djangoProcess.stdout.on('data', tryResolve);
      djangoProcess.stderr.on('data', (d) => { tryResolve(d); console.error('[django]', d.toString()); });
      djangoProcess.on('error', reject);
      setTimeout(() => { if (!resolved) { resolved = true; resolve(); } }, 6000);
    });
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440, height: 900, minWidth: 1024, minHeight: 700,
    title: 'ETcash',
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webSecurity: true
    },
    show: false
  });
  mainWindow.once('ready-to-show', () => mainWindow.show());
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(frontendPath, 'index.html'));
  }
  mainWindow.on('closed', () => { mainWindow = null; });
}

app.whenReady().then(async () => {
  try {
    if (!isDev) await startDjango();
    createWindow();
  } catch (err) {
    dialog.showErrorBox('ETcash Startup Error', String(err.message || err));
    app.quit();
  }
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate',          () => { if (!mainWindow) createWindow(); });
app.on('before-quit',       () => { if (djangoProcess) kill(djangoProcess.pid); });

ipcMain.handle('get-api-url',        () => DJANGO_URL);
ipcMain.handle('get-app-version',    () => app.getVersion());
ipcMain.handle('get-user-data-path', () => app.getPath('userData'));
ipcMain.handle('open-file-dialog',   (_, opts) => dialog.showOpenDialog(mainWindow, opts));
ipcMain.handle('save-file-dialog',   (_, opts) => dialog.showSaveDialog(mainWindow, opts));
ipcMain.handle('open-external',      (_, url)  => shell.openExternal(url));
