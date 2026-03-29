from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

from .config import DEFAULT_LANGUAGE, infer_language_for_voice
from .text import chunk_text


@dataclass(frozen=True, slots=True)
class SynthesisRequest:
    text: str
    voice: str
    language: str = DEFAULT_LANGUAGE
    speed: float = 1.0
    max_chars: int = 500
    pause_ms: int = 80
    trim: bool = True
    is_phonemes: bool = False


@dataclass(frozen=True, slots=True)
class SynthesizedChunk:
    index: int
    text: str
    audio: np.ndarray


@dataclass(frozen=True, slots=True)
class SynthesisResult:
    audio: np.ndarray
    sample_rate: int
    language: str
    chunks: list[SynthesizedChunk]


class KokoroSynthesizer:
    def __init__(self, model_path: Path, voices_path: Path):
        self._engine = Kokoro(str(model_path), str(voices_path))

    def list_voices(self) -> list[str]:
        return self._engine.get_voices()

    def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        language = _resolve_language(request.language, request.voice)
        text_chunks = [request.text] if request.is_phonemes else chunk_text(request.text, request.max_chars)
        if not text_chunks:
            raise ValueError("Input text is empty.")

        chunks: list[SynthesizedChunk] = []
        sample_rate = 24000

        for index, text_chunk in enumerate(text_chunks):
            audio, sample_rate = self._engine.create(
                text_chunk,
                voice=request.voice,
                speed=request.speed,
                lang=language,
                is_phonemes=request.is_phonemes,
                trim=request.trim,
            )
            chunks.append(
                SynthesizedChunk(
                    index=index,
                    text=text_chunk,
                    audio=np.asarray(audio, dtype=np.float32).reshape(-1),
                )
            )

        final_audio = _join_audio(chunks, pause_ms=request.pause_ms, sample_rate=sample_rate)
        return SynthesisResult(
            audio=final_audio,
            sample_rate=sample_rate,
            language=language,
            chunks=chunks,
        )


def write_audio(output_path: Path, audio: np.ndarray, sample_rate: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, audio, sample_rate)


def write_chunk_outputs(output_dir: Path, result: SynthesisResult) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for chunk in result.chunks:
        file_name = f"chunk-{chunk.index + 1:03d}.wav"
        write_audio(output_dir / file_name, chunk.audio, result.sample_rate)
        manifest.append({"index": chunk.index, "file": file_name, "text": chunk.text})

    with (output_dir / "chunks.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)


def _resolve_language(language: str, voice: str) -> str:
    if language == DEFAULT_LANGUAGE:
        return infer_language_for_voice(voice)
    return language


def _join_audio(
    chunks: list[SynthesizedChunk],
    pause_ms: int,
    sample_rate: int,
) -> np.ndarray:
    if not chunks:
        return np.array([], dtype=np.float32)

    pause_samples = max(int(sample_rate * (pause_ms / 1000.0)), 0)
    pause = np.zeros(pause_samples, dtype=np.float32)

    parts: list[np.ndarray] = []
    for index, chunk in enumerate(chunks):
        if index and pause_samples:
            parts.append(pause)
        parts.append(chunk.audio)

    return np.concatenate(parts)
