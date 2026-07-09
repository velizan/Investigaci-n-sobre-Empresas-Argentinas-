import os
import shutil

def aplanar_con_contador(ruta_origen, ruta_destino):
    if not os.path.exists(ruta_destino):
        os.makedirs(ruta_destino)

    total_procesados = 0
    errores = 0

    print(f"{'='*40}")
    print(f"Iniciando proceso de aplanado...")
    print(f"{'='*40}")

    # Listar carpetas de años
    for anio in os.listdir(ruta_origen):
        ruta_anio_origen = os.path.join(ruta_origen, anio)

        if os.path.isdir(ruta_anio_origen):
            ruta_anio_destino = os.path.join(ruta_destino, anio)
            if not os.path.exists(ruta_anio_destino):
                os.makedirs(ruta_anio_destino)

            print(f"\n📂 Procesando año: {anio}")

            # Recorrer subcarpetas
            for raiz, _, archivos in os.walk(ruta_anio_origen):
                for archivo in archivos:
                    try:
                        ruta_archivo_completa = os.path.join(raiz, archivo)
                        ruta_final = os.path.join(ruta_anio_destino, archivo)

                        # Manejo de nombres duplicados para no sobrescribir
                        if os.path.exists(ruta_final):
                            nombre, ext = os.path.splitext(archivo)
                            ruta_final = os.path.join(ruta_anio_destino, f"duplicado_{total_procesados}_{nombre}{ext}")

                        # MOVEMOS el archivo (puedes cambiarlo a shutil.copy2 si quieres)
                        shutil.move(ruta_archivo_completa, ruta_final)
                        
                        total_procesados += 1
                        
                        # Imprimir progreso cada 100 archivos para no saturar la consola
                        if total_procesados % 100 == 0:
                            print(f" ✅ {total_procesados} archivos movidos...")

                    except Exception as e:
                        print(f" ❌ Error con {archivo}: {e}")
                        errores += 1

    print(f"\n{'='*40}")
    print(f"RESUMEN FINAL:")
    print(f"Mismos años, estructura plana.")
    print(f"Total archivos procesados: {total_procesados}")
    print(f"Total errores: {errores}")
    print(f"{'='*40}")

# Configuración
ORIGEN = "edictos"
DESTINO = "edictos_objetos"

import os

def eliminar_duplicados_en_destino(ruta_referencia, ruta_destino):
    """
    Busca los archivos de 'ruta_referencia' dentro de 'ruta_destino' 
    y los elimina de 'ruta_destino' si coinciden en nombre.
    """
    # 1. Obtenemos solo los nombres de los archivos que queremos buscar
    # Usamos un set para que la búsqueda sea mucho más rápida
    archivos_a_buscar = set()
    
    for raiz, _, archivos in os.walk(ruta_referencia):
        for archivo in archivos:
            archivos_a_buscar.add(archivo)
    
    print(f"🔍 Se identificaron {len(archivos_a_buscar)} archivos en la carpeta de referencia.")
    
    total_eliminados = 0
    
    # 2. Recorremos la carpeta destino para encontrar y borrar coincidencias
    print(f"🚀 Iniciando limpieza en: {ruta_destino}...")
    
    for raiz, _, archivos in os.walk(ruta_destino):
        for archivo in archivos:
            if archivo in archivos_a_buscar:
                ruta_completa_borrar = os.path.join(raiz, archivo)
                try:
                    os.remove(ruta_completa_borrar)
                    total_eliminados += 1
                    if total_eliminados % 50 == 0:
                        print(f" 🗑️  {total_eliminados} archivos eliminados...")
                except Exception as e:
                    print(f" ❌ Error al eliminar {archivo}: {e}")

    print(f"\n{'='*40}")
    print(f"PROCESO DE LIMPIEZA COMPLETADO")
    print(f"Total de archivos eliminados de la carpeta destino: {total_eliminados}")
    print(f"{'='*40}")

# Ejemplo de uso:
# RUTA_CON_ARCHIVOS_REPETIDOS es la carpeta que tiene los archivos que quieres quitar del destino
# RUTA_DESTINO_PLANOS es la carpeta (2019, 2020...) donde ya habías movido todo
#eliminar_duplicados_en_destino("edictos_cargados", DESTINO)

aplanar_con_contador(ORIGEN, DESTINO)
