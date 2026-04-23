import re
import ftfy


def fix_encoding(text: str) -> str:
    return ftfy.fix_text(text)


def fix_ligatures(text: str) -> str:
    ligatures = {
        '\ufb01': 'fi',
        '\ufb02': 'fl',
        '\ufb00': 'ff',
        '\ufb03': 'ffi',
        '\ufb04': 'ffl',
    }
    for char, replacement in ligatures.items():
        text = text.replace(char, replacement)

    # fallback: ligadura já corrompida pelo parser (ﬁ virou I maiúsculo)
    text = re.sub(r'signiIcativ', 'significativ', text)
    text = re.sub(r'eIcaz', 'eficaz', text)
    text = re.sub(r'eIciên', 'eficiên', text)
    text = re.sub(r'beneIci', 'benefici', text)
    text = re.sub(r'especíIc', 'específic', text)
    return text


def remove_header_footer(text: str) -> str:
    patterns = [
        r'(?i)downloaded from .+?\n',
        r'(?i)for personal use only.*?\n',
        r'(?i)unauthorized reproduction prohibited.*?\n',
        r'(?i)journal of .+?issn[\s\S]{0,60}\n',
        r'(?i)vol\.\s*\d+,\s*no\.\s*\d+.*?\n',
        r'^\s*-?\s*\d+\s*-?\s*$',           # número de página isolado
        r'(?i)[A-Z\s]+ ET AL\..*?\n',        # SILVA ET AL.
        r'DOI:\s*[\d./\w-]+',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    return text


def remove_author_info(text: str) -> str:
    patterns = [
        r'(?i)correspond[eê]ncia?:.*?\n',
        r'(?i)ORCID:.*?\n',
        r'(?i)\d+universidade.*?\n',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # autores: padrão "Sobrenome, I.I.N," com números de afiliação
        r'^[A-ZÁÉÍÓÚÂÊÎÔÛÃÕ][a-záéíóúâêîôûãõ]+,\s[A-Z]\.[A-Z]?\..*?\n',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    return text


def remove_non_indexable_sections(text: str) -> str:
    patterns = [
        r'(?i)(referencias?|references?)[\s\S]*$',
        r'(?i)agradecimentos[\s\S]{0,800}',
        r'(?i)declara[cç][aã]o de conflito[\s\S]{0,400}',
        # remove bloco inteiro de resumo/abstract
        r'(?i)(resumo|abstract)[\s\S]{0,1200}?(?=\n\d+\.|\nIntrodu)',
        # palavras-chave — remove a linha inteira que sobrou
        r'(?i)(keywords?|palavras[- ]chave):.*?\n',
        # remove fragmentos soltos de keywords sem contexto (linhas só com vírgulas e palavras curtas)
        r'^(?:[A-Za-záéíóú]+,\s*){2,}[A-Za-záéíóú]+\s*$',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    return text

def remove_tables(text: str) -> str:
    # detecta blocos que parecem tabela: linhas curtas consecutivas com números
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # linha de legenda de tabela/figura
        if re.match(r'(?i)^(tabela|figura|table|figure)\s*\d+\.', line):
            i += 1
            # pula as próximas linhas curtas que são o conteúdo da tabela
            while i < len(lines) and len(lines[i].strip()) < 60:
                i += 1
            continue
        result.append(lines[i])
        i += 1
    return '\n'.join(result)

def fix_hyphenation(text: str) -> str:
    # palavra hife- \n nada → palavra hifenada correta
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    return text

def remove_figure_references(text: str) -> str:
    # remove referências soltas de figura sem conteúdo
    text = re.sub(r'(?i)ver figura\s*\d+[^.]*\.', '', text)
    text = re.sub(r'(?i)see figure\s*\d+[^.]*\.', '', text)
    return text


def remove_footnotes(text: str) -> str:
    # remove notas de rodapé injetadas no corpo
    text = re.sub(r'(?i)nota de rodape\s*\d*:.*?(?=\n\n|\n\d+\.|\Z)', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)footnote\s*\d*:.*?(?=\n\n|\n\d+\.|\Z)', '', text, flags=re.DOTALL)
    return text

def fix_line_breaks(text: str) -> str:
    # quebras de linha no meio de frase (linha não termina com ponto)
    text = re.sub(r'(?<![.\n])\n(?![A-Z\d\n])', ' ', text)
    return text


def normalize_spaces(text: str) -> str:
    text = re.sub(r'[ \t]{2,}', ' ', text)        # espaços duplos
    text = re.sub(r'\n{3,}', '\n\n', text)         # linhas em branco excessivas
    text = re.sub(r'[\x00\xa0\u200b]', ' ', text)  # espaços invisíveis
    return text.strip()


def clean(text: str) -> str:
    text = fix_encoding(text)
    text = fix_ligatures(text)
    text = remove_header_footer(text)
    text = remove_author_info(text)
    text = remove_non_indexable_sections(text)
    text = remove_tables(text) 
    text = remove_figure_references(text)
    text = remove_footnotes(text) 
    text = fix_hyphenation(text)
    text = fix_line_breaks(text)
    text = normalize_spaces(text)
    return text


if __name__ == "__main__":
    import sys
    from pipeline.extractor import extract_text_from_pdf

    if len(sys.argv) < 2:
        print("Uso: python -m pipeline.cleaner <caminho_do_pdf>")
        sys.exit(1)

    result = extract_text_from_pdf(sys.argv[1])
    full_text = "\n".join(p["text"] for p in result["pages"])

    print("=== TEXTO BRUTO ===\n")
    print(full_text[:1500])
    print("\n\n=== TEXTO LIMPO ===\n")
    print(clean(full_text)[:1500])