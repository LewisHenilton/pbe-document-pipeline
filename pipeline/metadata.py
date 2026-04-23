import re


ABORDAGENS = {
    'TCC': [
        'tcc', 'terapia cognitivo-comportamental', 'cognitive behavioral therapy', 'cbt',
        'cognitive behaviour therapy'
    ],
    'ACT': [
        'act', 'terapia de aceitacao e compromisso', 'terapia de aceitação e compromisso',
        'acceptance and commitment therapy'
    ],
    'DBT': [
        'dbt', 'terapia comportamental dialetica', 'terapia comportamental dialética',
        'dialectical behavior therapy', 'dialectical behaviour therapy'
    ],
    'EMDR': [
        'emdr', 'eye movement desensitization', 'dessensibilizacao por movimentos oculares'
    ],
    'EPR': [
        'epr', 'exposicao e prevencao de resposta', 'exposição e prevenção de resposta',
        'exposure and response prevention', 'exposure and ritual prevention'
    ],
    'MBCT': [
        'mbct', 'terapia cognitiva baseada em mindfulness', 'mindfulness-based cognitive therapy'
    ],
    'TAC': [
        'tac', 'ativacao comportamental', 'ativação comportamental',
        'behavioral activation', 'behavioural activation'
    ],
    'TPC': [
        'tpc', 'cpt', 'terapia de processamento cognitivo', 'cognitive processing therapy'
    ],
    'Exposição Prolongada': [
        'exposicao prolongada', 'exposição prolongada', 'prolonged exposure'
    ],
    'TIP': [
        'tip', 'ipt', 'terapia interpessoal', 'interpersonal therapy',
        'interpersonal psychotherapy'
    ],
    'EFT': [
        'eft', 'terapia focada na emocao', 'terapia focada na emoção',
        'emotion focused therapy', 'emotionally focused therapy'
    ],
    'CFT': [
        'cft', 'terapia focada na compaixao', 'terapia focada na compaixão',
        'compassion focused therapy'
    ],
    'Terapia do Esquema': [
        'terapia do esquema', 'schema therapy', 'terapia de esquemas'
    ],
    'Terapia Narrativa': [
        'terapia narrativa', 'narrative therapy'
    ],
    'Terapia Centrada na Pessoa': [
        'terapia centrada na pessoa', 'person-centered therapy', 'person centred therapy',
        'client-centered therapy', 'abordagem centrada na pessoa', 'rogers'
    ],
    'Terapia Psicodinâmica': [
        'psicodinamica', 'psicodinâmica', 'psychodynamic', 'psicanali',
        'psicanalítica', 'psychoanalytic', 'terapia psicodinamica'
    ],
    'Mindfulness': [
        'mindfulness', 'atencao plena', 'atenção plena', 'meditacao', 'meditação'
    ],
    'Terapia Comportamental': [
        'terapia comportamental', 'behavioral therapy', 'behaviour therapy',
        'behaviorismo', 'behaviorista'
    ],
    'Terapia Breve Estratégica': [
        'terapia breve', 'terapia estrategica', 'terapia estratégica',
        'brief strategic therapy', 'brief therapy'
    ],
}

TIPOS_ESTUDO = {
    'Meta-análise': ['meta-analise', 'meta-análise', 'meta-analysis'],
    'Revisão Sistemática': ['revisao sistematica', 'revisão sistemática', 'systematic review'],
    'RCT': ['ensaio clinico randomizado', 'randomized controlled trial', 'rct'],
    'Estudo de Caso': ['estudo de caso', 'case study', 'case report'],
    'Revisão Narrativa': ['revisao narrativa', 'narrative review'],
}


def extract_title(text: str) -> str:
    lines = text.strip().split('\n')
    title_lines = []
    
    stop_patterns = re.compile(
        r'(?i)^(resumo|abstract|introduc|keywords?|palavras[- ]chave|\d+\.|silva|oliveira|santos|journal|vol\.|downloaded|correspondência)',
        re.IGNORECASE
    )

    for line in lines[:20]:
        line = line.strip()
        if not line:
            if title_lines:
                break
            continue
        if stop_patterns.match(line):
            break
        if len(line) > 20:
            title_lines.append(line)

    return ' '.join(title_lines) if title_lines else 'Título não identificado'

def extract_year(text: str) -> str | None:
    match = re.search(r'\b(19|20)\d{2}\b', text)
    return match.group(0) if match else None


def extract_doi(text: str) -> str | None:
    match = re.search(r'10\.\d{4,}/[\w./\-]+', text)
    return match.group(0) if match else None


def extract_abordagens(text: str) -> list[str]:
    text_lower = text.lower()
    encontradas = []
    for nome, termos in ABORDAGENS.items():
        if any(t in text_lower for t in termos):
            encontradas.append(nome)
    return encontradas


def extract_tipo_estudo(text: str) -> list[str]:
    text_lower = text.lower()
    encontrados = []
    for nome, termos in TIPOS_ESTUDO.items():
        if any(t in text_lower for t in termos):
            encontrados.append(nome)
    return encontrados


def extract_language(text: str) -> str:
    portuguese_markers = ['que', 'com', 'para', 'uma', 'dos', 'nas', 'foi', 'são']
    english_markers = ['the', 'and', 'with', 'for', 'this', 'that', 'was', 'were']
    words = text.lower().split()[:200]
    pt = sum(1 for w in words if w in portuguese_markers)
    en = sum(1 for w in words if w in english_markers)
    return 'pt' if pt >= en else 'en'


def extract_metadata(raw_text: str, clean_text: str, filename: str) -> dict:
    return {
        'filename': filename,
        'title': extract_title(clean_text),  # usa texto limpo
        'year': extract_year(raw_text),       # usa bruto pra pegar ano do cabeçalho
        'doi': extract_doi(raw_text),         # usa bruto pra pegar DOI do cabeçalho
        'abordagens': extract_abordagens(raw_text),
        'tipo_estudo': extract_tipo_estudo(raw_text),
        'language': extract_language(clean_text),
    }


if __name__ == "__main__":
        import sys
        import json
        from pipeline.extractor import extract_text_from_pdf
        from pipeline.cleaner import clean

        if len(sys.argv) < 2:
            print("Uso: python -m pipeline.metadata <caminho_do_pdf>")
            sys.exit(1)

        result = extract_text_from_pdf(sys.argv[1])
        raw_text = "\n".join(p["text"] for p in result["pages"])
        clean_text = clean(raw_text)
        metadata = extract_metadata(raw_text, clean_text, result["filename"])

        print(json.dumps(metadata, ensure_ascii=False, indent=2))