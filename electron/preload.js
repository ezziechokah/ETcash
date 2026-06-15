const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('etcash', {
  getApiUrl:       ()     => ipcRenderer.invoke('get-api-url'),
  getAppVersion:   ()     => ipcRenderer.invoke('get-app-version'),
  getUserDataPath: ()     => ipcRenderer.invoke('get-user-data-path'),
  openFileDialog:  (opts) => ipcRenderer.invoke('open-file-dialog', opts),
  saveFileDialog:  (opts) => ipcRenderer.invoke('save-file-dialog', opts),
  openExternal:    (url)  => ipcRenderer.invoke('open-external', url),
});
