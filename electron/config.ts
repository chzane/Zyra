import { app } from "electron";

export const IS_DEV = !app.isPackaged;
export const IS_WIN = process.platform === "win32";