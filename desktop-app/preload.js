const { ipcRenderer } = require('electron');

// Expose ipcRenderer to renderer pages
window.ipcRenderer = ipcRenderer;
