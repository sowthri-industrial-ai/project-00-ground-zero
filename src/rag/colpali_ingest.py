"""ColPali vision embeddings · 2-3 structure-rich pages from NIST doc."""
from __future__ import annotations
import asyncio
from pathlib import Path
from src.config import get_settings

TARGET_PAGES = [14, 22, 31]


def render_pages(pdf_path: str, pages: list[int], out_dir: str) -> list[Path]:
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return []
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    images = convert_from_path(pdf_path, dpi=150, first_page=min(pages), last_page=max(pages))
    saved = []
    for p in pages:
        idx = p - min(pages)
        if idx < len(images):
            path = out / f"page_{p:03d}.png"
            images[idx].save(path, "PNG")
            saved.append(path)
    return saved


async def ingest(pdf_path: str = "data/nist-ai-rmf.pdf") -> int:
    s = get_settings()
    try:
        from colpali_engine.models import ColPali, ColPaliProcessor
        import torch
        from PIL import Image
        model = ColPali.from_pretrained("vidore/colpali-v1.2", torch_dtype=torch.float32).eval()
        processor = ColPaliProcessor.from_pretrained("vidore/colpali-v1.2")
        paths = render_pages(pdf_path, TARGET_PAGES, ".colpali_pages")
        if not paths:
            return 0
        images = [Image.open(p) for p in paths]
        batch = processor.process_images(images)
        with torch.no_grad():
            embeddings = model(**batch)
    except ImportError:
        print("colpali-engine not installed · scaffold only · install via requirements-brief-e.txt")
        return 0

    import asyncpg
    conn = await asyncpg.connect(s.pg_dsn)
    await conn.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE TABLE IF NOT EXISTS colpali_chunks (
            id SERIAL PRIMARY KEY, page_id INT, patch_id INT, page_image_path TEXT, embedding vector(128)
        );
    """)
    total = 0
    for pi, page in enumerate(TARGET_PAGES):
        for pat_i, vec in enumerate(embeddings[pi]):
            await conn.execute(
                "INSERT INTO colpali_chunks(page_id, patch_id, page_image_path, embedding) VALUES($1,$2,$3,$4)",
                page, pat_i, f".colpali_pages/page_{page:03d}.png", str(vec.tolist()),
            )
            total += 1
    await conn.close()
    return total


if __name__ == "__main__":
    print(f"ColPali indexed {asyncio.run(ingest())} patches")
