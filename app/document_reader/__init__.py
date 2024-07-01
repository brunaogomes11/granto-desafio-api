from app.document_reader.read_doc import ReadDocument
from app.document_reader.ner_model import NER 
from bson import Binary 
import base64

from datetime import datetime 

import tempfile

ner = NER()
doc_reader = ReadDocument()

def read_and_classify(file_data: Binary, filename: str) -> dict:  
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf_file:
        temp_pdf_path = temp_pdf_file.name
        temp_pdf_file.write(file_data)

    doc = doc_reader.read_document(temp_pdf_path)
    doc = ner.classify_text(doc)

    dt_string = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
    file_data = base64.b64encode(file_data).decode('utf-8')
    file_data_dict = {
        'filename': filename,
        'file_data': file_data,
        'created_at': dt_string,
        'updated_at': dt_string
    }
    doc.update(file_data_dict)
    
    return doc