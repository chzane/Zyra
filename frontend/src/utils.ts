export function createId(prefix: string) {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function compactText(text: string, edge = 8) {
    const normalized = text.replace(/\s+/g, " ").trim();
    if (normalized.length <= edge * 2 + 3) {
        return normalized;
    }
    return `${normalized.slice(0, edge)}...${normalized.slice(-edge)}`;
}

export function ellipsis(text: string, maxLength = 42) {
    const value = text.replace(/\s+/g, " ").trim();
    if (value.length <= maxLength) {
        return value;
    }
    return `${value.slice(0, maxLength)}...`;
}
