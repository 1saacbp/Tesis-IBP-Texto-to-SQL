# ===============================
# Imports
# ===============================
from llama_cpp import Llama
import multiprocessing
import sqlite3
import json

conn = sqlite3.connect("src/TasaDeInteres/mi_base.db")
cursor = conn.cursor()
n_threads = multiprocessing.cpu_count()

llm = Llama(
    model_path="models/mistral-7b-v0.1.Q4_K_M.gguf",
    n_threads=n_threads,
    n_ctx=4096,#4096 funciona bien
    n_batch=512,
    verbose=False
)
def generar_sql(pregunta):

    prompt = f"""
### Instruction:
Genera la consulta SQL correcta para la siguiente pregunta.

### Question:
{pregunta}

### Schema:
CREATE TABLE Entidades (
    id_entidad INTEGER PRIMARY KEY,tipo_entidad INTEGER,nombre_tipo_entidad TEXT,codigo_entidad INTEGER,
    nombre_entidad TEXT
);
CREATE TABLE Municipio (
    codigo_municipio INTEGER PRIMARY KEY,municipio TEXT,departamento TEXT
);
CREATE TABLE Ciiu (
    codigo_ciiu INTEGER PRIMARY KEY,actividad_economica TEXT
);
CREATE TABLE Deudor (
    id_deudor INTEGER PRIMARY KEY,tipo_persona TEXT,sexo TEXT,
    clase_deudor TEXT,codigo_municipio INTEGER,codigo_ciiu INTEGER,grupo_etnico TEXT ,
    antiguedad_empresa TEXT,tamano_empresa TEXT,
);
CREATE TABLE Credito (
    id_credito INTEGER PRIMARY KEY,fecha_corte TEXT,
    tipo_credito TEXT ,tipo_garantia TEXT,
    producto_credito TEXT ,plazo_credito TEXT,tasa_efectiva_promedio_ponderada REAL,
    margen_adicional REAL,monto_desembolsado INTEGER,numero_creditos_desembolsados INTEGER,
    tipo_tasa TEXT,rango_monto_desembolsado TEXT,id_deudor INTEGER,id_entidad INTEGER
);

### Response:
"""

    output = llm(
        prompt,
        max_tokens=90,
        temperature=0,
        stop=["###"]
    )

    sql = output["choices"][0]["text"].strip()
    sql = sql.replace("SQL:", "").replace("```sql","").replace("```","")

    return sql.strip()

dataset = []

with open("data/TasaDeInteres/validation.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        dataset.append(json.loads(line))


exact_match = 0
execution_correct = 0
execution_error = 0
total = len(dataset)
print(len(dataset))

#verificación de validez de los ejemplos gold
valid = 0
invalid = 0

errores = []
for i, row in enumerate(dataset):

    sql_gold = row["output"] 

    try:
        res_gold = cursor.execute(sql_gold).fetchall()
        valid += 1

    except Exception as e:

        invalid += 1

        errores.append({
            "index": i,
            "sql": sql_gold,
            "error": str(e)
        }
)
print(f"SQL válidos: {valid}")
print(f"SQL inválidos: {invalid}")
#------------------------------------
for row in dataset:

    pregunta = row["input"]
    sql_gold = row["output"]

    sql_modelo = generar_sql(pregunta)

    print("\nPregunta:", pregunta)
    print("SQL modelo:", sql_modelo)
    print("SQL gold:", sql_gold)

    # EXACT MATCH
    if sql_modelo.lower().strip() == sql_gold.lower().strip():
        exact_match += 1

    try:

        res_gold = cursor.execute(sql_gold).fetchall()
        res_model = cursor.execute(sql_modelo).fetchall()

        if res_gold == res_model:
            execution_correct += 1

    except Exception as e:
        execution_error += 1
        print("Error ejecución:", e)


conn.close()
print("\n----- RESULTADOS -----")

print("Total preguntas:", total)

print("Exact Match:", exact_match / total)

print("Execution Accuracy:", execution_correct / total)

print("Error Rate:", execution_error / total)