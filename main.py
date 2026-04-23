import json
from pathlib import Path
from pipeline.extractor import extract_text_from_pdf
from pipeline.cleaner import clean
from pipeline.metadata import extract_metadata
from pipeline.chunker import chunk_text


def process_pdf(pdf_path: str) -> list[dict]:
    print(f"Processando: {pdf_path}")

    result = extract_text_from_pdf(pdf_path)

    if result["has_scanned_pages"]:
        print("  ⚠ PDF tem páginas escaneadas — OCR não implementado ainda, pulando essas páginas.")

    raw_text = "\n".join(p["text"] for p in result["pages"])
    clean_text = clean(raw_text)
    metadata = extract_metadata(raw_text, clean_text, result["filename"])
    chunks = chunk_text(clean_text, metadata)

    print(f"  ✓ {len(chunks)} chunks gerados")
    print(f"  ✓ Título: {metadata['title'][:60]}...")
    print(f"  ✓ Abordagens: {metadata['abordagens']}")
    return chunks


def run():
    input_dir = Path("input")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    pdfs = list(input_dir.glob("*.pdf"))
    if not pdfs:
        print("Nenhum PDF encontrado na pasta input/")
        return

    all_chunks = []
    for pdf in pdfs:
        try:
            chunks = process_pdf(str(pdf))
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"  ✗ Erro ao processar {pdf.name}: {e}")

    output_file = output_dir / "chunks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nPipeline concluído.")
    print(f"Total de chunks: {len(all_chunks)}")
    print(f"Salvo em: {output_file}")


if __name__ == "__main__":
    run()