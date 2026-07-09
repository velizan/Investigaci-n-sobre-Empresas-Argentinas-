
import os
import time
import json
import docx
import shutil

# --- IMPORTACIONES PROPIAS ---
# Importamos estrictamente lo necesario para esta pasada de actualización
from src.database.database import gestionar_objetos
from src.api.ai_handler_objetos import extraer_json_gemini_objetos

# --- FUNCIÓN AUXILIAR PARA LEER WORD ---
def obtener_texto_de_docx(ruta_archivo):
    """Abre un .docx y extrae todo el texto de los párrafos."""
    try:
        doc = docx.Document(ruta_archivo)
        texto_completo = [parrafo.text for parrafo in doc.paragraphs]
        return "\n".join(texto_completo)
    except Exception as e:
        print(f"Error leyendo el archivo Word: {e}")
        return None

# --- 2. ORQUESTADOR EXCLUSIVO PARA OBJETOS ---
def procesar_edicto_objetos(texto_edicto, nombre_archivo, tiempo_inicio=None): 
    print(f"\n--- 🚀 Procesando Objetos: {nombre_archivo} ---")
    
    # Llamamos a la versión del handler específica para objetos
    datos = extraer_json_gemini_objetos(texto_edicto)
    
    if not datos: 
        mensaje = "Gemini no devolvió un JSON válido o la respuesta fue nula."
        print(f"❌ Error IA: {mensaje}")
        return False, "error_ia", mensaje 
    
    # Si 'datos' es una lista (múltiples edictos) o no es un diccionario, cancelamos antes de que rompa.
    if not isinstance(datos, dict):
        mensaje = "El documento contiene múltiples edictos o un formato no esperado."
        print(f"❌ Cancelando carga: {mensaje}")
        # Al devolver "formato_invalido", el orquestador lo mueve a esa carpeta y sigue con el próximo.
        return False, "formato_invalido", mensaje

    # --- VALIDACIÓN DE OBJETOS VACÍOS ---
    # Si id_objeto1 es nulo o no existe, saltamos la actualización en BD
    if not datos.get("id_objeto1"):
        mensaje = "El edicto no especifica un objeto societario (id_objeto1 es nulo)."
        print(f"⏭️ Omitiendo: {mensaje}")
        return False, "sin_objetos", mensaje

    try:
        # Llamamos a gestionar_objetos, que hace el SELECT y luego UPDATE o INSERT
        id_sociedad = gestionar_objetos(datos)
        
        if not id_sociedad:
            raise Exception("La transacción falló o no se pudo obtener el ID de la sociedad.")
            
        print(f"✅ Objetos incorporados/actualizados. ID Sociedad: {id_sociedad}")
        
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
    """Mueve el archivo fallido o sin objetos a su subcarpeta correspondiente y genera un log txt."""
    ruta_subcarpeta = os.path.join(carpeta_errores, categoria_error)
    os.makedirs(ruta_subcarpeta, exist_ok=True)
    
    ruta_error_docx = os.path.join(ruta_subcarpeta, archivo)
    ruta_error_txt = os.path.join(ruta_subcarpeta, f"{archivo}_detalle.txt")
    
    print(f"⚠️ Moviendo a '{ruta_subcarpeta}' y generando log...")
    try:
        shutil.move(ruta_origen, ruta_error_docx)
        with open(ruta_error_txt, "w", encoding="utf-8") as f:
            f.write(f"Archivo: {archivo}\n")
            f.write(f"Categoría: {categoria_error}\n")
            f.write(f"Motivo: {error_msg}\n")
    except Exception as e:
        print(f"❌ Error de sistema al intentar mover el archivo {archivo}: {e}")

def procesar_lote_objetos(carpeta_origen, carpeta_errores, tiempo_espera):
    """Orquesta la lectura, actualización de objetos y manejo de archivos."""
    archivos = [f for f in os.listdir(carpeta_origen) if f.endswith('.docx') and not f.startswith('~$')]
    
    if not archivos:
        print(f"📂 La carpeta '{carpeta_origen}' está vacía. Coloca tus archivos .docx ahí.")
        return

    print(f"📂 Se encontraron {len(archivos)} documentos Word para actualizar objetos.\n")
    
    procesados_ok = 0
    procesados_error = 0
    tiempo_inicio = time.time() 
    
    for i, archivo in enumerate(archivos, 1):
        print(f"\n[{i}/{len(archivos)}] Iniciando...")
        ruta_origen = os.path.join(carpeta_origen, archivo)
        
        contenido_texto = obtener_texto_de_docx(ruta_origen)
        
        if contenido_texto is None:
            exito, categoria_error, error_msg = False, "error_lectura", "El archivo de Word está corrupto o no se pudo leer."
        else:
            exito, categoria_error, error_msg = procesar_edicto_objetos(contenido_texto, archivo, tiempo_inicio)
            
        if exito:
            procesados_ok += 1
            # Eliminar archivo descartable si fue un éxito
            try:
                os.remove(ruta_origen)
                print(f"🗑️ Archivo eliminado de origen: {archivo}")
            except OSError as e:
                print(f"⚠️ Error al intentar eliminar {archivo}: {e}")
        else:
            procesados_error += 1
            registrar_error_archivo(archivo, ruta_origen, categoria_error, error_msg, carpeta_errores)
        
        if i < len(archivos):
            print(f"⏳ Esperando {tiempo_espera} segundos para no saturar la API...")
            time.sleep(tiempo_espera)

    tiempo_fin = time.time()
    tiempo_total = tiempo_fin - tiempo_inicio
    minutos, segundos = divmod(tiempo_total, 60)
    
    print("\n" + "="*45)
    print("📊 RESUMEN DE ACTUALIZACIÓN DE OBJETOS")
    print("="*45)
    print(f"✅ Edictos actualizados (y eliminados): {procesados_ok}")
    print(f"❌ Casos omitidos/errores (movidos): {procesados_error}")
    print(f"⏱️ Tiempo total de ejecución: {int(minutos)} min y {int(segundos)} seg")
    print("="*45)

# --- 3. BLOQUE DE EJECUCIÓN ---
if __name__ == "__main__":
    # Configuración actualizada a los nuevos requerimientos
    CARPETA_EDICTOS = "error_bd" 
    CARPETA_ERRORES = "errores" 
    TIEMPO_ESPERA = 5
    
    # Crear carpetas automáticamente si no existen
    for carpeta in [CARPETA_EDICTOS, CARPETA_ERRORES]:
        os.makedirs(carpeta, exist_ok=True)
        
    procesar_lote_objetos(CARPETA_EDICTOS, CARPETA_ERRORES, TIEMPO_ESPERA)
