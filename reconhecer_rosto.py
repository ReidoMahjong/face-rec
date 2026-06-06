import cv2
import face_recognition
import numpy as np

import conexao_bd as bd


def carregarTemplates():
    registros = bd.imagens.find({"template": {"$exists": True}})
    templates = []
    for registro in registros:
        templates.append(
            {"nome": registro["NomePessoa"], "template": np.array(registro["template"])}
        )
    return templates


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

    array = np.frombuffer(imagemBytes, dtype=np.uint8)
    frame = cv2.imdecode(array, cv2.IMREAD_COLOR)

    if frame is None:
        return []

    detectorRostos = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    templates = carregarTemplates()

    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rostos = detectorRostos.detectMultiScale(
        cinza, scaleFactor=1.1, minNeighbors=7, minSize=(40, 40)
    )

    resultado = []
    for x, y, w, h in rostos:
        recorte = np.ascontiguousarray(frame[y : y + h, x : x + w][:, :, ::-1])
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
