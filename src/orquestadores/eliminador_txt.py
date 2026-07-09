import os
from pathlib import Path

def es_archivo_txt(nombre_archivo):
    """Verifica si el archivo tiene extensión .txt."""
    return nombre_archivo.lower().endswith('.txt')

def eliminar_archivos_txt(ruta_carpeta):
    """
    Busca y elimina todos los archivos .txt en la ruta proporcionada.
    """
    if not os.path.isdir(ruta_carpeta):
        print(f"Error: La ruta '{ruta_carpeta}' no es un directorio válido.")
        return

    # Listar solo los archivos .txt
    archivos_a_eliminar = [f for f in os.listdir(ruta_carpeta) if es_archivo_txt(f)]

    if not archivos_a_eliminar:
        print("No se encontraron archivos .txt para eliminar.")
        return

    print(f"Se han encontrado {len(archivos_a_eliminar)} archivos .txt.")
    
    contador_eliminados = 0
    for nombre in archivos_a_eliminar:
        ruta_completa = os.path.join(ruta_carpeta, nombre)
        try:
            os.remove(ruta_completa)
            print(f"Eliminado: {nombre}")
            contador_eliminados += 1
        except Exception as e:
            print(f"No se pudo eliminar {nombre}: {e}")

    print(f"\nLimpieza completada. Total eliminados: {contador_eliminados}")

from pathlib import Path

def eliminar_archivos_zone_identifier(ruta_carpeta):
    # Convertir el texto de la ruta en un objeto Path
    ruta = Path(ruta_carpeta)
    
    # Validar que la ruta proporcionada realmente exista y sea una carpeta
    if not ruta.is_dir():
        print(f"Error: La ruta '{ruta_carpeta}' no existe o no es una carpeta válida.")
        return
        
    archivos_eliminados = 0
    
    # rglob("*Zone.Identifier") busca recursivamente en la carpeta y subcarpetas
    for elemento in ruta.rglob("*Zone.Identifier"):
        if elemento.is_file():
            try:
                elemento.unlink()  # Elimina el archivo físico
                print(f"✅ Eliminado: {elemento.name}")
                archivos_eliminados += 1
            except PermissionError:
                print(f"❌ Sin permisos para eliminar: {elemento.name}")
            except Exception as e:
                print(f"❌ Error inesperado al eliminar {elemento.name}: {e}")
                
    # Resumen final
    if archivos_eliminados == 0:
        print("No se encontraron archivos tipo 'Zone.Identifier' en esta ruta.")
    else:
        print(f"Limpieza completada: Se eliminaron {archivos_eliminados} archivo(s) residuales.")


# Ejemplo de uso:
mi_ruta = "edictos_objetos"


eliminar_archivos_zone_identifier(mi_ruta)
## --- Ejemplo de uso ---
#mi_ruta = 'error_bd'
#eliminar_archivos_txt(mi_ruta)
