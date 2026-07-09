# 🗄️ Esquema de Base de Datos y Modelo Relacional

<img src="/home/velizan/proyecto_bora/docs/der_edictosImagen.JPG" width="500" alt="Texto alternativo">

## 🧠 Decisiones de Diseño y Reglas de Negocio

[Seguro] La arquitectura relacional fue diseñada priorizando la integridad de los datos frente a la alta variabilidad de los textos legales, implementando restricciones estrictas a nivel de esquema:

* **Normalización de Atributos de Administración:** Para evitar la proliferación de columnas innecesarias o tablas de catálogos redundantes, la tabla `participacion_admin` consolida la naturaleza del rol utilizando una única columna `condicion`. Esto centraliza el estado del administrador (ej. Titular, Suplente) manteniendo el esquema flexible.
* **Aislamiento de Dominios (Cero Duplicación):** El modelo prohíbe la duplicación de entidades físicas. Ante escenarios donde los socios asumen funciones de control (cuando se prescinde de sindicatura), los registros no se duplican hacia las tablas de fiscalización. La separación estructural entre `participacion_socios` y `participacion_sindicatura` asegura que no haya datos redundantes.
* **Protección contra Ingesta Interrumpida (Upserts):** Las tablas de participación (`participacion_socios`, `participacion_admin`, `participacion_sindicatura`) implementan restricciones `UNIQUE(id_sociedad, id_entidad)`. Esto garantiza la idempotencia del script de extracción: si la canalización falla y se reinicia, la base de datos rechazará automáticamente la duplicación de roles.
* **Tolerancia a Datos Incompletos:** Entidades como el `cuit` en la tabla `sociedad` carecen de restricción `NOT NULL`, adaptándose a edictos en los que dicha información es omitida por el Boletín Oficial al momento de la publicación.

## 📖 Diccionario de Datos

### 1. Entidad Principal (Core)

**`sociedad`**
Almacena la cabecera de los edictos comerciales.

| Columna | Tipo | Restricción | Descripción |
| --- | --- | --- | --- |
| `id_sociedad` | BIGINT | PK | Identificador único autoincremental. |
| `denominacion` | TEXT |  | Razón social de la empresa. |
| `cuit` | TEXT |  | Clave de identificación tributaria (con guiones). |
| `anio_bo` | INTEGER |  | Año de publicación en el Boletín Oficial. |
| `capital_social` | NUMERIC |  | Monto del capital constitutivo. |
| `fecha_constitucion` | DATE |  | Fecha formal de constitución. |
| `id_objeto1, 2, 3` | BIGINT | FK | Referencias a los objetos societarios (Comercial, Servicios, etc). |

### 2. Entidades Físicas (Actores)

Las tablas almacenan los perfiles demográficos. El esquema separa a los individuos según su dominio de acción inicial para facilitar el filtrado analítico.

* **`socios`**: Almacena `dni`, `nombre_completo`, `edad` y referencia al `id_genero`.
* **`administrador`**: Contiene la información demográfica de los gestores ejecutivos de la sociedad.
* **`sindicatura`**: Registra a las personas encargadas de la fiscalización de las sociedades.

### 3. Tablas de Relación (Participaciones N:M)

Conectan a las entidades físicas con las sociedades en las que operan, absorbiendo los atributos específicos de esa relación.

**`participacion_socios`**

| Columna | Tipo | Restricción | Descripción |
| --- | --- | --- | --- |
| `id_sociedad` | BIGINT | PK, FK | Referencia a la sociedad (`ON DELETE CASCADE`). |
| `id_socio` | BIGINT | PK, FK | Referencia al socio (`ON DELETE CASCADE`). |
| `porcentaje` | NUMERIC |  | Participación accionaria/cuotas. |
| `cantidad_votos` | INTEGER |  | Poder de votación según estatuto. |
| *(Misma lógica de restricciones aplica para `participacion_admin` manejando `cargo` y `condicion`, y para `participacion_sindicatura` manejando `condicion_fiscal`).* |  |  |  |

### 4. Catálogos (Tablas de Búsqueda)

Tablas estáticas referenciadas para mantener la consistencia del texto extraído por la IA:

* `genero`: Estandarización de género (H, M, X).
* `objeto`: Tipificación económica (Industrial, Comercial, Servicios, Inmobiliario, Agropecuario).
* `tipo_societaria`: Naturaleza jurídica (SA, SAS, SRL).
* `nueva_preexistente`: Estado operativo inicial de la entidad.
* `tipo_fiscalizacion`: Órgano de control (Sindicatura, Socios).

---
