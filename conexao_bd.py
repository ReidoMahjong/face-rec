import io
import os
from datetime import datetime

import numpy as np
import face_recognition
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
mongo = os.getenv("mongo")
client = MongoClient(mongo)
bd = client["rf"]
imagens = bd["pessoas"]


"""Gera o encoding facial a partir dos bytes da imagem (sem salvar no disco)."""
def gerarTemplate(imagemBytes: bytes):
    imagem = face_recognition.load_image_file(io.BytesIO(imagemBytes))
    encodings = face_recognition.face_encodings(imagem)

    if len(encodings) == 0:
        raise ValueError("nenhum rosto na imagem")
    if len(encodings) > 1:
        raise ValueError("so pode haver 1 rosto na imagem")

    return encodings[0].tolist()

"""Gera o template e salva apenas os metadados no MongoDB."""
def salvarImagem(nomePessoa: str, nomeImagem: str, imagemBytes: bytes):
    template = gerarTemplate(imagemBytes)

    imagens.insert_one(
        {
            "NomePessoa": nomePessoa,
            "nomeImagem": nomeImagem,
            "template": template,
            "dataInsercao": datetime.now(),
        }
    )

def carregarTemplates():
    registros = imagens.find({"template": {"$exists": True}})
    templates = []
    for registro in registros:
        templates.append(
            {"nome": registro["NomePessoa"], "template": np.array(registro["template"])}
        )
    return templates
