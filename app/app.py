from flask import Flask, redirect, render_template, request, send_from_directory, current_app, g, jsonify, send_file
import os
# import configparser
from bson import ObjectId, Binary
import tempfile
from app.document_reader import read_and_classify
from app.db.database import Database
import base64
import json

app = Flask(__name__)
db = Database()


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
        doc = read_and_classify(file_data, filename)
        db.insert_document(doc)

        return jsonify({'message': 'Arquivo e dados guardados'})
    else:
        return jsonify({'message': 'Arquivo não encontrado'}), 404

@app.route("/listar/<pagina>")
@app.route("/listar/")
@app.route("/listar")
def listar(pagina=1):
    total_documentos = db.col.count_documents({})
    page = int(pagina) if pagina else 1
    page_size = 10
    start_index = (page - 1) * page_size
    num_pages = total_documentos // page_size + (1 if total_documentos % page_size > 0 else 0)
    final_index = (start_index+10) if ((start_index+10) < total_documentos) else total_documentos
    documentos = db.col.find({}).skip(start_index).limit(page_size)
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
        return jsonify({"Quantidade": db.col.count_documents({})})
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
        pagina = int(request.args.get('pagina'))
        query = request.args.get('query')
        all_list = [' ', '', '*']
        page = int(pagina) if pagina else 1
        page_size = 10
        start_index = (page - 1) * page_size
        if query not in all_list:
            index_config = {
                "$search": {
                    "index": "searchEntities",
                    "text": {
                        "query": query,
                        "path": {
                            "wildcard": "*"
                        }
                    }
                }
            }
            results = db.col.aggregate([index_config])
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
            total_documentos = db.col.count_documents({})
            num_pages = total_documentos // page_size + (1 if total_documentos % page_size > 0 else 0)
            final_index = (start_index+10) if ((start_index+10) < total_documentos) else total_documentos
            documentos = db.col.find({}).skip(start_index).limit(page_size)
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
    file_data = db.col.find_one({"_id": ObjectId(id)})
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

@app.route("/data_graficos/<grafico>")
def dados_graficos(grafico):
    if grafico != "mapa":
        pipeline = [
            {
                "$addFields": {
                    "valor_seguro_extracao": {
                        "$regexFind": {
                            "input": "$preambulo.valor",
                            "regex": "[0-9,.]+"
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "valor_seguro_limpo": {
                        "$replaceAll": {
                            "input": "$valor_seguro_extracao.match",
                            "find": ".",
                            "replacement": ""
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "valor_seguro_limpo": {
                        "$replaceAll": {
                            "input": "$valor_seguro_limpo",
                            "find": ",",
                            "replacement": "."
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "valor_seguro_numeric": {
                        "$toDouble": "$valor_seguro_limpo"
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$ifNull": ["$preambulo.organizacao.razao_social", "Empresa não especificada"]
                    },
                    "valor_total_seguro": {"$sum": "$valor_seguro_numeric"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "eixo_categorias": "$_id",
                    "eixo_valores": "$valor_total_seguro"
                }
            }
        ]
        resultado = list(db.col.aggregate(pipeline))
        data = {
            "data_name": "Valores Contratados por cada Empresa",
            "data_eixoX": "Valor em Reais",
            "data_eixoY": "Empresa",
            "tipo_grafico": "horizontalBar",
            "data": resultado
        }
        return jsonify(data)
    else:
        with open('app/estados.json', 'r', encoding='utf-8') as f:
            estados = json.load(f)

        # Criar um mapeamento de siglas para nomes de estados
        estados_conhecidos = {estado['sigla']: estado['nome'] for estado in estados}
        # Lista de estados com padrões adicionais para busca
        padroes_adicionais = {
            "Estado do ": "",
            "Estado da ": "",
            "Estado de ": ""
        }

        contagem_estados = {sigla: 0 for sigla in estados_conhecidos}

        # Consulta no MongoDB
        documentos = db.col.find()

        for doc in documentos:
            preambulo = doc.get('preambulo', {})
            endereco = preambulo.get('endereco', '')
            estado_encontrado = None
            
            # Busca por nome de estado ou sigla
            for sigla, nome in estados_conhecidos.items():
                if sigla in endereco or nome in endereco:
                    estado_encontrado = sigla
                    break
            
            # Se não encontrou, busca pelos padrões adicionais
            if not estado_encontrado:
                for padrao in padroes_adicionais.keys():
                    if padrao in endereco:
                        estado_encontrado = padroes_adicionais[padrao]
                        break
            
            # Se ainda não encontrou, define como "Estado não definido"
            if not estado_encontrado:
                estado_encontrado = "Estado não definido"

            # Incrementa a contagem para o estado encontrado
            if estado_encontrado in contagem_estados:
                contagem_estados[estado_encontrado] += 1
            else:
                contagem_estados[estado_encontrado] = 1

        # Formata o resultado para retornar como JSON no formato desejado
        resultado_final = {
            "states": [
                {sigla: {"name": estados_conhecidos.get(sigla, "Estado não definido"), "number": contagem}}
                for sigla, contagem in contagem_estados.items()
            ]
        }


        return jsonify(resultado_final)

if __name__ == '__main__':
    app.run(debug=True)
