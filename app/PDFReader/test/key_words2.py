import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from unidecode import unidecode
import re

# Baixar pacotes necessários
nltk.download('punkt')
nltk.download('stopwords')

# Texto original
text = """
Obriga-se a CONTRATANTE a fornecer à CONTRATADA todos os dados, documentos e informações que se façam necessários ao bom desempenho dos serviços ora contratados, em tempo hábil, nenhuma responsabilidade cabendo à segunda acaso recebidos intempestivamente.
"""

def summarize_to_words(text, word_limit=10):
    # Tokenizar o texto em palavras
    words = word_tokenize(text, language='portuguese')
    
    # Filtrar palavras que são apenas alfanuméricas e remover stopwords
    stop_words = set(stopwords.words('portuguese'))
    filtered_words = [word for word in words if word.isalnum() and word.lower() not in stop_words]
    
    # Limitar o resumo ao número máximo de palavras
    summary = ' '.join(filtered_words[:word_limit])
    return summary

def create_json_key(text):
    # Normalizar o texto para criar uma chave JSON
    normalized_text = unidecode(text)
    normalized_text = re.sub(r'\W+', '_', normalized_text).lower()
    return normalized_text

# Obter resumo de até 10 palavras
short_summary = summarize_to_words(text, word_limit=5)
print("Resumo:", short_summary)

# Criar chave JSON a partir do resumo
json_key = create_json_key(short_summary)
print("Chave JSON:", json_key)
