from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import base64
import tempfile
import os
import speech_recognition as sr

app = FastAPI()
# Adicionar configuração para aceitar solicitações de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitações de qualquer origem
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Permitir os métodos GET, POST, PUT, DELETE
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)
r = sr.Recognizer()


class Audio(BaseModel):
    audio_file: str

@app.post("/cadastrar_gasto/")
async def cadastrar_gasto(audio: Audio):
    try:
        # Decodificar a string base64 para bytes
        audio_bytes = base64.b64decode(audio.audio_file)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Falha ao decodificar o áudio base64")

    # Salvar os bytes decodificados como um arquivo .wav temporário
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        temp_audio_path = temp_audio_file.name
        temp_audio_file.write(audio_bytes)
    
    # Transcrever o áudio
    try:
        with sr.AudioFile(temp_audio_path) as source:
            # Ouça o áudio do arquivo
            audio = r.record(source)

            try:
                # Converta a fala em texto
                transcription = r.recognize_google(audio, language='pt-BR')
                
                # Faça o processamento de texto aqui, se necessário
                # Por exemplo, você pode usar o NLTK para análise de sentimentos, tokenização, etc.

            except sr.UnknownValueError:
                print("Não foi possível entender o áudio")
            except sr.RequestError as e:
                print("Erro ao fazer a requisição ao serviço de reconhecimento de fala; {0}".format(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Excluir o arquivo .wav temporário após a transcrição
    os.unlink(temp_audio_path)
    return {"transcription": transcription}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
