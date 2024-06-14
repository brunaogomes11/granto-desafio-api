import re

# pdf_path = "./test/data/minuta2.pdf"

text = """
ID: 123.456.789 Data de Nascimento: 12/04/1980. O número de contrato é 987.654.321.
Data de expiração: 15-09-2025. O cliente deve verificar o documento ID: 321.654.987. Mas no dia 19.11.2005 ele nasceu.
"""

# Expressão regular para IDs com pontos
id_pattern = r'\b\d{3}\.\d{3}\.\d{3}\b'

# Expressão regular para datas com diferentes formatos
date_pattern = r'\b\d{2}[-/.]\d{2}[-/.]\d{4}\b'

# Expressão regular para capturar contexto ao redor da entidade
context_window = 5  # Número de palavras antes e depois


def find_entities_with_context(text, entity_pattern, context_window=5):
    matches = []
    for match in re.finditer(entity_pattern, text):
        day, month, year = match.groups()
        standardized_date = f'{year}-{month}-{day}'
        return standardized_date

    #     # Contexto antes e depois
    #     before = text[max(0, start - 100):start].split()[-context_window:]
    #     after = text[end:end + 100].split()[:context_window]
        
    #     context = {
    #         'entity': match.group(),
    #         'before': ' '.join(before),
    #         'after': ' '.join(after)
    #     }
    #     matches.append(context)
    # return matches

# Encontrar IDs com contexto
id_matches = find_entities_with_context(text, id_pattern)
print("IDs com contexto:")
for match in id_matches:
    print(f"ID: {match['entity']}")
    print(f"Antes: {match['before']}")
    print(f"Depois: {match['after']}\n")

# Encontrar Datas com contexto
date_matches = find_entities_with_context(text, date_pattern)
print("Datas com contexto:")
for match in date_matches:
    print(f"Data: {match['entity']}")
    print(f"Antes: {match['before']}")
    print(f"Depois: {match['after']}\n")