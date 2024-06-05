import os
from flask import Flask, redirect, render_template, request, send_from_directory, current_app, g, jsonify
import os
import configparser
from pymongo import MongoClient, InsertOne

app = Flask(__name__)
# Atualizando para buscar a URI corretamente
client = MongoClient('mongodb+srv://brunogomesper:QZMyiNXxyuaaHyVi@granto-cluster.ydafxyj.mongodb.net/')
db = client.mydata
collection = db.mytable
@app.route("/")
def homePage():
    return render_template("index.html")

@app.route("/insercao")
def insercao():
    return render_template("insercao.html")

@app.route("/listagem", defaults={'lista_db':''})
def listagem(lista_db):
    if (lista_db != ''):
        return render_template('listagem.html', documents=lista_db)
    else:
        mydata_collection = collection.find()
        return render_template("listagem.html", documents=mydata_collection)

@app.route("/busca", methods=["GET","POST"])
def busca():
    if (request.method == "POST"):
        query = request.form.get("search-bar")
        if(query):
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
            return listagem(results)
        else:
            return 404

if __name__ == '__main__':
    app.run(debug=True)
