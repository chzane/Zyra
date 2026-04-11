import { BrowserWindow, screen } from "electron";
import { IS_WIN } from "../config";
import path from "path";

let mainWindow: BrowserWindow | null = null;
let settingsWindow: BrowserWindow | null = null;
let isQuitting = false;

const FLOAT_WINDOW_WIDTH = 420;
const FLOAT_WINDOW_DEFAULT_HEIGHT = 80;
const FLOAT_WINDOW_MIN_HEIGHT = 80;
const FLOAT_WINDOW_MAX_HEIGHT = 760;
const FLOAT_WINDOW_MARGIN_TOP = 16;
const FLOAT_WINDOW_MARGIN_RIGHT = 16;

/**
 * Clamp the height to the valid range.
 * 
 * @param height The height to clamp.
 * @returns The clamped height.
 */
function clampHeight(height: number) {
    return Math.max(FLOAT_WINDOW_MIN_HEIGHT, Math.min(FLOAT_WINDOW_MAX_HEIGHT, Math.round(height)));
}

/**
 * Get the top-right bounds for the window.
 * 
 * @param height The desired height of the window.
 * @returns The top-right bounds for the window.
 */
function getTopRightBounds(height: number) {
    const display = screen.getPrimaryDisplay();
    const { x, y, width, height: areaHeight } = display.workArea;
    const boundedHeight = Math.min(clampHeight(height), areaHeight - FLOAT_WINDOW_MARGIN_TOP * 2);
    return {
        x: x + width - FLOAT_WINDOW_WIDTH - FLOAT_WINDOW_MARGIN_RIGHT,
        y: y + FLOAT_WINDOW_MARGIN_TOP,
        width: FLOAT_WINDOW_WIDTH,
        height: boundedHeight,
    };
}

/**
 * Create the main window.
 * @param IS_DEV Whether the application is running in development mode.
 * @param AUTH_TOKEN The authentication token to use.
 */
export function createWindow(IS_DEV: boolean, AUTH_TOKEN: string) {
    const initialBounds = getTopRightBounds(FLOAT_WINDOW_DEFAULT_HEIGHT);

    mainWindow = new BrowserWindow({
        ...initialBounds,
        show: false,
        frame: false,
        hasShadow: false,
        alwaysOnTop: true,
        transparent: true,
        resizable: false,
        fullscreenable: false,
        skipTaskbar: true,
        webPreferences: {
            preload: path.join(__dirname, "../preload.js"),
            backgroundThrottling: false,
        },
    });

    mainWindow.setIgnoreMouseEvents(true, { forward: true });

    mainWindow.setAlwaysOnTop(true, "floating");
    mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

    mainWindow.on("closed", () => {
        mainWindow = null;
    });

    mainWindow.webContents.on("did-finish-load", () => {
        mainWindow?.webContents.send("auth:set-auth-token", AUTH_TOKEN);
    });

    if (IS_DEV) {
        mainWindow.loadURL("http://localhost:5173");
    } else {
        mainWindow.loadFile("dist/frontend/index.html");
    }

    return mainWindow;
}

function ensureSettingsWindow(IS_DEV: boolean, AUTH_TOKEN: string) {
    if (settingsWindow) {
        return settingsWindow;
    }

    const display = screen.getPrimaryDisplay();
    const bounds = display.workArea;
    const width = Math.min(840, Math.max(560, Math.round(bounds.width * 0.58)));
    const height = Math.min(720, Math.max(480, Math.round(bounds.height * 0.62)));
    const x = bounds.x + Math.round((bounds.width - width) / 2);
    const y = bounds.y + Math.round((bounds.height - height) / 3);

    settingsWindow = new BrowserWindow({
        x,
        y,
        width,
        height,
        show: false,
        frame: false,
        transparent: true,
        title: "Zyra 设置",
        resizable: true,
        fullscreenable: false,
        minimizable: true,
        maximizable: false,
        webPreferences: {
            preload: path.join(__dirname, "../preload.js"),
            backgroundThrottling: false,
        },
    });

    settingsWindow.on("close", (event) => {
        if (isQuitting) {
            return;
        }
        event.preventDefault();
        settingsWindow?.hide();
    });

    settingsWindow.on("closed", () => {
        settingsWindow = null;
    });

    settingsWindow.webContents.on("did-finish-load", () => {
        settingsWindow?.webContents.send("auth:set-auth-token", AUTH_TOKEN);
    });

    if (IS_DEV) {
        void settingsWindow.loadURL("http://localhost:5173/#/settings");
    } else {
        void settingsWindow.loadFile("dist/frontend/index.html", { hash: "/settings" });
    }

    return settingsWindow;
}

export function preloadSettingsWindow(IS_DEV: boolean, AUTH_TOKEN: string) {
    ensureSettingsWindow(IS_DEV, AUTH_TOKEN);
}

export function showSettingsWindow(IS_DEV: boolean, AUTH_TOKEN: string) {
    const window = ensureSettingsWindow(IS_DEV, AUTH_TOKEN);
    window.show();
    window.focus();
    return window;
}

export function markWindowsQuitting() {
    isQuitting = true;
}

/**
 * Set the height of the assistant window.
 * @param window The assistant window to set.
 * @param height The desired height of the assistant window.
 * @returns 
 */
export function setAssistantWindowHeight(window: BrowserWindow, height: number) {
    if (!Number.isFinite(height)) {
        return;
    }
    const boundedHeight = clampHeight(height);
    const { width } = window.getBounds();
    const display = screen.getDisplayMatching(window.getBounds());
    const nextBounds = {
        x: display.workArea.x + display.workArea.width - width - FLOAT_WINDOW_MARGIN_RIGHT,
        y: display.workArea.y + FLOAT_WINDOW_MARGIN_TOP,
        width,
        height: boundedHeight,
    };
    window.setBounds(nextBounds, true);
}
