from cleantext import clean


def clean_text(text):
    import re

    # Primeiro, remover quebras de linha indesejadas
    # Supomos que quebras de linha desejadas são duas ou mais quebras de linha consecutivas.
    # As quebras de linha indesejadas são aquelas no meio de frases ou parágrafos.
    lines = text.splitlines()
    cleaned_lines = []
    temp_line = ""
    
    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line == "":  # Linha vazia, pode ser uma quebra de parágrafo desejada
            if temp_line:
                cleaned_lines.append(temp_line)
                temp_line = ""
            cleaned_lines.append("")
        else:
            if temp_line:
                # Se a linha anterior não estava vazia, unir com espaço
                temp_line += " " + stripped_line
            else:
                temp_line = stripped_line
    
    if temp_line:
        cleaned_lines.append(temp_line)

    # Depois, processar quebras de linha desejadas
    # Reunir todas as linhas com uma única quebra de linha, e remover múltiplas quebras de linha
    processed_text = re.sub(r'\n\s*\n', '\n\n', '\n'.join(cleaned_lines))

    return processed_text

# Exemplo de uso
raw_text = """
Este é um exemplo de texto
que contém quebras de linha indesejadas.
O objetivo é unir estas linhas em um
único parágrafo, enquanto preservamos
Ola

as quebras de linha desejadas que indicam
o fim de um parágrafo e o início de outro.
"""

print(clean(raw_text, no_line_breaks=True, lang='eng'))


# cleaned_text = clean_text(raw_text)
# print(cleaned_text)