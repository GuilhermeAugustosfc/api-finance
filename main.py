from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr

from audio_utils import decode_audio, create_audio
from transcribe import transcribe_audio
from gpt3_utils import generate_response_gpt

app = FastAPI()
# Adicionar configuração para aceitar solicitações de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitações de qualquer origem
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permitir os métodos GET, POST, PUT, DELETE
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
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
