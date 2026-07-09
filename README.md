## ⚖️ Boletín Oficial Data Pipeline: De Texto Plano a Inteligencia de Negocios
**🚀 El Impacto**
La constitución de sociedades comerciales en Argentina genera un volumen masivo de datos no estructurados. Tradicionalmente, la lectura, interpretación manual y clasificación de los datos de un edicto (socios, capital, autoridades) demanda aproximadamente 20 minutos por documento.

Este proyecto implementa una canalización automatizada mediante IA que reduce el tiempo de procesamiento a 50 segundos por edicto. Se logró estructurar y persistir un lote histórico completo de 8.200 edictos con un costo operativo de infraestructura (API) de aproximadamente $25 USD.

## **🏗️ Arquitectura del Sistema**
El flujo de datos se divide en tres fases principales que separan la extracción, el almacenamiento y la visualización:

Extracción y Estructuración (Python + Gemini 2.5 Flash): Procesamiento de documentos de texto para extraer entidades legales complejas hacia un esquema JSON estricto. Se implementó una lógica de resiliencia que maneja un 15% de varianza en los formatos de origen (múltiples edictos por archivo) y fallos de respuesta del modelo mediante reintentos automáticos y segmentación.

Persistencia Relacional (Supabase / PostgreSQL): Inserción automatizada en una base de datos normalizada. El diseño del esquema prioriza la integridad de los datos evitando redundancias; por ejemplo, la tabla participacion_admin gestiona los roles mediante una columna consolidada de condicion (sin segmentar tipos de administración), y se evita deliberadamente la duplicación de datos de los socios hacia las tablas del órgano de fiscalización.

Inteligencia de Negocios (Power BI): Conexión directa a la base de datos para la generación de tableros interactivos y análisis de mercado.

## **📊 Análisis y Descubrimientos**
(Nota: Las visualizaciones detalladas se encuentran en la carpeta /dashboards)

La estructuración de estos datos permitió exponer métricas clave del tejido empresarial reciente, incluyendo:

Distribución del Objeto Societario: El 35% de las nuevas empresas se orientan al sector Comercial. Le siguen en volumen el sector de Servicios, Industrial, Inmobiliario y, por último, Agropecuario.

Composición Demográfica: Análisis detallado de la participación societaria segmentada por género.

## **🛠️ Desafíos Técnicos y Hoja de Ruta (Roadmap)**
Esta arquitectura fue concebida inicialmente como una ejecución por lotes (one-off batch) para ingestar un rezago histórico. Las lecciones aprendidas sobre concurrencia y límites de tasa de la API definen las siguientes oportunidades de mejora estructural:

Gestión de Estado Transaccional: La tolerancia a fallos actual se maneja mediante el consumo destructivo del directorio de origen (los archivos procesados se eliminan para permitir la reanudación). La próxima iteración reemplazará este enfoque con una base de datos local ligera (ej. SQLite) para mantener un estado estricto de cada documento (procesado, pendiente, error), aislando los archivos físicos de la lógica del script.

Ingesta Incremental Continua: Evolucionar el sistema de un procesamiento por lotes a una arquitectura preparada para ingestar actualizaciones incrementales diarias a medida que se publican nuevos edictos.
