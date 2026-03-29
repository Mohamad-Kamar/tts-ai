from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import (
    DEFAULT_INPUT_PATH,
    DEFAULT_LANGUAGE,
    DEFAULT_MAX_CHARS,
    DEFAULT_MODEL_DIR,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_PAUSE_MS,
    DEFAULT_SPEED,
    DEFAULT_VOICE,
    MAX_SPEED,
    MIN_SPEED,
)
from .download import ensure_model_files
from .synth import KokoroSynthesizer, SynthesisRequest, write_audio, write_chunk_outputs
from .text import normalize_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate speech from text with Kokoro ONNX."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Input text file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Output WAV file.")
    parser.add_argument("--text", help="Inline text instead of reading from a file.")
    parser.add_argument("--stdin", action="store_true", help="Read text from standard input.")
    parser.add_argument("--phonemes", action="store_true", help="Treat input as phonemes.")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Voice name, for example af_heart.")
    parser.add_argument(
        "--lang",
        default=DEFAULT_LANGUAGE,
        help="Language code for phonemization. Use auto to infer from the voice.",
    )
    parser.add_argument("--speed", type=float, default=DEFAULT_SPEED, help="Speech speed from 0.5 to 2.0.")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help="Soft per-chunk text limit before synthesis.",
    )
    parser.add_argument(
        "--pause-ms",
        type=int,
        default=DEFAULT_PAUSE_MS,
        help="Pause inserted between synthesized chunks.",
    )
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR, help="Directory for model files.")
    parser.add_argument("--refresh-models", action="store_true", help="Redownload model files.")
    parser.add_argument("--list-voices", action="store_true", help="Print available voices and exit.")
    parser.add_argument("--keep-chunks", type=Path, help="Write each chunk to a separate WAV file.")
    parser.add_argument("--no-trim", action="store_true", help="Keep leading and trailing silence.")
    parser.add_argument("--show-settings", action="store_true", help="Print the resolved synthesis settings.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    _validate_args(parser, args)

    try:
        files = ensure_model_files(args.model_dir, refresh=args.refresh_models)
        synthesizer = KokoroSynthesizer(files.model_path, files.voices_path)

        if args.list_voices:
            for voice in synthesizer.list_voices():
                print(voice)
            return 0

        text = _load_input_text(args)
        request = SynthesisRequest(
            text=text,
            voice=args.voice,
            language=args.lang,
            speed=args.speed,
            max_chars=args.max_chars,
            pause_ms=args.pause_ms,
            trim=not args.no_trim,
            is_phonemes=args.phonemes,
        )

        result = synthesizer.synthesize(request)
        write_audio(args.output, result.audio, result.sample_rate)

        if args.keep_chunks:
            write_chunk_outputs(args.keep_chunks, result)

        if args.show_settings:
            print(f"voice={args.voice}")
            print(f"lang={result.language}")
            print(f"speed={args.speed}")
            print(f"chunks={len(result.chunks)}")
            print(f"sample_rate={result.sample_rate}")

        print(f"Wrote {args.output} using voice {args.voice} in {result.language}.")
        return 0
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def _load_input_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return _require_text(normalize_text(args.text))

    if args.stdin:
        return _require_text(normalize_text(sys.stdin.read()))

    return _require_text(normalize_text(args.input.read_text(encoding="utf-8")))


def _require_text(text: str) -> str:
    if not text:
        raise ValueError("Input text is empty.")
    return text


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    sources = sum(bool(source) for source in (args.text is not None, args.stdin))
    if sources > 1:
        parser.error("Use only one of --text or --stdin. --input is the file fallback.")

    if not MIN_SPEED <= args.speed <= MAX_SPEED:
        parser.error(f"--speed must be between {MIN_SPEED} and {MAX_SPEED}.")

    if args.max_chars < 80:
        parser.error("--max-chars must be at least 80.")

    if args.pause_ms < 0:
        parser.error("--pause-ms must be zero or greater.")
