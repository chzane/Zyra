export type BadgeItem = {
    id: string;
    label: string;
    fullText: string;
    kind: "selection" | "file";
};

export type ChatMessageItem = {
    id: string;
    role: "user" | "assistant";
    text: string;
    pending?: boolean;
};
