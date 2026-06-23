import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from tqdm import tqdm
import os

# 1. Cargar datos
print("Cargando datos...")
df = pd.read_csv("data.csv")
textos = df['texto_para_ia'].astype(str).tolist()

# 2. Cargar modelo
print("Cargando modelo BETO...")
model_name = "dccuchile/bert-base-spanish-wwm-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
device = "cpu"
model.to(device)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[0, 0, :].numpy()

# 3. Procesar embeddings
embeddings = []
print("Generando embeddings...")
for text in tqdm(textos):
    embeddings.append(get_embedding(text))

# 4. Limpieza
matriz = np.array(embeddings)
matriz = np.nan_to_num(matriz, nan=0.0, posinf=0.0, neginf=0.0)

# 5. Guardar CSV (Aquí está la magia)
output_file = "matriz_limpia.csv"
df_matriz = pd.DataFrame(matriz)
df_matriz.to_csv(output_file, index=False)

# Imprimir la ruta absoluta para que sepas EXACTAMENTE dónde está
ruta_absoluta = os.path.abspath(output_file)
print(f"\n¡Éxito! Archivo guardado correctamente.")
print(f"Ruta del archivo: {ruta_absoluta}")
