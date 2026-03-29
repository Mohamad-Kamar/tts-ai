from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_INPUT_PATH = Path("input.txt")
DEFAULT_OUTPUT_PATH = Path("output.wav")
DEFAULT_MODEL_DIR = Path("models")
DEFAULT_MODEL_PATH = DEFAULT_MODEL_DIR / "kokoro-v1.0.onnx"
DEFAULT_VOICES_PATH = DEFAULT_MODEL_DIR / "voices-v1.0.bin"

DEFAULT_MODEL_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
    "model-files-v1.0/kokoro-v1.0.onnx"
)
DEFAULT_VOICES_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
    "model-files-v1.0/voices-v1.0.bin"
)

DEFAULT_VOICE = "af_heart"
DEFAULT_LANGUAGE = "auto"
DEFAULT_SPEED = 1.0
DEFAULT_MAX_CHARS = 500
DEFAULT_PAUSE_MS = 80

MIN_SPEED = 0.5
MAX_SPEED = 2.0

VOICE_PREFIX_TO_LANG = {
    "af_": "en-us",
    "am_": "en-us",
    "bf_": "en-gb",
    "bm_": "en-gb",
    "ef_": "es",
    "em_": "es",
    "ff_": "fr-fr",
    "hf_": "hi",
    "hm_": "hi",
    "if_": "it",
    "im_": "it",
    "jf_": "ja",
    "jm_": "ja",
    "pf_": "pt-br",
    "pm_": "pt-br",
    "zf_": "zh",
    "zm_": "zh",
}


@dataclass(frozen=True, slots=True)
class ModelFiles:
    model_path: Path
    voices_path: Path


def model_files_for_dir(model_dir: Path) -> ModelFiles:
    return ModelFiles(
        model_path=model_dir / DEFAULT_MODEL_PATH.name,
        voices_path=model_dir / DEFAULT_VOICES_PATH.name,
    )


def infer_language_for_voice(voice: str) -> str:
    for prefix, language in VOICE_PREFIX_TO_LANG.items():
        if voice.startswith(prefix):
            return language
    return "en-us"
