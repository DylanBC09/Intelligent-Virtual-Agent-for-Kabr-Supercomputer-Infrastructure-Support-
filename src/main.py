import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
import edge_tts
import os
import time
import re

# Nuevos imports para RAG y Embeddings
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# -----------------------------------------------------------------------------
# 1. CARGA DE MODELOS Y DATOS (Se ejecuta una sola vez al arrancar el servidor)
# -----------------------------------------------------------------------------
print("Cargando modelo BETO en FastAPI...")
model_name = "dccuchile/bert-base-spanish-wwm-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
beto_model = AutoModel.from_pretrained(model_name)
device = "cpu"  # Cambia a "cuda" si el servidor tiene GPU
beto_model.to(device)
beto_model.eval() # Modo inferencia

print("Cargando matriz de embeddings y dataset...")
# df_tickets debe ser el archivo que tiene las columnas de interacciones (ej. data.csv)
df_tickets = pd.read_csv("data.csv") 
# Cargamos la matriz de numpy generada previamente
matriz_embeddings = pd.read_csv("matriz_limpia.csv").values

# -----------------------------------------------------------------------------
# 2. CONFIGURACIONES GENERALES
# -----------------------------------------------------------------------------
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
if not os.path.exists("audio"): os.makedirs("audio")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# ATENCIÓN: Por seguridad, nunca dejes tu API Key hardcodeada en producción. 
# Considera usar os.getenv("GEMINI_API_KEY")
genai.configure(api_key="API")
model_gemini = genai.GenerativeModel("gemini-2.5-flash-lite")

user_state = {} 

# -----------------------------------------------------------------------------
# 3. FUNCIONES AUXILIARES (Voz, Correo y RAG)
# -----------------------------------------------------------------------------
def limpiar_texto_para_voz(texto):
    texto_limpio = re.sub(r'[\*\-\#\_]', '', texto)
    texto_limpio = re.sub(r'\n+', ' ', texto_limpio)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    return texto_limpio.strip()

def enviar_correo_infraestructura(user_id, correo_usuario, contexto):
    sugerencia = model_gemini.generate_content(
        f"Analiza esta solicitud de infraestructura y da una sugerencia técnica breve para el equipo de TI: {contexto}"
    ).text

    remitente = "benavidescastillo06@gmail.com"
    password = "password"
    destinatario = "dbenavides@cenat.ac.cr"

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = f"Ticket Infraestructura: Usuario {correo_usuario}"
    
    html_content = f"<html><body><h2>Ticket de Infraestructura</h2><p><b>Consulta:</b> {contexto}</p><p>{sugerencia}</p></body></html>"
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error: {e}")

def obtener_vector_consulta(texto):
    """Convierte la pregunta del usuario a un vector usando BETO."""
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = beto_model(**inputs)
    return outputs.last_hidden_state[0, 0, :].numpy()

def buscar_contexto_historico(query_vector, k=5):
    """Busca los k tickets más similares y concatena sus interacciones."""
    # Calcula similitud de coseno
    similitudes = cosine_similarity(query_vector.reshape(1, -1), matriz_embeddings)
    # Índices de los k más altos
    idx_top = np.argsort(similitudes[0])[-k:][::-1]
    
    contexto_acumulado = ""
    for i in idx_top:
        row = df_tickets.iloc[i]
        historial = []
        # Extraemos interacciones del 1 al 31 (ignorando NAs)
        for j in range(1, 32):
            col_name = f"interaction_{j}_body"
            if col_name in row and pd.notna(row[col_name]) and str(row[col_name]).strip() != "":
                historial.append(str(row[col_name]).strip())
                
        if historial:
            contexto_acumulado += "\n\n--- INICIO DE CASO HISTÓRICO DE REFERENCIA ---\n"
            contexto_acumulado += "\n | ".join(historial)
            contexto_acumulado += "\n--- FIN DE CASO ---"
            
    return contexto_acumulado

# -----------------------------------------------------------------------------
# 4. ENDPOINTS
# -----------------------------------------------------------------------------
class ChatRequest(BaseModel):
    user_id: str
    texto: str

@app.post("/chat")
async def chat(datos: ChatRequest):
    if datos.user_id not in user_state:
        user_state[datos.user_id] = {"estado": "ESPERANDO_CORREO", "correo": ""}
        respuesta_texto = "Hola, soy Sulkía, el agente virtual de Kabré. Antes de empezar, necesito que escribas tu correo institucional."
    
    elif user_state[datos.user_id]["estado"] == "ESPERANDO_CORREO":
        if "@" in datos.texto and "." in datos.texto:
            user_state[datos.user_id]["correo"] = datos.texto
            user_state[datos.user_id]["estado"] = "ESPERANDO_CONSULTA"
            respuesta_texto = "Gracias. He registrado tu correo. Por favor, indícame tu consulta."
        else:
            respuesta_texto = "Necesito un correo electrónico válido para continuar."
    
    else:
        # Evaluación con CoT (Chain of Thought)
        prompt_decision = f"""
        Actúa como un despachador experto HPC. Decide si esta consulta DEBE escalarse a técnico humano (instalación, acceso, permisos admin) o si la IA puede resolverla (error de código, duda informativa).
        Consulta: '{datos.texto}'
        Reglas: Responde solo una línea: "[RESULTADO: SI]" o "[RESULTADO: NO]".
        """
        analisis_ia = model_gemini.generate_content(prompt_decision).text.upper()

        if "[RESULTADO: SI]" in analisis_ia:
            enviar_correo_infraestructura(datos.user_id, user_state[datos.user_id]["correo"], datos.texto)
            respuesta_texto = "Esta solicitud requiere cambios en la infraestructura. He escalado tu ticket al equipo humano, pronto te contactarán."
        else:
            # === RAG: RECUPERACIÓN DE CONTEXTO ===
            query_vector = obtener_vector_consulta(datos.texto)
            
            # Ampliamos a k=5 para tener una visión más robusta del historial
            contexto_rag = buscar_contexto_historico(query_vector, k=5) 

            # === PROMPT MEJORADO CON RAG Y EVALUACIÓN CRÍTICA ===
            prompt_experto = f"""
            Eres Sulkía, asistente técnico virtual del Supercomputador Kabré.
            
            A continuación se te presenta un bloque con consultas previas matemáticamente similares a la actual.
            
            ATENCIÓN - REGLA DE ORO: Este historial es meramente un INSUMO REFERENCIAL. No representa una verdad absoluta y puede contener errores de usuarios anteriores, soluciones incompletas o respuestas desactualizadas del equipo de soporte. Tu deber es analizarlo críticamente.

            HISTORIAL DE CASOS SIMILARES (PARA EVALUACIÓN):
            {contexto_rag}

            CONSULTA ACTUAL DEL USUARIO:
            '{datos.texto}'

            INSTRUCCIONES PARA LA GENERACIÓN:
            1. Usa tu propio conocimiento experto en HPC, Linux y desarrollo para evaluar si las soluciones planteadas en el historial son técnicamente correctas para la consulta actual.
            2. Si el historial contiene errores o pasos innecesarios, descártalos y ofrece la solución óptima y corregida.
            3. Responde de forma directa, técnica y empática.
            4. NO uses viñetas, asteriscos, ni ningún formato markdown. Tu respuesta debe ser un texto plano completamente fluido para ser leído en voz alta.
            """
            respuesta_texto = model_gemini.generate_content(prompt_experto).text

    # Procesamiento para voz
    texto_para_voz = limpiar_texto_para_voz(respuesta_texto)
    nombre_archivo = f"resp_{datos.user_id}_{int(time.time())}.mp3"
    await edge_tts.Communicate(texto_para_voz, "es-MX-JorgeNeural").save(f"audio/{nombre_archivo}")
    
    return {
        "respuesta": respuesta_texto,
        "url_audio": f"http://127.0.0.1:8000/audio/{nombre_archivo}"
    }
