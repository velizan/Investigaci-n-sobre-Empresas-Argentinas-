# Lógica del Prompt y llamada a Gemini
import os
import json
#from dotenv import load_dotenv
#from google import genai
from google.genai import types
from src.database.config import client, MODEL_ID


def extraer_json_gemini_objetos(texto_edicto):
    """Envía el texto a Gemini usando el nuevo SDK y retorna un diccionario limpio."""
    
    prompt = f"""Actúa como un experto en extracción de datos legales y bases de datos PostgreSQL.

Tarea: Transcribir el texto de un edicto comercial de Argentina a un formato JSON estricto.

1. Esquema de Salida (JSON Obligatorio)
Devuelve exclusivamente un objeto JSON con esta estructura. Si un campo no existe o una sociedad no tiene objeto 2 o 3, usa null.

Ejemplo de referencia:

Entrada: "El 15 de abril de 2024, por instrumento privado, se constituyó LOGÍSTICA SUR S.R.L. CUIT: 30-98765432-1. Objeto: La sociedad tiene por objeto realizar por cuenta propia o de terceros actividades comerciales y de servicios."
Salida:
{{
  "denominacion": "LOGÍSTICA SUR S.R.L.",
  "cuit": "30-98765432-1",
  "anio_bo": 2024,
  "id_objeto1": 2,
  "id_objeto2": 3,
  "id_objeto3": null
}}

2. Diccionario de IDs para los objetos:
Asigna el número entero correspondiente según el texto del edicto:
1 = Industrial
2 = Comercial
3 = Servicios
4 = Inmobiliario
5 = Agropecuario

3. Reglas Críticas de Formato
- Nombre de la sociedad: Siempre en mayúsculas (ej: BECCAR S.A.).
- CUIT: Siempre con guiones (ej: "27-20817187-4"). Si no figura, devuelve null.
- IDs de Objeto: Deben ser estrictamente números enteros (1, 2, 3, 4 o 5) o null. No devuelvas texto en estos campos.
- Integridad: No inventar datos. Si falta, usar null.

Texto a procesar: {texto_edicto}
"""
    try:
        # Cambio principal: uso de client.models.generate_content y types.GenerateContentConfig
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # En el nuevo SDK, el texto está en response.text
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error parseando JSON de Gemini: {e}")
        return None