from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
import datetime
from bson import ObjectId
from audio_utils import decode_audio, create_audio
from transcribe import transcribe_audio
from gpt3_utils import generate_response_gpt
from driver.mongo import get_db_mongo
from model.operacao_model import OperacaoModel

app = FastAPI()
# Adicionar configuração para aceitar solicitações de qualquer origem.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitações de qualquer origem
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
    ],  # Permitir os métodos GET, POST, PUT, DELETE
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)


class Audio(BaseModel):
    audio_file: str


@app.post("/cadastrar_gasto/")
async def cadastrar_gasto(audio: Audio):
    audio_bytes = decode_audio(audio)
    create_audio(audio_bytes, "audio_decoded.wav", "wav")
    # Transcrever o áudio
    try:
        transcription = transcribe_audio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        response = generate_response_gpt(transcription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    db = get_db_mongo()
    model = OperacaoModel(db)
    model.criar_operacao(response)
    return response


class Operacao(BaseModel):
    user_id: str
    type: str
    amount: float
    date: str
    description: str
    source: str


@app.post("/operacoes/")
async def create_operacao(operacao: Operacao):
    # Converter a string de data para o formato datetime
    # operacao_date = datetime.datetime.fromisoformat(operacao.date)
    db = get_db_mongo()
    operacoes_collection = db["operacoes"]
    # Criar o documento da operação
    operacao_doc = {
        "user_id": operacao.user_id,
        "type": operacao.type,
        "amount": operacao.amount,
        "date": operacao.date,
        "description": operacao.description,
        "source": operacao.source
    }

    # Inserir a operação no MongoDB
    result = operacoes_collection.insert_one(operacao_doc)

    # Verificar se a operação foi inserida com sucesso
    if result.inserted_id:
        return {"message": "Operação criada com sucesso"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao criar a operação")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
