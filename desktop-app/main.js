const { app, BrowserWindow, screen, ipcMain, Tray, Menu, nativeImage } = require('electron');
const path = require('path');

// Keep global references so they aren't garbage collected
let orbWindow = null;
let chatWindow = null;
let tray = null;

// ─── ORB WINDOW (tiny circular floating icon) ─────────────────────────────
function createOrbWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  orbWindow = new BrowserWindow({
    width: 80,
    height: 80,
    x: width - 110,
    y: height - 110,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    hasShadow: false,
    roundedCorners: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  orbWindow.loadFile('orb.html');
  orbWindow.setAlwaysOnTop(true, 'screen-saver');

  // Make it click-through on the transparent area only
  orbWindow.setIgnoreMouseEvents(false);

  orbWindow.on('closed', () => {
    orbWindow = null;
  });
}

// ─── CHAT WINDOW (popup chatbot) ──────────────────────────────────────────
function createChatWindow(orbBounds) {
  const { width: sw, height: sh } = screen.getPrimaryDisplay().workAreaSize;

  const winW = 420;
  const winH = 640;

  // Position popup near orb, keep it on-screen
  let x = orbBounds.x - winW - 10;
  let y = orbBounds.y - winH + orbBounds.height;

  if (x < 10) x = orbBounds.x + orbBounds.width + 10;
  if (x + winW > sw - 10) x = sw - winW - 10;
  if (y < 10) y = 10;
  if (y + winH > sh - 10) y = sh - winH - 10;

  chatWindow = new BrowserWindow({
    width: winW,
    height: winH,
    x,
    y,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    hasShadow: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  chatWindow.loadFile('chat.html');
  chatWindow.setAlwaysOnTop(true, 'screen-saver');

  chatWindow.on('closed', () => {
    chatWindow = null;
    // Notify orb that chat closed
    if (orbWindow) {
      orbWindow.webContents.send('chat-closed');
    }
  });

  // Close chat when clicking outside (blur)
  chatWindow.on('blur', () => {
    // Small delay so clicks inside still register
    setTimeout(() => {
      if (chatWindow && !chatWindow.isFocused()) {
        chatWindow.close();
      }
    }, 200);
  });
}

// ─── IPC HANDLERS ─────────────────────────────────────────────────────────
ipcMain.on('toggle-chat', (event, orbBounds) => {
  if (chatWindow) {
    chatWindow.close();
    chatWindow = null;
  } else {
    createChatWindow(orbBounds);
  }
});

ipcMain.on('close-chat', () => {
  if (chatWindow) {
    chatWindow.close();
    chatWindow = null;
  }
});

ipcMain.on('minimize-chat', () => {
  if (chatWindow) {
    chatWindow.close();
    chatWindow = null;
  }
});

ipcMain.on('move-orb', (event, { x, y }) => {
  if (orbWindow) {
    orbWindow.setPosition(Math.round(x), Math.round(y));
  }
});

ipcMain.on('quit-app', () => {
  app.quit();
});

// ─── SYSTEM TRAY ──────────────────────────────────────────────────────────
function createTray() {
  let trayIcon;
  try {
    trayIcon = nativeImage.createFromPath(path.join(__dirname, 'assets', 'tray.png'));
    if (trayIcon.isEmpty()) throw new Error('empty');
  } catch {
    try {
      trayIcon = nativeImage.createFromPath(path.join(__dirname, 'assets', 'icon.ico'));
      if (trayIcon.isEmpty()) throw new Error('empty ico');
      trayIcon = trayIcon.resize({ width: 16, height: 16 });
    } catch {
      trayIcon = nativeImage.createEmpty();
    }
  }
  tray = new Tray(trayIcon);

  const menu = Menu.buildFromTemplate([
    {
      label: '🌪️ WeatherAI Widget',
      enabled: false
    },
    { type: 'separator' },
    {
      label: 'Show Widget',
      click: () => {
        if (orbWindow) orbWindow.show();
        else createOrbWindow();
      }
    },
    {
      label: 'Hide Widget',
      click: () => {
        if (orbWindow) orbWindow.hide();
        if (chatWindow) chatWindow.close();
      }
    },
    { type: 'separator' },
    {
      label: 'Quit WeatherAI',
      click: () => app.quit()
    }
  ]);

  tray.setToolTip('WeatherAI Desktop Widget');
  tray.setContextMenu(menu);
  tray.on('click', () => {
    if (orbWindow) {
      if (orbWindow.isVisible()) orbWindow.hide();
      else orbWindow.show();
    }
  });
}

// ─── APP LIFECYCLE ────────────────────────────────────────────────────────
app.whenReady().then(() => {
  createOrbWindow();
  createTray();
});

app.on('window-all-closed', (e) => {
  // Keep app alive in system tray even when all windows closed
  e.preventDefault();
});

app.on('activate', () => {
  if (!orbWindow) createOrbWindow();
});

app.on('before-quit', () => {
  if (tray) tray.destroy();
});
