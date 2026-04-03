import { contextBridge, ipcRenderer } from "electron";

const api = {
    getAppInfo: () => ipcRenderer.invoke("app:get-info") as Promise<{
        version: string;
        platform: string;
        isDev: boolean;
    }>,
    showWindow: () => ipcRenderer.invoke("window:show") as Promise<boolean>,
    hideWindow: () => ipcRenderer.invoke("window:hide") as Promise<boolean>,
    toggleWindow: () => ipcRenderer.invoke("window:toggle") as Promise<boolean>,
    setWindowHeight: (height: number) => ipcRenderer.invoke("window:set-height", height) as Promise<boolean>,
    onSetAuthToken: (callback: (token: string) => void) => ipcRenderer.on('auth:set-auth-token', (event, token) => callback(token))
};

contextBridge.exposeInMainWorld("zyra", api);
