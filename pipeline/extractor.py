import fitz  # pymupdf
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> dict:
    path = Path(pdf_path)
    doc: fitz.Document = fitz.open(pdf_path)
    pages = []

    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page_number": i + 1,
            "text": text,
            "is_empty": len(text.strip()) == 0
        })

    has_scanned = any(p["is_empty"] for p in pages)

    return {
        "filename": path.name,
        "total_pages": len(doc),
        "has_scanned_pages": has_scanned,
        "pages": pages
    }


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Uso: python -m pipeline.extractor <caminho_do_pdf>")
        sys.exit(1)

    result = extract_text_from_pdf(sys.argv[1])
    print(f"Arquivo: {result['filename']}")
    print(f"Total de páginas: {result['total_pages']}")
    print(f"Tem páginas escaneadas: {result['has_scanned_pages']}")
    print(f"\n--- Texto da página 1 ---\n")
    print(result['pages'][0]['text'][:1000])