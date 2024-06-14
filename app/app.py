import os
from flask import Flask, redirect, render_template, request, send_from_directory, current_app, g, jsonify, send_file
import os
import configparser
from pymongo import MongoClient, InsertOne
from bson import ObjectId, Binary
import tempfile
from dotenv import load_dotenv
from app.PDFReader.main import main
from app.PDFReader.src.db import Database 
import base64

app = Flask(__name__)
# Atualizando para buscar a URI corretamente
database_url = os.getenv('URI')
client = MongoClient(database_url)
db = client['Cluster0']
col = db['documents']
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
        db = Database()
        main(db, file_data, filename)
        return jsonify({'message': 'Arquivo e dados guardados'})
    else:
        return jsonify({'message': 'Arquivo não encontrado'}), 404

@app.route("/listar/<pagina>")
@app.route("/listar/")
@app.route("/listar")
def listar(pagina=1):
    total_documentos = col.count_documents({})
    page = int(pagina) if pagina else 1
    page_size = 10
    start_index = (page - 1) * page_size
    num_pages = total_documentos // page_size + (1 if total_documentos % page_size > 0 else 0)
    final_index = (start_index+10) if ((start_index+10) < total_documentos) else total_documentos
    documentos = col.find({}).skip(start_index).limit(page_size)
    try:
        result = []
        for data in documentos:
            data['_id'] = str(data['_id'])
            if ('file_data' in data):
                del data['file_data']
            result.append(data)
        return jsonify({'index_inicial':start_index, 'index_final':final_index,'total':total_documentos,'documentos': result, 'num_pages':num_pages})
    except:
        jsonify({"error":"Não foi possível encontrar nenhum dado"})

@app.route('/quantidade_documentos')
def quantidade_documentos():
    try:
        return jsonify({"Quantidade":col.count_documents({})})
    except:
        return 404

@app.route("/buscar/<pagina>/<query>/", methods=['GET', 'POST'])
@app.route("/buscar/<pagina>/<query>", methods=['GET', 'POST'])
@app.route("/buscar/<pagina>/", methods=['GET', 'POST'])
@app.route("/buscar/<pagina>", methods=['GET', 'POST'])
@app.route("/buscar/", methods=['GET', 'POST'])
@app.route("/buscar", methods=['GET', 'POST'])
def busca(query = '', pagina = None):
    if request.method == "POST":
        all_list = [' ', '', '*']
        page = int(pagina) if pagina else 1
        page_size = 10
        start_index = (page - 1) * page_size
        if query not in all_list:
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
            results = col.aggregate([index_config])
            formatted_results = []
            for result in results:
                result['_id'] = str(result['_id'])
                if ('file_data' in result):
                    del result['file_data']
                formatted_results.append(result)
            total_documentos = len(formatted_results)
            num_pages = total_documentos // page_size + (1 if total_documentos % page_size > 0 else 0)
            final_index = (start_index+10) if ((start_index+10) < total_documentos) else total_documentos
            return jsonify({'index_inicial':start_index, 'index_final':final_index,'total':total_documentos,'documentos': formatted_results, 'num_pages':num_pages})

        elif query in all_list:
            total_documentos = col.count_documents({})
            num_pages = total_documentos // page_size + (1 if total_documentos % page_size > 0 else 0)
            final_index = (start_index+10) if ((start_index+10) < total_documentos) else total_documentos
            documentos = col.find({}).skip(start_index).limit(page_size)
            try:
                result = []
                for data in documentos:
                    data['_id'] = str(data['_id'])
                    if ('file_data' in data):
                        del data['file_data']
                    result.append(data)
                return jsonify({'index_inicial':start_index, 'index_final':final_index,'total':total_documentos,'documentos': result, 'num_pages':num_pages})
            except:
                jsonify({"error":"Não foi possível encontrar nenhum dado"}), 404
        else:
            return jsonify({"error": "Formulário Inválido"}), 400
    else:
        return jsonify({"error": "Método não permitido"}), 405

@app.route("/baixar/<id>")
def baixar(id):
    file_data = col.find_one({"_id": ObjectId(id)})
    if file_data:
        # Obter os dados binários
        binary_data = file_data.get('file_data')
        binary_data = base64.b64decode(binary_data)
        nome = file_data.get('filename')
        # Criar um novo arquivo PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf_file:
            temp_pdf_path = temp_pdf_file.name
            temp_pdf_file.write(binary_data)

        # Enviar o PDF como resposta
        return send_file(temp_pdf_path, as_attachment=False, download_name=nome)
    else:
        return "Arquivo não encontrado", 404
        
if __name__ == '__main__':
    app.run(debug=True)
