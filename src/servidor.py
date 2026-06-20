from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
import edge_tts
import os
import time

app = FastAPI()

# 1. Configurar CORS para permitir comunicación desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Asegurar que la carpeta audio exista y servirla como archivos estáticos
if not os.path.exists("audio"):
    os.makedirs("audio")

# Esto sirve tanto los archivos del juego (index.html, Build/) como los audios generados
app.mount("/audio", StaticFiles(directory="audio", html=True), name="audio")

# 3. Configuración de Gemini
API_KEY = "" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite") # Actualizado a modelo recomendado

class ChatRequest(BaseModel):
    texto: str

@app.post("/chat")
async def chat(datos: ChatRequest):
    try:
        # Generar texto
        response = model.generate_content(datos.texto)
        texto_respuesta = response.text
        print(f"\n[Gemini dice]: {texto_respuesta}\n")
        
        # Generar audio
        nombre_archivo = f"respuesta_{int(time.time())}.mp3"
        ruta_archivo = f"audio/{nombre_archivo}"
        
        communicate = edge_tts.Communicate(texto_respuesta, "es-MX-JorgeNeural")
        await communicate.save(ruta_archivo)
        
        # URL accesible para Unity
        url_audio = f"http://127.0.0.1:8000/audio/{nombre_archivo}"
        
        return {
            "status": "success",
            "respuesta": texto_respuesta,
            "archivo": url_audio
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "mensaje": str(e)}
