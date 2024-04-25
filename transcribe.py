import speech_recognition as sr
import os
from fastapi import HTTPException

def transcribe_audio():
    r = sr.Recognizer()
    try:
        with sr.AudioFile('audio_decoded.wav') as source:
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
    
    os.unlink('audio_decoded.wav')
    return transcription
    