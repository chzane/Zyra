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
    onSetAuthToken: (callback: (token: string) => void) => void;
};

declare global {
    interface Window {
        zyra: ZyraBridge;
        authToken: string;
    }
}

export { ZyraBridge };
