from __future__ import annotations

import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from threading import RLock

from pydantic import Field

from config.base_config import ZyraBaseData


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class HistoryImageInfo(ZyraBaseData):
    iid: str
    name: str | None = None
    path: str | None = None
    mime_type: str | None = None
    size: int | None = None
    width: int | None = None
    height: int | None = None


class HistoryMessage(ZyraBaseData):
    mid: str
    role: str
    text: str = ""
    created_at: str = Field(default_factory=_now_iso)
    image_ids: list[str] = Field(default_factory=list)
    llm: "HistoryLLMInfo | None" = None


class HistoryTokenUsage(ZyraBaseData):
    completion_tokens: int | None = None
    prompt_cache_hit_tokens: int | None = None
    prompt_cache_miss_tokens: int | None = None
    prompt_tokens: int | None = None
    total_tokens: int | None = None


class HistoryLLMInfo(ZyraBaseData):
    request_model_name: str | None = None
    response_model: str | None = None
    provider_pid: str | None = None
    transport: str | None = None
    usage: HistoryTokenUsage | None = None


class HistoryRecord(ZyraBaseData):
    hid: str
    title: str = ""
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)
    messages: list[HistoryMessage] = Field(default_factory=list)
    images: list[HistoryImageInfo] = Field(default_factory=list)


class HistoryStore:
    def __init__(self):
        self._history_dir: Path | None = None
        self._records_dir: Path | None = None
        self._lock = RLock()

    def set_history_dir(self, history_dir: str | Path):
        path = Path(history_dir)
        path.mkdir(parents=True, exist_ok=True)
        records_dir = path / "records"
        records_dir.mkdir(parents=True, exist_ok=True)
        self._history_dir = path
        self._records_dir = records_dir

    def _require_records_dir(self) -> Path:
        if self._records_dir is None:
            raise ValueError("history directory is not initialized")
        return self._records_dir

    def _record_path(self, hid: str) -> Path:
        return self._require_records_dir() / f"{hid}.json"

    def _load_record_from_path(self, path: Path) -> HistoryRecord:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return HistoryRecord.model_validate(raw)

    def list_records(self) -> list[dict]:
        records_dir = self._require_records_dir()
        items: list[HistoryRecord] = []
        for path in records_dir.glob("*.json"):
            try:
                items.append(self._load_record_from_path(path))
            except Exception:
                continue
        items.sort(key=lambda item: item.updated_at, reverse=True)
        return [
            {
                "hid": item.hid,
                "title": item.title,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "message_count": len(item.messages),
                "image_count": len(item.images),
            }
            for item in items
        ]

    def get_record(self, hid: str) -> HistoryRecord:
        path = self._record_path(hid)
        if not path.exists():
            raise ValueError(f"History not found: {hid}")
        return self._load_record_from_path(path)

    def create_record(self, payload: dict) -> HistoryRecord:
        hid = str(payload.get("hid", "")).strip()
        if not hid:
            raise ValueError("hid is required")

        with self._lock:
            path = self._record_path(hid)
            if path.exists():
                raise ValueError(f"History already exists: {hid}")

            timestamp = _now_iso()
            record = HistoryRecord.model_validate({
                "hid": hid,
                "title": str(payload.get("title", "")).strip(),
                "created_at": payload.get("created_at") or timestamp,
                "updated_at": payload.get("updated_at") or timestamp,
                "messages": payload.get("messages", []),
                "images": payload.get("images", []),
            })
            path.write_text(
                json.dumps(record.model_dump(mode="json"), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return record

    def update_record(self, hid: str, payload: dict) -> HistoryRecord:
        with self._lock:
            current = self.get_record(hid)
            merged = current.model_dump(mode="python")

            for field in ("title", "messages", "images", "created_at"):
                if field in payload:
                    merged[field] = payload[field]

            merged["hid"] = hid
            merged["updated_at"] = _now_iso()
            record = HistoryRecord.model_validate(merged)
            self._record_path(hid).write_text(
                json.dumps(record.model_dump(mode="json"), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return record

    def delete_record(self, hid: str) -> HistoryRecord:
        with self._lock:
            record = self.get_record(hid)
            self._record_path(hid).unlink()
            return record


@lru_cache
def get_history_store() -> HistoryStore:
    return HistoryStore()
