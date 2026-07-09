import os
import time
import json
import docx
import shutil  # <-- IMPORTANTE: Librería estándar para mover archivos

# --- IMPORTACIONES PROPIAS ---
from src.database.database import (
    gestionar_sociedad, 
    registrar_socios, 
    registrar_administradores, 
    registrar_sindicatura 
)
from src.api.ai_handler import extraer_json_gemini

# --- FUNCIÓN AUXILIAR PARA LEER WORD ---
def obtener_texto_de_docx(ruta_archivo):
    try:
        doc = docx.Document(ruta_archivo)
        texto_completo = [parrafo.text for parrafo in doc.paragraphs]
        return "\n".join(texto_completo)
    except Exception as e:
        print(f"Error leyendo el archivo Word: {e}")
        return None

# --- 2. ORQUESTADOR PRINCIPAL CORREGIDO ---
# Agregamos tiempo_inicio como parámetro
def procesar_edicto_modular(texto_edicto, nombre_archivo, tiempo_inicio=None): 
    print(f"\n--- 🚀 Procesando: {nombre_archivo} ---")
    
    datos = extraer_json_gemini(texto_edicto)
    
    if not datos: 
        mensaje = "Gemini no devolvió un JSON válido o la respuesta fue nula."
        print(f"❌ Error IA: {mensaje}")
        return False, "error_ia", mensaje 

    try:
        id_sociedad = gestionar_sociedad(datos)
        if not id_sociedad:
            raise Exception("No se pudo obtener el ID de la sociedad desde Supabase.")
            
        print(f"✅ Sociedad insertada/actualizada. ID: {id_sociedad}")
        
        socios = datos.get('socios', [])
        if socios:
            registrar_socios(socios, id_sociedad)
            print(f"   ↳ 👥 Socios procesados: {len(socios)}")
            
        admins = datos.get('administradores', [])
        if admins:
            registrar_administradores(admins, id_sociedad)
            print(f"   ↳ 💼 Administradores procesados: {len(admins)}")
            
        sindicos = datos.get('sindicatura', [])
        if sindicos:
            registrar_sindicatura(sindicos, id_sociedad)
            print(f"   ↳ ⚖️ Síndicos procesados: {len(sindicos)}")
        
        # --- CÁLCULO DE TIEMPO ACUMULADO ---
        if tiempo_inicio:
            tiempo_actual = time.time() - tiempo_inicio
            minutos, segundos = divmod(tiempo_actual, 60)
            print(f"🏁 Finalizado exitosamente: {nombre_archivo} | ⏱️ Tiempo acumulado: {int(minutos)}m {int(segundos)}s")
        else:
            print(f"🏁 Finalizado exitosamente: {nombre_archivo}")
            
        return True, None, "" 

    except Exception as e:
        mensaje = str(e)
        print(f"❌ Error BD procesando {nombre_archivo}: {mensaje}")
        return False, "error_bd", mensaje

# --- FUNCIONES DE SOPORTE PARA ARCHIVOS Y ERRORES ---

def registrar_error_archivo(archivo, ruta_origen, categoria_error, error_msg, carpeta_errores):
    """Mueve el archivo fallido a su subcarpeta correspondiente y genera un log txt."""
    # 1. Definir y crear la ruta de la subcarpeta específica
    ruta_subcarpeta = os.path.join(carpeta_errores, categoria_error)
    os.makedirs(ruta_subcarpeta, exist_ok=True)
    
    # 2. Definir rutas finales para el Word y el TXT dentro de la subcarpeta
    ruta_error_docx = os.path.join(ruta_subcarpeta, archivo)
    ruta_error_txt = os.path.join(ruta_subcarpeta, f"{archivo}_detalle.txt")
    
    print(f"⚠️ Moviendo a '{ruta_subcarpeta}' y generando log...")
    try:
        shutil.move(ruta_origen, ruta_error_docx)
        with open(ruta_error_txt, "w", encoding="utf-8") as f:
            f.write(f"Archivo: {archivo}\n")
            f.write(f"Categoría: {categoria_error}\n")
            f.write(f"Motivo del error: {error_msg}\n")
    except Exception as e:
        print(f"❌ Error de sistema al intentar mover el archivo {archivo}: {e}")


def procesar_lote_edictos(carpeta_origen, carpeta_errores, tiempo_espera):
    """Orquesta la lectura, procesamiento y manejo de errores para todos los archivos de la carpeta."""
    archivos = [f for f in os.listdir(carpeta_origen) if f.endswith('.docx') and not f.startswith('~$')]
    
    if not archivos:
        print(f"📂 La carpeta '{carpeta_origen}' está vacía. Coloca tus archivos .docx ahí.")
        return

    print(f"📂 Se encontraron {len(archivos)} documentos Word para procesar.\n")
    
    # --- NUEVAS VARIABLES: Contadores y Temporizador ---
    procesados_ok = 0
    procesados_error = 0
    tiempo_inicio = time.time() # Inicia el cronómetro
    
    for i, archivo in enumerate(archivos, 1):
        print(f"\n[{i}/{len(archivos)}] Iniciando...")
        ruta_origen = os.path.join(carpeta_origen, archivo)
        
        contenido_texto = obtener_texto_de_docx(ruta_origen)
        
        # --- Lectura y Procesamiento ---
        if contenido_texto is None:
            exito, categoria_error, error_msg = False, "error_lectura", "El archivo de Word está corrupto o no se pudo leer."
        else:
            exito, categoria_error, error_msg = procesar_edicto_modular(contenido_texto, archivo, tiempo_inicio)
            
        # --- Manejo de Éxitos y Errores ---
        if exito:
            procesados_ok += 1
            # Eliminar el archivo si se procesó correctamente
            try:
                os.remove(ruta_origen)
                print(f"🗑️ Archivo eliminado de origen: {archivo}")
            except OSError as e:
                print(f"⚠️ Error al intentar eliminar {archivo}: {e}")
        else:
            procesados_error += 1
            registrar_error_archivo(archivo, ruta_origen, categoria_error, error_msg, carpeta_errores)
        
        # --- Pausa anti-saturación ---
        if i < len(archivos):
            print(f"⏳ Esperando {tiempo_espera} segundos para no saturar la API...")
            time.sleep(tiempo_espera)

    # --- CÁLCULO DE TIEMPO FINAL Y REPORTE ---
    tiempo_fin = time.time()
    tiempo_total = tiempo_fin - tiempo_inicio
    minutos, segundos = divmod(tiempo_total, 60) # Convierte a minutos y segundos
    
    print("\n" + "="*40)
    print("📊 RESUMEN DEL PROCESAMIENTO")
    print("="*40)
    print(f"✅ Procesados correctamente (y eliminados): {procesados_ok}")
    print(f"❌ Errores encontrados (movidos a subcarpetas): {procesados_error}")
    print(f"⏱️ Tiempo total de ejecución: {int(minutos)} min y {int(segundos)} seg")
    print("="*40)


# --- 3. BLOQUE DE EJECUCIÓN ---
if __name__ == "__main__":
    # Configuración
    CARPETA_EDICTOS = "error_bd" 
    
    
    CARPETA_ERRORES = "errores" 
    TIEMPO_ESPERA = 5 
    
    # Crear carpetas principales automáticamente si no existen
    for carpeta in [CARPETA_EDICTOS, CARPETA_ERRORES]:
        os.makedirs(carpeta, exist_ok=True)
        
    # Llamada limpia al nuevo orquestador de lotes
    procesar_lote_edictos(CARPETA_EDICTOS, CARPETA_ERRORES, TIEMPO_ESPERA)
    