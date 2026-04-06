import { spawn } from "child_process";
import log from "./logger";

let backendProcess: any;

/**
 * Start the backend process.
 * @param AUTH_TOKEN The authentication token to use.
 * @param PORT The port number to use.
 * @param IS_DEV Whether the application is running in development mode.
 * @param PLATFORM The platform of the application running.
 */
export function startBackend(AUTH_TOKEN: string, PORT: number, IS_DEV: boolean, PLATFORM: string, APP_DATA_DIR: string) {
    if (IS_DEV) {
        let pythonPath: string;
        switch (PLATFORM) {
            case "win32":
                pythonPath = "backend\\.venv\\Scripts\\python.exe";
                break;
            case "darwin":
                pythonPath = "backend/.venv/bin/python";
                break;
            case "linux":
                pythonPath = "backend/.venv/bin/python";
                break;
            default:
                pythonPath = "backend/.venv/bin/python";
                break;
        }

        backendProcess = spawn(
            pythonPath, [
            "backend/main.py",
            AUTH_TOKEN,
            PORT.toString(),
            IS_DEV.toString(),
            APP_DATA_DIR
        ], {
            env: { ...process.env }
        });

        backendProcess.stdout.on("data", (data: Buffer) => {
            log.info(`[Flask]: ${data}`);
        });

        backendProcess.stderr.on("data", (data: Buffer) => {
            log.error(`[Flask ERROR]: ${data}`);
        });

        backendProcess.on("exit", (code: number) => {
            log.error(`[Backend exited]: code=${code}`);
        });
    }
}

/**
 * Stop the backend process.
 */
export function stopBackend() {
    if (backendProcess) {
        backendProcess.kill();
    }
}

/**
 * Generate a random port number.
 * @returns A random port number.
 */
export function randomPort() {
    return Math.floor(Math.random() * 65535) + 1024;
}
