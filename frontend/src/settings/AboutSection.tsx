import { useEffect, useState } from "react";

type ZyraAppInfo = {
    name: string;
    version: string;
    gitRepository: string;
    platform: string;
    isDev: boolean;
};

export function AboutSection() {
    const [info, setInfo] = useState<ZyraAppInfo | null>(null);

    useEffect(() => {
        let cancelled = false;

        const run = async () => {
            try {
                const next = await window.zyra.getAppInfo();
                if (cancelled) {
                    return;
                }
                setInfo(next);
            } catch {
                if (cancelled) {
                    return;
                }
                setInfo(null);
            }
        };

        void run();

        return () => {
            cancelled = true;
        };
    }, []);

    return (
        <div className="settings-section">
            <div className="settings-glass-card">
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%" }}>
                    <img src="/icon/logo.png" alt="Zyra" style={{ width: 80, height: 80 }} />
                    <div style={{ marginTop: 12, fontSize: 26, color: "#000000ff", fontWeight: "bold" }}>Zyra</div>
                    <div style={{ marginTop: 2, fontSize: 14, color: "#414141d1" }}>{info?.version ?? ""}</div>
                    <div style={{ marginTop: 18, fontSize: 14, color: "#414141d1" }}>Made with love ❤️ by Zane</div>
                </div>
            </div>
            {info?.gitRepository && (
                <div className="settings-glass-card" style={{ marginTop: 16, paddingTop: 0, paddingBottom: 10 }}>
                    <div className="about-actions">
                        <button
                            type="button"
                            className="about-action"
                            onClick={() => window.open(info?.gitRepository, "_blank", "noopener,noreferrer")}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8" />
                            </svg>
                            {info?.gitRepository.replace(/^https:\/\/github\.com\//, "").replace(/\/$/, "")}
                        </button>
                        <a href={`${info?.gitRepository.replace(/\/$/, "")}/issues`} target="_blank" rel="noopener noreferrer" className="about-action">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M4.978.855a.5.5 0 1 0-.956.29l.41 1.352A5 5 0 0 0 3 6h10a5 5 0 0 0-1.432-3.503l.41-1.352a.5.5 0 1 0-.956-.29l-.291.956A5 5 0 0 0 8 1a5 5 0 0 0-2.731.811l-.29-.956z" />
                                <path d="M13 6v1H8.5v8.975A5 5 0 0 0 13 11h.5a.5.5 0 0 1 .5.5v.5a.5.5 0 1 0 1 0v-.5a1.5 1.5 0 0 0-1.5-1.5H13V9h1.5a.5.5 0 0 0 0-1H13V7h.5A1.5 1.5 0 0 0 15 5.5V5a.5.5 0 0 0-1 0v.5a.5.5 0 0 1-.5.5zm-5.5 9.975V7H3V6h-.5a.5.5 0 0 1-.5-.5V5a.5.5 0 0 0-1 0v.5A1.5 1.5 0 0 0 2.5 7H3v1H1.5a.5.5 0 0 0 0 1H3v1h-.5A1.5 1.5 0 0 0 1 11.5v.5a.5.5 0 1 0 1 0v-.5a.5.5 0 0 1 .5-.5H3a5 5 0 0 0 4.5 4.975" />
                            </svg>
                            反馈 Bug
                        </a>
                        <button
                            type="button"
                            className="about-action"
                            onClick={() => window.open(`${info?.gitRepository.replace(/\/$/, "")}/releases`, "_blank", "noopener,noreferrer")}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor">
                                <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z" />
                                <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466" />
                            </svg>
                            检查更新
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
