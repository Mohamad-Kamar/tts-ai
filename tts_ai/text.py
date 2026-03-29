from __future__ import annotations

import re

WHITESPACE_RE = re.compile(r"[ \t]+")
PARAGRAPH_RE = re.compile(r"\n\s*\n+")
SENTENCE_RE = re.compile(r"(?<=[.!?;:])\s+")
CLAUSE_RE = re.compile(r"(?<=[,])\s+")


def normalize_text(text: str) -> str:
    lines = [WHITESPACE_RE.sub(" ", line.strip()) for line in text.splitlines()]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def chunk_text(text: str, max_chars: int) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []

    paragraphs = [part.strip() for part in PARAGRAPH_RE.split(normalized) if part.strip()]
    chunks: list[str] = []

    for paragraph in paragraphs:
        sentences = [part.strip() for part in SENTENCE_RE.split(paragraph) if part.strip()]
        current = ""

        for sentence in sentences:
            for piece in _split_oversized(sentence, max_chars):
                candidate = piece if not current else f"{current} {piece}"
                if current and len(candidate) > max_chars:
                    chunks.append(current)
                    current = piece
                else:
                    current = candidate

        if current:
            chunks.append(current)

    return _merge_tiny_tail(chunks, max_chars=max_chars)


def _split_oversized(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    pieces = [text]
    for splitter in (CLAUSE_RE, None):
        next_pieces: list[str] = []
        for piece in pieces:
            if len(piece) <= max_chars:
                next_pieces.append(piece)
                continue
            next_pieces.extend(_split_piece(piece, max_chars=max_chars, splitter=splitter))
        pieces = next_pieces

    return pieces


def _split_piece(text: str, max_chars: int, splitter: re.Pattern[str] | None) -> list[str]:
    parts = text.split() if splitter is None else [part.strip() for part in splitter.split(text)]
    parts = [part for part in parts if part]

    if not parts:
        return [text]

    chunks: list[str] = []
    current = ""

    for part in parts:
        if len(part) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_long_token(part, max_chars=max_chars))
            continue

        candidate = part if not current else f"{current} {part}"
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = part
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def _split_long_token(text: str, max_chars: int) -> list[str]:
    return [text[index : index + max_chars] for index in range(0, len(text), max_chars)]


def _merge_tiny_tail(chunks: list[str], max_chars: int) -> list[str]:
    if len(chunks) < 2:
        return chunks

    merged = list(chunks)
    if len(merged[-1]) >= 80:
        return merged

    candidate = f"{merged[-2]} {merged[-1]}"
    if len(candidate) <= max_chars:
        merged[-2] = candidate
        merged.pop()

    return merged
