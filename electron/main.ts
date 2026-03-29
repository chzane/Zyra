import { app } from "electron";
import log from "./core/logger";
import { createAuthToken } from "./core/auth";
import { startBackend, stopBackend, randomPort } from "./core/backend";
import { createWindow } from "./core/window";
import { IS_DEV, IS_WIN } from "./config";

let AUTH_TOKEN: string;
let BACKEND_PORT: number;

log.info("Application starting...");

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

app.whenReady().then(() => {
    startBackend(AUTH_TOKEN, BACKEND_PORT, IS_DEV, IS_WIN);
    createWindow(IS_DEV, AUTH_TOKEN);
});

app.on("will-quit", () => {
    stopBackend();
});