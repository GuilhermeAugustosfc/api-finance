from fastapi import FastAPI, HTTPException, Depends, status
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
import database.MySQLDatabase as MySQL
from database.MySQLDatabase import get_db
from oauthlib.oauth2 import RequestValidator, WebApplicationServer
from datetime import datetime, timedelta
from model.TokenModel import AccessToken, RefreshToken, OAuth2Client
from sqlalchemy.orm import Session
from oauthlib.common import generate_token
from model.TokenModel import generate_client_secret
import mysql.connector

MySQL.create_tables()

app = FastAPI()
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

    # db = get_db_mongo()
    # model = OperacaoModel(db)
    # model.criar_operacao(response)
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


@app.get("/testeRDS")
async def get_rds_test_file():
    config = {
        "host": "database-1.cpigwcyuk6vv.us-east-2.rds.amazonaws.com",
        "user": "admin",
        "password": "SO9yvDX5GwQfF1EWEM5u",
    }
    db = mysql.connector.connect(**config)
    cursor = db.cursor()
    cursor.execute("USE teste")
    cursor.execute("SELECT * FROM clientes")
    resultados = cursor.fetchall()
    cursor.close()
    db.close()
    return resultados


# Implementação do OAuth2
class MyRequestValidator(RequestValidator):
    def validate_client_id(self, client_id, request, *args, **kwargs):
        db = MySQL.SessionLocal
        client = db.query(OAuth2Client).filter(OAuth2Client.client_id == client_id).first()
        if not client:
            return False
        return True

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        db = MySQL.SessionLocal
        client = db.query(OAuth2Client).filter(OAuth2Client.client_id == client_id).first()
        if not client:
            return False
        if client.redirect_uri != redirect_uri:
            return False
        return True

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        db = MySQL.SessionLocal
        client = db.query(OAuth2Client).filter(OAuth2Client.client_id == client_id).first()
        return client.redirect_uri

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        pass

    def get_authorization_code(self, client_id, code, request, *args, **kwargs):
        pass

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        pass

    def save_token(self, token, request, *args, **kwargs):
        pass

    def fetch_token(self, access_token, request, *args, **kwargs):
        pass

    def validate_bearer_token(self, token, scopes, request):
        pass


oauth2_server = WebApplicationServer(MyRequestValidator())



@app.post("/oauth/token")
def token(request, db: Session = Depends(get_db)):
    uri = 'http://127.0.0.1:8000/oauth/token'
    headers, body, status = oauth2_server.create_token_response(uri, request.method, request.body, request.headers)
    return body, status, headers


@app.post("/clients/")
def create_client(client_id: str, redirect_uri: str, db: Session = Depends(get_db)):
    db_client = db.query(OAuth2Client).filter(OAuth2Client.client_id == client_id).first()
    if db_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client already registered")
    client_secret = generate_client_secret()
    new_client = OAuth2Client(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


@app.post("/refresh_token/")
def create_refresh_token(access_token: str, db: Session = Depends(get_db)):
    db_access_token = db.query(AccessToken).filter(AccessToken.token == access_token).first()
    if not db_access_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access token not found")

    # Calculando o tempo de expiração do Refresh Token (por exemplo, 7 dias a partir de agora)
    expire_at = datetime.utcnow() + timedelta(days=7)

    refresh_token = generate_token()

    db_refresh_token = RefreshToken(token=refresh_token, expire_at=expire_at, access_token_id=db_access_token.id)
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)

    return {"refresh_token": refresh_token}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
