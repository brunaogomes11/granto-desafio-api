from spacy import load


class NER():
    def __init__(self):
        self.nlp = load('./app/document_reader/models/ner-v2_6')
        self.__initial_key = "preambulo"
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
            'NE': 'nota_de_empenho',
            'OBJ': 'objeto',
            'DOC': 'documento',
            'VIG': 'vigencia'
        }

        self.child_name = {}
        self.child_name.update(self.labels)
        self.child_name.update({
            'ORG': 'razao_social',
            'PER': 'nome',
            'DOC': 'tipo',
        })

        # INFO | CHILDREN
        self.probable_labels = {
            'ORG':  [('CNPJ', 'LOC', 'EMAIL', 'TEL'), ('PER')],
            'PER': [('CPF', 'RG', 'EMAIL', 'TEL', 'LOC'), ()],
            'DOC': [('CCT', 'CCR', 'EDITAL_CCR', 'SEI', 'SEI_CCT', 'DO', 'CFF', 'NE'), ()],
            'DATA': [('HORA', 'VIG'), ()],
            'HORA': [('DATA', 'VIG'), ()],
            'VIG': [('DATA', 'HORA'), ()]
        }


    def classify_text(self, text_dict: dict) -> dict:
        result = {}
        find_value = False
        main_keys = []

        for key, list_ in text_dict.items():
            clause = {}

            for paragraph in list_:
                doc = self.nlp(paragraph)
                
                i = 0
                while i < len(doc.ents):
                    ent = doc.ents[i]

                    entity = {}
                    increment = 0

                    if ent.label_ in self.probable_labels.keys():
                        _entity, increment = self.add_entity_attributes(i, doc.ents)
                        entity.update(_entity)
                    
                    if ent.label_ == 'VALOR' and not find_value:
                        if key == self.__initial_key:
                            entity.update({'valor': ent.text})

                        elif self.__initial_key in result.keys():
                            result[self.__initial_key].update({'valor': ent.text})
                        
                        else:
                            for mkey in main_keys:
                                result[mkey].update({'valor': ent.text})

                        find_value = True

                    label = self.auto_label(self.labels[ent.label_], clause)


                    if len(entity.keys()) > 1:
                        clause[label] = entity

                    # elif ent.label_ in ['VALOR', 'PRAZO', 'DATA', 'HORA', 'PORC']:
                    else:
                        clause[label] = ent.text

                    i += 1 + increment

            clause_keys = list(clause.keys())
            
            # Searching for 'Contratante' and 'Contratada'
            if len(clause_keys) > 1:
                for i in range(len(clause_keys) - 1):
                    key_in = clause_keys[i]
                    next_key_in = clause_keys[i + 1]

                    if 'organizacao' in key_in and 'organizacao' in next_key_in:
                        if type(clause[key_in]) is dict and type(clause[next_key_in]) is dict:
                            if key not in main_keys:
                                main_keys.append(key) 

                            contratante = clause.pop(key_in, {})
                            contratada = clause.pop(next_key_in, {})

                            clause.update({
                                self.auto_label('contratante', clause): contratante,
                                self.auto_label('contratada', clause): contratada,
                            })

            if bool(clause):
                result[key] = clause

        return result

    # Searching for the entity's children
    def add_entity_attributes(self, start_index, doc_ents, depth = 0) -> tuple:
        entity = {}
        increment = 0

        entity[self.child_name[doc_ents[start_index].label_]] = doc_ents[start_index].text
        
        ent_probable_labels = self.probable_labels[doc_ents[start_index].label_]

        for j in range(len(ent_probable_labels[depth])):
            if start_index + j + 1 >= len(doc_ents):
                return (entity, increment)

            next_ent = doc_ents[start_index + j + 1]
            label = self.labels[next_ent.label_]
            if next_ent.label_ in ent_probable_labels[depth]:
                entity[self.auto_label(label, entity)] = next_ent.text
                increment += 1

            elif depth < 1 and next_ent.label_ in ent_probable_labels[depth + 1]:
                _entity, _increment = self.add_entity_attributes(start_index + j + 1, doc_ents) #, depth
                entity[self.auto_label(label, entity)] = _entity
                increment += 1 + _increment

            else:
                break

        return (entity, increment)


    def auto_label(self, label: str, entity: dict) -> str:
        i = 0
        label_i = label

        while label_i in entity.keys():
            label_i = f'{label}_{i}'
            i += 1
        return label_i


if __name__ == '__main__':
    ner = NER()
    print(ner.nlp.get_pipe('ner').labels)