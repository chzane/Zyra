import { useEffect, useState } from "react";


function App() {
    const [inputValue, setInputValue] = useState<string>("");

    useEffect(() => {
        const lines = inputValue.split("\n").length;
        const estimatedWrappedLines = Math.ceil(inputValue.length / 32);
        const extraLines = Math.max(lines, estimatedWrappedLines);
        const desiredHeight = Math.min(760, 180 + extraLines * 24);
        void window.zyra.setWindowHeight(desiredHeight);
    }, [inputValue]);

    return (
        <div>
            <textarea
                value={inputValue}
                onChange={(event) => setInputValue(event.target.value)}
                placeholder=""
                rows={3}
                style={{ width: "100%" }}
            />
        </div>
    );
}

export default App;
