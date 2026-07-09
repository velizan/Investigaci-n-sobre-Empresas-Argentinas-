import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print("\n--- MODELOS DISPONIBLES (LISTA CRUDA) ---")
    
    # Iteramos directamente sin filtrar propiedades complejas
    pager = client.models.list() 
    
    for model in pager:
        # En la nueva SDK, a veces se accede como diccionario o como objeto
        # Intentamos obtener el nombre de ambas formas por seguridad
        try:
            name = getattr(model, 'name', None)
            if not name:
                name = model['name']
        except:
            name = str(model)

        print(f"Nombre encontrado: {name}")
        
        # Generamos la sugerencia limpia
        if "/" in str(name):
            clean_name = str(name).split("/")[-1]
            print(f"👉 PRUEBA PONER ESTO EN CONFIG.PY: {clean_name}")
        print("-" * 30)

except Exception as e:
    print(f"\n❌ Error fatal conectando: {e}")
    print("Verifica que tu API KEY sea correcta en el archivo .env")