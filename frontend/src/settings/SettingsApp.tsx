import { useMemo, useState } from "react";
import { DEFAULT_SETTINGS, SETTINGS_SECTIONS, SETTINGS_STORAGE_KEY, type SettingsSectionId } from "./registry";
import { useLocalStorageState } from "./useLocalStorageState";

export function SettingsApp() {
    const [settings, setSettings] = useLocalStorageState(SETTINGS_STORAGE_KEY, DEFAULT_SETTINGS);
    const [active, setActive] = useState<SettingsSectionId>("general");

    const current = useMemo(() => SETTINGS_SECTIONS.find((s) => s.id === active) ?? SETTINGS_SECTIONS[0], [active]);

    return (
        <div className="settings-shell">
            <div className="settings-layout">
                <div className="settings-nav settings-glass-card">
                    {SETTINGS_SECTIONS.map((section) => (
                        <button
                            key={section.id}
                            type="button"
                            className={`settings-nav-item ${section.id === current.id ? "active" : ""}`}
                            onClick={() => setActive(section.id)}
                        >
                            {section.icon}
                            {section.title}
                        </button>
                    ))}
                    <div className="settings-nav-spacer" />
                    <button type="button" className="settings-nav-item" onClick={() => window.close()}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M18 6 6 18"></path>
                            <path d="m6 6 12 12"></path>
                        </svg>
                        关闭
                    </button>
                </div>
                <div className="settings-content">
                    <div className="settings-glass-card settings-content-title">{current.title}</div>
                    {current.render({ value: settings, setValue: setSettings })}
                </div>
            </div>
        </div>
    );
}
