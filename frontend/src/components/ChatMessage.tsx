import { useEffect, useState } from "react";
import type { ChatMessageItem } from "../types";

type ChatMessageProps = {
    item: ChatMessageItem;
};

export function ChatMessage({ item }: ChatMessageProps) {
    const isAssistant = item.role === "assistant";
    const baseClasses = "message-bubble";
    const roleClass = isAssistant ? "message-assistant glass-card" : "message-user";
    const pendingClass = item.pending ? "message-pending" : "";

    const [renderedChars, setRenderedChars] = useState<string[]>([]);

    useEffect(() => {
        if (item.pending || !isAssistant) {
            setRenderedChars(Array.from(item.text));
            return;
        }

        let i = 0;
        const textArray = Array.from(item.text);
        setRenderedChars([]);

        const interval = setInterval(() => {
            i++;
            setRenderedChars(textArray.slice(0, i));
            if (i >= textArray.length) {
                clearInterval(interval);
            }
        }, 30);

        return () => clearInterval(interval);
    }, [item.text, item.pending, isAssistant]);

    return (
        <div className={`${baseClasses} ${roleClass} ${pendingClass}`}>
            {item.pending ? (
                <div className="assistant-wave" />
            ) : (
                <>
                    <div className="message-content">
                        {isAssistant
                            ? renderedChars.map((char, index) => (
                                  <span key={index} className="typing-char">
                                      {char}
                                  </span>
                              ))
                            : item.text}
                    </div>
                    {isAssistant && <div className="message-meta">模型：— · Tokens：—</div>}
                </>
            )}
        </div>
    );
}
