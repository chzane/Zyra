import { app, BrowserWindow, ipcMain } from "electron";
import { setAssistantWindowHeight } from "./window";

type GetMainWindow = () => BrowserWindow | null;

export function registerIpcHandlers(IS_DEV: boolean, getMainWindow: GetMainWindow) {
    // === App ===
    /**
     * Get app info
     */
    ipcMain.handle("app:get-info", () => {
        return {
            version: app.getVersion(),
            platform: process.platform,
            isDev: IS_DEV,
        };
    });

    // === Window ===
    /**
     * Show window
     */
    ipcMain.handle("window:show", () => {
        const mainWindow = getMainWindow();
        if (!mainWindow) {
            return false;
        }
        mainWindow.show();
        mainWindow.focus();
        return true;
    });

    /**
     * Hide window
     */
    ipcMain.handle("window:hide", () => {
        const mainWindow = getMainWindow();
        if (!mainWindow) {
            return false;
        }
        mainWindow.hide();
        return true;
    });

    /**
     * Toggle window
     */
    ipcMain.handle("window:toggle", () => {
        const mainWindow = getMainWindow();
        if (!mainWindow) {
            return false;
        }
        if (mainWindow.isVisible()) {
            mainWindow.hide();
            return false;
        }
        mainWindow.show();
        mainWindow.focus();
        return true;
    });

    /**
     * Set window height
     * @param height The desired height of the window.
     */
    ipcMain.handle("window:set-height", (_event, height: number) => {
        const mainWindow = getMainWindow();
        if (!mainWindow) {
            return false;
        }
        if (!Number.isFinite(height)) {
            return false;
        }
        setAssistantWindowHeight(mainWindow, height);
        return true;
    });
}
