import sqlite3
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import re
import shutil
import PyPDF2

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_PATH = "store.db"
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Almacena el último texto cargado para RAG
last_uploaded_text = ""

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class QueryRequest(BaseModel):
    question: str

def adaptar_sql_para_sqlite(sql_query: str) -> str:
    # Reemplaza SELECT TOP N ... por SELECT ... LIMIT N
    import re
    # Detecta SELECT TOP N ... FROM ...
    top_match = re.match(r'(SELECT)\s+TOP\s+(\d+)\s+(.*?FROM\s+.+)', sql_query, re.IGNORECASE)
    if top_match:
        select, top_n, rest = top_match.groups()
        # Quita TOP N y agrega LIMIT N al final
        sql_query = f"{select} {rest} LIMIT {top_n}"
    # Reemplaza YEAR(Fecha) por strftime('%Y', Fecha)
    sql_query = re.sub(r'YEAR\(([^)]+)\)', r"strftime('%Y', \1)", sql_query, flags=re.IGNORECASE)
    # Reemplaza comillas simples dobles por simples
    sql_query = sql_query.replace("''", "'")
    return sql_query

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Leer el texto del archivo (txt o pdf)
    global last_uploaded_text
    try:
        if file.filename.lower().endswith('.pdf'):
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            last_uploaded_text = text
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                last_uploaded_text = f.read()
        return JSONResponse({"message": f"Archivo '{file.filename}' subido y listo para consulta RAG."})
    except Exception as e:
        last_uploaded_text = ""
        return JSONResponse({"message": f"Archivo subido pero no se pudo leer el texto: {e}"})

@app.post("/ask")
def ask_question(req: QueryRequest):
    question = req.question
    # Si hay texto cargado, usarlo como contexto para RAG
    if last_uploaded_text:
        # Prompt para RAG
        prompt = f"""Eres un asistente experto. Usa el siguiente contexto para responder la pregunta de la forma más precisa posible. Si el contexto no es suficiente, responde lo mejor posible.

Contexto:
{last_uploaded_text}

Pregunta: {question}
Respuesta:"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content
        return {"response": result}
    # --- FLUJO ORIGINAL SQL ---
    # 1. Leer el prompt base desde archivo externo
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt_base = f.read()
    prompt = prompt_base.replace("{question}", question)
    # 2. Consultar a OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content
    # 3. Extraer el query SQL de la respuesta
    sql_blocks = re.findall(r'```sql\s*([\s\S]+?)\s*```', result, re.IGNORECASE)
    sql_query = None
    if sql_blocks:
        for block in sql_blocks:
            if re.search(r'\bSELECT\b|\bUPDATE\b|\bDELETE\b|\bINSERT\b', block, re.IGNORECASE):
                sql_query = block.strip()
                break
        if not sql_query:
            sql_query = sql_blocks[0].strip()
    else:
        lines = result.splitlines()
        for line in lines:
            if re.match(r'\s*(SELECT|UPDATE|DELETE|INSERT) ', line, re.IGNORECASE):
                sql_query = line.strip()
                break
    if not sql_query:
        return {"response": "No se pudo extraer el query SQL de la respuesta."}
    # --- ADAPTAR SQL PARA SQLITE ---
    sql_query = adaptar_sql_para_sqlite(sql_query)
    # 4. Ejecutar el query en la base de datos local
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
    except Exception as e:
        return {"response": f"Error al ejecutar el query SQL: {e}"}
    # 5. Construir la tabla HTML
    table_html = '<table border="1"><tr>' + ''.join(f'<th>{col}</th>' for col in columns) + '</tr>'
    for row in rows:
        table_html += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
    table_html += '</table>'
    # 6. Extraer la interpretación
    interp_match = re.search(r'Interpretaci[oó]n:\s*(.*?)\n(Resultados:|Query:|$)', result, re.DOTALL)
    interpretacion = interp_match.group(1).strip() if interp_match else ""
    interpretacion = interpretacion.split('Query:')[0].strip()
    # 7. Responder con interpretación, tabla real y query
    respuesta = (
        f"<div style='margin-bottom:18px;'><b>Interpretación:</b><br>{interpretacion}</div>"
        f"<div style='margin-bottom:18px; text-align:center;'>{table_html}</div>"
        f"<div class='small' style='margin-top:18px; color:#555;'><b>Query SQL generado:</b><br><code style='font-size:0.95em'>{sql_query}</code></div>"
    )
    return {"response": respuesta}