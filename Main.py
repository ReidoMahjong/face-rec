import os
import shutil

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import conexao_bd as bd
import reconhecer_rosto as rr

app = FastAPI()

# permite que o browser se comunique com a API
# em producao, troque "*" pelo dominio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
def frontend():
    return FileResponse("index.html")


@app.get("/detalhes")
def status():
    return {"status": "online"}


@app.post("/cadastrar")
async def cadastrar(
    nomePessoa: str = Form(...),
    nomeImagem: str = Form(...),
    imagem: UploadFile = File(...),
):

    # validação do arquivo
    if not imagem.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Formato invalido. Use JPG ou PNG.")

    os.makedirs("img", exist_ok=True)
    extensao = os.path.splitext(imagem.filename)[1]
    caminhoTemp = f"img/temp_{nomeImagem}{extensao}"

    with open(caminhoTemp, "wb") as buffer:
        shutil.copyfileobj(imagem.file, buffer)

    try:
        destino = bd.salvarImagem(nomePessoa, nomeImagem, caminhoTemp)
        return {"mensagem": "Imagem cadastrada com sucesso", "caminho": destino}
    except ValueError as e:
        os.remove(caminhoTemp)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        os.remove(caminhoTemp)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reconhecer")
async def reconhecer(frame: UploadFile = File(...)):

    # recebe iframe do browser
    conteudo = await frame.read()
    resultado = rr.processarFrame(conteudo)
    return {"rostos": resultado}
