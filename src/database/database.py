# Funciones de inserción (CRUD)

from src.database.config import supabase

# --- 2. MÓDULO DE SOCIEDAD ---
def gestionar_sociedad(datos_sociedad):
    # Separamos los campos de la lista para la tabla 'sociedad'
    campos_sociedad = {
        "denominacion": datos_sociedad.get('denominacion'),
        "cuit": datos_sociedad.get('cuit'),
        "anio_bo": datos_sociedad.get('anio_bo'),
        "capital_social": datos_sociedad.get('capital_social'),
        "fecha_constitucion": datos_sociedad.get('fecha_constitucion'),
        "id_objeto": datos_sociedad.get('id_objeto'),
        "id_nueva_preexistente": datos_sociedad.get('id_nueva_preexistente'),
        "id_tipo_societaria": datos_sociedad.get('id_tipo_societaria'),
        "id_tipo_fiscalizacion": datos_sociedad.get('id_tipo_fiscalizacion')
    }

    # Para ser idéntico al SQL: INSERT directo
    res = supabase.table("sociedad").insert(campos_sociedad).execute()
    
    if res.data:
        return res.data[0]['id_sociedad']
    raise Exception("No se pudo insertar la sociedad")

# --- 3. MÓDULO DE SINDICATURA (ROBUSTO) ---
def registrar_sindicatura(lista_sindicatura, id_sociedad):
    if not lista_sindicatura: return

    for s in lista_sindicatura:
        # 1. Insertar en maestro de sindicatura (idéntico al SQL)
        res_s = supabase.table("sindicatura").insert({
            "dni": s.get('dni'),
            "nombre_completo": s.get('nombre_completo'),
            "id_genero": s.get('id_genero')
        }).execute()

        if res_s.data:
            id_sindi = res_s.data[0]['id_sindicatura']
            
            # 2. Insertar en tabla intermedia
            supabase.table("participacion_sindicatura").insert({
                "id_sociedad": id_sociedad,
                "id_sindicatura": id_sindi,
                "condicion_fiscal": s.get('condicion_fiscal', 'Titular')
            }).execute()

# --- 4. MÓDULO DE SOCIOS (ROBUSTO) ---
def registrar_socios(lista_socios, id_sociedad):
    """
    Inserta socios y sus participaciones. 
    Alineado con la función SQL cargar_edicto_completo.
    """
    if not lista_socios: 
        return 
    
    for s in lista_socios:
        try:
            # 1. Insertar Socio (Equivale al INSERT INTO public.socios del SQL)
            # Nota: Si el DNI ya existe y es PK, esto fallará. 
            # Si quieres evitarlo, usa .upsert(..., on_conflict='dni')
            res_p = supabase.table("socios").insert({
                "dni": s.get('dni'),
                "nombre_completo": s.get('nombre_completo'), 
                "edad": s.get('edad'),
                "id_genero": s.get('id_genero')
            }).execute()
            
            if not res_p.data:
                continue
                
            id_socio_db = res_p.data[0]['id_socio']
            
            # 2. Vincular Participación (Equivale al Paso 2.2 del SQL)
            # Usamos insert para ser idénticos al SQL
            supabase.table("participacion_socios").insert({
                "id_sociedad": id_sociedad, 
                "id_socio": id_socio_db,
                "porcentaje": s.get('porcentaje'), 
                "cantidad_votos": s.get('cantidad_votos', 0)
            }).execute()

        except Exception as e:
            print(f"Error procesando socio {s.get('nombre_completo')}: {e}")

# --- 5. MÓDULO DE ADMINISTRADORES (ROBUSTO) ---
def registrar_administradores(lista_admins, id_sociedad):
    if not lista_admins: return

    for a in lista_admins:
        try:
            # 1. Insertar Administrador
            # Usamos insert simple para replicar comportamiento SQL
            res_a = supabase.table("administrador").insert({
                "dni": a.get('dni'), 
                "nombre_completo": a.get('nombre_completo'), 
                "id_genero": a.get('id_genero')
            }).execute()
            
            # Validación de seguridad: Si falló el insert, saltamos al siguiente
            if not res_a.data:
                print(f"Error insertando admin: {a.get('nombre_completo')}")
                continue

            id_admin_db = res_a.data[0]['id_admin']
            
            # 2. Calcular condición (Lógica COALESCE + Capitalize)
            condicion_raw = a.get('condicion')
            # Si es None o string vacío, usa 'Titular'. Si no, lo capitaliza.
            condicion_final = condicion_raw.capitalize() if condicion_raw else 'Titular'
            
            cargo_final = a.get('cargo')
            if cargo_final: cargo_final = cargo_final.capitalize()

            # 3. Insertar Participación
            supabase.table("participacion_admin").upsert({
                "id_sociedad": id_sociedad, 
                "id_admin": id_admin_db,
                "cargo": cargo_final, 
                "condicion": condicion_final 
            }, on_conflict='id_sociedad, id_admin').execute()

        except Exception as e:
            print(f"Excepción procesando administrador {a.get('dni')}: {e}")


# 5. INCORPORACIÓN TARDÍA DE OBJETOS

def gestionar_objetos(datos_sociedad):
    denominacion = datos_sociedad.get("denominacion")
    cuit = datos_sociedad.get("cuit")
    anio_bo = datos_sociedad.get("anio_bo")
    
    # Estructuramos los campos de los objetos tal cual se llaman en tu BD
    campos_objetos = {
        "id_objeto1": datos_sociedad.get("id_objeto1"),
        "id_objeto2": datos_sociedad.get("id_objeto2"),
        "id_objeto3": datos_sociedad.get("id_objeto3")
    }
    
    id_existente = None

    # REGLA 2: Si denominacion y cuit son nulos a la vez, no buscamos coincidencia.
    # Se saltará la búsqueda e irá directo a la creación de una nueva instancia.
    if denominacion is not None or cuit is not None:
        
        # Iniciamos la consulta base
        query = supabase.table("sociedad").select("id_sociedad")
        
        # REGLA 2: Si el CUIT es nulo pero la denominación NO, buscamos solo por denominación
        if cuit is None:
            query = query.eq("denominacion", denominacion)
        else:
            # Si el CUIT existe, buscamos por coincidencia de ambos campos (Denominación Y CUIT)
            query = query.eq("denominacion", denominacion).eq("cuit", cuit)
            
        res_busqueda = query.execute()
        
        # Si encontramos al menos un registro previo que coincida
        if res_busqueda.data:
            id_existente = res_busqueda.data[0]['id_sociedad']

    # --- CASO A: SI HUBO COINCIDENCIA -> ACTUALIZAR ---
    if id_existente:
        # Modificamos únicamente las columnas correspondientes a los objetos
        res_update = supabase.table("sociedad").update(campos_objetos).eq("id_sociedad", id_existente).execute()
        
        if res_update.data:
            return res_update.data[0]['id_sociedad']
        raise Exception(f"No se pudieron actualizar los objetos para la sociedad con ID {id_existente}")
        
    # --- CASO B: NO HUBO COINCIDENCIA (O AMBOS ERAN NULOS) -> CREAR NUEVA INSTANCIA ---
    else:
        # REGLA 3 y 4: Armamos el diccionario para el INSERT. 
        # Si id_objeto2 o id_objeto3 no vienen en el JSON, .get() devolverá None (null en Supabase).
        nueva_sociedad = {
            "denominacion": denominacion,
            "cuit": cuit,
            "anio_bo": anio_bo,  # Incluido si aparece en el JSON
            **campos_objetos
        }
        
        res_insert = supabase.table("sociedad").insert(nueva_sociedad).execute()
        
        if res_insert.data:
            return res_insert.data[0]['id_sociedad']
        raise Exception("No se pudo insertar la nueva instancia de la sociedad")