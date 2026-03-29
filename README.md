# tts-local

`tts-local` is a small Python CLI for turning text into a local speech file with Kokoro.

## What It Does

- Reads text from `input.txt`, a text file, inline text, or stdin
- Generates speech locally
- Writes a `.wav` file
- Downloads the required model files automatically on first run
- Keeps the default flow simple, with extra control available through flags

## Requirements

- Python 3.10+

## Quick Setup

```bash
python3 -m pip install -r requirements.txt
```

## Quick Start

Default flow:

```bash
python3 tts.py
```

This reads `input.txt` and writes `output.wav`.

## Common Examples

Generate from a file:

```bash
python3 tts.py --input my-script.txt --output my-script.wav
```

Generate from inline text:

```bash
python3 tts.py --text "Hello from Kokoro."
```

Choose a voice and speed:

```bash
python3 tts.py --voice am_michael --speed 0.95
```

List available voices:

```bash
python3 tts.py --list-voices
```

Keep chunk files as separate WAVs:

```bash
python3 tts.py --keep-chunks chunk-audio
```

## Options

- `--input`: input text file, defaults to `input.txt`
- `--output`: output WAV path, defaults to `output.wav`
- `--text`: inline text instead of a file
- `--stdin`: read text from standard input
- `--voice`: voice name, defaults to `af_heart`
- `--lang`: language code, defaults to `auto`
- `--speed`: speech speed from `0.5` to `2.0`
- `--max-chars`: soft chunk size for long text
- `--pause-ms`: pause between generated chunks
- `--list-voices`: print voices and exit
- `--keep-chunks`: save each generated chunk as a separate WAV
- `--refresh-models`: redownload model files
- `--no-trim`: keep leading and trailing silence
- `--show-settings`: print resolved runtime settings

## Notes

- `--lang auto` infers the language from the voice prefix.
- Long text is chunked automatically for more stable output.
- The first run may take longer because model files are downloaded.

## Testing

```bash
python3 -m unittest discover -s tests
```
