from spacy import load


class NER():
    def __init__(self):
        self.nlp = load('./app/document_reader/models/ner_model')
        self.initial_key = 'preambulo'
        self.labels = {
            'PER': 'pessoa',
            'ORG': 'organizacao',
            'CPF': 'cpf',
            'RG': 'rg',
            'CNPJ': 'cnpj',
            'PRAZO': 'prazo',
            'EMAIL': 'email',
            'TEL': 'telefone',
            'LOC': 'endereco',
            'VALOR': 'valor',
            'PORC': 'porcentagem',
            'DATA': 'data',
            'HORA': 'hora',
            'CCT': 'contrato',
            'CCR': 'concorrencia',
            'SEI': 'sei',
            'SEI_CCT': 'sei_contrato',
            'EDITAL_CCR': 'edital_de_concorrencia',
            'DO': 'dotacao_orcamentaria',
            'CFF': 'cronograma_fisico_financeiro',
            'NE': 'nota_de_empenho'
        }


    def classify_text(self, text_dict: dict) -> dict:
        result = {}
        header_values = ['OBJETO', 'CONTRATANTE', 'CONTRATADO', 'CONTRATADA', 'TIPO']

        for key, list_ in text_dict.items():
            clause = {}

            for paragraph in list_:
                doc = self.nlp(paragraph)

                if key == self.initial_key:
                    for value in header_values:
                        if paragraph[:len(value)] == value:
                            clause[value.lower()] = paragraph
                            continue

                i = 0
                while i < len(doc.ents):
                    ent = doc.ents[i]
                    entity = {}
                    increment = 0

                    if ent.label_ == 'PER':
                        entity['nome'] = ent.text
                        probable_labels = ['CPF', 'RG', 'EMAIL', 'TEL']
                        entity, increment = self.add_entity_attributes(i, probable_labels, entity, doc.ents)

                    elif ent.label_ == 'ORG':
                        entity['razao_social'] = ent.text
                        probable_labels = ['CNPJ', 'LOC', 'EMAIL', 'TEL']
                        entity, increment = self.add_entity_attributes(i, probable_labels, entity, doc.ents)


                    if not bool(entity): # Entity is empty
                        clause[self.labels[ent.label_]] = ent.text
                    else:
                        clause[self.labels[ent.label_]] = entity
                    
                    i += 1 + increment

            if bool(clause):
                result[key] = clause

        return result


    def add_entity_attributes(self, index: int, probable_labels: list, entity: dict, doc_ents):
        increment = 0
        for j in range(len(probable_labels)):
            if index + j + 1 >= len(doc_ents) - 1:
                return (entity, increment)

            next_ent = doc_ents[index + j + 1]
            if next_ent.label_ in probable_labels:    
                entity[self.labels[next_ent.label_]] = next_ent.text
                increment += 1
            else:
                break
        
        return (entity, increment)


if __name__ == '__main__':
    ner = NER()
    print(ner.nlp.get_pipe('ner').labels)