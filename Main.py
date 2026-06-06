from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import conexao_bd as bd
import reconhecer_rosto as rr

app = FastAPI()

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
    if not imagem.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Formato invalido. Use JPG ou PNG.")

    imagemBytes = await imagem.read()

    try:
        bd.salvarImagem(nomePessoa, nomeImagem, imagemBytes)
        return {"mensagem": "Imagem cadastrada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reconhecer")
async def reconhecer(frame: UploadFile = File(...)):
    conteudo = await frame.read()
    resultado = rr.processarFrame(conteudo)
    return {"rostos": resultado}
