from pathlib import Path

def contar_docx_en_subcarpeta(nombre_carpeta):
    # Obtiene la ruta de la carpeta donde está este script (.py)
    directorio_base = Path(__file__).resolve().parent
    
    # Une la ruta base con el nombre de tu carpeta de edictos
    ruta_objetivo = directorio_base / nombre_carpeta
    
    if not ruta_objetivo.exists():
        print(f"Error: La carpeta '{nombre_carpeta}' no existe en {directorio_base}")
        return 0

    # Buscamos archivos .docx que NO sean temporales (los que empiezan con ~$)
    archivos = [
        f for f in ruta_objetivo.rglob('*.docx') 
        if not f.name.startswith('~$')
    ]
    
    # Opcional: Imprimir los nombres encontrados para verificar
    for archivo in archivos:
        print(f"Encontrado: {archivo.name}")
        
    return len(archivos)

# USO: Solo pon el nombre de la carpeta (ej: 'Extracción de edictos')
# Si la carpeta se llama exactamente igual que en tu error anterior:
nombre = 'error_bd'
total = contar_docx_en_subcarpeta(nombre)


print(f"\nTotal de archivos .docx válidos: {total}")
