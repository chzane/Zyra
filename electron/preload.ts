import { contextBridge, ipcRenderer, webUtils } from "electron";

const api = {
    getAppInfo: () => ipcRenderer.invoke("app:get-info") as Promise<{
        name: string;
        version: string;
        gitRepository: string;
        platform: string;
        isDev: boolean;
    }>,
    showWindow: () => ipcRenderer.invoke("window:show") as Promise<boolean>,
    toggleWindow: () => ipcRenderer.invoke("window:toggle") as Promise<boolean>,
    setWindowHeight: (height: number) => ipcRenderer.invoke("window:set-height", height) as Promise<boolean>,
    setIgnoreMouseEvents: (ignore: boolean, options?: { forward?: boolean }) => ipcRenderer.send("window:set-ignore-mouse-events", ignore, options),
    sendMessage: (payload: { message: string; fileNames?: string[] }) =>
        ipcRenderer.invoke("chat:send-message", payload) as Promise<{ text: string }>,
    pickFiles: () => ipcRenderer.invoke("file:pick") as Promise<string[]>,
    getPathForFile: (file: File) => webUtils.getPathForFile(file),
    showItemInFolder: (path: string) => ipcRenderer.invoke("file:show-item", path) as Promise<void>,
    onSetAuthToken: (callback: (token: string) => void) => {
        const listener = (_event: Electron.IpcRendererEvent, token: string) => callback(token);
        ipcRenderer.on("auth:set-auth-token", listener);
        return () => ipcRenderer.removeListener("auth:set-auth-token", listener);
    },
    onWindowHidden: (callback: () => void) => {
        const listener = () => callback();
        ipcRenderer.on("window:hidden", listener);
        return () => ipcRenderer.removeListener("window:hidden", listener);
    },
    onWindowShown: (callback: () => void) => {
        const listener = () => callback();
        ipcRenderer.on("window:shown", listener);
        return () => ipcRenderer.removeListener("window:shown", listener);
    },
    onWindowHideRequest: (callback: () => void) => {
        const listener = () => callback();
        ipcRenderer.on("window:hide-request", listener);
        return () => ipcRenderer.removeListener("window:hide-request", listener);
    },
    confirmWindowHidden: () => ipcRenderer.invoke("window:hidden-confirm") as Promise<boolean>,
};

contextBridge.exposeInMainWorld("zyra", api);
