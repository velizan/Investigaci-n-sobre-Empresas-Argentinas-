 # Flujo principal y punto de entrada
import os
import time
import json
import docx  # Requiere: pip install python-docx

# --- IMPORTACIONES PROPIAS ---
# Asegúrate de que en database.py existan todas estas funciones corregidas
from src.database.database import (
    gestionar_sociedad, 
    registrar_socios, 
    registrar_administradores, 
    registrar_sindicatura 
)
from src.api.ai_handler import extraer_json_gemini
# --- FUNCIÓN AUXILIAR PARA LEER WORD ---
def obtener_texto_de_docx(ruta_archivo):
    """Abre un .docx y extrae todo el texto de los párrafos."""
    try:
        doc = docx.Document(ruta_archivo)
        texto_completo = []
        for parrafo in doc.paragraphs:
            texto_completo.append(parrafo.text)
        return "\n".join(texto_completo)
    except Exception as e:
        print(f"Error leyendo el archivo Word: {e}")
        return None

# --- 2. ORQUESTADOR PRINCIPAL CORREGIDO ---
def procesar_edicto_modular(texto_edicto, nombre_archivo):
    print(f"\n--- 🚀 Procesando: {nombre_archivo} ---")
    
    # A. Obtener Datos de la IA
    datos = extraer_json_gemini(texto_edicto)
    
    if not datos: 
        print(f"❌ Error: Gemini no devolvió JSON válido para {nombre_archivo}")
        return

    # Debug opcional: descomentar para ver qué devuelve la IA
    # print(f"🔍 DEBUG JSON RECIBIDO:\n{json.dumps(datos, indent=2, ensure_ascii=False)}")

    try:
        # B. Gestionar Sociedad (La Cabecera)
        # CORRECCIÓN: Pasamos 'datos' completo (es un JSON plano), no datos['sociedad']
        id_sociedad = gestionar_sociedad(datos)
        
        if not id_sociedad:
            raise Exception("No se pudo obtener el ID de la sociedad.")
            
        print(f"✅ Sociedad insertada/actualizada. ID: {id_sociedad}")
        
        # C. Delegar a los módulos específicos (Arrays)
        
        # 1. Socios
        socios = datos.get('socios', [])
        if socios:
            registrar_socios(socios, id_sociedad)
            print(f"   ↳ 👥 Socios procesados: {len(socios)}")
        
        # 2. Administradores
        admins = datos.get('administradores', [])
        if admins:
            registrar_administradores(admins, id_sociedad)
            print(f"   ↳ 💼 Administradores procesados: {len(admins)}")
            
        # 3. Sindicatura (NUEVO)
        sindicos = datos.get('sindicatura', [])
        if sindicos:
            registrar_sindicatura(sindicos, id_sociedad)
            print(f"   ↳ ⚖️ Síndicos procesados: {len(sindicos)}")
        
        print(f"🏁 Finalizado exitosamente: {nombre_archivo}")

    except Exception as e:
        print(f"❌ Error crítico procesando {nombre_archivo}: {e}")

# --- 3. BLOQUE DE EJECUCIÓN ---
if __name__ == "__main__":
    # Configuración
    CARPETA_EDICTOS = "edictos_prueba" 
    TIEMPO_ESPERA = 10 # Segundos entre llamadas a la API
    
    # Verificar carpeta
    if not os.path.exists(CARPETA_EDICTOS):
        os.makedirs(CARPETA_EDICTOS)
        print(f"📂 Carpeta '{CARPETA_EDICTOS}' creada. Por favor, coloca tus archivos .docx ahí.")
    else:
        # Filtrar solo archivos .docx
        archivos = [f for f in os.listdir(CARPETA_EDICTOS) if f.endswith('.docx') and not f.startswith('~$')]
        
        print(f"📂 Se encontraron {len(archivos)} documentos Word para procesar.\n")
        
        for i, archivo in enumerate(archivos, 1):
            print(f"\n[{i}/{len(archivos)}] Iniciando...")
            ruta_completa = os.path.join(CARPETA_EDICTOS, archivo)
            
            # Paso 1: Leer Word
            contenido_texto = obtener_texto_de_docx(ruta_completa)
            
            # Paso 2: Procesar
            if contenido_texto:
                procesar_edicto_modular(contenido_texto, archivo)
                
                # Paso 3: Pausa anti-saturación (solo si no es el último archivo)
                if i < len(archivos):
                    print(f"⏳ Esperando {TIEMPO_ESPERA} segundos para no saturar la API...")
                    time.sleep(TIEMPO_ESPERA) 
            else:
                print(f"⚠️ El archivo {archivo} parece estar vacío o corrupto.")
