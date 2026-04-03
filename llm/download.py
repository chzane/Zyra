from huggingface_hub import snapshot_download
from pathlib import Path


MODEL_ID = input("HuggingFace模型ID: ")

SAVE_DIR = Path(f"./models/{MODEL_ID}")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

local_path = snapshot_download(
    repo_id=MODEL_ID,
    local_dir=str(SAVE_DIR),
    local_dir_use_symlinks=False,
    resume_download=True
)

print(f"模型已下载到: {local_path}")