from __future__ import annotations

import re
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from config.config_manager import get_config


_MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")
_FOLDER_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")

_TASKS: dict[str, dict] = {}
_TASKS_LOCK = threading.Lock()
_DOWNLOAD_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="model-download")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_model_id(model_id: str) -> str:
    value = model_id.strip()
    if not value:
        raise ValueError("model_id cannot be empty")
    if not _MODEL_ID_PATTERN.fullmatch(value):
        raise ValueError("model_id must follow '<namespace>/<repo_name>' format")
    return value


def _validate_folder_name(folder_name: str) -> str:
    value = folder_name.strip()
    if not value:
        raise ValueError("target_folder cannot be empty")
    if not _FOLDER_NAME_PATTERN.fullmatch(value):
        raise ValueError("target_folder must use only letters, digits, '.', '_' or '-', max length 64")
    return value


def _ensure_safe_target_dir(base_model_dir: Path, target_folder: str) -> Path:
    base_dir = base_model_dir.expanduser().resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    target_dir = (base_dir / target_folder).resolve()
    if target_dir == base_dir:
        raise ValueError("target_folder cannot point to model_dir root")
    if base_dir not in target_dir.parents:
        raise ValueError("target_folder resolves outside model_dir")

    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def _update_task(task_id: str, **fields):
    with _TASKS_LOCK:
        task = _TASKS.get(task_id)
        if task is None:
            return
        task.update(fields)
        task["updated_at"] = _now_iso()


def _run_download_task(task_id: str, model_id: str, target_dir: Path):
    _update_task(task_id, status="running")

    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:
        _update_task(task_id, status="failed", error=f"huggingface_hub import failed: {exc}")
        return

    try:
        local_path = snapshot_download(
            repo_id=model_id,
            local_dir=str(target_dir),
            local_dir_use_symlinks=False,
            resume_download=True
        )
    except Exception as exc:
        _update_task(task_id, status="failed", error=str(exc))
        return

    _update_task(
        task_id,
        status="completed",
        local_path=str(Path(local_path).resolve())
    )


def create_download_task(model_id: str, target_folder: str) -> dict:
    """
    Create a background task for downloading a HuggingFace model.

    Security constraints:
    - model_id must be strict '<namespace>/<repo_name>' format
    - target_folder must be a single folder name, no path traversal
    - resulting path must stay inside config.local_model.model_dir
    """
    config = get_config()
    base_model_dir = config.local_model.model_dir
    if base_model_dir is None:
        raise ValueError("config.local_model.model_dir is not set")

    safe_model_id = _validate_model_id(model_id)
    safe_folder_name = _validate_folder_name(target_folder)
    safe_target_dir = _ensure_safe_target_dir(Path(base_model_dir), safe_folder_name)

    task_id = str(uuid4())
    task_info = {
        "task_id": task_id,
        "status": "queued",
        "model_id": safe_model_id,
        "target_folder": safe_folder_name,
        "target_dir": str(safe_target_dir),
        "error": None,
        "local_path": None,
        "created_at": _now_iso(),
        "updated_at": _now_iso()
    }

    with _TASKS_LOCK:
        _TASKS[task_id] = task_info

    _DOWNLOAD_EXECUTOR.submit(_run_download_task, task_id, safe_model_id, safe_target_dir)
    return task_info.copy()
