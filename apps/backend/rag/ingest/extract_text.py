"""
Extração e chunking de PDFs e dados de scraping, com categorização por
documento.

Cada PDF em base/ é classificado numa categoria (ver CATEGORY_MAP) para
permitir o filtro de self_query.py. Se adicionares novos documentos,
adiciona também a entrada correspondente em CATEGORY_MAP -- documentos
sem entrada caem em "geral" por defeito.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import nltk
from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


# Mapeia nome de ficheiro -> categoria. Ajusta conforme adicionares documentos.
CATEGORY_MAP = {
    "constituicao.pdf": "juridico",
    "lei da protecção social.pdf": "juridico",
    "lei da proteção social.pdf": "juridico",
}


def categorize(filename: str) -> str:
    return CATEGORY_MAP.get(filename.lower(), "geral")


@dataclass
class Chunk:
    text: str
    source: str
    page: int
    chunk_id: str
    category: str


def extract_pages(pdf_path: Path) -> list[tuple[int, str]]:
    try:
        reader = PdfReader(str(pdf_path))
    except (PdfReadError, PdfStreamError, OSError) as exc:
        print(f"  !! {pdf_path.name}: PDF ignorado ({exc})")
        return []

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except (PdfReadError, PdfStreamError, OSError) as exc:
            print(f"  !! {pdf_path.name} página {i}: página ignorada ({exc})")
            continue

        text = " ".join(text.split())
        if text.strip():
            pages.append((i, text))
    return pages


def chunk_pdf(pdf_path: Path, target_chars: int = 800, overlap_sentences: int = 2) -> list[Chunk]:
    chunks: list[Chunk] = []
    pages = extract_pages(pdf_path)
    source_name = pdf_path.name
    category = categorize(source_name)

    for page_num, page_text in pages:
        sentences = nltk.sent_tokenize(page_text, language="portuguese")
        if not sentences:
            continue

        current: list[str] = []
        current_len = 0
        idx = 0
        i = 0
        while i < len(sentences):
            sent = sentences[i]
            current.append(sent)
            current_len += len(sent)

            is_last = i == len(sentences) - 1
            if current_len >= target_chars or is_last:
                chunk_text = " ".join(current).strip()
                if chunk_text:
                    chunks.append(
                        Chunk(
                            text=chunk_text,
                            source=source_name,
                            page=page_num,
                            chunk_id=f"{source_name}_p{page_num}_{idx}",
                            category=category,
                        )
                    )
                    idx += 1
                current = current[-overlap_sentences:] if overlap_sentences else []
                current_len = sum(len(s) for s in current)
            i += 1

    return chunks


def chunk_directory(pdf_dir: Path, **kwargs) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    for pdf_file in sorted(pdf_dir.glob("*.pdf")):
        chunks = chunk_pdf(pdf_file, **kwargs)
        print(f"  -> {pdf_file.name} [{categorize(pdf_file.name)}]: {len(chunks)} chunks")
        all_chunks.extend(chunks)
    return all_chunks


def load_scraped_chunks(json_path: Path) -> list[Chunk]:
    if not json_path.exists():
        return []

    raw_chunks = json.loads(json_path.read_text(encoding="utf-8"))
    chunks: list[Chunk] = []
    for idx, item in enumerate(raw_chunks):
        text = " ".join(str(item.get("text", "")).split())
        if not text:
            continue

        chunk_id = item.get("chunk_id") or f"{json_path.stem}_{idx}"
        chunks.append(
            Chunk(
                text=text,
                source=str(item.get("source") or json_path.name),
                page=int(item.get("page") or 1),
                chunk_id=str(chunk_id),
                category=str(item.get("category") or "institucional"),
            )
        )

    print(f"  -> {json_path.name} [scraping]: {len(chunks)} chunks")
    return chunks


def chunk_knowledge_base(base_dir: Path, **kwargs) -> list[Chunk]:
    chunks = chunk_directory(base_dir, **kwargs)
    chunks.extend(load_scraped_chunks(base_dir / "scraped_website.json"))
    return chunks
