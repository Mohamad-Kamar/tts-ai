from __future__ import annotations

import shutil
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

import certifi

from .config import DEFAULT_MODEL_URL, DEFAULT_VOICES_URL, ModelFiles, model_files_for_dir


def ensure_model_files(model_dir: Path, refresh: bool = False) -> ModelFiles:
    files = model_files_for_dir(model_dir)
    _ensure_file(files.model_path, DEFAULT_MODEL_URL, refresh=refresh)
    _ensure_file(files.voices_path, DEFAULT_VOICES_URL, refresh=refresh)
    return files


def _ensure_file(path: Path, url: str, refresh: bool) -> None:
    if path.exists() and not refresh:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "tts-local/1.0"})
    temp_path = path.with_suffix(path.suffix + ".part")
    context = ssl.create_default_context(cafile=certifi.where())

    with urlopen(request, context=context) as response, temp_path.open("wb") as handle:
        shutil.copyfileobj(response, handle)

    temp_path.replace(path)
