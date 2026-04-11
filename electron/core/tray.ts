import { BrowserWindow, Menu, Tray, app, nativeImage } from "electron";

type TrayActions = {
    openSettings: () => void;
};

let trayRef: Tray | null = null;

const TRAY_ICON_DATA_URL =
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAbFBMVEVHcEz////2YfD/l0D/s1T/8UX/8Fv/5lb/4lj/vWr/8VT/s2P/5Wf/3HP/4mz/x4f/7Vr/1Xf/yYH/3Gn/6Fv/9Uj/5V3/7lD/8Vn/4Wf/0n7/9UT/9Fj/8E7/2nf/6Vz/2G7/6mH/7Fn/9VD///87KH9hAAAAI3RSTlMALfQHC0czxJk/UQj2f2kgDG7m0vhaE8ChN8hVnA2zq1U7d3HIOwAAAJ9JREFUGNNjYGBkYmBiZWNhY2fg5uHl4xcQFBIWERUTFxCUkpYQlZBWUVeQVpFX09QwtLC0sraxt7B0cQ8IDAkNC4+IjIqOiY2Lj4hMSk5JTUtPSMzKzsnNw8vPyCzMzcsvKKxQVFJWUVVT19DU0tbR1dPX09fQNDI2MTSzt7B0cQxKTklNS8/JzcsvKKqoqq6prnF0cQ8AIB8LEhQSu2CeAAAAAElFTkSuQmCC";

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
    const icon = nativeImage.createFromDataURL(TRAY_ICON_DATA_URL);
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
