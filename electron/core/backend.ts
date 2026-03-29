import { spawn } from "child_process";
import log from "./logger";

let backendProcess: any;

/**
 * Start the backend process.
 * @param AUTH_TOKEN The authentication token to use.
 * @param IS_DEV Whether the application is running in development mode.
 * @param IS_WIN Whether the application is running on Windows.
 */
export function startBackend(AUTH_TOKEN: string, PORT: number, IS_DEV: boolean, IS_WIN: boolean) {
    if (IS_DEV) {
        const pythonPath = IS_WIN
            ? "backend\\.venv\\Scripts\\python.exe"
            : "backend/.venv/bin/python";

        backendProcess = spawn(pythonPath, ["backend/main.py", AUTH_TOKEN, PORT.toString()], {
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