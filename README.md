# pbe-document-pipeline

A document preprocessing pipeline designed to clean and structure academic PDF articles on **Evidence-Based Psychology (EBP)** for use as a knowledge base in RAG (Retrieval-Augmented Generation) systems.

This is **Repository 1** of a two-part project. The output of this pipeline feeds directly into [pbe-chatbot](#) (Repository 2), a conversational AI that answers questions about evidence-based psychological interventions by grounding its responses in indexed scientific literature.

---

## The Problem

Academic PDFs are notoriously difficult to process for machine consumption. A PDF that looks clean and readable to a human is often a mess of mixed columns, repeated headers, broken hyphenation, corrupted encodings, and irrelevant sections when parsed programmatically.

Feeding raw PDF text into a vector database produces low-quality embeddings and poor retrieval results — the AI ends up reasoning over journal headers, author affiliations, and bibliography entries instead of actual scientific content.

This pipeline solves that by transforming raw academic PDFs into clean, structured, semantically meaningful chunks ready for indexing.

---

## What Gets Cleaned

The pipeline handles every major category of noise found in academic psychology papers:

**Extraction artifacts**
- Mixed two-column layout text
- Corrupted encoding characters (`â€™` → `'`, `Ã§` → `ç`)
- Typographic ligatures parsed incorrectly (`ﬁ` → `fi`, `ﬂ` → `fl`)
- Invisible characters and control bytes (`\x00`, `\xa0`, `\u200b`)

**Repetitive page structure**
- Journal headers (name, volume, issue, ISSN)
- Page footers (DOI, copyright, page numbers)
- Watermarks ("Downloaded from...", "For personal use only")
- Running author heads ("SILVA ET AL.")

**Non-indexable sections**
- References / bibliography
- Acknowledgements
- Conflict of interest declarations
- Author affiliations and contact info
- Abstract (kept as metadata, not indexed in chunks)
- Isolated keyword lines

**Formatting issues**
- Line-break hyphenation (`trata-\nmento` → `tratamento`)
- Mid-sentence line breaks
- Double/triple spaces
- Tables converted to unstructured linear text
- Footnotes injected into body paragraphs
- Dangling figure references ("See Figure 3")

---

## Metadata Extraction

Each chunk is stored alongside structured metadata extracted from the document:

| Field | Description |
|---|---|
| `title` | Article title |
| `year` | Publication year |
| `doi` | Digital Object Identifier |
| `abordagens` | Therapeutic approaches identified (TCC, ACT, DBT, EMDR, etc.) |
| `tipo_estudo` | Study type (RCT, Systematic Review, Meta-analysis, etc.) |
| `language` | Detected language (`pt` or `en`) |
| `filename` | Source file name |

This metadata enables filtered retrieval in the chatbot — for example, retrieving only CBT studies published after 2015 about social anxiety.

---

## Architecture

```
input/                        # Raw PDF files
    └── article.pdf
        ↓
pipeline/extractor.py         # Step 1-2: Raw text extraction + scanned page detection
        ↓
pipeline/cleaner.py           # Steps 3-7: Full text cleaning pipeline
        ↓
pipeline/metadata.py          # Step 8: Structured metadata extraction
        ↓
pipeline/chunker.py           # Step 9: Semantic chunking with overlap
        ↓
output/chunks.json            # Clean chunks with metadata, ready for vector DB indexing
```

---

## Project Structure

```
pbe-document-pipeline/
├── input/                  # Drop raw PDFs here
├── output/                 # Clean chunks output (JSON)
├── pipeline/
│   ├── __init__.py
│   ├── extractor.py        # PyMuPDF-based extraction, scanned page detection
│   ├── cleaner.py          # Full cleaning pipeline (encoding, structure, formatting)
│   ├── metadata.py         # Title, year, DOI, therapeutic approach detection
│   └── chunker.py          # RecursiveCharacterTextSplitter with semantic separators
├── main.py                 # Orchestrates the full pipeline for all PDFs in input/
├── inspect_chunks.py       # Quick visual inspection of generated chunks
└── requirements.txt
```

---

## Tech Stack

- **PyMuPDF (fitz)** — Primary PDF text extraction
- **pdfplumber** — Fallback for complex layouts
- **ftfy** — Automatic encoding correction
- **LangChain Text Splitters** — Semantic chunking with configurable overlap
- **pandas** — Chunk inspection and quality analysis
- **Streamlit** — Quick demo interface for testing without spinning up the full stack

---

## Getting Started

**Requirements:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/yourusername/pbe-document-pipeline
cd pbe-document-pipeline

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add PDFs to the input/ folder, then run
python main.py
```

Output is saved to `output/chunks.json`.

---

## Design Decisions

**Why clean before chunking, not after?**
Chunking dirty text embeds the noise into the vector space. A chunk containing a journal header mixed with content will produce a misleading embedding that confuses retrieval. Cleaning first ensures every chunk represents a coherent semantic unit.

**Why extract metadata from raw text rather than clean text?**
Fields like DOI, publication year, and journal name are often present only in the header — which is removed during cleaning. The pipeline extracts these fields from the raw text before cleaning, then uses the clean text for title and language detection.

**Why discard the abstract?**
The abstract summarizes the full article. Indexing it alongside the full content creates retrieval redundancy — the same information gets retrieved twice with slightly different wording, which can confuse the LLM's synthesis. The abstract is captured as metadata only.

**Why 800-token chunks with 100-token overlap?**
This size balances semantic coherence (enough context per chunk for meaningful retrieval) with precision (small enough to avoid diluting relevance scores). The 100-token overlap prevents information loss at chunk boundaries, particularly for sentences that span paragraph breaks.

---

## Roadmap

- [ ] OCR support for scanned PDFs (Tesseract integration)
- [ ] HTML source support (PubMed full-text articles)
- [ ] Automatic language detection for mixed-language documents
- [ ] Chunk quality scoring before indexing
- [ ] Direct integration with ChromaDB / FAISS for one-command indexing

---

## Related

- **[pbe-chatbot](#)** — RAG-based chatbot that uses this pipeline's output as its knowledge base. Built with FastAPI, LangChain, ChromaDB, and Angular.