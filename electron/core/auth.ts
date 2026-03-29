import crypto from "crypto";

/**
 * Create a new authentication token.
 * @returns The created authentication token.
 */
export function createAuthToken() {
    return crypto.randomBytes(32).toString("hex");
}