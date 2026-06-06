import os
import shutil
from datetime import datetime

import face_recognition
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
mongo = os.getenv("mongo")
client = MongoClient(mongo)
bd = client["rf"]
imagens = bd["pessoas"]


def gerarTemplate(caminhoImagem):
    imagem = face_recognition.load_image_file(caminhoImagem)
    encodings = face_recognition.face_encodings(imagem)

    if len(encodings) == 0:
        raise ValueError("nenhum rosto na imagem")
    if len(encodings) > 1:
        raise ValueError("so pode haver 1 rosto na imagem")

    return encodings[0].tolist()


def salvarImagem(NomePessoa, nomeImagem, caminhoOrigem):
    os.makedirs("img", exist_ok=True)

    extensao = os.path.splitext(caminhoOrigem)[1]
    nomeArquivo = nomeImagem + extensao
    caminhoDestino = os.path.join("img", nomeArquivo)

    shutil.copy2(caminhoOrigem, caminhoDestino)

    template = gerarTemplate(caminhoDestino)

    imagens.insert_one(
        {
            "NomePessoa": NomePessoa,
            "nomeImagem": nomeImagem,
            "caminho": caminhoDestino,
            "template": template,
            "dataInsercao": datetime.now(),
        }
    )

    return caminhoDestino
