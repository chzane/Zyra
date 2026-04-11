import { app, BrowserWindow, dialog, ipcMain, shell } from "electron";
import { setAssistantWindowHeight } from "./window";
import { confirmHideAssistantWindow } from "../main";
import { APP_NAME, APP_VERSION, APP_GIT_REPOSITORY, IS_MAC, IS_WIN } from "../config";

type GetMainWindow = () => BrowserWindow | null;

export function registerIpcHandlers(IS_DEV: boolean, getMainWindow: GetMainWindow) {
    // === App ===
    /**
     * Get app info
     */
    ipcMain.handle("app:get-info", () => {
        return {
            name: APP_NAME,
            version: APP_VERSION,   
            gitRepository: APP_GIT_REPOSITORY,
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
    ipcMain.handle("window:hidden-confirm", () => {
        confirmHideAssistantWindow();
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

    /**
     * Send chat message
     */
    ipcMain.handle("chat:send-message", async (_event, payload: {
        message: string;
        fileNames?: string[];
    }) => {
        await new Promise((resolve) => setTimeout(resolve, 1200));
        const message = payload.message.trim();
        const hasFiles = (payload.fileNames ?? []).length > 0;
        const filesLabel = hasFiles ? `，以及 ${(payload.fileNames ?? []).length} 个文件` : "";
        return {
            text: `已收到你的需求：${message}${filesLabel}。这里是预留的云端 LLM 接口返回占位内容。`,
        };
    });

    /**
     * Pick files
     * @returns The selected file paths.
     */
    ipcMain.handle("file:pick", async () => {
        const mainWindow = getMainWindow();
        if (!mainWindow) {
            return [];
        }
        const result = await dialog.showOpenDialog(mainWindow, {
            properties: ["openFile", "multiSelections"],
        });
        if (result.canceled) {
            return [];
        }
        return result.filePaths;
    });

    /**
     * Show file item in folder
     */
    ipcMain.handle("file:show-item", (_event, filePath: string) => {
        // Log current platform state for debug
        if (IS_MAC) {
            console.log(`[Mac] Opening finder for: ${filePath}`);
        } else if (IS_WIN) {
            console.log(`[Windows] Opening explorer for: ${filePath}`);
        }
        shell.showItemInFolder(filePath);
    });
}
