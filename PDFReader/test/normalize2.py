import re

text = """
As datas são 12/04/1980, 15-09-2025 e 15.09.2025. (11) 2394-1234, 11-2432-3425
"""

date_pattern = r'\b\d{2}[/.]\d{2}[/.]\d{4}\b'
tel_pattern = r'\b\d{2}[-\s]\d{4,5}\-\d{4}\b'


# # Padrões para IDs e datas
# id_pattern = r'\b\d{3}[.\-\s]?\d{3}[.\-\s]?\d{3}\b'
# date_pattern = r'\b(\d{2})[\/\-.](\d{2})[\/\-.](\d{4})\b'

def standardize_dates(match):
    day, month, year = re.sub(r'[\s.\]', '', match.group())
    # day, month, year = match.groups()
    standardized_date = f'{year}-{month}-{day}'
    return standardized_date    

# Substituir IDs e datas no texto
# standardized_text = re.sub(tel_pattern, standardize_ids, text)

standardized_text = ''
for match in re.finditer(date_pattern, text):
    day, month, year = match.group()
    standardized_date = f'{year}-{month}-{day}'

    standardized_text = re.sub(date_pattern, standardized_date, text)
    print(standardized_text)