text = "16.1.5. No caso de descumprimento dos requisitos previstos neste instrumento, estabelecidos com base no Decreto Municipal n. 50.977/2009, o limite de prazo para a sanção administrativa de proibição de contratar com a Administração Pública pelo período de até 03 meses, nos termos do inciso V, do § 8° do art. 72 da Lei Federal n. 9.605/1998, observadas as normas legais e regulamentares pertinentes, independentemente da responsabilização na esfera criminal."


def spacym():
    import spacy

    # Carregar o modelo de linguagem para português
    nlp = spacy.load("pt_core_news_sm")

    # Processar o texto
    doc = nlp(text)

    # Identificar palavras-chave (substantivos, por exemplo)
    keywords_spacy = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"]]

# def rakem():
#     import nltk
#     nltk.download('stopwords')
#     nltk.download('punkt')

#     from rake_nltk import Rake

#     # Inicializar RAKE
#     rake_nltk_var = Rake(language='portuguese')

#     # Extrair palavras-chave
#     rake_nltk_var.extract_keywords_from_text(text)
#     return rake_nltk_var.get_ranked_phrases()


# print("Palavras-chave:", spacym())
# print("Palavras-chave:", rakem())
from gensim.summarization import summarize

summary = summarize(text, word_count=20)

print(summary)