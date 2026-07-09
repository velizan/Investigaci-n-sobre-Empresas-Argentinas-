import os
from docx import Document

def es_archivo_valido(nombre_archivo):
    """Verifica si el archivo es .txt o .doc."""
    extensiones_validas = ('.txt', '.doc')
    return nombre_archivo.lower().endswith(extensiones_validas)

def convertir_a_docx(ruta_origen, ruta_destino):
    """Lógica para transformar el contenido de un archivo a formato .docx."""
    try:
        doc = Document()
        
        # Intentamos leer con utf-8 (estándar moderno)
        try:
            with open(ruta_origen, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except UnicodeDecodeError:
            # Fallback a latin-1 para archivos de sistemas más antiguos
            with open(ruta_origen, 'r', encoding='latin-1') as f:
                contenido = f.read()

        doc.add_paragraph(contenido)
        doc.save(ruta_destino)
        return True
    except Exception as e:
        print(f"Error al convertir {ruta_origen}: {e}")
        return False

def procesar_directorio(ruta_carpeta):
    """Coordina la validación y conversión de todos los archivos en la carpeta."""
    if not os.path.isdir(ruta_carpeta):
        print(f"La ruta {ruta_carpeta} no es un directorio válido.")
        return

    archivos = [f for f in os.listdir(ruta_carpeta) if es_archivo_valido(f)]
    
    if not archivos:
        print("No se encontraron archivos .txt o .doc para procesar.")
        return

    print(f"Procesando {len(archivos)} archivos...")

    for nombre in archivos:
        ruta_txt_doc = os.path.join(ruta_carpeta, nombre)
        # Reemplazamos la extensión original por .docx
        nombre_sin_ext = os.path.splitext(nombre)[0]
        ruta_docx = os.path.join(ruta_carpeta, f"{nombre_sin_ext}.docx")

        if convertir_a_docx(ruta_txt_doc, ruta_docx):
            print(f"Éxito: {nombre} -> {nombre_sin_ext}.docx")

# --- Ejecución ---
mi_ruta = 'edictos_prueba' 

procesar_directorio(mi_ruta)