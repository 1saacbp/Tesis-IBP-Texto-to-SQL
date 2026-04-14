import streamlit as st
from llama_cpp import Llama
import multiprocessing
import sqlite3
import pandas as pd

st.title("SQLCoder - GENERADOR DE CONSULTAS SQL")

DB_PATH = "src/TasaDeInteres/mi_base.db"

@st.cache_resource
def cargar_llm():
    return Llama(
        model_path="models/mistral_fineT_q4km.gguf",
        n_threads=multiprocessing.cpu_count(),
        n_ctx=2058,
        verbose=False
    )
def obtener_schema():
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    schema = ""
    for (tabla,) in tablas:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{tabla}';")
        ddl = cursor.fetchone()[0]
        schema += ddl + ";\n\n"
    con.close()
    return schema

def ejecutar_sql(query: str):
    con = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, con)
        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        con.close()

def extraer_sql(texto: str) -> str:
    texto = texto.strip()
    if "```sql" in texto:
        texto = texto.split("```sql")[1].split("```")[0]
    elif "```" in texto:
        texto = texto.split("```")[1].split("```")[0]
    return texto.strip()

llm = cargar_llm()
schema = obtener_schema()

with st.expander("📋 Ver schema de la base de datos"):
    st.code(schema, language="sql")
    
prompt = st.text_area("Pregunta en lenguaje natural", value="")

if st.button("Generar y ejecutar SQL"):
    if not prompt.strip():
        st.warning("Escribe una pregunta primero.")
    else:
        with st.spinner("Generando consulta SQL..."):
            output = llm(
                f"""### Instruction:
Genera la consulta SQL correcta para la siguiente pregunta.

### Input:
{prompt}

### Output:
""",
                max_tokens=128,
                temperature=0.2,
                stop=["###","n\n",";"],
                echo=False,
                top_k=20
            )
            sql = extraer_sql(output["choices"][0]["text"])

        st.subheader("SQL generado")
        st.code(sql, language="sql")

        st.subheader("Resultado")
        df, error = ejecutar_sql(sql)
        if error:
            st.error(f"Error al ejecutar la consulta: {error}")
        elif df.empty:
            st.info("La consulta no devolvió resultados.")
        else:
            st.dataframe(df, use_container_width=True)