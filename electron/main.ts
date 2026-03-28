import { app, BrowserWindow } from "electron";
import { spawn } from "child_process";
import path from "path";
import crypto from "crypto";

let mainWindow: BrowserWindow | null = null;
let backendProcess: any;

let AUTH_TOKEN: string;
if (process.env.ZYRA_AUTH_TOKEN) {
    AUTH_TOKEN = process.env.ZYRA_AUTH_TOKEN;
    console.log(`[INFO] Using environment variable ZYRA_AUTH_TOKEN: ${AUTH_TOKEN}`);
} else {
    AUTH_TOKEN = createAuthToken();
}

/**
 * Start the the backend process.
 * 
 * @param AUTH_TOKEN The authentication token to use for the backend process.
 */
function startBackend() {
    backendProcess = spawn("python", ["backend/main.py"], { env: { ...process.env, AUTH_TOKEN } });

    backendProcess.stdout.on("data", (data: Buffer) => {
        console.log(`[Flask]: ${data}`);
    });

    backendProcess.stderr.on("data", (data: Buffer) => {
        console.error(`[Flask ERROR]: ${data}`);
    });
}

/**
 * Create a new authentication token.
 * 
 * @param length The length of the token to create. Defaults to 32 characters.
 * @returns The created authentication token.
 */
function createAuthToken() {
    const token = crypto.randomBytes(32).toString("hex");
    return token;
}

/**
 * Create the main window.
 * 
 * @param mainWindow The main window to create.
 */
function createWindow() {
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

    mainWindow.loadURL("http://localhost:5173");
}

app.whenReady().then(async () => {
    startBackend();
    createWindow();
});

app.on("will-quit", () => {
    if (backendProcess) backendProcess.kill();
});