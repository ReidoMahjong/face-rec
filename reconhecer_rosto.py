import io

import cv2
import face_recognition
import numpy as np
from PIL import Image

import conexao_bd as bd


def identificarRosto(encodingRosto, templates, t=0.5):
    if not templates:
        return "desconhecido"

    templatesComparados = [t["template"] for t in templates]
    resultados = face_recognition.compare_faces(
        templatesComparados, encodingRosto, tolerance=t
    )
    maisProximo = face_recognition.face_distance(templatesComparados, encodingRosto)

    if True in resultados:
        return templates[np.argmin(maisProximo)]["nome"]

    return "desconhecido"


def processarFrame(imagemBytes: bytes) -> list:
    # Pillow decodifica em RGB — consistente com o cadastro
    frame = np.array(Image.open(io.BytesIO(imagemBytes)))

    if frame is None or frame.size == 0:
        return []

    # OpenCV utilizado apenas para detecção via Haar Cascade
    detectorRostos = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    templates = bd.carregarTemplates()

    cinza = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  # RGB → cinza (era BGR → cinza)

    rostos = detectorRostos.detectMultiScale(
        cinza, scaleFactor=1.1, minNeighbors=7, minSize=(40, 40)
    )

    resultado = []
    for x, y, w, h in rostos:
        # Recorte já em RGB, sem necessidade de conversão manual de canais
        recorte = np.ascontiguousarray(frame[y : y + h, x : x + w])
        encodings = face_recognition.face_encodings(recorte)

        nome = identificarRosto(encodings[0], templates) if encodings else "erro"

        resultado.append(
            {
                "nome": nome,
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "conhecido": nome != "desconhecido",
            }
        )

    return resultado
