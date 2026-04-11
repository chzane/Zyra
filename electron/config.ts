import { app } from "electron";

export const APP_NAME: string = "Zyra";
export const APP_VERSION: string = app.getVersion();
export const APP_GIT_REPOSITORY: string = "https://github.com/chzane/Zyra";

export const IS_DEV: boolean = !app.isPackaged;

export const PLATFORM: string = process.platform;
export const IS_WIN: boolean = PLATFORM === "win32";
export const IS_MAC: boolean = PLATFORM === "darwin";
export const IS_LINUX: boolean = PLATFORM === "linux";
