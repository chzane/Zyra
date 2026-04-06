from pathlib import Path
from threading import Lock

import joblib
from sentence_transformers import SentenceTransformer


class TaskRouterClient:
    """
    Task router client for routing messages to specific models
    """
    
    def __init__(self, model_dir: str | None = None, preload_languages: list[str] | None = None):
        """
        Initialize the task router client.
        """
        self.model_dir = Path(model_dir)
        self._assets: dict[str, dict] = {}
        self._lock = Lock()

        if preload_languages:
            for language in preload_languages:
                self._load_language_assets(language)

    def _load_language_assets(self, language: str):
        """
        Load the assets for a specific language.
        """
        language_key = str(language).lower().strip()
        if language_key in self._assets:
            return self._assets[language_key]

        classifier_path = self.model_dir / f"router_classifier_{language_key}.pkl"
        label_encoder_path = self.model_dir / f"label_encoder_{language_key}.pkl"
        embedding_model_dir = self.model_dir / f"embedding_model_{language_key}"

        if (
            not classifier_path.exists()
            or not label_encoder_path.exists()
            or not embedding_model_dir.exists()
        ):
            raise FileNotFoundError(
                f"Task router assets not found for language: {language_key}"
            )

        with self._lock:
            if language_key in self._assets:
                return self._assets[language_key]

            classifier = joblib.load(classifier_path)
            label_encoder = joblib.load(label_encoder_path)
            embed_model = SentenceTransformer(str(embedding_model_dir))

            self._assets[language_key] = {
                "classifier": classifier,
                "label_encoder": label_encoder,
                "embed_model": embed_model,
            }

        return self._assets[language_key]

    def route(self, text: str, language: str):
        """
        Route the text to a specific model.
        """
        text_value = str(text).strip()
        if not text_value:
            raise ValueError("input cannot be empty")

        language_key = str(language).lower().strip()
        assets = self._load_language_assets(language_key)

        emb = assets["embed_model"].encode(
            [text_value],
            normalize_embeddings=True
        )

        pred = assets["classifier"].predict(emb)[0]
        label = str(assets["label_encoder"].inverse_transform([pred])[0]).upper()

        route = (
            "local" if label == "LOCAL"
            else "cloud" if label == "CLOUD"
            else "unknown"
        )

        return {
            "input": text_value,
            "language": str(language).lower().strip(),
            "label": label,
            "route": route,
        }
