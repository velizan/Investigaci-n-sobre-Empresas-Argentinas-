# Lógica del Prompt y llamada a Gemini
import os
import json
#from dotenv import load_dotenv
#from google import genai
from google.genai import types
from src.database.config import client, MODEL_ID


def extraer_json_gemini(texto_edicto):
    """Envía el texto a Gemini usando el nuevo SDK y retorna un diccionario limpio."""
    
    prompt = f"""Actúa como un experto en extracción de datos legales y bases de datos PostgreSQL.

Tarea: Transcribir el texto de un edicto comercial de Argentina a un formato JSON estricto.

1. Esquema de Salida (JSON Obligatorio)
Devuelve exclusivamente un objeto JSON con esta estructura. Si una lista no tiene datos, usa [].

JSON
abro llave

  "denominacion": "NOMBRE DE LA SOCIEDAD",
  "cuit": "xx-xxxxxxxx-x o null",
  "anio_bo": 2024,
  "capital_social": 100000.00,
  "fecha_constitucion": "YYYY-MM-DD",
  "id_objeto": "1: Industrial, 2: Comercial, 3: Servicios, 4: Inmobilirio, 5: Agropecuario",
  "id_nueva_preexistente": "1: Nueva, 2: Preexistente",
  "id_tipo_societaria": "1: SA, 2: SAS, 3: SRL",
  "id_tipo_fiscalizacion": "1: Prescinde de sindicatura (socios), 2: Sindicatura, null: No aclara",
  "socios": [],
  "administradores": [],
  "sindicatura": []

cierro llave
2. Especificación de Arrays
socios: Cada objeto debe tener 
abro llave
dni (sin puntos), nombre_completo, edad (a la fecha del edicto), id_genero (1:H, 2:M, 3:X), porcentaje, cantidad_votos
cierro llave

administradores: Cada objeto debe tener 
abro llave
dni (sin puntos), nombre_completo, id_genero, cargo (Capitalize), condicion (Capitalize)
cierro llave
Por defecto, condición es "Titular".
Si una persona tiene más de un cargo, priorizar el más importante. 
El cargo debe ir solo, nunca acompañado de la condicion (titular o suplente).
El cargo debe ir en masculino (Presidente, Gerente, Director, etc.)

sindicatura: Cada objeto debe tener 
abro llave
dni (sin puntos), nombre_completo, id_genero, condicion_fiscal (Capitalize)
cierro llave
SOLO cuando se prescinde de sindicatura (id_tipo_fiscalizacion = 1) los socios se deben 
agregar al array de sindicatura.
Por defecto, condicion_fiscal es "Titular", salvo se aclare que es suplente. 

3. Reglas Críticas de Formato
Nombre de la sociedad: siempre en mayúsculas. (ej: BECCAR S.A.)
DNI: Siempre como cadena numérica sin puntos (ej: "20817187").

CUIT: Siempre con guiones (ej: "27-20817187-4").

Edad: Calcular restando el año de nacimiento al año de la fecha del edicto.

nombre_completo: escribir en Capitalize

Capitalización: Cargos ("Presidente", "Gerente", etc) y condiciones ("Titular" o "Suplente) siempre con la primera letra en Mayúscula (ej: "Presidente", "Gerente", "Suplente").

id_tipo_fiscalizacion: si se aclara que se prescinde de sindicatura entonces va "1" (socios)
                       si se aclara que existe sindicatura, órgano de fiscalización o similar entonces va "2" (sindicatura).
                       si NO SE ACLARA ninguna de las dos anteriores entonces va "null" (ser estricto con esto).

Integridad: No inventar datos. Si falta, usar null.

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