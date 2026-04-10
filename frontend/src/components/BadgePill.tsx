import type { BadgeItem } from "../types";

type BadgePillProps = {
    item: BadgeItem;
    onClick?: () => void;
    onRemove?: () => void;
};

export function BadgePill({ item, onClick, onRemove }: BadgePillProps) {
    return (
        <div className={`badge-pill badge-${item.kind} glass-card`} title={item.fullText} onClick={onClick}>
            <span className="badge-content">{item.label}</span>
            {onRemove && (
                <span
                    className="badge-remove"
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemove();
                    }}
                >
                    &times;
                </span>
            )}
        </div>
    );
}
