# tec2025sql

**Agente SQL para análisis de datos de negocio**  
Asistente conversacional para responder preguntas de negocio sobre ventas, productos y distribuidores, usando una base de datos SQLite y un modelo de lenguaje (OpenAI GPT-4) para generar y ejecutar consultas SQL automáticamente.

---

## Contenido del proyecto

- **main.py**  
  API principal construida con FastAPI. Expone dos endpoints:
  - `/` (GET): Muestra la interfaz web (chat) para interactuar con el asistente.
  - `/ask` (POST): Recibe preguntas en lenguaje natural, consulta a OpenAI para generar el SQL, ejecuta la consulta en la base de datos y devuelve la interpretación, resultados y el query SQL generado.

- **create_db.py**  
  Script para crear y poblar la base de datos `store.db` con datos de ejemplo:
  - Crea las tablas `Productos`, `Distribuidores` y `Ventas`.
  - Inserta 100 productos, 20 distribuidores y 300 ventas simuladas.

- **prompt.txt**  
  Prompt base que guía al modelo de lenguaje para interpretar preguntas de negocio, generar consultas SQL y explicar los resultados de forma profesional y clara.

- **templates/index.html**  
  Interfaz web (chat) para interactuar con el asistente. Permite enviar preguntas y visualizar respuestas con tablas y explicaciones.

- **requirements.txt**  
  Lista de dependencias necesarias para ejecutar el proyecto (FastAPI, Uvicorn, OpenAI, Pydantic, Jinja2, LangGraph, LangChain).

---

## ¿Cómo funciona?

1. **Inicialización de la base de datos**  
   Ejecuta `create_db.py` para crear y poblar la base de datos SQLite con datos de ejemplo.

2. **Ejecución del servidor**  
   Inicia el servidor FastAPI (`uvicorn main:app --reload`).  
   Accede a la interfaz web en `http://localhost:8000`.

3. **Interacción**  
   - El usuario escribe una pregunta de negocio (ej: "¿Cuáles son los productos más vendidos?").
   - El backend lee el prompt base, inserta la pregunta y consulta a OpenAI.
   - El modelo genera una interpretación, un query SQL y una tabla de resultados.
   - El backend ejecuta el SQL en la base de datos local y muestra los resultados y la explicación en la web.

---

## Estructura de la base de datos

- **Productos**
  - `CveArticulo` (INT, PK)
  - `Nombre_Articulo` (VARCHAR)
  - `Categoria` (VARCHAR)
  - `TamanioDeFoto` (VARCHAR)
  - `TamanioFotoConNumero` (FLOAT)
  - `NumeroPagina` (INT)
  - `NumeroPaginaCatalogo` (VARCHAR)
  - `Posicion` (VARCHAR)
  - `Rango_PN_Nuevo` (VARCHAR)
  - `Rango_PE_Nuevo` (VARCHAR)
  - `TBasica` (VARCHAR)
  - `Precio_Especial_Unitario` (FLOAT)
  - `Precio_Normal_Unitario` (FLOAT)

- **Distribuidores**
  - `ClaveDistribuidor` (VARCHAR, PK)
  - `Clasificacion` (VARCHAR)
  - `Cod_Aso` (INT)
  - `Municipio` (VARCHAR)
  - `Estado` (VARCHAR)
  - `Zona_Metropolitana` (VARCHAR)

- **Ventas**
  - `id` (INTEGER, PK, AUTOINCREMENT)
  - `Catálogo` (INT)
  - `ClaveDistribuidor` (VARCHAR, FK)
  - `CveArticulo` (INT, FK)
  - `Descuento` (FLOAT)
  - `RangoDescuentos` (VARCHAR)
  - `UnidadesVendidas` (INT)
  - `VentaCatalogo` (FLOAT)
  - `Fecha` (DATE)

---

## Detalle de cada archivo

- **main.py**  
  - Define la API y la lógica para recibir preguntas, consultar a OpenAI, extraer y adaptar el SQL, ejecutar la consulta y devolver resultados.
  - Incluye funciones para adaptar queries a SQLite y construir respuestas HTML.

- **create_db.py**  
  - Elimina y crea las tablas necesarias.
  - Inserta datos de ejemplo realistas para pruebas y demostraciones.

- **prompt.txt**  
  - Define el comportamiento del asistente: interpretación de preguntas, generación de SQL, formato de respuesta y reglas de negocio para métricas frecuentes.

- **templates/index.html**  
  - Interfaz de usuario moderna y responsiva.
  - Permite enviar preguntas y ver respuestas con tablas y explicaciones.

- **requirements.txt**  
  - Dependencias para el backend, frontend y conexión con OpenAI.

---

## Ejemplo de uso

1. Ejecuta el script de base de datos:
   ```
   python create_db.py
   ```
2. Inicia el servidor:
   ```
   uvicorn main:app --reload
   ```
3. Abre tu navegador en `http://localhost:8000` y escribe preguntas como:
   - "¿Cuáles son los productos más vendidos?"
   - "¿Cuál es el descuento promedio por categoría?"
   - "¿Cuántos distribuidores hay por estado?"

---

## Notas

- El asistente está optimizado para responder preguntas de negocio, no técnicas.
- El modelo adapta automáticamente queries a SQLite.
- Puedes modificar los datos de ejemplo en `create_db.py` según tus necesidades.


