import { BrowserWindow } from "electron";
import path from "path";

let mainWindow: BrowserWindow | null = null;

/**
 * Create the main window.
 * @param IS_DEV Whether the application is running in development mode.
 * @param AUTH_TOKEN The authentication token to use.
 */
export function createWindow(IS_DEV: boolean, AUTH_TOKEN: string) {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
        },
    });

    mainWindow.webContents.on("did-finish-load", () => {
        mainWindow?.webContents.send("set-auth-token", AUTH_TOKEN);
    });

    if (IS_DEV) {
        mainWindow.loadURL("http://localhost:5173");
    } else {
        mainWindow.loadFile("dist/frontend/index.html");
    }
}