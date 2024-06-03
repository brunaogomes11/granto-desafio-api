import os
from flask import Flask, redirect, render_template, request, send_from_directory, current_app, g
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

@app.route("/listagem")
def listagem():
    mydata_collection = collection.find()
    return render_template("listagem.html", documents=mydata_collection)

if __name__ == '__main__':
    app.run(debug=True)
