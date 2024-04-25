import base64
from fastapi import HTTPException
from pydub import AudioSegment
import io

def decode_audio(audio):
    try:
        # Decodificar a string base64 para bytes
        audio_bytes = base64.b64decode(audio.audio_file)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Falha ao decodificar o áudio base64")
    return audio_bytes

def create_audio(audio_bytes, name_audio, format):
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
    # Salvar o arquivo de áudio em formato WAV
    audio_segment.export(name_audio, format=format)

