import { useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent, DragEvent } from "react";
import { BadgePill } from "./components/BadgePill";
import { ChatMessage } from "./components/ChatMessage";
import { SettingsApp } from "./settings/SettingsApp";
import type { BadgeItem, ChatMessageItem } from "./types";
import { compactText, createId, ellipsis } from "./utils";

function AssistantApp() {
    const [inputValue, setInputValue] = useState("");
    const [messages, setMessages] = useState<ChatMessageItem[]>([]);
    const [badges, setBadges] = useState<BadgeItem[]>([]);
    const [isSending, setIsSending] = useState(false);
    const [showAnimation, setShowAnimation] = useState(false);

    const [isHiding, setIsHiding] = useState(false);

    const inputRef = useRef<HTMLTextAreaElement | null>(null);
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const previewMessages = useMemo(
        () => messages.filter((item) => item.role === "assistant").slice(-1),
        [messages]
    );

    useEffect(() => {
        const focusInput = () => {
            inputRef.current?.focus();
        };
        const unsubscribeHide = window.zyra.onWindowHidden(() => {
            setMessages([]);
            setBadges([]);
            setInputValue("");
            setShowAnimation(false);
            setIsHiding(false);
        });
        const unsubscribeShow = window.zyra.onWindowShown(() => {
            setShowAnimation(true);
            setIsHiding(false);
        });
        const unsubscribeHideReq = window.zyra.onWindowHideRequest(() => {
            setIsHiding(true);
            setTimeout(() => {
                void window.zyra.confirmWindowHidden();
            }, 250);
        });

        focusInput();
        window.addEventListener("focus", focusInput);
        return () => {
            window.removeEventListener("focus", focusInput);
            unsubscribeHide();
            unsubscribeShow();
            unsubscribeHideReq();
        };
    }, []);

    useEffect(() => {
        const lines = Math.max(2, inputValue.split("\n").length);
        const desiredHeight = Math.min(
            760,
            180 + previewMessages.length * 58 + badges.length * 28 + lines * 14
        );
        void window.zyra.setWindowHeight(desiredHeight);
    }, [badges.length, inputValue, previewMessages.length]);

    const addFileBadge = (filePath: string) => {
        const name = filePath.split(/[/\\]/).pop() || filePath;
        setBadges((prev) => {
            const exists = prev.some((item) => item.kind === "file" && item.fullText === filePath);
            if (exists) {
                return prev;
            }
            return [
                ...prev,
                {
                    id: createId("file"),
                    kind: "file",
                    fullText: filePath,
                    label: compactText(name, 9),
                },
            ];
        });
    };

    const resolveFilePath = (file: File) => {
        const absolutePath = window.zyra.getPathForFile(file);
        if (absolutePath) {
            return absolutePath;
        }
        const reflectedPath = Reflect.get(file, "path");
        if (typeof reflectedPath === "string" && reflectedPath) {
            return reflectedPath;
        }
        return file.name;
    };

    const handleFileInputChange = (event: ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(event.target.files ?? []);
        files.forEach((file) => {
            addFileBadge(resolveFilePath(file));
        });
        event.target.value = "";
    };

    const handleDrop = (event: DragEvent<HTMLDivElement>) => {
        event.preventDefault();
        const files = Array.from(event.dataTransfer.files ?? []);
        files.forEach((file) => {
            addFileBadge(resolveFilePath(file));
        });
    };

    const handleSubmit = async () => {
        const content = inputValue.trim();
        if (!content || isSending) {
            return;
        }
        setIsSending(true);
        const userMessageId = createId("user");
        const pendingAssistantId = createId("assistant");
        setMessages((prev) => [
            ...prev,
            { id: userMessageId, role: "user", text: ellipsis(content, 72) },
            { id: pendingAssistantId, role: "assistant", text: "", pending: true },
        ]);
        setInputValue("");

        try {
            const response = await window.zyra.sendMessage({
                message: content,
                fileNames: badges.filter((item) => item.kind === "file").map((item) => item.fullText),
            });
            setMessages((prev) =>
                prev.map((item) =>
                    item.id === pendingAssistantId
                        ? { ...item, pending: false, text: response.text || "已收到。", role: "assistant" }
                        : item
                )
            );
        } catch {
            setMessages((prev) =>
                prev.map((item) =>
                    item.id === pendingAssistantId
                        ? { ...item, pending: false, text: "发送失败，请稍后重试。", role: "assistant" }
                        : item
                )
            );
        } finally {
            setIsSending(false);
            inputRef.current?.focus();
        }
    };

    return (
        <div className={`assistant-shell ${showAnimation && !isHiding ? "animate-show" : ""} ${isHiding ? "animate-hide" : ""}`} onDragOver={(event) => event.preventDefault()} onDrop={handleDrop}>
            <div className="assistant-panel">
                <div className="input-row glass-card">
                    <textarea
                        ref={inputRef}
                        value={inputValue}
                        onChange={(event) => setInputValue(event.target.value)}
                        onKeyDown={(event) => {
                            if (event.key === "Enter" && !event.shiftKey) {
                                event.preventDefault();
                                void handleSubmit();
                            }
                        }}
                        placeholder="输入你的需求，回车发送"
                        rows={1}
                    />
                </div>
                {badges.length > 0 && (
                    <div className="badge-line">
                        {badges.map((item) => (
                            <BadgePill
                                key={item.id}
                                item={item}
                                onClick={() => {
                                    if (item.kind === "file") {
                                        void window.zyra.showItemInFolder(item.fullText);
                                    }
                                }}
                                onRemove={() => setBadges((prev) => prev.filter((b) => b.id !== item.id))}
                            />
                        ))}
                    </div>
                )}
                {previewMessages.length > 0 && (
                    <div className="message-preview">
                        {previewMessages.map((item) => (
                            <ChatMessage key={item.id} item={item} />
                        ))}
                    </div>
                )}
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden-file-input"
                    multiple
                    onChange={handleFileInputChange}
                />
            </div>
        </div>
    );
}

function App() {
    if (window.location.hash === "#/settings") {
        return <SettingsApp />;
    }
    return <AssistantApp />;
}

export default App;
