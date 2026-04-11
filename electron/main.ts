import { app, globalShortcut } from "electron";
import log from "./core/logger";
import { createAuthToken } from "./core/auth";
import { startBackend, stopBackend, randomPort } from "./core/backend";
import { registerIpcHandlers } from "./core/ipc";
import { createWindow, showSettingsWindow } from "./core/window";
import { createTray, destroyTray } from "./core/tray";
import { IS_DEV, PLATFORM } from "./config";
import dotenv from "dotenv";
import path from "path";

dotenv.config();

let AUTH_TOKEN: string;
let BACKEND_PORT: number;
let APP_DATA_DIR: string = path.join(app.getPath("userData"), "zyra_storage");

let mainWindowRef: ReturnType<typeof createWindow> | null = null;

async function showAssistantWindow() {
    if (!mainWindowRef) {
        return;
    }
    mainWindowRef.show();
    mainWindowRef.focus();
    mainWindowRef.webContents.send("window:shown");
}

function hideAssistantWindow() {
    if (!mainWindowRef) {
        return;
    }
    mainWindowRef.webContents.send("window:hide-request");
}

export function confirmHideAssistantWindow() {
    if (!mainWindowRef) {
        return;
    }
    mainWindowRef.hide();
    mainWindowRef.webContents.send("window:hidden");
}

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
    startBackend(AUTH_TOKEN, BACKEND_PORT, IS_DEV, PLATFORM, APP_DATA_DIR);

    const mainWindow = createWindow(IS_DEV, AUTH_TOKEN);
    mainWindowRef = mainWindow;
    createTray(() => mainWindowRef, {
        openSettings: () => {
            showSettingsWindow(IS_DEV, AUTH_TOKEN);
        },
    });

    const shortcut = "CommandOrControl+Escape";
    const isRegistered = globalShortcut.register(shortcut, () => {
        if (mainWindowRef?.isVisible()) {
            hideAssistantWindow();
            return;
        }
        void showAssistantWindow();
    });

    if (!isRegistered) {
        log.error(`[ERROR] Failed to register global shortcut: ${shortcut}`);
    }
});

app.on("will-quit", () => {
    globalShortcut.unregisterAll();
    destroyTray();
    mainWindowRef = null;
    stopBackend();
});
