import os
from flask import Flask, redirect, render_template, request, send_from_directory, current_app, g, jsonify, send_file
import os
import configparser
from pymongo import MongoClient, InsertOne
from bson import ObjectId, Binary
import tempfile
from dotenv import load_dotenv

app = Flask(__name__)
# Atualizando para buscar a URI corretamente
database_url = os.getenv('DB_URI_PASS')
client = MongoClient(database_url)
db = client.mydata
collection = db.mytable
@app.route("/")
def homePage():
    return "Servidor Ok"

@app.route("/inserir")
def inserir():
    file = request.files['file']
    other_data = request.form.to_dict()
    id_objeto = ObjectId()
    if file:
        filename = file.filename
        file_data = Binary(file.read())
        # Insere o arquivo no MongoDB
        document = {'_id':id_objeto, 'filename': filename, 'file_data': file_data}
        # Adiciona outros dados ao documento
        document.update(other_data)
        collection.insert_one(document)
        return jsonify({'message': 'Arquivo e dados guardados'})
    else:
        return jsonify({'message': 'Arquivo não encontrado'}), 404

@app.route("/listar/<pagina>")
@app.route("/listar/")
@app.route("/listar")
def listar(pagina=None):
    total_documentos = collection.count_documents({})
    page = int(pagina) if pagina else 1
    page_size = 10
    start_index = (page - 1) * page_size
    num_pages = total_documentos // page_size + (1 if total_documentos % page_size > 0 else 0)
    final_index = (start_index+10) if ((start_index+10) < total_documentos) else total_documentos
    documentos = collection.find({}).skip(start_index).limit(page_size)
    try:
        result = []
        for data in documentos:
            data['_id'] = str(data['_id'])
            if ('file_data' in data):
                del data['file_data']
            result.append(data)
        return jsonify({'index_inicial':start_index, 'index_final':final_index,'total':total_documentos,'documentos': result})
    except:
        jsonify({"error":"Não foi possível encontrar nenhum dado"})

@app.route('/quantidade_documentos')
def quantidade_documentos():
    try:
        return jsonify({"Quantidade":collection.count_documents({})})
    except:
        return 404
@app.route("/buscar", methods=["GET", "POST"])
def busca():
    try:
        query = request.form.get("search-bar")
        if query:
            index_config = {
                "$search": {
                    "index": "teste-search",
                    "text": {
                        "query": query,
                        "path": {
                            "wildcard": "*"
                        }
                    }
                }
            }
            results = collection.aggregate([index_config])
            formatted_results = []
            for result in results:
                result['_id'] = str(result['_id'])
                del result['file_data']
                formatted_results.append(result)
            return jsonify(formatted_results)
        else:
            return jsonify({"error": "Formulário Inválido"}), 400
    except:
        return jsonify({"error": "Método não permitido"}), 405

@app.route("/baixar", methods=["GET", "POST"])
def baixar():
    id_objeto = request.form.get("_id")
    file_data = collection.find_one({"_id": ObjectId(id_objeto)})
    if file_data:
        # Obter os dados binários
        binary_data = file_data.get('file_data')
        nome = file_data.get('filename')
        # Criar um novo arquivo PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf_file:
            temp_pdf_path = temp_pdf_file.name
            temp_pdf_file.write(binary_data)

        # Enviar o PDF como resposta
        return send_file(temp_pdf_path, as_attachment=True)
    else:
        return "Arquivo não encontrado", 404
        
if __name__ == '__main__':
    app.run(debug=True)
