import type { ReactNode } from "react";

export type SettingsSectionId = "general" | "appearance";

export type ZyraSettings = {
    general: {
        launchOnStartup: boolean;
    };
    appearance: {
        compactMode: boolean;
    };
};

export type SettingsSection = {
    id: SettingsSectionId;
    title: string;
    icon: ReactNode;
    render: (args: {
        value: ZyraSettings;
        setValue: (next: ZyraSettings) => void;
    }) => ReactNode;
};

export const SETTINGS_STORAGE_KEY = "zyra.settings";

export const DEFAULT_SETTINGS: ZyraSettings = {
    general: {
        launchOnStartup: false,
    },
    appearance: {
        compactMode: false,
    },
};

export const SETTINGS_SECTIONS: SettingsSection[] = [
    {
        id: "general",
        title: "通用",
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
        ),
        render: ({ value, setValue }) => {
            return (
                <div className="settings-section settings-glass-card">
                    <div className="settings-row">
                        <div className="settings-label">开机启动</div>
                        <label className="settings-switch">
                            <input
                                type="checkbox"
                                checked={value.general.launchOnStartup}
                                onChange={(e) =>
                                    setValue({
                                        ...value,
                                        general: { ...value.general, launchOnStartup: e.target.checked },
                                    })
                                }
                            />
                            <span className="settings-slider" />
                        </label>
                    </div>
                </div>
            );
        },
    },
    {
        id: "appearance",
        title: "外观",
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20"></path>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
        ),
        render: ({ value, setValue }) => {
            return (
                <div className="settings-section settings-glass-card">
                    <div className="settings-row">
                        <div className="settings-label">紧凑模式</div>
                        <label className="settings-switch">
                            <input
                                type="checkbox"
                                checked={value.appearance.compactMode}
                                onChange={(e) =>
                                    setValue({
                                        ...value,
                                        appearance: { ...value.appearance, compactMode: e.target.checked },
                                    })
                                }
                            />
                            <span className="settings-slider" />
                        </label>
                    </div>
                </div>
            );
        },
    },
];
