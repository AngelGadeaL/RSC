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
import os
import subprocess
import json
import sys
from dotenv import load_dotenv
#CORS = Cross- Origin Resource Sharing

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Determinar la ruta al ejecutable de Azure CLI
def get_az_cli_path():
    # En Windows, Azure CLI se instala típicamente en:
    windows_paths = [
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Azure CLI\bin\az.cmd",
        r"C:\Program Files (x86)\Azure CLI\bin\az.cmd"
    ]
    
    # Comprobar si existe en alguna de las rutas habituales
    for path in windows_paths:
        if os.path.exists(path):
            return path
    
    # Si no se encuentra en las rutas habituales, intentar con el comando directo
    # que funcionará si está en el PATH
    return "az"

# Ruta al ejecutable de Azure CLI
AZ_CLI_PATH = get_az_cli_path()

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

# Endpoint para obtener recursos de un grupo específico
@app.get("/azure-resources/")
def get_azure_resources(search: str = None):
    try:
        # Obtener recursos del grupo de recursos RSGYAPE001 usando Azure CLI a través de PowerShell
        print(f"Ejecutando Azure CLI a través de PowerShell")
        print("Consultando recursos del grupo RSGYAPE001...")
        
        # Comando PowerShell para ejecutar Azure CLI
        powershell_command = "powershell -Command \"az resource list --resource-group RSGYAPE001\""
        
        # Este comando utiliza la autenticación actual de Azure CLI
        result = subprocess.run(
            powershell_command,
            shell=True,
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error en Azure CLI: {result.stderr}")
            return {"error": f"Error al ejecutar Azure CLI: {result.stderr}"}
        
        resources_json = result.stdout
        print(f"Datos recibidos de Azure CLI: {len(resources_json)} bytes")
        
        try:
            resources = json.loads(resources_json)
        except json.JSONDecodeError:
            return {"error": "Error al decodificar la respuesta de Azure CLI"}
        
        # Formatear los recursos para la respuesta
        formatted_resources = []
        for resource in resources:
            formatted_resources.append({
                "id": resource["id"],
                "name": resource["name"], 
                "type": resource["type"],
                "location": resource.get("location", "Global")
            })
        
        # Filtrar por término de búsqueda si se proporciona
        if search and search.strip():
            search = search.strip()
            results = []
            
            for resource in formatted_resources:
                if (search.lower() in resource["name"].lower() or 
                    search.lower() in resource["type"].lower() or
                    search.lower() in resource.get("location", "").lower()):
                    results.append(resource)
            
            return {"resources": results}
        
        # Si no hay filtro, devolver todos los recursos
        return {"resources": formatted_resources}
        
    except Exception as e:
        print(f"Error al obtener recursos: {str(e)}")
        return {"error": f"Error al obtener recursos: {str(e)}"}