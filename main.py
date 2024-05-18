from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from audio_utils import decode_audio, create_audio
from transcribe import transcribe_audio
from gpt3_utils import generate_response_gpt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth_utils import (
    authenticate_user,
    create_refresh_token_pair,
)
from db_operations import (
    register_user,
    create_user_tokens,
    insert_operacao_mongo,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class Audio(BaseModel):
    audio_file: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/cadastrar_gasto/")
async def cadastrar_gasto(audio: Audio):
    audio_bytes = decode_audio(audio)
    create_audio(audio_bytes, "audio_decoded.wav", "wav")

    try:
        transcription = transcribe_audio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        response = generate_response_gpt(transcription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return response


class Operacao(BaseModel):
    user_id: str
    type: str
    amount: float
    date: str
    description: str
    source: str


@app.post("/register")
def register(username: str, password: str):
    try:
        register_user(username, password)
    except HTTPException as e:
        raise e
    return {"msg": "User registered successfully"}


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = authenticate_user(form_data.username, form_data.password)
        access_token, refresh_token = create_user_tokens(user)
    except HTTPException as e:
        raise e

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh_token")
def refresh_access_token(refresh_token: str):
    try:
        access_token, new_refresh_token = create_refresh_token_pair(refresh_token)
    except HTTPException as e:
        raise e

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@app.post("/operacoes/")
async def create_operacao(operacao: Operacao):
    try:
        insert_operacao_mongo(operacao)
    except HTTPException as e:
        raise e
    return {"message": "Operação criada com sucesso"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
