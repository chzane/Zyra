type ZyraAppInfo = {
    version: string;
    platform: string;
    isDev: boolean;
};

type ZyraBridge = {
    getAppInfo: () => Promise<ZyraAppInfo>;
    showWindow: () => Promise<boolean>;
    hideWindow: () => Promise<boolean>;
    toggleWindow: () => Promise<boolean>;
    setWindowHeight: (height: number) => Promise<boolean>;
    sendMessage: (payload: { message: string; fileNames?: string[] }) => Promise<{ text: string }>;
    pickFiles: () => Promise<string[]>;
    getPathForFile: (file: File) => string;
    showItemInFolder: (path: string) => Promise<void>;
    onSetAuthToken: (callback: (token: string) => void) => () => void;
    onWindowHidden: (callback: () => void) => () => void;
    onWindowShown: (callback: () => void) => () => void;
    onWindowHideRequest: (callback: () => void) => () => void;
    confirmWindowHidden: () => Promise<boolean>;
};

declare global {
    interface Window {
        zyra: ZyraBridge;
        authToken: string;
    }
}

export { ZyraBridge };
