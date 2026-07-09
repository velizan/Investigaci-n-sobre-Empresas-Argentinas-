# Inicialización de clientes (Supabase, Gemini)
import os
from dotenv import load_dotenv
from supabase import create_client
from google import genai  # Esta es la librería nueva

load_dotenv()

# Cliente Supabase (se mantiene igual)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# NUEVO Cliente Gemini (reemplaza a configure y GenerativeModel)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Definimos el ID del modelo sin el prefijo "models/"
MODEL_ID = "gemini-2.5-flash"