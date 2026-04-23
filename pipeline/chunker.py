from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(clean_text: str, metadata: dict) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
    )

    chunks = splitter.split_text(clean_text)

    result = []
    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 100:  # descarta chunks muito curtos
            continue
        result.append({
            "chunk_index": i,
            "text": chunk.strip(),
            "metadata": metadata,
        })

    return result


if __name__ == "__main__":
    import sys
    import json
    from pipeline.extractor import extract_text_from_pdf
    from pipeline.cleaner import clean
    from pipeline.metadata import extract_metadata

    if len(sys.argv) < 2:
        print("Uso: python -m pipeline.chunker <caminho_do_pdf>")
        sys.exit(1)

    result = extract_text_from_pdf(sys.argv[1])
    raw_text = "\n".join(p["text"] for p in result["pages"])
    clean_text = clean(raw_text)
    metadata = extract_metadata(raw_text, clean_text, result["filename"])
    chunks = chunk_text(clean_text, metadata)

    print(f"Total de chunks gerados: {len(chunks)}\n")
    for c in chunks:
        print(f"--- Chunk {c['chunk_index']} ---")
        print(c["text"][:300])
        print()