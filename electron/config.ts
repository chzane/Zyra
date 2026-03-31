import { app } from "electron";

export const IS_DEV: boolean = !app.isPackaged;

export const PLATFORM: string = process.platform;
export const IS_WIN: boolean = PLATFORM === "win32";
export const IS_MAC: boolean = PLATFORM === "darwin";
export const IS_LINUX: boolean = PLATFORM === "linux";
