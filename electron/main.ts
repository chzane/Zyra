import { app, BrowserWindow } from "electron";
import { spawn } from "child_process";
import path from "path";

let mainWindow: BrowserWindow | null = null;
let backendProcess: any;

function startBackend() {
    backendProcess = spawn("python", ["backend/main.py"]);

    backendProcess.stdout.on("data", (data: Buffer) => {
        console.log(`[Flask]: ${data}`);
    });

    backendProcess.stderr.on("data", (data: Buffer) => {
        console.error(`[Flask ERROR]: ${data}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
        },
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