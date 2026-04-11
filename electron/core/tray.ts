import { BrowserWindow, Menu, Tray, app, nativeImage } from "electron";
import path from "path";

type TrayActions = {
    openSettings: () => void;
};

let trayRef: Tray | null = null;

const TRAY_ICON_RELATIVE_PATH = path.join("assets", "icon", "logo.png");

function getTrayIcon() {
    const iconPath = path.join(app.getAppPath(), TRAY_ICON_RELATIVE_PATH);
    const fileIcon = nativeImage.createFromPath(iconPath);
    return fileIcon;
}

function buildTrayMenu(window: BrowserWindow, actions: TrayActions) {
    return Menu.buildFromTemplate([
        {
            label: "设置",
            click: () => {
                actions.openSettings();
            },
        },
        { type: "separator" },
        {
            label: "退出",
            click: () => {
                app.quit();
            },
        },
    ]);
}

export function createTray(getMainWindow: () => BrowserWindow | null, actions: TrayActions) {
    const icon = getTrayIcon();
    trayRef = new Tray(icon.resize({ width: 18, height: 18 }));
    trayRef.setToolTip("ZyraAI");

    const window = getMainWindow();
    if (window && trayRef) {
        trayRef.setContextMenu(buildTrayMenu(window, actions));
    }

    trayRef.on("click", () => {
        if (!trayRef) {
            return;
        }
        trayRef.popUpContextMenu();
    });

    return trayRef;
}

export function destroyTray() {
    if (!trayRef) {
        return;
    }
    trayRef.destroy();
    trayRef = null;
}
