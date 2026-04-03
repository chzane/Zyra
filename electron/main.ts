import { app, globalShortcut } from "electron";
import log from "./core/logger";
import { createAuthToken } from "./core/auth";
import { startBackend, stopBackend, randomPort } from "./core/backend";
import { registerIpcHandlers } from "./core/ipc";
import { createWindow } from "./core/window";
import { IS_DEV, PLATFORM } from "./config";
import dotenv from "dotenv";

dotenv.config();

let AUTH_TOKEN: string;
let BACKEND_PORT: number;

let mainWindowRef: ReturnType<typeof createWindow> | null = null;

if (IS_DEV && process.env.ZYRA_AUTH_TOKEN) {
    AUTH_TOKEN = process.env.ZYRA_AUTH_TOKEN;
    log.info(`[INFO] Using env token: ${AUTH_TOKEN}`);
} else {
    AUTH_TOKEN = createAuthToken();
}

if (IS_DEV && process.env.ZYRA_BACKEND_PORT) {
    BACKEND_PORT = parseInt(process.env.ZYRA_BACKEND_PORT);
    log.info(`[INFO] Using env port: ${BACKEND_PORT}`);
} else {
    BACKEND_PORT = randomPort();
}

registerIpcHandlers(IS_DEV, () => mainWindowRef);

app.whenReady().then(() => {
    startBackend(AUTH_TOKEN, BACKEND_PORT, IS_DEV, PLATFORM);
    const mainWindow = createWindow(IS_DEV, AUTH_TOKEN);
    mainWindowRef = mainWindow;

    const shortcut = "CommandOrControl+Escape";
    const isRegistered = globalShortcut.register(shortcut, () => {
        if (mainWindow.isVisible()) {
            mainWindow.hide();
            return;
        }
        mainWindow.show();
        mainWindow.focus();
    });

    if (!isRegistered) {
        log.error(`[ERROR] Failed to register global shortcut: ${shortcut}`);
    }

    mainWindow.on("blur", () => {
        if (mainWindow.isVisible()) {
            mainWindow.hide();
        }
    });
});

app.on("will-quit", () => {
    globalShortcut.unregisterAll();
    mainWindowRef = null;
    stopBackend();
});
