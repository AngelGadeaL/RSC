#Caso:
#El equipo de estrategia recibe muchos documentos internos
#(reportes, memos, investigaciones), pero no logra aprovechar
#ese conocimiento historico al tomar decisiones rapidas.

#Objetivo: Desarrollar una herramienta que permita consultar
#texto libre y obtener los documentos internos más relevantes
#usando busqueca semantica (base vectorial)

#Embeddings --sentences tranformers / BERT
#Base Vectorial --FAISS
#API REST ---FASTAPI
#Front End --STREAMLIT /HTML + JS

#S9_APP_LLM/
# --backend/
        #s9_app.py
# --data
        #documentos.txt
# --frontend/
        #index,app.html/py

#------------------------------------------------------
#------------------------------------------------------
#----Creando el backend del modelo---------------------

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
#CORS = Cross- Origin Resource Sharing

#Invocar el objeto para el uso de api
app = FastAPI()

#Habilitar CORS para permitir conexión con Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

#Cargar el documento:
with open("data/documentos.txt","r",encoding="utf-8") as f:
    documentos = [line.strip() for line in f.readlines()]

modelo = SentenceTransformer("all-MiniLM-L6-v2")
embeddings= modelo.encode(documentos,convert_to_numpy=True).astype("float32")
embeddings= embeddings/np.linalg.norm(embeddings,axis=1,keepdims=True)

#FAISS con Inner Product (FlatIP)  (similitud de Coseno)
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)


@app.get("/buscar/")
def buscar(query: str = Query(...),k: int=3):
    vec = modelo.encode([query],convert_to_numpy=True).astype("float32")
    vec = vec/np.linalg.norm(vec)
    similitudes, indices = index.search(vec,k)
    resultados = []
    for i,idx in enumerate(indices[0]):
        resultados.append({
            "documento": documentos[idx],
            "similitud":float(similitudes[0][i])
        })
    return {"consulta": query,"resultados":resultados}