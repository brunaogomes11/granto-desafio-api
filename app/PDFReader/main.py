from app.PDFReader.src.read_pdf import ReadDocument
from app.PDFReader.src.ner_model import NER
from pprint import pprint
from app.PDFReader.src.db import Database 
import tempfile
from time import time
from json import dump

ner = NER()

def main(db: Database, file_data, filename):  
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf_file:
        temp_pdf_path = temp_pdf_file.name
        temp_pdf_file.write(file_data)
    doc_reader = ReadDocument(temp_pdf_path)

    start = time()

    text_dict = doc_reader.get_text_dict_from_pdf()
    print(text_dict.keys())
    doc = ner.classify_text(text_dict)

    pprint(doc, sort_dicts=False)
    print(time() - start)

    with open('app/PDFReader/test/data/result.json', mode='w') as j:
        dump(doc, j)

    db.insert_document(doc)


if __name__ == '__main__':
    db = Database()
    main(db)